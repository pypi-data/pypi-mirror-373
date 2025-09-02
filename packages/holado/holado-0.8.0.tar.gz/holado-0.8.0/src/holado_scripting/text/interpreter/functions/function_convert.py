
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
from holado_core.common.exceptions.functional_exception import FunctionalException
import logging
from holado_core.common.tools.tools import Tools
from holado_test.scenario.step_tools import StepTools
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class FunctionConvert(BaseFunction):

    def __init__(self, convert_func, text_interpreter, var_manager):
        self.__convert_func = convert_func
        self.__text_interpreter = text_interpreter
        self.__variable_manager = var_manager
        
        
    def apply(self, args):
        # Verify arguments
        if not isinstance(args, list):
            raise TechnicalException("Arguments must be a list")
        if len(args) != 1:
            raise FunctionalException(f"Converting function requires one argument.")

        src = args[0]
        res = src
        
        # Interpret source
        if isinstance(res, str):
            res = StepTools.extract_string_value(res)
            res = self.__text_interpreter.interpret(res)
        
        # Manage if source is a variable expression
        if isinstance(res, str) and self.__variable_manager.exists_variable(expression=res):
            res = self.__variable_manager.get_value(res)

        res = self.__convert_func(res)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[FunctionConvert({self.__convert_func})] Converted [{src}] (type: {Typing.get_object_class_fullname(src)}) -> [{res}] (type: {Typing.get_object_class_fullname(res)})")
        return res
    
