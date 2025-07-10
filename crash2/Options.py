from typing import List, Dict, Any
from dataclasses import dataclass
from worlds.AutoWorld import PerGameCommonOptions
from Options import Choice, OptionGroup, Toggle, DefaultOnToggle

# Common variable
GAME_TITLE="Crash2"
GAME_TITLE_FULL="CrashBandicoot2"

def create_option_groups() -> List[OptionGroup]:
    option_group_list: List[OptionGroup] = []
    for name, options in option_groups.items():
        option_group_list.append(OptionGroup(name=name, options=options))

    return option_group_list

class DummyOption(Choice):
    """
    DummyOption: Placeholeder
    """
    display_name = "DummyOption"
    option_1 = 1
    option_2 = 2
    option_3 = 3
    default = 1

class UseProgressItemInsteadOfPowerStones(Choice):
    """
    UseProgressItemInsteadOfPowerStones: Placeholeder
    """
    display_name = "UseProgressItemInsteadOfPowerStones"
    option_use_progress_items = 0
    option_use_powerstone_as_vanilla = 1
    default = 0


@dataclass
class Crash2Options(PerGameCommonOptions):
    DummyOption:            DummyOption
    UseProgressItemInsteadOfPowerStones: UseProgressItemInsteadOfPowerStones

option_groups: Dict[str, List[Any]] = {
    "General Options": [DummyOption, UseProgressItemInsteadOfPowerStones],
}

slot_data_options: List[str] = {
    "DummyOption",
    "UseProgressItemInsteadOfPowerStones",
}