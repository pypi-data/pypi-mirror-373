
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

from holado_scripting.text.base.base_function import BaseFunction
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_scripting.text.interpreter.functions.function_to_bytes import FunctionToBytes
from holado_python.standard_library.typing import Typing


class FunctionEscapeAllBytes(BaseFunction):

    def __init__(self, text_interpreter, var_manager):
        self.__func_to_bytes = FunctionToBytes(text_interpreter, var_manager)
    
    def apply(self, args):
        src = self.__func_to_bytes.apply(args)
        
        # Convert source to bytes
        if isinstance(src, bytes):
            res = "b'{}'".format(''.join('\\x{:02x}'.format(b) for b in src))
        else:
            raise TechnicalException(f"Unexpected source type {Typing.get_object_class_fullname(src)} (allowed types: bytes)")
        
        return res
    
