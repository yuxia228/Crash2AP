# Common import
from typing import Optional, Dict
import asyncio
import multiprocessing
import traceback
from CommonClient import get_base_parser, logger, server_loop, gui_enabled
import Utils
# Load Universal Tracker modules with aliases
tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import (TrackerCommandProcessor as ClientCommandProcessor,
                                              TrackerGameContext as CommonContext, UT_VERSION)
    tracker_loaded = True
except ImportError:
    from CommonClient import ClientCommandProcessor, CommonContext
    print("ERROR: Universal Tracker is not loaded")

# Game title dedicated
from . import Locations, Items
from .Crash2Interface import Crash2Interface
from .Callbacks import init, update
from .Options import GAME_TITLE, GAME_TITLE_FULL

CLIENT_INIT_LOG=f"{GAME_TITLE} Client"
CLIENT_VERSION="v0.1.0"

class CommandProcessor(ClientCommandProcessor):
    # This is not mandatory for the game. Just a client command implementation.
    # def _cmd_kill(self):
    #     """Kill the game."""
    #     if isinstance(self.ctx, Crash2Context):
    #         self.ctx.game_interface.kill_player()
    pass


class Crash2Context(CommonContext):
    # Client variables
    command_processor = CommandProcessor
    game_interface: Crash2Interface
    game = f"{GAME_TITLE_FULL}"
    pine_client_sync_task: Optional[asyncio.Task] = None
    is_connected_to_game: bool = False
    is_connected_to_server: bool = False
    slot_data: Optional[dict[str, Utils.Any]] = None
    last_error_message: Optional[str] = None
    notification_queue: list[str] = []
    notification_timestamp: float = 0
    showing_notification: bool = False
    deathlink_timestamp: float = 0
    death_link_enabled = False
    queued_deaths: int = 0
    
    items_handling = 0b111 # This is mandatory

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.game_interface = Crash2Interface(logger)

    def notification(self, text: str):
        self.notification_queue.append(text)

    def on_deathlink(self, data: Utils.Dict[str, Utils.Any]) -> None:
        super().on_deathlink(data)
        if self.death_link_enabled:
            self.queued_deaths += 1
            cause = data.get("cause", "")
            if cause:
                self.notification(f"DeathLink: {cause}")
            else:
                self.notification(f"DeathLink: Received from {data['source']}")

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = f"{GAME_TITLE} Client v{CLIENT_VERSION}"
        if tracker_loaded:
            ui.base_title += f" | Universal Tracker {UT_VERSION}"

        # AP version is added behind this automatically
        ui.base_title += " | Archipelago"
        return ui

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super(Rac3Context, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        if cmd == "Connected":
            self.slot_data = args["slot_data"]
            # logger.info(f"Received data: {args}")
            self.location_table = self.server_locations # list
            self.game_interface.proc_option(self.slot_data)

            # Set death link tag if it was requested in options
            if "death_link" in args["slot_data"]:
                self.death_link_enabled = bool(args["slot_data"]["death_link"])
                Utils.async_start(self.update_death_link(
                    bool(args["slot_data"]["death_link"])))
                Utils.async_start(self.send_msgs([{
                    "cmd": "LocationScouts",
                    "locations": [
                        Locations.location_dict[location].code
                        for location in Locations.location_groups["Purchase"]
                    ]
                }]))

def update_connection_status(ctx, status: bool):
    if ctx.is_connected_to_game == status:
        return

    if status:
        logger.info(f"Connected to {GAME_TITLE}")
    else:
        logger.info("Unable to connect to the PCSX2 instance, attempting to reconnect...")

    ctx.is_connected_to_game = status

async def pine_client_sync_task(ctx):
    logger.info(f"Starting {GAME_TITLE} Connector, attempting to connect to emulator...")
    ctx.game_interface.connect_to_game()
    while not ctx.exit_event.is_set():
        try:
            is_connected = ctx.game_interface.get_connection_state()
            update_connection_status(ctx, is_connected)
            if is_connected:
                await _handle_game_ready(ctx)
            else:
                await _handle_game_not_ready(ctx)
        except ConnectionError:
            logger.info(f"ConnectionError")
            ctx.game_interface.disconnect_from_game()
        except Exception as e:
            logger.info(f"ExceptionError")
            if isinstance(e, RuntimeError):
                logger.error(str(e))
            else:
                logger.error(traceback.format_exc())
            await asyncio.sleep(3)
            continue

async def _handle_game_ready(ctx) -> None:
    connected_to_server = (ctx.server is not None) and (ctx.slot is not None)

    new_connection = ctx.is_connected_to_server != connected_to_server
    if new_connection:
        await init(ctx, connected_to_server)
        ctx.is_connected_to_server = connected_to_server
    
    await update(ctx, connected_to_server)

    if ctx.server:
        ctx.last_error_message = None
        if not ctx.slot:
            await asyncio.sleep(1)
            return
    else:
        message = "Waiting for player to connect to server"
        if ctx.last_error_message is not message:
            logger.info("Waiting for player to connect to server")
            ctx.last_error_message = message
        await asyncio.sleep(1)
    
    await asyncio.sleep(1)


async def _handle_game_not_ready(ctx):
    """If the game is not connected, this will attempt to retry connecting to the game."""
    ctx.game_interface.connect_to_game()
    await asyncio.sleep(3)

def launch_client():
    Utils.init_logging(CLIENT_INIT_LOG)

    async def main():
        multiprocessing.freeze_support()
        logger.info("main")
        parser = get_base_parser()
        args = parser.parse_args()
        ctx = Crash2Context(args.connect, args.password)

        logger.info("Connecting to server...")
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="Server Loop")

        # Runs Universal Tracker's internal generator
        if tracker_loaded:
            ctx.run_generator()
            ctx.tags.remove("Tracker")
        else:
            logger.warning("Could not find Universal Tracker.")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        logger.info("Running game...")
        ctx.pine_client_sync_task = asyncio.create_task(pine_client_sync_task(ctx), name="Pine Client Sync")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.pine_client_sync_task:
            await asyncio.sleep(3)
            await ctx.pine_client_sync_task

    import colorama

    colorama.init()

    asyncio.run(main())
    colorama.deinit()

if __name__ == "__main__":
    launch_client()
