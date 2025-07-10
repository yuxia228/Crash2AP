from enum import  IntEnum
from typing import Optional, NamedTuple, Tuple, Dict, List
from math import ceil
import struct
from logging import Logger
from time import sleep, time

from .pine_interface.pine import Pine
from .Crash2Addresses import LOCATIONS, CHECK_TYPE, COMPARE_TYPE, ADDRESSES, LEVEL
from . import Items, Locations
import random

class Dummy(IntEnum):
    test = 0

class GameInterface():
    """
    Base class for connecting with a Pine supported emulator
    """

    pine_interface: Pine = Pine()
    logger: Logger
    game_id_error: Optional[str] = None
    current_game: Optional[str] = None
    addresses: Dict = {}

    def __init__(self, logger) -> None:
        self.logger = logger

    def _read8(self, address: int):
        return self.pine_interface.read_int8(address)

    def _read16(self, address: int):
        return self.pine_interface.read_int16(address)

    def _read32(self, address: int):
        return self.pine_interface.read_int32(address)

    def _read_bytes(self, address: int, n: int):
        return self.pine_interface.read_bytes(address, n)

    def _read_float(self, address: int):
        return struct.unpack("f",self.pine_interface.read_bytes(address, 4))[0]

    def _write8(self, address: int, value: int):
        self.pine_interface.write_int8(address, value)

    def _write16(self, address: int, value: int):
        self.pine_interface.write_int16(address, value)

    def _write32(self, address: int, value: int):
        self.pine_interface.write_int32(address, value)

    def _write_bytes(self, address: int, value: bytes):
        self.pine_interface.write_bytes(address, value)

    def connect_to_game(self):
        """
        Initializes the connection to Emulator and verifies it is connected to the
        right game
        """
        if not self.pine_interface.is_connected():
            self.pine_interface.connect()
            if not self.pine_interface.is_connected():
                return
            self.logger.info("Connected to Emulator")
        try:
            game_id = self.pine_interface.get_game_id()
            # WA: Add SCPS to game_id
            game_id = f"SCPS{game_id}"
            # self.logger.info(f"game_id: {game_id}")
            # The first read of the address will be null if the client is faster than the emulator
            self.current_game = None
            if game_id in ADDRESSES.keys():
                self.current_game = game_id
                self.addresses = ADDRESSES[game_id]
            if self.current_game is None and self.game_id_error != game_id and game_id != b'\x00\x00\x00\x00\x00\x00':
                self.logger.warning(
                    f"Connected to the wrong game ({game_id})")
                self.game_id_error = game_id
        except RuntimeError:
            pass
        except ConnectionError:
            pass

    def disconnect_from_game(self):
        self.pine_interface.disconnect()
        self.current_game = None
        self.logger.info("Disconnected from Emulator")

    def get_connection_state(self) -> bool:
        try:
            connected = self.pine_interface.is_connected()
            return connected and self.current_game is not None
        except RuntimeError:
            return False

class Crash2Interface(GameInterface):
    ########################################
    # Mandatory functions                  #
    ########################################

    # Called at once when client started
    def Init(self):
        self.power_stone = 0
        self.white_gem = 0
        self.red_gem = 0
        self.blue_gem = 0
        self.yellow_gem = 0
        self.green_gem = 0
        self.purple_gem = 0
        
        self.power_stone_wait_counter = [0] * 8 # 0x6DBA0 ~ 6DBA7 8bytes

    # Called in periodically
    def Update(self):
        self.MemoryUpdate()
        pass

    def get_victory_code(self):
        victory_name = "Boss05" # This must can be changed by option
        return Locations.location_table[victory_name].ap_code

    def proc_option(self, slot_data):
        self.logger.info(f"{slot_data}")
        self.DummyOption = slot_data["options"]["DummyOption"]

    def item_received(self, item_code, processed_items_count = 0):
        # self.logger.info(f"{item_code}")
        if item_code == 51000000: # power_stone
            self.power_stone += 1
        elif item_code == 51000001: # White Gem
            self.white_gem += 1
        elif item_code == 51000002: # Red Gem
            self.red_gem += 1
        elif item_code == 51000003: # Blue Gem
            self.blue_gem += 1
        elif item_code == 51000004: # Yellow Gem
            self.yellow_gem += 1
        elif item_code == 51000005: # Green Gem
            self.green_gem += 1
        elif item_code == 51000006: # Purple Gem
            self.purple_gem += 1
        else: # not implemented
            pass
        # if list(Items.weapon_items.values())[0].ap_code <= item_code and \
        #     item_code <= list(Items.weapon_items.values())[-1].ap_code:
        #     self.ReceivedWeapon(item_code)
        pass
    ############################################
    # Common functions (no need to be changed) #
    ############################################

    def is_location_checked(self, ap_code):
        target_location = {}
        # search target location
        for location in LOCATIONS:
            if location["Id"] == ap_code:
                target_location = location
                break
        
        #############################
        # Crash 2 Dedicated process #
        #############################
        # Only checking in WarpRoom
        addr = ADDRESSES[self.current_game]["CurrentLevel"]
        level = self._read8(addr)
        if level != LEVEL.WarpRoom:
            return False
        #############################
        # Crash 2 Dedicated process #
        #############################
        
        # Check location flag
        _value = 0
        addr = target_location["Address"]
        # addr = self.AddressConvert(addr)
        if target_location["CheckType"] == CHECK_TYPE.bit or \
            target_location["CheckType"] == CHECK_TYPE.falseBit:
            _value = self._read8(addr)
            _value = (_value >> target_location["AddressBit"]) & 0x01
        elif target_location["CheckType"] == CHECK_TYPE.byte:
            _value = self._read8(addr)
        elif target_location["CheckType"] == CHECK_TYPE.short:
            _value = self._read16(addr)
        else:
            _value = self._read32(addr)

        _compare_value = 0
        if target_location["CheckType"] == CHECK_TYPE.bit:
            _compare_value = 0x01
        elif target_location["CheckType"] == CHECK_TYPE.falseBit:
            _compare_value = 0x00
        else:
            _compare_value = int(target_location["CheckValue"], 0)

        _compare_type = COMPARE_TYPE.Match
        if 'CompareType' in target_location:
            _compare_type = target_location.CompareType

        if _compare_type == COMPARE_TYPE.Match:
            return (_value == _compare_value)
        elif _compare_type == COMPARE_TYPE.GreaterThan:
            return (_value > _compare_value)
        elif _compare_type == COMPARE_TYPE.LessThan:
            return (_value < _compare_value)

    def __init__(self, logger):
        super().__init__(logger)  # GameInterfaceの初期化

    ###################################
    # Game dedicated functions        #
    ###################################
    
    def MemoryUpdate(self):
        # Get Current Level
        addr = ADDRESSES[self.current_game]["CurrentLevel"]
        level = self._read8(addr)

        # Check Powerstone and erase flag after location is found
        if level != LEVEL.WarpRoom:
            power_stone_location = set([loc["Address"] for loc in LOCATIONS if "Power Stone" in loc["name"] ])
            for idx, addr in enumerate(power_stone_location):
                mem = self._read8(addr)
                if mem == 0:
                    continue
                # if mem is changed, wait for location is found then clear flag
                self.power_stone_wait_counter[idx] += 1
                if self.power_stone_wait_counter[idx] > 1:
                    self._write8(addr, 0)
                    self.power_stone_wait_counter[idx] = 0
        
        # Power stone checker
        dummy_power_stone_address_list = [0x6DBA0, 0x6DBA5, 0x6DBA6, 0x6DBA7]
        for i in range(self.power_stone//8+1):
            addr = dummy_power_stone_address_list[i]
            if i == (self.power_stone//8):
                values = [0x00, 0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3f, 0x7f, 0xff]
                self._write8(addr, values[(self.power_stone%8)])
            else:
                self._write8(addr, 0xff)
        
        # Logic Fixes
        ## Color Gem
        color_gem_addr = 0x6DA2B
        if level != LEVEL.WarpRoom:
            value = 0
            if self.red_gem and level != LEVEL.Stage02:
                value |= 0x04
            if self.green_gem and level != LEVEL.Stage10:
                value |= 0x08
            if self.purple_gem and level != LEVEL.Stage20:
                value |= 0x10
            if self.blue_gem and level != LEVEL.Stage01:
                value |= 0x20
            if self.yellow_gem and level != LEVEL.Stage11:
                value |= 0x40
            current_value = self._read8(color_gem_addr)
            self._write8(color_gem_addr, (current_value | value) )
        else:
            current_value = self._read8(color_gem_addr)
            mask = 0x83 # 10000011
            self._write8(color_gem_addr, (current_value & mask) )
