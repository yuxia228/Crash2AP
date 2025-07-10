from typing import Dict, TYPE_CHECKING, NamedTuple, Optional

if TYPE_CHECKING:
    from . import Crash2World
    
class LocData(NamedTuple):
    ap_code: Optional[int]
    region: Optional[str]
    addr: Optional[int]
    bit: Optional[int]

def get_total_locations(world) -> int:
    locations = [ l for l in world.multiworld.get_locations() if l.player == world.player ]
    return len(locations)

def get_location_names() -> Dict[str, int]:
    names = {name: data.ap_code for name, data in location_table.items()}
    return names

def get_regions() -> list:
    regions = [data.region for _, data in location_table.items()]
    return regions

def get_ap_code(location_name) -> list:
    ap_code = [data.ap_code for name, data in location_table.items() if location_name == name]
    return ap_code

class stageType():
    stage=0
    boss=1

# ap_code = 50_XX_YY_ZZ:
#   XX: 00 == stage, 01 == boss
#   YY: stage(01~27), if boss, set 00
#   ZZ: item_number(starts 1)

# Power Stone: 0x6DBA0 ~ 6DBA7 (8 byte) Max 64(stage(25) + unused(39))
#   Used: 6DBA0: 00 F4 EF EF 5F 00 00 00
# Gem: 0x6DA24 ~ 0x6DA2B ( 8 byte ) Max 64(White(37) + Color(5) + unused(22))
#   Used: 6DA24: FE F7 EF EF FF 00 00 7E
# Color Gem
#   Red:    0x6DA2B: 0000_0X00(3bit) 0x04
#   Green:  0x6DA2B: 0000_X000(4bit) 0x08
#   Purple: 0x6DA2B: 000X_0000(5bit) 0x10
#   Blue:   0x6DA2B: 00X0_0000(6bit) 0x20
#   Yellow: 0x6DA2B: 0X00_0000(7bit) 0x40
#   Unknown:0x6DA2B: X000_0000(8bit) 0x80
#
# 6DA84: Boss defeated flag?? 
#   0x0006D9D8: C8 1100_1000
#               Boss01: 0x40
#               Boss03: 0x08
#               Boss05: 0x80
#   0x0006D9D9: 43 1000_0011
#               Boss02: 0x01
#               Boss04: 0x02
#               ??????: 0x40
# 
# Power stone:
#  0x6DBA0: (not used) Done: 0
#  0x6DBA1: Done: 5
#  0x6DBA2: Done: 7
#  0x6DBA3: Done: 7
#  0x6DBA4: Done: 6
#  0x6DBA5: (not used)
#  0x6DBA6: (not used)
#  0x6DBA7: (not used)
# Gem
#  0x6DA24: Done: 7
#  0x6DA25: Done: 7
#  0x6DA26: Done: 7
#  0x6DA27: Done: 7
#  0x6DA28: Done: 8
#  0x6DA29: Dummy: 0
#  0x6DA2A: Dummy: 0
#  0x6DA2B: 1 + color x5
# Stage_dict = {location_name: address_bit}
stage_dict = {
    "Stage01: Power Stone": 8*3+6, # 0x6DBA3: 0x40 0X00_0000
    "Stage01: White Gem"  : 8*3+6, # 0x6DA27: 0x40 0X00_0000
    "Stage01: Blue Gem(Not brake boxes)"   : 8*7+5, # 0x6DA2B: 00X0_0000(6bit) 0x20
    "Stage02: Power Stone": 8*1+6, # 0x6DBA1: 0x40 0X00_0000
    "Stage02: White Gem"  : 8*1+6, # 0x6DA25: 0X00_0000 0x40
    "Stage02: Red Gem(from Stage07)"    : 8*7+2, # 0x6DA2B: 0000_0X00(3bit) 0x04
    "Stage03: Power Stone": 8*3+1, # 0x6DBA3: 0x02 0000_00X0
    "Stage03: White Gem1(need Blue Gem)" : 8*3+1, # 0x6DA27: 0x02 0000_00X0
    "Stage03: White Gem2(time trial)" : 8*0+1, # 0x6DA24: 0x02 0000_00X0
    "Stage04: Power Stone": 8*3+7, # 0x6DBA3: 0x80 X000_0000
    "Stage04: White Gem"  : 8*3+7, # 0x6DA27: 0x80 X000_0000
    "Stage05: Power Stone": 8*3+0, # 0x6DBA3: 0x01 0000_000X
    "Stage05: White Gem"  : 8*3+0, # 0x6DA27: 0x01 0000_000X
    "Stage06: Power Stone": 8*2+1, # 0x6DBA2: 0x02 0000_00X0
    "Stage06: White Gem(need Red Gem)"  : 8*2+1, # 0x6DA26: 0x02 0000_00X0
    "Stage07: Power Stone": 8*4+0, # 0x6DBA4: 0x01 0000_000X
    "Stage07: White Gem1(from Stage13)" : 8*4+0, # 0x6DA28: 0x01 0000_000X 
    "Stage07: White Gem2(Dokuro course)" : 8*0+2, # 0x6DA24: 0x04 0000_0X00
    "Stage08: Power Stone": 8*3+5, # 0x6DBA3: 0x20 00X0_0000
    "Stage08: White Gem"  : 8*3+5, # 0x6DA27: 0x20 00X0_0000
    "Stage09: Power Stone": 8*3+3, # 0x6DBA3: 0x08 0000_X000
    "Stage09: White Gem"  : 8*3+3, # 0x6DA27: 0x08 0000_X000
    "Stage10: Power Stone": 8*4+3, # 0x6DBA4: 0x08 0000_X000
    "Stage10: White Gem"  : 8*4+3, # 0x6DA28: 0x08 0000_X000 
    "Stage10: Green Gem"  : 8*7+3, # 0x6DA2B: 0000_X000(4bit) 0x08
    "Stage11: Power Stone": 8*4+1, # 0x6DBA4: 0x02 0000_00X0
    "Stage11: White Gem"  : 8*4+1, # 0x6DA28: 0x02 0000_00X0 
    "Stage11: Yellow Gem(time trial)" : 8*7+6, # 0x6DA2B: 0X00_0000(7bit) 0x40
    "Stage12: Power Stone": 8*1+2, # 0x6DBA1: 0x04 0000_0X00
    "Stage12: White Gem1" : 8*1+2, # 0x6DA25: 0x04 0000_0X00 
    "Stage12: White Gem2(need Yellow Gem)" : 8*0+3, # 0x6DA24: 0x08 0000_X000
    "Stage13: Power Stone": 8*4+2, # 0x6DBA4: 0x04 0000_0X00
    "Stage13: White Gem"  : 8*4+2, # 0x6DA28: 0x04 0000_0X00 
    "Stage14: Power Stone": 8*2+6, # 0x6DBA2: 0x40 0X00_0000
    "Stage14: White Gem1(from Stage17)" : 8*2+6, # 0x6DA26: 0x40 0X00_0000
    "Stage14: White Gem2" : 8*0+4, # 0x6DA24: 0x10 000X_0000 
    "Stage15: Power Stone": 8*2+7, # 0x6DBA2: 0x80 X000_0000
    "Stage15: White Gem"  : 8*2+7, # 0x6DA26: 0x80 X000_0000 
    "Stage16: Power Stone": 8*1+5, # 0x6DBA1: 0x20 00X0_0000
    "Stage16: White Gem"  : 8*1+5, # 0x6DA25: 0x20 00X0_0000 
    "Stage17: Power Stone": 8*2+5, # 0x6DBA2: 0x20 00X0_0000
    "Stage17: White Gem1" : 8*2+5, # 0x6DA26: 0x20 00X0_0000 
    "Stage17: White Gem2" : 8*1+0, # 0x6DA25: 0x01 0000_000X 
    "Stage18: Power Stone": 8*2+3, # 0x6DBA2: 0x08 0000_X000
    "Stage18: White Gem1" : 8*2+3, # 0x6DA26: 0x08 0000_X000
    "Stage18: White Gem2" : 8*1+1, # 0x6DA25: 0x02 0000_00X0 
    "Stage19: Power Stone": 8*1+7, # 0x6DBA1: 0x80 X000_0000
    "Stage19: White Gem1" : 8*1+7, # 0x6DA25: 0x80 X000_0000
    "Stage19: White Gem2(need Green Gem)" : 8*7+1, # 0x6DA2B: 0x02 0000_00X0
    "Stage20: Power Stone": 8*4+4, # 0x6DBA4: 0x10 000X_0000
    "Stage20: White Gem"  : 8*4+4, # 0x6DA28: 0x10 000X_0000 
    "Stage20: Purple Gem" : 8*7+4, # 0x6DA2B: 000X_0000(5bit) 0x10
    "Stage21: Power Stone": 8*2+0, # 0x6DBA2: 0x01 0000_000X
    "Stage21: White Gem1" : 8*2+0, # 0x6DA26: 0x01 0000_000X
    "Stage21: White Gem2" : 8*0+5, # 0x6DA24: 0x20 00X0_0000 
    "Stage22: Power Stone": 8*2+2, # 0x6DBA2: 0x04 0000_0X00
    "Stage22: White Gem"  : 8*2+2, # 0x6DA26: 0x04 0000_0X00
    "Stage23: Power Stone": 8*1+4, # 0x6DBA1: 0x10 000X_0000
    "Stage23: White Gem1" : 8*1+4, # 0x6DA25: 0x10 000X_0000 
    "Stage23: White Gem2" : 8*0+6, # 0x6DA24: 0x40 0X00_0000 
    "Stage24: Power Stone": 8*3+2, # 0x6DBA3: 0x04 0000_0X00
    "Stage24: White Gem"  : 8*3+2, # 0x6DA27: 0x04 0000_X000
    "Stage25: Power Stone": 8*4+6, # 0x6DBA4: 0x40 0X00_0000
    "Stage25: White Gem1" : 8*4+6, # 0x6DA28: 0x40 0X00_0000 
    "Stage25: White Gem2(need All Color Gems)" : 8*0+7, # 0x6DA24: 0x80 X000_0000 
    # Secret stage
    "Stage26: White Gem"  : 8*4+5, # 0x6DA28: 0x20 00X0_0000 
    "Stage27: White Gem"  : 8*4+7, # 0x6DA28: 0x80 X000_0000 
}

def gen_stage_locations(stage_dict: Dict[str, int]):
    location_dict = {}
    item_counter = 1
    prev_stage_num = 0
    for name, data in stage_dict.items():
        stage_num = int(name.split(":")[0].replace("Stage",""), 10) -1 # 1~5 -> 0~4
        floor_num = stage_num // 5 + 1
        if stage_num == prev_stage_num:
            item_counter += 1
        else:
            item_counter = 1  
        prev_stage_num = stage_num
        # AP code
        ap_code = 50000000 + stage_num*100 + item_counter
        # Region
        region = f"{floor_num}F"
        if floor_num > 5: # Secret stage case
            region = f"{name.split(':')[0]}"
        # Address
        if "Gem" in name:
            addr = 0x6DA24 + (data//8)
        else: # Power Stone
            addr = 0x6DBA0 + (data//8)
        # Bit
        bit =  (data % 8)

        # Generate locations
        location_dict[name] = LocData(ap_code, region, addr, bit)
    return location_dict

stage_locations = gen_stage_locations(stage_dict)
boss_locations = {
    "Boss01": LocData(50010001, "2F", 0x0006D9D8, 6),
    "Boss02": LocData(50010002, "3F", 0x0006D9D9, 0),
    "Boss03": LocData(50010003, "4F", 0x0006D9D8, 3),
    "Boss04": LocData(50010004, "5F", 0x0006D9D9, 1),
    "Boss05": LocData(50010005, "6F", 0x0006D9D8, 7),
}

location_table = {
    **stage_locations,
    **boss_locations,
}

# _stage_locations = {
#     "Stage01: Power Stone": LocData(50000101, "1F"),
#     "Stage01: White Gem"  : LocData(50000102, "1F"),
#     "Stage01: Blue Gem"   : LocData(50000103, "1F"),
#     "Stage02: Power Stone": LocData(50000001, "1F"),
#     "Stage02: White Gem"  : LocData(50000102, "1F"),
#     "Stage02: Red Gem"    : LocData(50000103, "1F"),
#     "Stage03: Power Stone": LocData(50000001, "1F"),
#     "Stage03: White Gem1" : LocData(50000102, "1F"),
#     "Stage03: White Gem2" : LocData(50000102, "1F"),
#     "Stage04: Power Stone": LocData(50000001, "1F"),
#     "Stage04: White Gem"  : LocData(50000102, "1F"),
#     "Stage05: Power Stone": LocData(50000001, "1F"),
#     "Stage05: White Gem"  : LocData(50000102, "1F"),

#     "Stage06: Power Stone": LocData(50000001, "2F"),
#     "Stage06: White Gem"  : LocData(50000102, "1F"),
#     "Stage07: Power Stone": LocData(50000001, "2F"),
#     "Stage07: White Gem1" : LocData(50000102, "1F"),
#     "Stage07: White Gem2" : LocData(50000102, "1F"),
#     "Stage08: Power Stone": LocData(50000001, "2F"),
#     "Stage08: White Gem"  : LocData(50000102, "1F"),
#     "Stage09: Power Stone": LocData(50000001, "2F"),
#     "Stage09: White Gem"  : LocData(50000102, "1F"),
#     "Stage10: Power Stone": LocData(50000001, "2F"),
#     "Stage10: White Gem"  : LocData(50000102, "1F"),
#     "Stage10: Green Gem"  : LocData(50000102, "1F"),

#     "Stage11: Power Stone": LocData(50000001, "3F"),
#     "Stage11: White Gem"  : LocData(50000102, "1F"),
#     "Stage11: Yellow Gem" : LocData(50000102, "1F"),
#     "Stage12: Power Stone": LocData(50000001, "3F"),
#     "Stage12: White Gem1" : LocData(50000102, "1F"),
#     "Stage12: White Gem2" : LocData(50000102, "1F"),
#     "Stage13: Power Stone": LocData(50000001, "3F"),
#     "Stage13: White Gem"  : LocData(50000102, "1F"),
#     "Stage14: Power Stone": LocData(50000001, "3F"),
#     "Stage14: White Gem1" : LocData(50000102, "1F"),
#     "Stage14: White Gem2" : LocData(50000102, "1F"),
#     "Stage15: Power Stone": LocData(50000001, "3F"),
#     "Stage15: White Gem"  : LocData(50000102, "1F"),

#     "Stage16: Power Stone": LocData(50000001, "3F"),
#     "Stage16: White Gem"  : LocData(50000102, "1F"),
#     "Stage17: Power Stone": LocData(50000001, "3F"),
#     "Stage17: White Gem1" : LocData(50000102, "1F"),
#     "Stage17: White Gem2" : LocData(50000102, "1F"),
#     "Stage18: Power Stone": LocData(50000001, "3F"),
#     "Stage18: White Gem1" : LocData(50000102, "1F"),
#     "Stage18: White Gem2" : LocData(50000102, "1F"),
#     "Stage19: Power Stone": LocData(50000001, "3F"),
#     "Stage19: White Gem1" : LocData(50000102, "1F"),
#     "Stage19: White Gem2" : LocData(50000102, "1F"),
#     "Stage20: Power Stone": LocData(50000001, "3F"),
#     "Stage20: White Gem"  : LocData(50000102, "1F"),
#     "Stage20: Purple Gem" : LocData(50000102, "1F"),

#     "Stage21: Power Stone": LocData(50000001, "5F"),
#     "Stage21: White Gem1" : LocData(50000102, "1F"),
#     "Stage21: White Gem2" : LocData(50000102, "1F"),
#     "Stage22: Power Stone": LocData(50000001, "5F"),
#     "Stage22: White Gem"  : LocData(50000102, "1F"),
#     "Stage23: Power Stone": LocData(50000001, "5F"),
#     "Stage23: White Gem1" : LocData(50000102, "1F"),
#     "Stage23: White Gem2" : LocData(50000102, "1F"),
#     "Stage24: Power Stone": LocData(50000001, "5F"),
#     "Stage24: White Gem"  : LocData(50000102, "1F"),
#     "Stage25: Power Stone": LocData(50000001, "5F"),
#     "Stage25: White Gem1" : LocData(50000102, "1F"),
#     "Stage25: White Gem2" : LocData(50000102, "1F"),

#     "Stage26: White Gem"  : LocData(50000001, "Extra"),
#     "Stage27: White Gem"  : LocData(50000001, "Extra"),
# }


#class EventData(NamedTuple):
#    name:       str
#    ap_code:    Optional[int] = None
#class LocData(NamedTuple):
#    ap_code: Optional[int]
#    region: Optional[str]
def get_level_locations(region):
    return map(lambda l: l[0], get_level_location_data(region))

def get_level_location_data(region):
    return filter(lambda l: l[1].region == (region), location_table.items())

