
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
from holado_core.common.tools.comparators.comparator import Comparator,\
    CompareOperator
from holado_core.common.tools.tools import Tools
from holado.common.context.session_context import SessionContext
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class StringComparator(Comparator):

    def __init__(self, text_interpreter=None, text_verifier=None):
        super().__init__("string")
        self.__text_interpreter = text_interpreter
        self.__text_verifier = text_verifier
        
    def __get_text_interpreter(self):
        if self.__text_interpreter is not None:
            return self.__text_interpreter
        elif SessionContext.instance().has_scenario_context():
            return SessionContext.instance().get_scenario_context().get_text_interpreter()
        else:
            return SessionContext.instance().text_interpreter
    
    def __get_text_verifier(self):
        if self.__text_verifier is not None:
            return self.__text_verifier
        elif SessionContext.instance().has_scenario_context():
            return SessionContext.instance().get_scenario_context().get_text_verifier()
        else:
            return SessionContext.instance().text_verifier
    
    def _compare_by_operator(self, obj_1, operator: CompareOperator, obj_2, is_obtained_vs_expected = True, raise_exception = True, redirect_to_equals=True):
        if operator == CompareOperator.Equal:
            return self.__verify_by_text_interpreter(obj_1, obj_2, is_obtained_vs_expected, raise_exception)
        else:
            i_obj_1 = self.__get_text_interpreter().interpret(obj_1)
            i_obj_2 = self.__get_text_interpreter().interpret(obj_2)
            super()._compare_by_operator(i_obj_1, operator, i_obj_2, is_obtained_vs_expected, raise_exception, redirect_to_equals=redirect_to_equals)
    
    def _convert_input(self, obj, name):
        if isinstance(obj, str):
            res = obj
        else:
            res = str(obj)
        return res
    
    def __verify_by_text_interpreter(self, str_1, str_2, is_obtained_vs_expected = True, raise_exception = True):
        """
        Compare by equality.
        Switch is_obtained_vs_expected:
            - True: value 1 is considered obtained ; value 2 is considered expected ; only expected value is interpreted
            - False: value 1 is considered expected ; value 2 is considered obtained ; only expected value is interpreted
            - None: value 1 is compared to value 2 ; both values are interpreted
        """
        if not isinstance(str_1, str):
            if raise_exception:
                raise VerifyException(f"{self._get_name_1(is_obtained_vs_expected).capitalize()} value is not a string: [{str_1}] (type: {Typing.get_object_class_fullname(str_1)})")
            else:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Compare result is false since {self._get_name_1(is_obtained_vs_expected)} value is not a string: [{str_1}] (type: {Typing.get_object_class_fullname(str_1)})")
                return False
        if not isinstance(str_2, str):
            if raise_exception:
                raise VerifyException(f"{self._get_name_2(is_obtained_vs_expected).capitalize()} value is not a string: [{str_2}] (type: {Typing.get_object_class_fullname(str_2)})")
            else:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Compare result is false since {self._get_name_2(is_obtained_vs_expected)} value is not a string: [{str_2}] (type: {Typing.get_object_class_fullname(str_2)})")
                return False
        
        if is_obtained_vs_expected is None:
            # Interpret obtained as TextInterpreter.verify won't do it on obtained parameter
            str_1 = self.__get_text_interpreter().interpret(str_1)
        
        if is_obtained_vs_expected == True or is_obtained_vs_expected is None:
            res = self.__get_text_verifier().verify(str_1, str_2, raise_exception=raise_exception)
        else:
            res = self.__get_text_verifier().verify(str_2, str_1, raise_exception=raise_exception)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("[{}] str_1 equals str_2 => {}\n    str_1 = [{}]\n    str_2 = [{}]".format(Typing.get_object_class(self).__name__, res, str_1, str_2))
        return res
    
    
