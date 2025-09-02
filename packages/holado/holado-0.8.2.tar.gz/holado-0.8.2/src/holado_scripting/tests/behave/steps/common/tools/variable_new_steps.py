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


from holado_value.common.tables.value_table_manager import ValueTableManager
from holado_test.scenario.step_tools import StepTools
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
import logging
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
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




@Given(r"(?P<var_name>{Variable}) = new (?P<type_name>{Str}) with attributes")
def step_impl(context, var_name, type_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    type_name = StepTools.evaluate_string_parameter(type_name)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    
    # Get class type
    class_ = Typing.get_class_for_type_name(type_name)
    
    # Create object
    obj = class_()
    ValueTableManager.set_object_attributes_according_name_value_table(obj, table)
    
    # Store in variable
    __get_variable_manager().register_variable(var_name, obj)

@Given(r"(?P<var_name>{Variable}) = new (?P<type_name>{Str}) with constructor parameters")
def step_impl(context, var_name, type_name):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    type_name = StepTools.evaluate_string_parameter(type_name)
    
    # Get class type
    class_ = Typing.get_class_for_type_name(type_name)
    
    # Create object
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    unnamed_parameters, named_parameters = ValueTableConverter.convert_name_value_table_2_list_and_dict(table)
    logger.info("creating new '{}' with parameters {} and {}".format(class_, unnamed_parameters, named_parameters))
    obj = class_(*unnamed_parameters, **named_parameters)
    
    # Store in variable
    __get_variable_manager().register_variable(var_name, obj)
    
@Given(r"(?P<var_name>{Variable}) = list")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.convert_step_table_2_value_table(context.table)
    if table.nb_columns > 1 and table.nb_rows > 1:
        raise FunctionalException("Table must be a single column or a single row")
    
    if table.nb_rows > 1:
        res = list(table.get_column(0).cells_value)
    else:
        res = list(table.get_row(0).cells_value)
    
    # Store in variable
    __get_variable_manager().register_variable(var_name, res)
    
@Given(r"(?P<var_name>{Variable}) = multiline text")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    res = BehaveStepTools.get_step_multiline_text(context)
    __get_variable_manager().register_variable(var_name, res)
    
@Given(r"(?P<var_name>{Variable}) = new unique integer")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    res = __get_unique_value_manager().new_integer()
    __get_variable_manager().register_variable(var_name, res)
    
@Given(r"(?P<var_name>{Variable}) = new unique HEX integer")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    res = __get_unique_value_manager().new_hex()
    __get_variable_manager().register_variable(var_name, res)
    
@Given(r"(?P<var_name>{Variable}) = new unique HEX integer \(length: (?P<length>{Int})\)")
def step_impl(context, var_name, length):
    var_name = StepTools.evaluate_variable_name(var_name)
    length = StepTools.evaluate_scenario_parameter(length)
    res = __get_unique_value_manager().new_hex(length=length)
    __get_variable_manager().register_variable(var_name, res)
    
@Given(r"(?P<var_name>{Variable}) = new unique string")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    res = __get_unique_value_manager().new_string()
    __get_variable_manager().register_variable(var_name, res)
    
@Given(r"(?P<var_name>{Variable}) = new unique string \(padding length: (?P<pad_len>{Int})\)")
def step_impl(context, var_name, pad_len):
    var_name = StepTools.evaluate_variable_name(var_name)
    pad_len = StepTools.evaluate_scenario_parameter(pad_len)
    res = __get_unique_value_manager().new_string(padding_length=pad_len)
    __get_variable_manager().register_variable(var_name, res)


