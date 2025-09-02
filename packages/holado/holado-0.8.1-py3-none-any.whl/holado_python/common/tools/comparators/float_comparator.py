
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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.converters.converter import Converter
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class FloatComparator(Comparator):
    
    def __init__(self, diff_precision=None, relative_precision=1e-15):
        """
        Define the comparing method and its associated precision.
        If difference precision is defined, difference comparison is applied, else relative comparison is applied.
        By default, a relative comparison is used with a precision of 1e-15
        
        Notes: 
        1. Usually, python implement float type with 52 digits for significant digits, which is a precision of 2**-52=2.220446049250313e-16. 
           The default relative precision is 1e-15, a little bit over this limit precision, in order to manage small computational errors.
           In many cases, this precision is too small ; if you don't know which precision to use, a relative precision of 1e-9 is quite usual.
        2. For the same reason, the appropriate difference precision is dependent on the values compared and the number of comparable significant digits.
           If you are not sure, prefer the relative comparison. 
        :param diff_precision: If defined, a difference comparison is done with this precision
        :param relative_precision: If defined, a relative comparison is done with this precision
        """
        super().__init__("float")
        
        self.__diff_precision = diff_precision
        self.__relative_precision = relative_precision

        if self.__diff_precision is not None:
            self.__relative_precision = None        
        if self.__diff_precision is None and self.__relative_precision is None:
            raise TechnicalException("A precision must be defined") 
    
    def _convert_input(self, obj, name):
        if Converter.is_float(obj):
            res = float(obj)
        else:
            res = obj
            
        if not isinstance(res, float):
            raise FunctionalException(f"{name.capitalize()} value is not a float: [{res}] (type: {Typing.get_object_class_fullname(res)})")
        return res
    
    def _compare_result(self, obj_1, operator: CompareOperator, obj_2):
        if operator == CompareOperator.Different:
            return not self.__almost_equals(obj_1, obj_2)
        elif operator == CompareOperator.Equal:
            return self.__almost_equals(obj_1, obj_2)
        elif operator == CompareOperator.Inferior:
            return (obj_1 < obj_2)
        elif operator == CompareOperator.InferiorOrEqual:
            return (obj_1 < obj_2) or self.__almost_equals(obj_1, obj_2)
        elif operator == CompareOperator.Superior:
            return (obj_1 > obj_2)
        elif operator == CompareOperator.SuperiorOrEqual:
            return (obj_1 > obj_2) or self.__almost_equals(obj_1, obj_2)
        else:
            raise TechnicalException(f"Unmanaged compare operator {operator}")
    
    def __almost_equals(self, val_1, val_2):
        if self.__relative_precision is not None:
            return self.__almost_equals_relative(val_1, val_2)
        else:
            return self.__almost_equals_diff(val_1, val_2)
    
    def __almost_equals_diff(self, val_1, val_2):
        diff = abs(val_1 - val_2)
        return (diff < self.__diff_precision)
    
    def __almost_equals_relative(self, val_1, val_2):
        diff = abs(val_1 - val_2)
        vmax = max(abs(val_1), abs(val_2))
        if vmax > 0:
            return (diff < vmax * self.__relative_precision)
        else:
            return True
    
    
    
