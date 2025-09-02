
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

from builtins import int
import logging
from datetime import datetime
import string
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class UniqueValueManager(object):
    """
    @summary: Unique value manager.
    An internal counter is used to generate a unique integer at any moment.
    At first use, this counter is initialized with the number of seconds since 01/01/2020, to ensure a minimal uniqueness between sessions.
    
    This manager can generate unique integers and unique strings.
    For strings, a unique integer is encoded in a base in range [2, 62] (default: 62).
    """
    
    def __init__(self, padding_character='0'):
        self.__last_unique_int = None
        self.__padding_character = padding_character
        
        self.__digs = string.digits + string.ascii_uppercase + string.ascii_lowercase
        
    def new_integer(self, do_log=True):
        if self.__last_unique_int is None:
            # Compute timestamp as number of seconds since 01/01/2016
            self.__last_unique_int = int((datetime.now() - datetime(2020, 1, 1)).total_seconds()) - 1
            
        self.__last_unique_int += 1
        res = self.__last_unique_int
        
        if do_log:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"New unique integer: {res}")
        return res
    
    def new_hex(self, length=None, truncate_to_length=True, do_log=True):
        res = self.new_string(base=16, padding_length=length, padding_character="0", raise_if_padding_impossible=not truncate_to_length, do_log=False)
        res = res.upper()
        if length is not None and len(res) > length:
            if truncate_to_length:
                res = res[-length:]
            else:
                raise TechnicalException(f"Unique HEX integer ({res}) has length {len(res)} that exceeds expected length {length}")
        
        if do_log:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"New unique HEX integer: {res}")
        return res
    
    def new_string(self, base=62, padding_length=None, padding_character=None, raise_if_padding_impossible=True, do_log=True):
        if base < 2 or base > 62:
            raise TechnicalException("Base must be in range [2, 62]")
        value = self.new_integer(do_log=False)
        res = self.__encode_int_until_base62(value, base)
        
        if padding_length:
            if len(res) > padding_length and raise_if_padding_impossible:
                raise TechnicalException(f"Unique string before padding has length {len(res)}, it is not possible to apply a padding length of {padding_length}")
            if len(res) < padding_length:
                if padding_character is None and self.__padding_character is None:
                    raise TechnicalException(f"In order to manage padding, the padding character must be given as parameter to UniqueValueManager.new_string or constructor of UniqueValueManager")
                pc = padding_character if padding_character is not None else self.__padding_character
                res = res.rjust(padding_length, pc)
            
        if do_log:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"New unique string: [{res}]")
        return res
    
    def __encode(self, int_value, base):
        # Encode given integer in 36 base
        return self.__encode_int_until_base62(int_value, base)
    
    def __encode_int_until_base62(self, x, base):
        if x < 0: 
            sign = -1
        elif x == 0: 
            return self.__digs[0]
        else: 
            sign = 1
        x *= sign
        digits = []
        while x:
            x, ind_digits = divmod(x, base)
            digits.append(self.__digs[ind_digits])
        if sign < 0:
            digits.append('-')
        digits.reverse()
        return ''.join(digits)

