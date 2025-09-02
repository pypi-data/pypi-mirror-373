
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
from holado_core.common.tools.comparators.comparator import Comparator
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class BytesComparator(Comparator):
    
    def __init__(self, encoding_1=None, encoding_2=None):
        super().__init__("bytes")
        
        self.__encoding_1 = encoding_1
        self.__encoding_2 = encoding_2
    
    def _convert_input1(self, obj, name):
        return self.__convert_input(obj, name, self.__encoding_1)
    
    def _convert_input2(self, obj, name):
        return self.__convert_input(obj, name, self.__encoding_2)
    
    def __convert_input(self, obj, name, encoding):
        if isinstance(obj, str):
            if encoding is not None:
                res = obj.encode(encoding=encoding)
            else:
                res = obj.encode()
        else:
            res = obj
            
        if not isinstance(res, bytes):
            raise FunctionalException(f"{name.capitalize()} value is not a bytes: [{res}] (type: {Typing.get_object_class_fullname(res)})")
        return res

