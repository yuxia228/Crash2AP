from worlds.generic.Rules import add_rule, set_rule
from typing import TYPE_CHECKING
# from .Locations import rac3_locations
# from .Items import gadget_items

if TYPE_CHECKING:
    from . import Crash2World


def set_rules_floor(world):
    # Floor elevator
    add_rule(world.multiworld.get_entrance("1F -> 2F", world.player),
             lambda state: state.has("Power Stone", world.player, count=5))
    add_rule(world.multiworld.get_entrance("2F -> 3F", world.player),
             lambda state: state.has("Power Stone", world.player, count=10))
    add_rule(world.multiworld.get_entrance("3F -> 4F", world.player),
             lambda state: state.has("Power Stone", world.player, count=15))
    add_rule(world.multiworld.get_entrance("4F -> 5F", world.player),
             lambda state: state.has("Power Stone", world.player, count=20))
    add_rule(world.multiworld.get_entrance("5F -> 6F", world.player),
             lambda state: state.has("Power Stone", world.player, count=25))

def set_rules_hard_location(world):
    ### Color Gem limitaion
    # Stage3 White gem1 needs Blue gem
    add_rule(world.multiworld.get_location("Stage03: White Gem1", world.player),
             lambda state: state.has("Blue Gem", world.player))
    # Stage6 White gem1 needs Red gem
    add_rule(world.multiworld.get_location("Stage06: White Gem", world.player),
             lambda state: state.has("Red Gem", world.player))
    # Stage12 White gem2 needs Yellow gem
    add_rule(world.multiworld.get_location("Stage12: White Gem2", world.player),
             lambda state: state.has("Yellow Gem", world.player))
    # Stage19 White gem2 needs Green gem
    add_rule(world.multiworld.get_location("Stage19: White Gem2", world.player),
             lambda state: state.has("Green Gem", world.player))
    # Stage25 White gem2 needs All color gems
    add_rule(world.multiworld.get_location("Stage25: White Gem2", world.player),
             lambda state: state.has("Green Gem", world.player)
             and state.has("Red Gem", world.player)
             and state.has("Blue Gem", world.player)
             and state.has("Purple Gem", world.player)
             and state.has("Yellow Gem", world.player))

    ### Floor limitation
    # Stage2 Red gem needs Stage 7
    add_rule(world.multiworld.get_location("Stage02: Red Gem", world.player),
             lambda state: state.has("Power Stone", world.player, count=5))
    # Stage07 White Gem1 needs Stage13
    add_rule(world.multiworld.get_location("Stage07: White Gem1", world.player),
             lambda state: state.has("Power Stone", world.player, count=10))
    # Stage14 White Gem1 needs Stage17
    add_rule(world.multiworld.get_location("Stage14: White Gem1", world.player),
             lambda state: state.has("Power Stone", world.player, count=15))


    pass
        
def set_rules(world):

    # Rules for planets connection
    set_rules_floor(world)
    
    # Rules for hard to get Location
    set_rules_hard_location(world)

    #world.multiworld.completion_condition[world.player] = lambda state: state.has("Dr. Nefarious Defeated!", world.player)
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Defeat Cortex!", world.player)

