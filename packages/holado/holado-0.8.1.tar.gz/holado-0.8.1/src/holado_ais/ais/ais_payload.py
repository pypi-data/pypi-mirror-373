
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
from holado_binary.ipc.binary import Binary

logger = logging.getLogger(__name__)


class AISPayload(object):
    
    @classmethod
    def bin_2_ascii(cls, bin_msg):
        hex_msg = Binary.convert_bin_str_to_hex_str(bin_msg, nbbits_by_block=6)
        res_chars = []
        for i in range(len(hex_msg)//2):
            char_int = int(hex_msg[i*2:i*2+2],16)
            if char_int < 40:
                char_int += 48
            else:
                char_int += 56
            res_chars.append(chr(char_int))
        return "".join(res_chars)
    

