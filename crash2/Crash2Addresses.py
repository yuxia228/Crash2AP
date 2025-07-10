class CHECK_TYPE:
  bit = 0
  int = 1
  uint = 2
  byte = 3
  short = 4
  falseBit = 5
  long = 6
  nibble = 7

class COMPARE_TYPE:
  Match = 0
  GreaterThan = 1
  LessThan = 2

ADDRESSES = {
  "SCPS-10047": {
    "GAME_ID": 0x106CE,
    "CurrentLevel": 0x699ec,
  }
}
class LEVEL:
  WarpRoom = 0x02
  BOSS05 = 0x07
  Stage01 = 0x1E
  Stage02 = 0x0E
  Stage03 = 0x19
  Stage04 = 0x1F
  Stage05 = 0x18
  Stage06 = 0x11
  Stage07 = 0x20
  Stage08 = 0x1D
  Stage09 = 0x1B
  Stage10 = 0x23
  Stage11 = 0x21
  Stage12 = 0x0A
  Stage13 = 0x22
  Stage14 = 0x16
  Stage15 = 0x17
  Stage16 = 0x0D
  Stage17 = 0x15
  Stage18 = 0x13
  Stage19 = 0x0F
  Stage20 = 0x24
  Stage21 = 0x10
  Stage22 = 0x12
  Stage23 = 0x0C
  Stage24 = 0x1A
  Stage25 = 0x26
  Stage26 = 0x25
  Stage27 = 0x27
  NormalED = 0x29
  BestED = 0x28

from .Locations import location_table
LOCATIONS = []
for name, loc_data in location_table.items():
  LOCATIONS.append({
    "name": name,
    "Id": loc_data.ap_code,
    "Address": loc_data.addr,
    "CheckType": CHECK_TYPE.bit,
    "AddressBit": loc_data.bit,
  })
  
  # {
  #   "Name": "Received Shock Cannon",
  #   "Id": 50001000,
  #   "Address": "0x00142CC7",
  #   "CheckType": 0,
  #   "AddressBit": 0
  # },