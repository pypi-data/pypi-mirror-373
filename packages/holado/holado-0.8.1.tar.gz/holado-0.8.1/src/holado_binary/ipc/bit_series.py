
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.exceptions.technical_exception import TechnicalException
from typing import NamedTuple, Iterable
from holado_core.common.tables.table_row import TableRow
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_binary.ipc.binary import Binary
from holado_python.standard_library.typing import Typing
from holado_core.common.tools.string_tools import StrTools

logger = logging.getLogger(__name__)


class BitSeries():
    """
    Define a bit-series as a list of bit sections. 
    A bit section is a tuple (name, bit length, type, value).
    
    It can be used in 'declaration' mode, ie when bit sections are added without "value" and values are filled after declaration with method "from_hex".
    
    BitSeries can be compared. If a bit section mustn't be compared, simply set its value to None in one BitSeries.
    """
    def __init__(self, bit_sections_list = None):
        self.__series = []
        self.__index_by_name = {}
        self.__len = None
        
        self.add_bit_section(bit_sections_list = bit_sections_list)
        
    def __iter__(self):
        return self.__series.__iter__()
    
    def __next__(self):
        return self.__series.__next__()
            
    def __len__(self):
        if self.__len is None:
            self.__len = sum(iter(bs.length for bs in self.__series))
        return self.__len
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.get_bit_section(index=key).value
        elif isinstance(key, str):
            return self.get_bit_section(name=key).value
        else:
            raise TechnicalException(f"Unmanaged key: {key} (type: {Typing.get_object_class_fullname(key)})")
        
    def __setitem__(self, key, value):
        if isinstance(key, int):
            return self.set_bit_section_value(index=key, value=value)
        elif isinstance(key, str):
            return self.set_bit_section_value(name=key, value=value)
        else:
            raise TechnicalException(f"Unmanaged key: {key}")
        
    @property
    def nb_bits(self):
        return len(self)
    
    @property
    def nb_bit_sections(self):
        return len(self.__series)
    
    def add_bit_section(self, bit_section=None, bit_sections_list=None):
        """
        Parameter "bit_section" is an iterable of 3 elements (name, bit length, type) or 4 elements (name, bit length, type, value).
            The "value" is usually omitted when in declaration mode, ie when .
        Parameter "bit_sections_list" is an iterable of "bit_section".
        """
        if bit_sections_list is not None:
            if not isinstance(bit_sections_list, Iterable):
                raise TechnicalException(f"Parameter 'bit_sections_list' has to be an iterable (obtained type: {Typing.get_object_class_fullname(bit_sections_list)})")
            for bit_section in bit_sections_list:
                self.add_bit_section(bit_section=bit_section)
            return
        
        if bit_section is not None:
            if len(bit_section) < 3 or len(bit_section) > 5:
                raise TechnicalException(f"bit_section must be an iterable of length between 3 and 5")
            
            # Declare bit section
            bs = NamedTuple('BitSection', name=str, length=int, type=type, value=int, right_padded=bool)
            
            if isinstance(bit_section[0], str):
                bs.name = bit_section[0]
            else:
                raise TechnicalException(f"First bit_section element is the name and must be a string (obtained type: {Typing.get_object_class_fullname(bit_section[0])})")
            
            if isinstance(bit_section[1], int) and bit_section[1] >= 0:
                bs.length = bit_section[1]
            else:
                raise TechnicalException(f"Second bit_section element is the bit length and must be a positive integer (obtained type: {Typing.get_object_class_fullname(bit_section[1])} ; value: {bit_section[1]})")
            
            if isinstance(bit_section[2], type):
                bs.type = bit_section[2]
            else:
                raise TechnicalException(f"Third bit_section element is the value type and must be a type in (int, str, bytes) (obtained type: {Typing.get_object_class_fullname(bit_section[2])} ; value: {bit_section[2]})")
            
            # Set right padding
            if len(bit_section) > 4:
                if bit_section[4] is None or isinstance(bit_section[4], bool):
                    bs.right_padded = bit_section[4]
                else:
                    raise TechnicalException(f"Fifth bit_section element define if right padding must be done and must be a boolean or None (obtained type: {Typing.get_object_class_fullname(bit_section[4])} ; value: {bit_section[4]})")
            else:
                bs.right_padded = None
                
            self.__series.append(bs)
            self.__len = None
            self.__update_index_by_name()
            
            # Set value
            if len(bit_section) > 3:
                self.set_bit_section_value(bs.name, bit_section[3])
    
    def __update_index_by_name(self):
        self.__index_by_name = {}
        for index, bs in enumerate(self):
            self.__index_by_name[bs.name] = index
            
    def get_bit_section(self, index=None, name=None):
        if name is not None:
            if name in self.__index_by_name:
                index = self.__index_by_name[name]
            else:
                raise FunctionalException(f"No bit section of name '{name}'")

        if index is not None:
            return self.__series[index]
        else:
            raise TechnicalException("Undefined parameter 'index' or 'name'")
    
    def set_bit_section_value(self, name=None, value=None, index=None):
        bs = self.get_bit_section(index=index, name=name)
        if value is None:
            bs.value = value
        elif bs.type is int:
            if not isinstance(value, int):
                raise FunctionalException(f"Unexpected value type {type(value)} (bit section '{bs.name}' has type {bs.type})")
            bs.value = value
        elif bs.type is str:
            if not isinstance(value, str):
                raise FunctionalException(f"Unexpected value type {type(value)} (bit section '{bs.name}' has type {bs.type})")
            if StrTools.is_hex(value):
                bs.value = value
            else:
                raise TechnicalException(f"If value is set in string format, it has to be an hexa string (value: [{value}])")
        elif bs.type is bytes:
            if not isinstance(value, bytes):
                raise FunctionalException(f"Unexpected value type {type(value)} (bit section '{bs.name}' has type {bs.type})")
            bs.value = value
        else:
            raise TechnicalException(f"Value must be a positive integer, a hexa string, bytes or None (value type: {Typing.get_object_class_fullname(value)} ; value: {value})")
    
    def from_hex(self, hex_str, right_padded=False):
        """
        Fill bit series from given hexadecimal string.
        
        If bit series has a bit length that is not a multiple of 4, padding is expected in hex_str at left or right depending on parameter right_padded.
        A control is made if padding bits are only zeros.
        """
        # Verify padding
        bin_str = Binary.convert_hex_str_to_bin_str(hex_str)
        nb_bits_out_of_block = len(bin_str) - self.nb_bits
        if nb_bits_out_of_block < 0:
            raise FunctionalException(f"Hexadecimal string has not enough bits (expected: {self.nb_bits} ; obtained: {len(hex_str) * 4}")
        elif nb_bits_out_of_block > 0:
            if right_padded:
                padding_bits = bin_str[-nb_bits_out_of_block:]
            else:
                padding_bits = bin_str[0:nb_bits_out_of_block]
            value = int(padding_bits, 2)
            if value != 0:
                raise FunctionalException(f"Hexadecimal string has unexpected padded characters, only zero padding is managed (expected bits number: {self.nb_bits} ; {'right' if right_padded else 'left'} padding ; obtained padding bits: {padding_bits})\n    obtained bits: {bin_str}")
        
        # Fill bit sections
        bit_offset = 0 if right_padded else nb_bits_out_of_block
        for bs in self:
            # Extract bit section value
            try:
                hex_value = self.__from_hex_get_bit_section_value(hex_str, bit_offset=bit_offset, bit_length=bs.length, right_padding=bs.right_padded)
                if bs.type is int:
                    value = int(hex_value, 16)
                elif bs.type is bytes:
                    value = StrTools.hex_to_bytes(hex_value)
                elif bs.type is str:
                    value = hex_value
                else:
                    raise TechnicalException(f"Unmanaged bit section value type {bs.type} (possible types: int, str, bytes)")
            except Exception as exc:
                raise TechnicalException(f"Error while extracting value of field '{bs.name}': {exc}") from exc
                
            # Set value
            self.set_bit_section_value(bs.name, value)
            
            # Prepare next round
            bit_offset += bs.length
    
    def __from_hex_get_bit_section_value(self, hex_str, bit_offset, bit_length, right_padding):
        bin_str = "".join(["{:04b}".format(int(hc, 16)) for hc in hex_str])
        bs_bin_str = bin_str[bit_offset : bit_offset + bit_length]
        if bit_length % 4 > 0:
            str_padding = "0" * (4 - bit_length % 4)
            if right_padding is not None and right_padding:
                bs_bin_str_padded = bs_bin_str + str_padding
            else:
                bs_bin_str_padded = str_padding + bs_bin_str
        else:
            bs_bin_str_padded = bs_bin_str
        bs_hex_str = "".join(["{:X}".format(int(bs_bin_str_padded[i*4:i*4+4],2)) for i in range(len(bs_bin_str_padded)//4)])
        # logger.info(f"++++++++++ __from_hex_get_bit_section_value: bit_offset={bit_offset} ; bit_length={bit_length}\n    hex_str: [{hex_str}]\n    bin_str: [{bin_str}]\n    bs_bin_str: [{bs_bin_str}]\n    bs_bin_str: [{bs_bin_str_padded}]\n => bs_hex_str: [{bs_hex_str}]")
        return bs_hex_str
    
    def to_bin(self, right_padding=False):
        """
        Convert bit series to binary string.
        
        If a bit section is of type str and has a bit length lower than its section value,
        the section value is considered padded with zeros at left or right, depending on parameter right_padding.
        """
        res_list = []
        for bs in self:
            try:
                if bs.right_padded is not None:
                    bs_right_padded = bs.right_padded
                else:
                    bs_right_padded = right_padding
                    
                if bs.type is int:
                    bs_format = f"{{:0{bs.length}b}}"
                    res_bs = bs_format.format(bs.value)
                elif bs.type is str or bs.type is bytes:
                    if bs.type is bytes:
                        value = StrTools.to_hex(bs.value)
                    else:
                        value = bs.value
                    
                    res_bs = "".join(["{:04b}".format(int(hc, 16)) for hc in value])
                    if len(res_bs) > bs.length:
                        # The section value was padded
                        if bs_right_padded:
                            res_bs_padding = res_bs[bs.length:]
                            res_bs = res_bs[0:bs.length]
                        else:
                            res_bs_padding = res_bs[0:-bs.length]
                            res_bs = res_bs[-bs.length:]
                        if int(res_bs_padding, 2) != 0:
                            raise TechnicalException(f"For field '{bs.name}', the value was padded with {len(res_bs_padding)} bits ('{res_bs_padding}') at {'right' if right_padding else 'left'} with non zero bits")
                else:
                    raise TechnicalException(f"For field '{bs.name}', unmanaged type {bs.type}")
            except TechnicalException as exc:
                raise exc
            except Exception as exc:
                raise TechnicalException(f"Error while formatting field '{bs.name}': {exc}") from exc
            
            if len(res_bs) != bs.length:
                raise FunctionalException(f"For field '{bs.name}', the value [{bs.value}] has binary length {len(res_bs)} (expected length: {bs.length})")
            res_list.append(res_bs)
        return "".join(res_list)
    
    def to_hex(self, right_padding=False, bytes_padding=True, nbbits_by_block=None):
        """
        Convert bit series to hexadecimal string (ex: 'A2FF').
        
        If bit series has a length that is not a multiple of block size, a padding with zeros is made at left or right, depending on parameter right_padding.
        The block size is equal to:
            1. nbbits_by_block (if nbbits_by_block is not None)
            2. 8 (else if bytes_padding is True)
            3. 4 (in other cases)
        """
        # Convert to binary string
        res_bin = self.to_bin(right_padding=right_padding)

        # Convert binary string to hexadecimal string
        if nbbits_by_block is None:
            nbbits_by_block = 8 if bytes_padding else 4
        return Binary.convert_bin_str_to_hex_str(res_bin, right_padding, nbbits_by_block=nbbits_by_block)
    
def convert_bit_series_to_table(bit_series):
    res = TableWithHeader()
    res.header = TableRow(cells_content=["Name", "Bit length", "Type", "Value"])
    for bit_section in bit_series:
        res.add_row(cells_content=[bit_section.name, bit_section.length, bit_section.type, bit_section.value])
    return res

def convert_bit_series_to_name_value_table(bit_series):
    res = TableWithHeader()
    res.header = TableRow(cells_content=["Name", "Value"])
    for bit_section in bit_series:
        res.add_row(cells_content=[bit_section.name, bit_section.value])
    return res


