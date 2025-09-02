
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
import abc
from enum import Enum
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class CompareOperator(str, Enum):
    Different = ("!=", "Equal", "Different")
    Equal = ("==", "Different", "Equal")
    Inferior = ("<", "SuperiorOrEqual", "Superior")
    InferiorOrEqual = ("<=", "Superior", "SuperiorOrEqual")
    Superior = (">", "InferiorOrEqual", "Inferior")
    SuperiorOrEqual = (">=", "Inferior", "InferiorOrEqual")
    
    def __new__(cls, value, not_name, switch_name):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__not_name = not_name
        obj.__switch_name = switch_name
        return obj
    
    @property
    def not_(self):
        return CompareOperator[self.__not_name]
    
    @property
    def switch(self):
        return CompareOperator[self.__switch_name]
    

class Comparator(object):
    """
    Mother class of comparator objects.
    """
    __metaclass__ = abc.ABCMeta	
    
    def __init__(self, type_description):
        self.__type_description = type_description
        self.__do_convert_input1 = True
        self.__do_convert_input2 = True

    @property
    def do_convert_input1(self):
        return self.__do_convert_input1
    
    @do_convert_input1.setter
    def do_convert_input1(self, value: bool):
        self.__do_convert_input1 = value

    @property
    def do_convert_input2(self):
        return self.__do_convert_input2
    
    @do_convert_input2.setter
    def do_convert_input2(self, value: bool):
        self.__do_convert_input2 = value
    
    def equals(self, obj_1, obj_2, is_obtained_vs_expected = True, raise_exception = True):
        """
        Compare by equality.
        """
        return self.compare(obj_1, CompareOperator.Equal, obj_2, is_obtained_vs_expected, raise_exception, redirect_to_equals=False)

    def compare(self, obj_1, operator: CompareOperator, obj_2, is_obtained_vs_expected = True, raise_exception = True, redirect_to_equals=True):
        """
        Compare by given CompareOperator.
        """
        obj_1, obj_2 = self._convert_inputs(obj_1, obj_2, is_obtained_vs_expected)
        return self._compare_by_operator(obj_1, operator, obj_2, is_obtained_vs_expected, raise_exception, redirect_to_equals=redirect_to_equals)
    
    def _convert_inputs(self, obj_1, obj_2, is_obtained_vs_expected):
        if self.do_convert_input1:
            obj_1 = self._convert_input1(obj_1, self._get_name_1(is_obtained_vs_expected))
        if self.do_convert_input2:
            obj_2 = self._convert_input2(obj_2, self._get_name_2(is_obtained_vs_expected))
        return [obj_1, obj_2]
    
    def _convert_input1(self, obj, name):
        return self._convert_input(obj, name)
    
    def _convert_input2(self, obj, name):
        return self._convert_input(obj, name)
    
    def _convert_input(self, obj, name):
        """
        Method applied to compared objects before comparison.
        To compare similar types that are not comparable directly, override this method to convert objects in comparable types
        """ 
        # By default no conversion is applied
        return obj
    
    def _compare_by_operator(self, obj_1, operator: CompareOperator, obj_2, is_obtained_vs_expected = True, raise_exception = True, redirect_to_equals=True):
        if redirect_to_equals and operator == CompareOperator.Equal:
            return self.equals(obj_1, obj_2, is_obtained_vs_expected, raise_exception)
    
        res = self._compare_result(obj_1, operator, obj_2)
        
        # logger.debug("[{}] obj_1 equals obj_2 => {}\n    obj_1 = [{}]\n    obj_2 = [{}]".format(Typing.get_object_class(self).__name__, res, obj_1, obj_2))
        if not res and raise_exception:
            raise VerifyException(f"Match failure, {self.__type_description} values don't verify expression [{self._get_name_1(is_obtained_vs_expected)} {operator.value} {self._get_name_2(is_obtained_vs_expected)}]:\n  {self._get_name_1(is_obtained_vs_expected)}: {obj_1} (type: {Typing.get_object_class_fullname(obj_1)})\n  {self._get_name_2(is_obtained_vs_expected)}: {obj_2} (type: {Typing.get_object_class_fullname(obj_2)})")
        return res
    
    def _compare_result(self, obj_1, operator: CompareOperator, obj_2):
        if operator == CompareOperator.Different:
            return (obj_1 != obj_2)
        elif operator == CompareOperator.Equal:
            return (obj_1 == obj_2)
        elif operator == CompareOperator.Inferior:
            return (obj_1 < obj_2)
        elif operator == CompareOperator.InferiorOrEqual:
            return (obj_1 <= obj_2)
        elif operator == CompareOperator.Superior:
            return (obj_1 > obj_2)
        elif operator == CompareOperator.SuperiorOrEqual:
            return (obj_1 >= obj_2)
        else:
            raise TechnicalException(f"Unmanaged compare operator {operator}")
        
    def _get_name_1(self, is_obtained_vs_expected):
        if is_obtained_vs_expected == True:
            return "obtained"
        elif is_obtained_vs_expected == False:
            return "expected"
        else:
            return "1"
        
    def _get_name_2(self, is_obtained_vs_expected):
        if is_obtained_vs_expected == True:
            return "expected"
        elif is_obtained_vs_expected == False:
            return "obtained"
        else:
            return "2"

