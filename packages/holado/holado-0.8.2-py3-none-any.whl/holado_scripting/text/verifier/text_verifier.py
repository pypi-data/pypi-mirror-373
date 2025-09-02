
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

from holado_core.common.exceptions.verify_exception import VerifyException
import logging
from holado_scripting.text.verifier.functions.verify_function_extract_in import VerifyFunctionExtractIn
from holado_scripting.text.verifier.functions.verify_function_match_pattern import VerifyFunctionMatchPattern
from holado_scripting.text.base.text_inspecter import TextInspecter
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class TextVerifier(TextInspecter):

    def __init__(self):
        super().__init__()
        
        self.__text_interpreter = None
        self.__process_log_match_failure = True
        
    def initialize(self, var_manager, expression_evaluator, text_interpreter):
        super().initialize(var_manager, expression_evaluator)
        self.__text_interpreter = text_interpreter
        
        self.__register_default_functions()

    def verify(self, obtained, expected, do_check_case = True, raise_exception = True):
        res = True
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
        
            logger.trace(f"Verifying obtained '{obtained}' with expected '{expected}'...")
        
        # Check if expected is a verify function
        if expected is not None:
            result = self.__evaluate_function_verify(expected, obtained, raise_exception)
            if result is not None:
                return result
            
        # Interpret expected
        interpreted_expected = self.__text_interpreter.interpret(expected)
        
        # Verify
        if interpreted_expected != obtained:
            # Build message
            msg = "Match failure: '{}' is different than '{}'".format(obtained, interpreted_expected)
            if interpreted_expected != expected:
                msg += " (from '{}')".format(expected)
                
            # log
            self._log_match_failure(msg)
            
            # Manage raise
            if raise_exception:
                raise VerifyException(msg)
            else:
                res = False
            
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Verify obtained '{obtained}' with expected '{expected}' => [{res}]")
        return res

    def __evaluate_function_verify(self, expected, obtained, raise_exception):
        func_name, args_str = self._get_function_and_args_strings(expected)
        verify_function = self._get_function(func_name) if func_name is not None else None
        if verify_function is None:
            return None

        if func_name == "ExtractIn":
            args = [args_str]
        else:
            args = self._get_args(args_str)
            
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            
            logger.trace(f"Evaluating verify function '{func_name}' with args {args} on obtained '{obtained}'")
        res = verify_function.apply(obtained, args, raise_exception=raise_exception)
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Evaluate verify function [{expected}] => [{func_name}({', '.join(args)})] => [{res}] (type: {Typing.get_object_class_fullname(res)})")
        return res
                
    def __register_default_functions(self):
        self.register_function("MatchPattern", VerifyFunctionMatchPattern(self._variable_manager))
        self.register_function("ExtractIn", VerifyFunctionExtractIn(self._variable_manager))

    def _log_match_failure(self, msg):
        if self.__process_log_match_failure:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"--- VERIFIER --- {msg}")
        
    
