
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

from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
import string
from holado_core.common.exceptions.functional_exception import FunctionalException
import re
from holado_python.standard_library.typing import Typing

try:
    from bitarray import bitarray
    with_bitarray = True
except:
    with_bitarray = False

logger = logging.getLogger(__name__)


class StrTools(object):
    
    #TODO EKL: move following methods from Tools to this class
    # @classmethod
    # def get_indent_string(cls, indent):
    #     return " " * indent
    #
    # @classmethod
    # def indent_string(cls, indent, txt):
    #     ind_str = StrTools.get_indent_string(indent)
    #     lines = txt.split("\n") if txt else []
    #     return ind_str + ("\n" + ind_str).join(lines)
    #
    # @classmethod
    # def truncate_text(cls, text, length = Config.message_truncate_length, truncated_suffix = "[...]", is_length_with_suffix=False):
    #     if len(text) > length:
    #         if truncated_suffix:
    #             if is_length_with_suffix:
    #                 return text[0 : length - len(truncated_suffix)] + truncated_suffix
    #             else:
    #                 return text[0 : length] + truncated_suffix
    #         else:
    #             return text[0 : length]
    #     else:
    #         return text
    
    if with_bitarray:
        @classmethod
        def is_bitarray(cls, src):
            # Convert source to str
            if isinstance(src, bytes):
                value_str = src.decode('utf-8')
            elif isinstance(src, str):
                value_str = src
            else:
                raise FunctionalException(f"Unexpected source type {Typing.get_object_class_fullname(src)} (allowed types: string, bytes)")
            
            try:
                bitarray(value_str)
            except:
                return False
            return True
    
    @classmethod
    def is_hex(cls, src):
        if not isinstance(src, str):
            return False
        
        hex_digits = set(string.hexdigits)
        return all(c in hex_digits for c in src)
    
    @classmethod
    def hex_to_bytes(cls, src):
        if not cls.is_hex(src):
            raise FunctionalException(f"Source [{src}] (type: {Typing.get_object_class_fullname(src)}) is not an hexadecimal string")
        
        if len(src) % 2 != 0:
            raise FunctionalException(f"Hex string must have a length multiple of 2. If not, a padding is usually applied with a 0 at left or right. Hex string: '{src}'")
        
        try:
            res = bytes.fromhex(src)
        except ValueError as exc:
            raise TechnicalException(f"Error with hex string '{src}'") from exc
        
        # if len(res) * 2 != len(src):
        #     raise TechnicalException(f"Failed to convert hex to bytes: hex length is {len(src)} ; bytes length is {len(res)}")
        
        return res
    
    @classmethod
    def to_bytes(cls, src):
        if isinstance(src, int):
            signed = True if src < 0 else False
        
            length = 1
            val = src
            while val > 255:
                length += 1
                val = val / 256
        
            res = src.to_bytes(length, 'big', signed=signed)
        elif isinstance(src, bytes):
            res = src
        elif isinstance(src, str):
            if re.match(r"^b('|\").*\1$", src):
                res = eval(src)
                if not isinstance(res, bytes):
                    raise TechnicalException(f"Failed to eval string [{src}] as bytes ; eval result: [{res}] (type: {Typing.get_object_class_fullname(res)})")
            else:
                res = src.encode('utf-8')
        else:
            raise FunctionalException(f"Unexpected source type {Typing.get_object_class_fullname(src)} (allowed types: int, string, bytes)")
        
        return res
    
    @classmethod
    def to_hex(cls, src, do_upper=True):
        src_bytes = cls.to_bytes(src)
        
        res = src_bytes.hex()
        if do_upper:
            res = res.upper()
        
        return res
    
    @classmethod
    def to_string(cls, src):
        if isinstance(src, bytes):
            return src.decode('utf-8')
        elif isinstance(src, str):
            return src
        else:
            return str(src)


