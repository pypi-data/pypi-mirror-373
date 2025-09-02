
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.string_tools import StrTools

logger = logging.getLogger(__name__)


class Binary():
    """
    Tools to manipulate binary data.
    """
    
    @classmethod
    def convert_bin_str_to_hex_str(cls, bin_str, right_padding=False, nbbits_by_block=8):
        """
        Convert binary string to hexadecimal string (ex: 'A2FF').
        
        If binary string has a length that is not a multiple of nbbits_by_block, a padding with zeros is made at left or right, depending on parameter right_padding.
        """
        # Manage padding for bits out of blocks of nbbits_by_block bits
        nb_bits_out_of_block = len(bin_str) % nbbits_by_block
        if nb_bits_out_of_block > 0:
            padding_bits = "0" * (nbbits_by_block - nb_bits_out_of_block)
            if right_padding:
                bin_str += padding_bits
            else:
                bin_str = padding_bits + bin_str
        if len(bin_str) % nbbits_by_block != 0:
            raise TechnicalException("Failed to pad binary series")
        
        # Manage 4-bits blocks
        res_list = []
        for i in range(len(bin_str) // 4):
            res_list.append("{:X}".format(int(bin_str[i*4:i*4+4],2)))
        return "".join(res_list)
    
    @classmethod
    def convert_hex_str_to_bin_str(cls, hex_str, bit_length=None, right_padded=False):
        """
        Convert hexadecimal string to binary string (ex: '10001101').
        """
        res = "".join(["{:04b}".format(int(hc, 16)) for hc in hex_str])
        
        if bit_length is not None:
            if bit_length > len(hex_str) * 4:
                raise FunctionalException(f"Data bit length ({bit_length}) is greater than data size ({len(hex_str) * 4})")
            if right_padded:
                res = res[:bit_length]
            else:
                res = res[-bit_length:]
        
        return res
        
    @classmethod
    def pad_bin_str_with_itself(cls, bin_str, bit_length, right_padding=False):
        if len(bin_str) == 0:
            raise FunctionalException(f"Binary string is empty, it is not possible to pad it with itself")
        if bit_length < len(bin_str):
            raise FunctionalException(f"Binary string has a length ({len(bin_str)}) greater than expected length ({bit_length}) after padding")
        
        res = bin_str
        while len(res) < bit_length:
            missing_len = bit_length - len(res)
            if len(bin_str) <= missing_len:
                pad_str = bin_str
            else:
                pad_str = bin_str[:missing_len]
            if right_padding:
                res += pad_str
            else:
                res = pad_str + res
        
        return res

    @classmethod
    def pad_data(cls, data_str, data_length, padding_char='0', right_padding=False):
        if data_length < len(data_str):
            raise FunctionalException(f"Data has a length ({len(data_str)}) greater than expected length ({data_length}) after padding")
        
        pad_str = padding_char * (data_length - len(data_str))
        if right_padding:
            return data_str + pad_str
        else:
            return pad_str + data_str

    @classmethod
    def data_length_after_padding(cls, data_length, multiple_of_length):
        if data_length == 0:
            return 0
        else:
            return ((data_length - 1) // multiple_of_length + 1) * multiple_of_length

    @classmethod
    def get_data_bit_length(cls, data):
        """Return number of bits of data after conversion in binary format.
        Note: for string data type, data is supposed to be in hexadecimal format.
        """
        if isinstance(data, int):
            return len(f"{data:b}")
        elif isinstance(data, bytes):
            return len(data) * 8
        elif isinstance(data, str):
            if StrTools.is_hex(data):
                return len(data) * 4
            else:
                raise TechnicalException(f"String data must be in hexadecimal format: [{data}]")
        else:
            raise TechnicalException(f"Unmanaged data of type {type(data)}")



