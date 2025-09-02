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


from holado_test.behave.behave import *  # @UnusedWildImport
from holado_value.common.tables.value_table_manager import ValueTableManager
from holado_test.scenario.step_tools import StepTools
from holado_binary.ipc.bit_series import BitSeries
import copy
from holado_binary.ipc import bit_series
from holado_value.common.tables.comparators.table_2_value_table_with_header_comparator import Table2ValueTable_WithHeaderComparator
import logging
from holado_core.common.tables.comparators.table_with_header_comparator import TableWithHeaderComparator
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado.common.context.session_context import SessionContext
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter

logger = logging.getLogger(__name__)



def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


def __verify_table_is_bit_series_table(table):
    if not ValueTableManager.verify_table_is_x_table(table, "Name", "Bit length", "Type", "Value", raise_exception=False) \
            and not ValueTableManager.verify_table_is_x_table(table, "Name", "Bit length", "Type", raise_exception=False):
        raise FunctionalException("Table header has to be [Name, Bit length, Type, Value] or [Name, Bit length, Type]")


@Step(r"(?P<var_name>{Variable}) = bit series")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    
    __verify_table_is_bit_series_table(table)
    bs = BitSeries(bit_sections_list = ValueTableConverter.convert_table_2_list_of_tuples(table, as_generator=True))
    
    __get_variable_manager().register_variable(var_name, bs)

@Step(r"fill bit series (?P<bs_var_name>{Variable}) from hexadecimal string (?P<hex_str>{Str})(?: \((?P<padding_side>right|left) padded\))?")
def step_impl(context, bs_var_name, hex_str, padding_side):
    bs = StepTools.evaluate_variable_value(bs_var_name)
    hex_str = StepTools.evaluate_scenario_parameter(hex_str)
    right_padded = padding_side == "right"
    
    bs.from_hex(hex_str, right_padded=right_padded)

@Step(r"(?P<var_name>{Variable}) = convert bit series (?P<bs_var_name>{Variable}) to hexadecimal string(?: \((?P<padding_side>right|left) padded\))?")
def step_impl(context, var_name, bs_var_name, padding_side):
    var_name = StepTools.evaluate_variable_name(var_name)
    bs = StepTools.evaluate_variable_value(bs_var_name)
    right_padding = padding_side == "right"
    
    res = bs.to_hex(right_padding=right_padding)
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = convert bit series (?P<bs_var_name>{Variable}) to name/value table")
def step_impl(context, var_name, bs_var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    bs = StepTools.evaluate_variable_value(bs_var_name)
    
    res = bit_series.convert_bit_series_to_name_value_table(bs)
    
    __get_variable_manager().register_variable(var_name, res)

@Then(r"hexadecimal string (?P<hex_str>{Str}) is bit series")
def step_impl(context, hex_str):
    hex_str = StepTools.evaluate_scenario_parameter(hex_str)
    expected_table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    
    __verify_table_is_bit_series_table(expected_table)
    
    # Build a table representing the bit series in hexadecimal string
    declare_table = copy.copy(expected_table)
    declare_table.remove_column(name="Value")
    bs = BitSeries(bit_sections_list=ValueTableConverter.convert_table_2_list_of_tuples(declare_table, as_generator=True))
    bs.from_hex(hex_str)
    obtained_table = bit_series.convert_bit_series_to_table(bs)
    
    comparator = Table2ValueTable_WithHeaderComparator()
    comparator.equals(obtained_table, expected_table)

@Then(r"hexadecimal string (?P<hex_str>{Str}) is bit series (?P<var_bit_series>{Variable})")
def step_impl(context, hex_str, var_bit_series):
    hex_str = StepTools.evaluate_scenario_parameter(hex_str)
    expected_bs = StepTools.evaluate_variable_value(var_bit_series)
    
    # Build a table representing the bit series in hexadecimal string
    bs = copy.copy(expected_bs)
    bs.from_hex(hex_str)
    obtained_table = bit_series.convert_bit_series_to_table(bs)
    
    expected_table = bit_series.convert_bit_series_to_table(expected_bs)

    comparator = TableWithHeaderComparator()
    comparator.equals(obtained_table, expected_table)

@Then(r"bit series (?P<var_bit_series>{Variable}) is")
def step_impl(context, var_bit_series):
    bs = StepTools.evaluate_variable_value(var_bit_series)
    expected_table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    
    __verify_table_is_bit_series_table(expected_table)
    
    obtained_table = bit_series.convert_bit_series_to_table(bs)
    
    comparator = Table2ValueTable_WithHeaderComparator()
    comparator.equals(obtained_table, expected_table)



