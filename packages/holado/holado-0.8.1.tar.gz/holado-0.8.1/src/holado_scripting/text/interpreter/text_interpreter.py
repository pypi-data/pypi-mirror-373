
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
from holado_scripting.text.interpreter.functions.function_dynamic_value import FunctionDynamicValue
import re
from holado_scripting.text.interpreter.exceptions.interpreter_exception import NotExistingFunctionTextInterpreterException
from holado_scripting.text.interpreter.functions.function_cast import FunctionCast
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_scripting.text.interpreter.functions.function_to_base_64 import FunctionToBase64
from holado_scripting.text.interpreter.functions.function_to_hex import FunctionToHex
from holado_scripting.text.interpreter.functions.function_hex_to_int import FunctionHexToInt
from holado_scripting.text.interpreter.functions.function_to_bytes import FunctionToBytes
from holado_scripting.text.interpreter.functions.function_hex_to_bytes import FunctionHexToBytes
from holado_core.common.tools.tools import Tools
from holado_scripting.text.base.text_inspecter import TextInspecter
from holado_scripting.text.interpreter.functions.function_escape_all_bytes import FunctionEscapeAllBytes
from holado_scripting.common.tools.evaluate_parameters import EvaluateParameters
from holado_scripting.text.interpreter.functions.function_exists_variable import FunctionExistsVariable
from holado_scripting.text.interpreter.functions.function_convert import FunctionConvert
from holado_python.common.tools.datetime import DateTime
from holado_python.standard_library.typing import Typing
from holado_scripting.text.interpreter.functions.function_to_string import FunctionToString
from holado_scripting.text.interpreter.functions.function_apply_function import FunctionApplyFunction

logger = logging.getLogger(__name__)


class TextInterpreter(TextInspecter):

    def __init__(self):
        super().__init__()
        
        self.__text_verifier = None
        
        # self.__regex_to_be_interpreted = re.compile(r"^\$\{((?:(?!\$\{)[^\}])*)\}$")
        self.__regex_to_be_interpreted = re.compile(r"^\$\{(.*)\}$")
        
    def initialize(self, var_manager, expression_evaluator, text_verifier, dynamic_text_manager):
        super().initialize(var_manager, expression_evaluator)
        self.__text_verifier = text_verifier
        
        self.__register_default_functions(dynamic_text_manager)

    def interpret(self, str_to_interpret, eval_params=EvaluateParameters.default_without_raise(), log_level=logging.DEBUG):
        """
        @summary: Interpret given text by replacing all occurrences of "${...}" by corresponding values.
        @param str_to_interpret: String - Text to interpret
        @return: Interpreted result
        """
        
        if str_to_interpret is None:
            return None
        
        if Tools.do_log(logger, logging.TRACE, max_log_level=log_level):  # @UndefinedVariable
            logger.log(Tools.do_log_level(logging.TRACE, log_level), "Interpreting '{}'...".format(str_to_interpret))  # @UndefinedVariable
        
        # Interpret and get result as object
        res, _ = self.__interpret(str_to_interpret, eval_params=eval_params, log_level=log_level)

        if Tools.do_log_if_objects_are_different(logger, log_level, str_to_interpret, res):
            logger.log(log_level, "Interpreting '{}' -> [{}] (type: {})".format(str_to_interpret, res, type(res)))
            
        return res

    def _interpret_sections(self, str_to_interpret, eval_params=EvaluateParameters.default_without_raise(), log_level=logging.DEBUG):
        """
        @summary: Interpret given text by replacing all occurrences of "${...}" by variables containing corresponding values.
        @param str_to_interpret: String - Text to interpret
        @return: Interpreted result
        """
        
        if str_to_interpret is None:
            return None
        
        if Tools.do_log(logger, logging.TRACE, max_log_level=log_level):  # @UndefinedVariable
            logger.log(Tools.do_log_level(logging.TRACE, log_level), "Interpreting sections in '{}'...".format(str_to_interpret))  # @UndefinedVariable
        
        # Interpret and get result as object
        res, locals_ = self.__interpret(str_to_interpret, replace_sections_by_variables=True, eval_params=eval_params, log_level=log_level)

        if Tools.do_log_if_objects_are_different(logger, log_level, str_to_interpret, res):
            logger.log(log_level, f"Interpreting sections in '{str_to_interpret}' -> [{res}] (type: {type(res)}, locals: {locals_})")
        return res, locals_

    def __interpret(self, str_to_interpret, replace_sections_by_variables=False, eval_params=EvaluateParameters.default_without_raise(), log_level=logging.DEBUG):
        res = None
        locals_ = {}
        
        # If the string is to be interpreted
        section_indexes = self._search_all_interpret_sections(str_to_interpret)
        if (0,len(str_to_interpret)) in section_indexes:
            r_match = self.__regex_to_be_interpreted.match(str_to_interpret)
            if r_match:
                str_under_interpret = r_match.group(1).strip()
                res = self.__interpret_text(str_under_interpret, eval_params=eval_params, log_level=log_level)
                # Text is not interpretable ; expect it will be the case later
                if res == str_under_interpret:
                    res = str_to_interpret
                elif isinstance(res, str) and self.__text_verifier._has_function(res, with_interpreted=False):
                    res = f"${{{res}}}"
            else:
                raise TechnicalException(f"Failed to find interpret section whereas its indexes were found")
        else:
            res, locals_ = self.__find_and_interpret_sections(str_to_interpret, replace_sections_by_variables=replace_sections_by_variables, eval_params=eval_params, log_level=log_level)
            
        return res, locals_
    
    def __interpret_text(self, text, eval_params=EvaluateParameters.default_without_raise(), log_level=logging.DEBUG):  # @UndefinedVariable
        # Manage functions
        if self._has_function(text, with_interpreted=False):
            return self.__evaluate_function(text, eval_params=eval_params, log_level=log_level)
        
        # Manage evaluation
        _, res = self._expression_evaluator.evaluate_expression(text, eval_params=eval_params, log_level=Tools.do_log_level(log_level, logging.TRACE))  # @UndefinedVariable
        return res
    
    def __find_and_interpret_sections(self, str_to_interpret, replace_sections_by_variables=False, eval_params=EvaluateParameters.default_without_raise(), log_level=logging.DEBUG):
        res = str_to_interpret
        locals_ = {}
        
        offset = 0
        excluded_indexes = []
        while True:
            indexes = self._search_interpret_section(res, offset, excluded_indexes)
            if indexes is None:
                # Try again from beginning (in case of nested sections)
                indexes = self._search_interpret_section(res, 0, excluded_indexes)
                if indexes is not None:
                    offset = 0
                else:
                    # No more section to replace
                    break
                                
            ind_beg, ind_end = indexes
            sub_str = res[ind_beg:ind_end]
            
            # Interpret sub-section
            interpreted_value = self.interpret(sub_str, eval_params=eval_params, log_level=log_level)
            
            # Manage sections that aren't interpretable
            interpreted_str = f"{interpreted_value}"
            if interpreted_str == sub_str:
                excluded_indexes.append((ind_beg, ind_end))
                offset = ind_end
                continue
            
            # Define section replacement
            if replace_sections_by_variables and type(interpreted_value) not in [str, int, float, bytes]:
                var_name = self._variable_manager.new_local_variable_name()
                locals_[var_name] = interpreted_value
                section_replace_str = var_name
            else:
                section_replace_str = interpreted_str
            
            # Replace by interpreted value
            res = f"{res[0:ind_beg]}{section_replace_str}{res[ind_end:]}"
            
            # Prepare next replacement
            offset = ind_beg + len(section_replace_str)
                
        return res, locals_
    
    def __evaluate_function(self, fct_str, eval_params=EvaluateParameters.default_without_raise(), log_level=logging.DEBUG):
        func_name, args_str = self._get_function_and_args_strings(fct_str, with_interpreted=False)
        func = self._get_function(func_name) if func_name is not None else None
        if func is None:
            raise NotExistingFunctionTextInterpreterException("Cannot find a function in '{}'".format(fct_str))
        
        args = self._get_args(args_str)
        
        if Tools.do_log(logger, logging.TRACE, max_log_level=log_level):  # @UndefinedVariable
            logger.log(Tools.do_log_level(logging.TRACE, max_log_level=log_level), f"Evaluating function '{func_name}' with args {args}")  # @UndefinedVariable
            # logger.trace(f"Evaluating function '{func_name}' with args {args} (eval_params: {eval_params})", stack_info=True)
        try:
            res = func.apply(args)
        except BaseException as exc:
            if eval_params.raise_on_interpret_error:
                raise exc
            else:
                res = fct_str
                
        if Tools.do_log(logger, log_level):
            logger.log(log_level, f"Evaluate function [{fct_str}] => [{func_name}({', '.join(args)})] => [{res}] (type: {Typing.get_object_class_fullname(res)})")
        return res
    
    def __register_default_functions(self, dynamic_text_manager):
        self.register_function("len", FunctionApplyFunction(len, self, self._variable_manager))
        self.register_function("DynamicValue", FunctionDynamicValue(dynamic_text_manager))
        self.register_function("ExistsVariable", FunctionExistsVariable(self._variable_manager))
        
        # Convert
        self.register_function("int", FunctionCast(int, self, self._variable_manager))
        self.register_function("float", FunctionCast(float, self, self._variable_manager))
        self.register_function("str", FunctionCast(str, self, self._variable_manager))
        self.register_function("EscapeAllBytes", FunctionEscapeAllBytes(self, self._variable_manager))
        self.register_function("HexToBytes", FunctionHexToBytes(self._expression_evaluator))
        self.register_function("HexToInt", FunctionHexToInt(self, self._variable_manager))
        self.register_function("ToBase64", FunctionToBase64(self, self._variable_manager))
        self.register_function("ToBytes", FunctionToBytes(self, self._variable_manager))
        self.register_function("ToHex", FunctionToHex(self, self._variable_manager))
        self.register_function("ToString", FunctionToString(self, self._variable_manager))
        self.register_function("DatetimeUTCToTAI", FunctionConvert(lambda dt: DateTime.datetime_utc_to_tai(dt), self, self._variable_manager))
        self.register_function("DatetimeTAIToUTC", FunctionConvert(lambda dt: DateTime.datetime_tai_to_utc(dt), self, self._variable_manager))
        
    
    
    
    
