# Common import
from typing import Optional, Dict
import asyncio
import multiprocessing
import traceback
import Utils
import logging
logger = logging.getLogger("Client")

# For Bizhawk client
from typing import TYPE_CHECKING
from NetUtils import ClientStatus
import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext, BizHawkClientCommandProcessor

# Game title dedicated
from . import Locations, Items
from .Options import GAME_TITLE, GAME_TITLE_FULL
from .Crash2Addresses import LOCATIONS, CHECK_TYPE, COMPARE_TYPE, ADDRESSES, LEVEL
CLIENT_INIT_LOG=f"{GAME_TITLE} Client"
CLIENT_VERSION="v0.1.0"


def CommandProcessor(self: "BizHawkClientCommandProcessor"):
    # This is not mandatory for the game. Just a client command implementation.
    # def _cmd_kill(self):
    #     """Kill the game."""
    #     if isinstance(self.ctx, Crash2Context):
    #         self.ctx.game_interface.kill_player()
    pass


class Crash2Client(BizHawkClient):
    game = f"{GAME_TITLE_FULL}"
    system = "PSX"
    patch_suffix = ".apcrash2"

    # Client variables
    command_processor = CommandProcessor
    slot_data: Optional[dict[str, Utils.Any]] = None
    last_error_message: Optional[str] = None
    notification_queue: list[str] = []
    notification_timestamp: float = 0
    showing_notification: bool = False
    deathlink_timestamp: float = 0
    death_link_enabled = False
    queued_deaths: int = 0
    items_handling = 0b111 # This is mandatory
    location_table = []
    # For Bizhawk client
    server = None
    server_address = None
    connect_address = None
    _messagebox_connection_loss = False
    disconnected_intentionally = False
    current_reconnect_delay = 0
    autoreconnect_task = None
    max_size = 10_000_000  # 適当なバッファサイズでOK
    def handle_connection_loss(self, message: str): logger.warning(f"Connection lost: {message}")
    async def connection_closed(self): pass
    def cancel_autoreconnect(self): pass


    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            # Check ROM name/patch version
            rom_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(ADDRESSES["SCPS-10047"]["GAME_ID"], 10, "MainRAM")]))[0]).decode("ascii")
            if rom_name != "SCPS-10047":
                return False  # Not a MYGAME ROM
        except bizhawk.RequestFailedError:
            return False  # Not able to get a response, say no for now

        # This is a MYGAME ROM
        ctx.game = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True
        ctx.game_id = rom_name

        # initialize variables
        await init_function(ctx)
        
        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        try:
            if ctx.slot_data is not None:
                # Check recieved items
                await handle_received_items(ctx)
                # Check archieved locations
                await handle_checked_locations(ctx)
                # Check goal is checked or not
                await handle_check_goal(ctx)
                # Check and Modify in game memory for randomizer
                await handle_memory_update(ctx)

        except bizhawk.RequestFailedError:
            # The connector didn't respond. Exit handler and return to main loop to reconnect
            pass


    def notification(self, text: str):
        self.notification_queue.append(text)

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = f"{GAME_TITLE} Client v{CLIENT_VERSION}"
        if tracker_loaded:
            ui.base_title += f" | Universal Tracker {UT_VERSION}"

        # AP version is added behind this automatically
        ui.base_title += " | Archipelago"
        return ui

    def on_package(self, ctx, cmd: str, args: dict):
        super().on_package(ctx, cmd, args)
        if cmd == "Connected":
            logger.info(f"================================================\n"
                        f"    -- Connected to Bizhawk successfully! --    \n"
                        f"      Archipelago Crash2 version {CLIENT_VERSION}\n"
                        f"================================================\n")
            ctx.slot_data = args["slot_data"]
            # logger.info(f"Received data: {args}")
            ctx.location_table = ctx.server_locations # list


############################################
# Common Function for Client               #
############################################
async def handle_received_items(ctx: 'Context') -> None:
    """共通的なアイテム受信処理。"""
    if ctx.slot_data is None:
        return

    # 初回だけ記録用に items_received の長さを記憶しておく
    if not hasattr(ctx, "processed_item_count"):
        ctx.processed_item_count = -1
        new_items = ctx.items_received[0:]
    else:
        new_items = ctx.items_received[ctx.processed_item_count:]

    for index, item in enumerate(new_items):
        item_id = item.item
        await item_received(ctx, item_id, ctx.processed_item_count)
        # logger.info(f"Received item: ({item_id})")
        
    ctx.processed_item_count = len(ctx.items_received)


async def handle_checked_locations(ctx: 'Context') -> None:
    """共通的なロケーションチェック処理。"""
    if ctx.slot_data is None:
        return

    # logger.info(f"{ctx.location_table}")
    new_checks = []
    for ap_code in ctx.location_table:
        if ap_code in ctx.checked_locations:
            continue
        if await is_location_checked(ctx, ap_code) is True:
            new_checks.append(ap_code)

    if new_checks:
        await ctx.send_msgs([{"cmd": 'LocationChecks', "locations": new_checks}])
        ctx.locations_checked.update(new_checks)
    # else:
    #     logger.info("Not found new location")

async def handle_check_goal(ctx: 'Context') -> None:
    """Checks if the goal is completed"""
    if ctx.slot_data is None:
        return

    victory_code = get_victory_code(ctx)
    if victory_code in ctx.checked_locations:
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]) 

async def handle_memory_update(ctx: 'Context') -> None:
    """Checks and modify memory for randomizer"""
    if ctx.slot_data is None:
        return
    await memory_update(ctx)



#####################################
# Utility functions for memory edit #
#####################################

async def _read8(ctx, addr):
    _val = await bizhawk.read(ctx.bizhawk_ctx, [(addr, 1, "MainRAM")] )
    return int.from_bytes(_val[0], byteorder='little')
async def _read16(ctx, addr):
    _val = await bizhawk.read(ctx.bizhawk_ctx, [(addr, 2, "MainRAM")] )
    return int.from_bytes(_val[0], byteorder='little')    
async def _read32(ctx, addr):
    _val = await bizhawk.read(ctx.bizhawk_ctx, [(addr, 4, "MainRAM")] )
    return int.from_bytes(_val[0], byteorder='little')

async def _write8(ctx, addr, value):
    write_value = [value]
    await bizhawk.write(ctx.bizhawk_ctx, [(addr, write_value, "MainRAM")] )

async def _write16(ctx, addr, value): # Not tested
    write_value = [ (value >> 8*x)&0xff for x in range(2)]
    await bizhawk.write(ctx.bizhawk_ctx, [(addr, write_value, "MainRAM")] )

async def _write32(ctx, addr, value): # Not tested
    write_value = [ (value >> 8*x)&0xff for x in range(4)]
    await bizhawk.write(ctx.bizhawk_ctx, [(addr, write_value, "MainRAM")] )

################################################################
# Dedicated Function for Client, which called common functions #
################################################################
async def init_function(ctx):
    ctx.power_stone = 0
    ctx.white_gem = 0
    ctx.red_gem = 0
    ctx.blue_gem = 0
    ctx.yellow_gem = 0
    ctx.green_gem = 0
    ctx.purple_gem = 0
    
    ctx.power_stone_wait_counter = [0] * 8 # 0x6DBA0 ~ 6DBA7 8bytes

def get_victory_code(ctx):
    victory_name = "Boss05" # This must can be changed by option
    return Locations.location_table[victory_name].ap_code

async def item_received(ctx, item_code, item_count):
    # logger.info(f"{item_code}")
    if item_code == 51000000: # power_stone
        ctx.power_stone += 1
    elif item_code == 51000001: # White Gem
        ctx.white_gem += 1
    elif item_code == 51000002: # Red Gem
        ctx.red_gem += 1
    elif item_code == 51000003: # Blue Gem
        ctx.blue_gem += 1
    elif item_code == 51000004: # Yellow Gem
        ctx.yellow_gem += 1
    elif item_code == 51000005: # Green Gem
        ctx.green_gem += 1
    elif item_code == 51000006: # Purple Gem
        ctx.purple_gem += 1
    else: # not implemented
        pass

async def is_location_checked(ctx, ap_code):
    target_location = {}
    # search target location
    for location in LOCATIONS:
        if location["Id"] == ap_code:
            target_location = location
            break
    #############################
    # Crash 2 Dedicated process #
    #############################
    # Only checking in WarpRoom
    addr = ADDRESSES[ctx.game_id]["CurrentLevel"]
    level = await _read8(ctx, addr)
    if level != LEVEL.WarpRoom:
        return False
    #############################
    # Crash 2 Dedicated process #
    #############################
    
    # Check location flag
    _value = 0
    addr = target_location["Address"]
    # addr = ctx.AddressConvert(addr)
    if target_location["CheckType"] == CHECK_TYPE.bit or \
        target_location["CheckType"] == CHECK_TYPE.falseBit:
        _value = await _read8(ctx, addr)
        _value = (_value >> target_location["AddressBit"]) & 0x01
    elif target_location["CheckType"] == CHECK_TYPE.byte:
        _value = await _read8(ctx, addr)
    elif target_location["CheckType"] == CHECK_TYPE.short:
        _value = await _read16(ctx, addr)
    else:
        _value = await _read32(ctx, addr)

    _compare_value = 0
    if target_location["CheckType"] == CHECK_TYPE.bit:
        _compare_value = 0x01
    elif target_location["CheckType"] == CHECK_TYPE.falseBit:
        _compare_value = 0x00
    else:
        _compare_value = int(target_location["CheckValue"], 0)

    _compare_type = COMPARE_TYPE.Match
    if 'CompareType' in target_location:
        _compare_type = target_location.CompareType

    if _compare_type == COMPARE_TYPE.Match:
        return (_value == _compare_value)
    elif _compare_type == COMPARE_TYPE.GreaterThan:
        return (_value > _compare_value)
    elif _compare_type == COMPARE_TYPE.LessThan:
        return (_value < _compare_value)


async def memory_update(ctx):
    # Get Current Level
    addr = ADDRESSES[ctx.game_id]["CurrentLevel"]
    level = await _read8(ctx, addr)

    # Check Powerstone and erase flag after location is found
    if level != LEVEL.WarpRoom:
        power_stone_location = set([loc["Address"] for loc in LOCATIONS if "Power Stone" in loc["name"] ])
        for idx, addr in enumerate(power_stone_location):
            mem = await _read8(ctx, addr)
            if mem == 0:
                continue
            # if mem is changed, wait for location is found then clear flag
            ctx.power_stone_wait_counter[idx] += 1
            if ctx.power_stone_wait_counter[idx] > 1:
                await _write8(ctx, addr, 0x00)
                ctx.power_stone_wait_counter[idx] = 0
    
    # Power stone checker
    dummy_power_stone_address_list = [0x6DBA0, 0x6DBA5, 0x6DBA6, 0x6DBA7]
    for i in range(ctx.power_stone//8+1):
        addr = dummy_power_stone_address_list[i]
        if i == (ctx.power_stone//8):
            values = [0x00, 0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3f, 0x7f, 0xff]
            await _write8(ctx, addr, values[(ctx.power_stone%8)])
        else:
            await _write8(ctx, addr, 0xff)
    
    # Logic Fixes
    ## Color Gem
    color_gem_addr = 0x6DA2B
    write_val = 0x00
    current_value = await _read8(ctx, color_gem_addr)
    if level != LEVEL.WarpRoom:
        value = 0
        if ctx.red_gem and level != LEVEL.Stage02:
            value |= 0x04
        if ctx.green_gem and level != LEVEL.Stage10:
            value |= 0x08
        if ctx.purple_gem and level != LEVEL.Stage20:
            value |= 0x10
        if ctx.blue_gem and level != LEVEL.Stage01:
            value |= 0x20
        if ctx.yellow_gem and level != LEVEL.Stage11:
            value |= 0x40
        write_val = (current_value | value)
    else:
        mask = 0x83 # 10000011
        write_val = (current_value & mask)
    await _write8(ctx, color_gem_addr, write_val)

##############################
# Other functions for coding #
##############################
