from typing import Dict
from BaseClasses import MultiWorld, Item, ItemClassification, Tutorial
from worlds.AutoWorld import World, CollectionState, WebWorld
from .Items import item_table, create_itempool, create_item
from .Locations import get_location_names, get_total_locations, get_level_locations, get_regions
from .Options import Crash2Options, GAME_TITLE, GAME_TITLE_FULL
from .Regions import create_regions
from .Rules import set_rules
from typing import Dict, Optional, Mapping, Any
from .Client import Crash2Client # Unused, but required to register with BizHawkClient 

from worlds.LauncherComponents import Component, SuffixIdentifier, Type, components, launch_subprocess
def run_client(_url: Optional[str] = None):
    from .Crash2Client import launch_client
    launch_subprocess(launch_client, name=f"{GAME_TITLE} Client")

components.append(
    Component(f"{GAME_TITLE_FULL} Client", func=run_client, component_type=Type.CLIENT,
              file_identifier=SuffixIdentifier(".apcb2"))
)
class Crash2Web(WebWorld):
    theme = "ocean"
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Ratchet and Clank 3: Up Your Arsenal for Archipelago. "
        "This guide covers single-player, multiworld, and related software.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Bread"]
    )]

class Crash2World(World):
    """
    Ratchet and Clank 3 is a third person action shooter.
    Blast your enemies with over the top weaponry and save the galaxy from total disaster.
    """

    game = GAME_TITLE_FULL
    item_name_to_id = {name: data.ap_code for name, data in item_table.items()}
    location_name_to_id = get_location_names()
    # Config for Universal Tracker
    ut_can_gen_without_yaml = False
    disable_ut = False

    location_name_groups = {}
    for region in get_regions():
        location_name_groups[region] = set(get_level_locations(region))

    options_dataclass = Crash2Options
    options = Crash2Options
    web = Crash2Web()

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)

    def generate_early(self):
        # starting_weapon = (weapon_type_to_name[WeaponType(self.options.StartingWeapon)])
        # self.multiworld.push_precollected(self.create_item(starting_weapon))
        pass

    def create_regions(self):
        create_regions(self)

    def create_items(self):
        self.multiworld.itempool += create_itempool(self)

    def set_rules(self):
        set_rules(self)

    def create_item(self, name: str) -> Item:
        return create_item(self, name)

    def fill_slot_data(self) -> Dict[str, object]:
        slot_data: Dict[str, object] = {
            "options": {
                "DummyOption": self.options.DummyOption.value,
                "UseProgressItemInsteadOfPowerStones": self.options.UseProgressItemInsteadOfPowerStones.value,
            },
            "Seed": self.multiworld.seed_name,  # to verify the server's multiworld
            "Slot": self.multiworld.player_name[self.player],  # to connect to server
            "TotalLocations": get_total_locations(self)
        }

        return slot_data

    def collect(self, state: "CollectionState", item: "Item") -> bool:
        return super().collect(state, item)

    def remove(self, state: "CollectionState", item: "Item") -> bool:
        return super().remove(state, item)

    # For Univesal Tracker integration
    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        # Trigger a regen in UT
        return slot_data

