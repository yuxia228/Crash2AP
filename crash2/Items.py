from BaseClasses import Item, ItemClassification
from .Locations import get_total_locations, location_table, get_ap_code
from typing import List, Dict, TYPE_CHECKING, NamedTuple, Optional
from .Options import GAME_TITLE_FULL
if TYPE_CHECKING:
    from . import Crash2World

class Crash2Item(Item):
    game = GAME_TITLE_FULL

class ItemData(NamedTuple):
   ap_code: Optional[int]
   classification: ItemClassification
   count: Optional[int] = 1

def create_itempool(world) -> List[Item]:
    itempool: List[Item] = []
    options = world.options
    junk_dict = junk_items

    for name in item_table.keys():
        item_type: ItemClassification = item_table.get(name).classification
        item_amount: int = item_table.get(name).count
        itempool += create_multiple_items(world, name, item_amount, item_type)

    for loc in world.multiworld.get_locations(world.player):
        print(f"  '{loc.name}: {get_ap_code(loc.name)}'")

    victory = create_item(world, "Defeat Cortex!")
    world.multiworld.get_location("Boss05", world.player).place_locked_item(victory)
    itempool += create_junk_items(world, get_total_locations(world) - len(itempool) - 1, junk_dict)
    return itempool

def create_multiple_items(world, name: str, count: int = 1,
                          item_type: ItemClassification = ItemClassification.progression) -> List[Item]:
    data = item_table[name]
    itemlist: List[Item] = []

    for i in range(count):
        itemlist += [Crash2Item(name, item_type, data.ap_code, world.player)]

    return itemlist

def create_item(world, name: str) -> Item:
    data = item_table[name]
    return Crash2Item(name, data.classification, data.ap_code, world.player)

def create_junk_items(world, count: int, junk_dict: Dict[str, object]) -> List[Item]:
    junk_pool: List[Item] = []
    # For now, all junk has equal weights
    for i in range(count):
        junk_pool.append(world.create_item(world.random.choices(list(junk_dict.keys()), k=1)[0]))
    return junk_pool

items = {
    "Power Stone": ItemData(51000000, ItemClassification.progression, 25),
    "White Gem"  : ItemData(51000001, ItemClassification.useful, 37),
    "Red Gem"    : ItemData(51000002, ItemClassification.progression, 1),
    "Blue Gem"   : ItemData(51000003, ItemClassification.progression, 1),
    "Yellow Gem" : ItemData(51000004, ItemClassification.progression, 1),
    "Green Gem"  : ItemData(51000005, ItemClassification.progression, 1),
    "Purple Gem" : ItemData(51000006, ItemClassification.progression, 1),
}
victory_items = {
    "Defeat Cortex!" : ItemData(51000010, ItemClassification.progression, 1),
}
junk_items = {
    "Apple" : ItemData(51000100, ItemClassification.filler, 0),
}

item_table ={
    **items,
    **victory_items,
    **junk_items,
}

def filter_items(classification):
    return filter(lambda l: l[1].classification == (classification), item_table.items())

def filter_item_names(classification):
    return map(lambda entry: entry[0], filter_items(classification))

