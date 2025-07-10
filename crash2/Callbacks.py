from typing import TYPE_CHECKING
from time import sleep, time
from random import randint

from NetUtils import ClientStatus
from CommonClient import logger

##################################################
# Only change point: Change filename/Class name  #
##################################################
if TYPE_CHECKING:
    from .Crash2Client import Context as Context
##################################################
# Only change point: Change filename/Class name  #
##################################################

# common functions
async def update(ctx: 'Context', ap_connected: bool) -> None:
    """Called continuously"""

    # Quite a lot of stuff ended up in this function, even though it might
    # have fit better in init(). It just didn't work when I put it there,
    # probably because of when the game loads stuff.

    if ap_connected and ctx.slot_data is not None:
        # Check recieved items
        await handle_received_items(ctx)
        # Check archieved locations
        await handle_checked_locations(ctx)
        # Check goal is checked or not
        await handle_check_goal(ctx)

        ctx.game_interface.Update()
        
        # logger.info(f"Update is called")


async def init(ctx: 'Context', ap_connected: bool) -> None:
    """Called when the player connects to the AP server or enters a new episode"""
    if ap_connected:
        # Initialize all date
        ctx.game_interface.Init()
        pass


async def handle_received_items(ctx: 'Context') -> None:
    """
    共通的なアイテム受信処理。
    """
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
        ctx.game_interface.item_received(item_id, ctx.processed_item_count)
        # logger.info(f"Received item: ({item_id})")
        
    ctx.processed_item_count = len(ctx.items_received)


async def handle_checked_locations(ctx: 'Context') -> None:
    """
    共通的なロケーションチェック処理。
    """
    if ctx.slot_data is None:
        return

    # logger.info(f"{ctx.location_table}")
    new_checks = []
    for ap_code in ctx.location_table:
        if ap_code in ctx.checked_locations:
            continue
        if ctx.game_interface.is_location_checked(ap_code) is True:
            new_checks.append(ap_code)

    if new_checks:
        await ctx.send_msgs([{"cmd": 'LocationChecks', "locations": new_checks}])
        ctx.locations_checked.update(new_checks)
    # else:
    #     logger.info("Not found new location")


async def handle_deathlink(ctx: 'Context') -> None:
    """Receive and send deathlink"""
    if not ctx.death_link_enabled:
        return

    if time()-ctx.deathlink_timestamp > 10:
        if ctx.game_interface.alive():
            if ctx.queued_deaths > 0:
                ctx.game_interface.kill_player()
                ctx.queued_deaths -= 1
                ctx.deathlink_timestamp = time()
        else:
            # Maybe add something that writes a cause?
            await ctx.send_death()
            ctx.deathlink_timestamp = time()


async def handle_check_goal(ctx: 'Context') -> None:
    """Checks if the goal is completed"""
    if ctx.slot_data is None:
        return

    victory_code = ctx.game_interface.get_victory_code()
    if victory_code in ctx.checked_locations:
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]) 

