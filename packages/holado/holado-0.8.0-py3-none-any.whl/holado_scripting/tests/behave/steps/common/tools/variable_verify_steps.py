# -*- coding: utf-8 -*-

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


from holado_test.scenario.step_tools import StepTools
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_core.common.tables.table_manager import TableManager
from holado_value.common.tables.comparators.table_2_value_table_comparator import Table2ValueTable_Comparator
from holado_core.common.tools.comparators.comparator import CompareOperator
from holado_core.common.tables.table import Table
from holado_core.common.tools.comparators.object_comparator import ObjectComparator
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_value.common.tables.value_table_with_header import ValueTableWithHeader
from holado_value.common.tables.comparators.table_2_value_table_with_header_comparator import Table2ValueTable_WithHeaderComparator
from holado_core.common.tables.comparators.table_with_header_comparator import TableWithHeaderComparator
from holado_value.common.tables.value_table import ValueTable
from holado_core.common.tables.comparators.table_comparator import TableComparator
import logging
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_python.common.tools.comparators.string_comparator import StringComparator
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_unique_value_manager():
    return SessionContext.instance().unique_value_manager

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()




# @Then(r'\'{object_string}\' is {type_name:S}')
# def step_impl(context, object_string, type_name):
#     obj = __get_text_interpreter().interpret(object_string)
# 
#     # Get class type
#     class_ = Typing.get_class_for_type_name(type_name)
#     
#     if isinstance(obj, class_):
#         if isinstance(obj, basestring):
#             # Verify scenario table structure
#             if len(context.table.headings) != 1 or len(context.table.rows) != 1:
#                 raise FunctionalException("For a string, scenario table must be a one column table with header and only one row")
#             
#             # Verify strings
#             cell = ValueTableCell(context.table.rows[0].cells[0])
#             expected = cell.value
#             if obj != expected:
#                 raise FunctionalException("String value is wrong (expected: '{}' ; obtained: '{}')".format(expected, obj))
#         else:
#             raise NotImplementedError(u"Check content of type '{}'".format(Typing.get_object_class_fullname(obj)))
#     else:
#         raise FunctionalException("Object is of type '{}' (expected type: '{}')".format(Typing.get_object_class_fullname(obj), type_name))



@Then(r"(?P<value_1>{Any}) (?P<operator>==|!=|<|<=|>|>=) (?P<value_2>(?:(?! \(as ).)+)")
def step_impl(context, value_1, operator, value_2):  # @DuplicatedSignature
    val1 = StepTools.evaluate_scenario_parameter(value_1)
    val2 = StepTools.evaluate_scenario_parameter(value_2)
    operator = CompareOperator(operator)
    
    if isinstance(val1, Table) and isinstance(val2, Table):
        if isinstance(val1, TableWithHeader) and isinstance(val2, TableWithHeader):
            if isinstance(val2, ValueTableWithHeader):
                comparator = Table2ValueTable_WithHeaderComparator()
            else:
                comparator = TableWithHeaderComparator()
        else:
            if isinstance(val2, ValueTable):
                comparator = Table2ValueTable_Comparator()
            else:
                comparator = TableComparator()
    elif isinstance(val1, str) and isinstance(val2, str):
        comparator = StringComparator()
    else:
        comparator = ObjectComparator()
        
    comparator.compare(val1, operator, val2)



@Then(r"(?P<value>{Str}) is list")
def step_impl(context, value):  # @DuplicatedSignature
    val = StepTools.evaluate_scenario_parameter(value)
    if not isinstance(val, list):
        raise VerifyException(f"Value [{val}] (from expression [{value}]) is not a list (type: {Typing.get_object_class_fullname(val)})")
    
    if hasattr(context, "table") and context.table is not None:
        table = BehaveStepTools.convert_step_table_2_value_table(context.table)
        obtained = TableManager.convert_list_2_column_table(val)
        comparator = Table2ValueTable_Comparator()
        comparator.equals(obtained, table)

@Then(r"(?P<value>{Str}) is empty list")
def step_impl(context, value):  # @DuplicatedSignature
    val = StepTools.evaluate_scenario_parameter(value)
    if not isinstance(val, list):
        raise VerifyException(f"Value [{val}] (from expression [{value}]) is not a list (type: {Typing.get_object_class_fullname(val)})")
    
    if len(val) > 0:
        raise VerifyException(f"List is not empty, it contains {len(val)} elements: [{val}] (from expression [{value}])")


# @Then(r"dictionary (?P<value>{Str}) is")
# def step_impl(context, value):  # @DuplicatedSignature
#     val = StepTools.evaluate_scenario_parameter(value)
#     if not isinstance(val, dict):
#         raise VerifyException(f"Value [{val}] (from expression [{value}]) is not a dictionary (type: {Typing.get_object_class_fullname(val)})")
#
#     if hasattr(context, "table") and context.table is not None:
#         table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
#         ValueTableManager.verify_table_is_x_table(table, "Key", "Value")
#         table.sort(names=['Key'])
#
#         obtained = TableManager.convert_dict_2_name_value_table(val)
#         obtained.sort(names=['Name'])
#
#         comparator = Table2ValueTable_Comparator()
#         comparator.equals(obtained, table)

@Then(r"(?P<value>{Str}) is text")
def step_impl(context, value):  # @DuplicatedSignature
    obtained = StepTools.evaluate_scenario_parameter(value)
    if not isinstance(obtained, str):
        raise VerifyException(f"Value [{obtained}] (from expression [{value}]) is not a text (type: {Typing.get_object_class_fullname(obtained)})")
    
    # Note: in current implementation of BehaveStepTools.get_step_multiline_text, multiline text is stripped,
    #       thus value must be also stripped
    obtained = obtained.strip()
    
    text = BehaveStepTools.get_step_multiline_text(context)
    if text is not None:
        comparator = StringComparator()
        comparator.equals(obtained, text)



