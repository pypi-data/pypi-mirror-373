
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



from builtins import super
from holado_core.common.tables.comparators.table_cell_comparator import TableCellComparator
from holado_value.common.tools.value_types import ValueTypes
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.verify_exception import VerifyException
from holado.common.context.session_context import SessionContext
from holado_core.common.tools.comparators.comparator import CompareOperator
from holado_core.common.exceptions.functional_exception import FunctionalException
import logging
from holado_core.common.tools.comparators.object_comparator import ObjectComparator
from holado_value.common.tables.value_table_cell import ValueTableCell
from holado_scripting.text.verifier.text_verifier import TextVerifier
from holado_core.common.tools.tools import Tools
from holado_python.common.tools.comparators.type_comparator import TypeComparator
from holado_python.common.tools.comparators.string_comparator import StringComparator
from holado_python.standard_library.typing import Typing
from holado_python.common.tools.comparators.float_comparator import FloatComparator
from holado.common.handlers.undefined import undefined_value

logger = logging.getLogger(__name__)


class Table2ValueTable_CellComparator(TableCellComparator):
    def __init__(self, **kwargs):
        super().__init__()
        
        self.__kwargs = kwargs
        self.__float_comparator = None
    
    def __get_float_comparator(self):
        if self.__float_comparator is None:
            float_kwargs = {}
            if 'float_diff_precision' in self.__kwargs:
                float_kwargs['diff_precision'] = self.__kwargs['float_diff_precision']
            if 'float_relative_precision' in self.__kwargs:
                float_kwargs['relative_precision'] = self.__kwargs['float_relative_precision']
            self.__float_comparator = FloatComparator(**float_kwargs)
        return self.__float_comparator
    
    def __get_scenario_context(self):
        return SessionContext.instance().get_scenario_context()
            
    def __get_text_verifier(self) -> TextVerifier:
        return self.__get_scenario_context().get_text_verifier()
    
    def __get_variable_manager(self):
        return self.__get_scenario_context().get_variable_manager()
    
    @property
    def __type_comparator(self):
        if not hasattr(self, "__type_comparator_inst"):
            self.__type_comparator_inst = TypeComparator()
        return self.__type_comparator_inst

    @property
    def __string_comparator(self):
        if not hasattr(self, "__string_comparator_inst"):
            self.__string_comparator_inst = StringComparator()
            self.__string_comparator_inst.do_convert_input1 = False
        return self.__string_comparator_inst
        
    def compare(self, obj_1, operator: CompareOperator, obj_2, is_obtained_vs_expected = True, raise_exception = True, redirect_to_equals=True):
        if operator == CompareOperator.Equal:
            return self.__equals(obj_1, obj_2, is_obtained_vs_expected, raise_exception)
        else:
            #TODO: Adapt compare method to cell value types as in __equals
            super().compare(obj_1, operator, obj_2, is_obtained_vs_expected, raise_exception, redirect_to_equals=redirect_to_equals)
    
    def __get_values_to_compare(self, cell_1, cell_2):
        compare_result = undefined_value
        
        if isinstance(cell_1, ValueTableCell):
            if cell_1.value_type == ValueTypes.NotApplicable:
                compare_result = True
            cell_1_value = cell_1.get_value()
        else:
            cell_1_value = cell_1.content
        
        if cell_2.value_type == ValueTypes.NotApplicable:
            compare_result = True
        cell_2_value = cell_2.get_value()
        
        return cell_1_value, cell_2_value, compare_result
        
    def __equals(self, cell_1, cell_2, is_obtained_vs_expected = True, raise_exception = True):
        res = False
        
        # Extract cell values to compare
        cell_1_value, cell_2_value, compare_result = self.__get_values_to_compare(cell_1, cell_2)
        if compare_result is not undefined_value:
            return compare_result
        
        cause = None
        try:
            # value_type = cell_2.value_type
            value_type = cell_2.content_type
            if value_type == ValueTypes.NotApplicable:
                res = True
            elif value_type == ValueTypes.Null:
                res = (cell_1_value is None)
            elif value_type in [ValueTypes.Boolean, ValueTypes.Integer]:
                res = (cell_1_value == cell_2_value)
            elif value_type == ValueTypes.Float:
                res = self.__get_float_comparator().equals(cell_1_value, cell_2_value, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception)
            elif value_type == ValueTypes.Generic:
                comparator = ObjectComparator()
                res = comparator.equals(cell_1_value, cell_2_value, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception)
            elif value_type == ValueTypes.Merged:
                return super().equals(cell_1, cell_2, is_obtained_vs_expected, raise_exception)
            elif ValueTypes.is_string(value_type):
                res = self._equals_string(cell_1, cell_2, is_obtained_vs_expected, raise_exception)
            elif value_type == ValueTypes.Symbol:
                res = self._equals_symbol(cell_1, cell_2, is_obtained_vs_expected, raise_exception)
            else:
                raise TechnicalException("Unmanaged value of type '{}'".format(value_type.name))
        except FunctionalException as exc:
            if not raise_exception:
                # Unexpected exception
                raise TechnicalException("Unexpected exception while raise_exception=False") from exc
            res = False
            cause = exc
        
        if not res and raise_exception:
            msg_list = [f"Cells are not equal",
                        f"    cell {self._get_name_1(is_obtained_vs_expected)}: {cell_1.represent()} (type: {Typing.get_object_class_fullname(cell_1_value)})"]
            msg_line = f"    cell {self._get_name_2(is_obtained_vs_expected)}: {cell_2.represent()} (scenario type: {value_type.name}"
            if cell_2_value != cell_2.content:
                msg_line += f" ; value: {cell_2_value} ; value type: {Typing.get_object_class_fullname(cell_2_value)}"
            msg_line += ")"
            msg_list.append(msg_line)
            msg = "\n".join(msg_list)
            if cause is not None:
                raise VerifyException(msg) from cause
            else:
                raise VerifyException(msg)
        return res
    
    def _equals_string(self, cell_1, cell_2, is_obtained_vs_expected = True, raise_exception = True):
        """
        Method used to compare cell_1 to string cell_2.
        First cell_1 content is verified to be a string, then cells contents are compared
        """
        
        content_1, content_2 = self._convert_inputs(cell_1, cell_2, is_obtained_vs_expected)
        
        # Verify cell_1 content type
        if not self.__type_comparator.equals(content_1, str, raise_exception=False):
            if raise_exception:
                raise VerifyException(f"{self._get_name_1(is_obtained_vs_expected).capitalize()} value is not a string: [{content_1}] (type: {Typing.get_object_class_fullname(content_1)})")
            else:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Compare result is false since {self._get_name_1(is_obtained_vs_expected)} value is not a string: [{content_1}] (type: {Typing.get_object_class_fullname(content_1)})")
                return False
        
        # Verify cells content, without converting cell_1 content as string (cf property __string_comparator)
        return self.__string_comparator.equals(content_1, content_2, is_obtained_vs_expected, raise_exception)
        
    def _equals_symbol(self, cell_1, cell_symbol, is_obtained_vs_expected = True, raise_exception = True):
        res = True
        
        if isinstance(cell_1, ValueTableCell):
            cell_1_value = cell_1.value
        else:
            cell_1_value = cell_1.content
        
        symbol_value = cell_symbol.value
        if symbol_value is None:
            if cell_1_value is not None:
                if raise_exception:
                    raise VerifyException("Cell value is not None (cell: [{}])".format(cell_1))
                else:
                    res = False
        elif isinstance(symbol_value, str) and self.__get_text_verifier().is_to_interpret(symbol_value):
            # Case where symbol contains a verify function
            res = self.__get_text_verifier().verify(cell_1_value, symbol_value, raise_exception=raise_exception)
        else:
            comparator = ObjectComparator()
            res = comparator.equals(cell_1_value, symbol_value, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception)
        
        return res
    
