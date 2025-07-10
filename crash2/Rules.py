from worlds.generic.Rules import add_rule, set_rule
from typing import TYPE_CHECKING
from .Options import GAME_TITLE_FULL, UseProgressItemInsteadOfPowerStones
# from .Items import gadget_items

if TYPE_CHECKING:
    from . import Crash2World


def set_rules_floor(world):
    options = world.options
    # Progressive Item Option
    if options.UseProgressItemInsteadOfPowerStones.value == UseProgressItemInsteadOfPowerStones.option_use_progress_items:
        item_name = "Progressive Floor"
        base_value = 1
    else: # options.UseProgressItemInsteadOfPowerStones.value == UseProgressItemInsteadOfPowerStones.option_use_powerstone_as_vanilla:
        item_name = "Power Stone"
        base_value = 5

    # Floor elevator
    add_rule(world.multiworld.get_entrance("1F -> 2F", world.player),
             lambda state: state.has(item_name, world.player, count=base_value*1))
    add_rule(world.multiworld.get_entrance("2F -> 3F", world.player),
             lambda state: state.has(item_name, world.player, count=base_value*2))
    add_rule(world.multiworld.get_entrance("3F -> 4F", world.player),
             lambda state: state.has(item_name, world.player, count=base_value*3))
    add_rule(world.multiworld.get_entrance("4F -> 5F", world.player),
             lambda state: state.has(item_name, world.player, count=base_value*4))
    add_rule(world.multiworld.get_entrance("5F -> 6F", world.player),
             lambda state: state.has(item_name, world.player, count=base_value*5))


def set_rules_hard_location(world):
    options = world.options
    # Progressive Item Option
    if options.UseProgressItemInsteadOfPowerStones.value == UseProgressItemInsteadOfPowerStones.option_use_progress_items:
        item_name = "Progressive Floor"
        base_value = 1
    else: # options.UseProgressItemInsteadOfPowerStones.value == UseProgressItemInsteadOfPowerStones.option_use_powerstone_as_vanilla:
        item_name = "Power Stone"
        base_value = 5

    ### Color Gem limitaion
    # Stage3 White gem1 needs Blue gem
    add_rule(world.multiworld.get_location("Stage03: White Gem1(need Blue Gem)", world.player),
             lambda state: state.has("Blue Gem", world.player))
    # Stage6 White gem1 needs Red gem
    add_rule(world.multiworld.get_location("Stage06: White Gem(need Red Gem)", world.player),
             lambda state: state.has("Red Gem", world.player))
    # Stage12 White gem2 needs Yellow gem
    add_rule(world.multiworld.get_location("Stage12: White Gem2(need Yellow Gem)", world.player),
             lambda state: state.has("Yellow Gem", world.player))
    # Stage19 White gem2 needs Green gem
    add_rule(world.multiworld.get_location("Stage19: White Gem2(need Green Gem)", world.player),
             lambda state: state.has("Green Gem", world.player))
    # Stage25 White gem2 needs All color gems
    add_rule(world.multiworld.get_location("Stage25: White Gem2(need All Color Gems)", world.player),
             lambda state: state.has("Green Gem", world.player)
             and state.has("Red Gem", world.player)
             and state.has("Blue Gem", world.player)
             and state.has("Purple Gem", world.player)
             and state.has("Yellow Gem", world.player))

    ### Floor limitation
    # Stage2 Red gem needs Stage 7
    add_rule(world.multiworld.get_location("Stage02: Red Gem(from Stage07)", world.player),
             lambda state: state.has(item_name, world.player, count=base_value*1))
    # Stage07 White Gem1 needs Stage13
    add_rule(world.multiworld.get_location("Stage07: White Gem1(from Stage13)", world.player),
             lambda state: state.has(item_name, world.player, count=base_value*2))
    # Stage14 White Gem1 needs Stage17
    add_rule(world.multiworld.get_location("Stage14: White Gem1(from Stage17)", world.player),
             lambda state: state.has(item_name, world.player, count=base_value*3))


    pass
        
def set_rules(world):

    # Rules for planets connection
    set_rules_floor(world)
    
    # Rules for hard to get Location
    set_rules_hard_location(world)

    #world.multiworld.completion_condition[world.player] = lambda state: state.has("Dr. Nefarious Defeated!", world.player)
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Defeat Cortex!", world.player)

