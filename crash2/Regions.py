from BaseClasses import Region, Location
from typing import TYPE_CHECKING
from .Locations import location_table
from .Options import GAME_TITLE_FULL

if TYPE_CHECKING:
    from . import Crash2World

class Crash2Location(Location):
    game = GAME_TITLE_FULL

def create_regions(world):

    #----- Introduction Sequence -----#
    menu = create_region(world, "Menu")
    Room1F = create_region_and_connect(world, "1F", "Menu -> 1F", menu)
    Room2F = create_region_and_connect(world, "2F", "1F -> 2F", menu)
    Room3F = create_region_and_connect(world, "3F", "2F -> 3F", menu)
    Room4F = create_region_and_connect(world, "4F", "3F -> 4F", menu)
    Room5F = create_region_and_connect(world, "5F", "4F -> 5F", menu)
    Room6F = create_region_and_connect(world, "6F", "5F -> 6F", menu)

    # Stage 15 -> 26
    Stage26 = create_region(world, "Stage26")
    Room3F.connect(Stage26)
    # Stage 16 -> 27
    Stage27 = create_region(world, "Stage27")
    Room4F.connect(Stage27)
    

def create_region(world, name: str) -> Region:
    reg = Region(name, world.player, world.multiworld)

    for (key, data) in location_table.items():
        if data.region == name:
            location = Crash2Location(world.player, key, data.ap_code, reg)
            reg.locations.append(location)

    world.multiworld.regions.append(reg)
    return reg


def create_region_and_connect(world: "Crash2World",
                              name: str, entrancename: str, connected_region: Region) -> Region:
    reg: Region = create_region(world, name)
    connected_region.connect(reg, entrancename)
    return reg
