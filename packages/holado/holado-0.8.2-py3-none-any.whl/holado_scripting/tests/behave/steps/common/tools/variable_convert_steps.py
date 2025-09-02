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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
import base64
import codecs
import logging
from holado_core.common.tables.table import Table
from holado_value.common.tables.value_table_with_header import ValueTableWithHeader
from holado_value.common.tables.value_table import ValueTable
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing
from holado_value.common.tables.value_table_manager import ValueTableManager

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_unique_value_manager():
    return SessionContext.instance().unique_value_manager

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()





@Given(r"(?P<var_name>{Variable}) = convert list (?P<list_var_name>{Variable}) to list of object attribute (?P<attribute_name>{Str})")
def step_impl(context, var_name, list_var_name, attribute_name):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    attr_name = StepTools.evaluate_scenario_parameter(attribute_name)
    list_obj = StepTools.evaluate_variable_value(list_var_name)
    
    res = []
    for index, obj in enumerate(list_obj):
        if hasattr(obj, attr_name):
            attr_val = getattr(obj, attr_name)
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Result list - add attribute value [{attr_val}] (type: {Typing.get_object_class_fullname(attr_val)} ; dir: {dir(attr_val)})")
            res.append(attr_val)
        else:
            raise FunctionalException(f"In list, object of index {index} hasn't attribute '{attr_name}'")
    
    __get_variable_manager().register_variable(var_name, res)
    
@Step(r"(?P<var_name>{Variable}) = convert object value (?P<object_value>{Str}) to string")
def step_impl(context, var_name, object_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    object_value = StepTools.evaluate_variable_value(object_value)
    if isinstance(object_value, bytes):
        res = object_value.decode('utf-8')
    else:
        res = str(object_value)
    __get_variable_manager().register_variable(var_name, res)
    
@Step(r"(?P<var_name>{Variable}) = convert object value (?P<object_value>{Str}) to integer")
def step_impl(context, var_name, object_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    object_value = StepTools.evaluate_variable_value(object_value)
    __get_variable_manager().register_variable(var_name, int(object_value))
    
@Step(r"(?P<var_name>{Variable}) = convert object value (?P<object_value>{Str}) to list")
def step_impl(context, var_name, object_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    object_value = StepTools.evaluate_variable_value(object_value)
    
    if isinstance(object_value, Table):
        table = object_value
        if table.nb_columns > 1 and table.nb_rows > 1:
            raise FunctionalException(f"Table must have only one column or only one row (table has {table.nb_columns} and {table.nb_rows})")
        
        if table.nb_columns > 1 and table.nb_rows == 1:
            row = table.get_row(0)
        elif table.nb_rows > 1 and table.nb_columns == 1:
            row = table.get_column(0)
        else:
            row = None
            
        if row is not None:
            if ValueTableManager.is_value_table(table):
                res = [c.value for c in row]
            else:
                res = [c.content for c in row]
        else:
            res = []
    else:
        res = list(object_value)
    
    __get_variable_manager().register_variable(var_name, res)
    
@Step(r"(?P<var_name>{Variable}) = convert object value (?P<object_value>{Str}) to dict")
def step_impl(context, var_name, object_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    object_value = StepTools.evaluate_variable_value(object_value)
    __get_variable_manager().register_variable(var_name, dict(object_value))

@Step(r"(?P<var_name>{Variable}) = convert object value (?P<object_value>{Str}) to base 64")
def step_impl(context, var_name, object_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    object_value = StepTools.evaluate_variable_value(object_value)
    if isinstance(object_value, bytes):
        value_bytes = object_value
    elif isinstance(object_value, str):
        value_bytes = object_value.encode('utf-8')
    else:
        raise TechnicalException(f"Unexpected object value type {Typing.get_object_class_fullname(object_value)} (allowed types: string, bytes)")
    res = base64.b64encode(value_bytes)
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = convert hex string (?P<object_value>{Str}) to bytes")
def step_impl(context, var_name, object_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    object_value = StepTools.evaluate_scenario_parameter(object_value)
    if isinstance(object_value, str):
        res = codecs.decode(object_value, 'hex_codec')
    else:
        raise TechnicalException(f"Unexpected value type {Typing.get_object_class_fullname(object_value)}")
    __get_variable_manager().register_variable(var_name, res)
    
@Step(r"(?P<var_name>{Variable}) = convert hex string (?P<object_value>{Str}) to base 64")
def step_impl(context, var_name, object_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    execute_steps(u"""
        {keyword} __{var_name}_BYTES__ = convert hex string {object_value} to bytes
        {keyword} {var_name} = convert object value __{var_name}_BYTES__ to base 64
        """.format(keyword=context.step.keyword, var_name=var_name, object_value=object_value))
    

@Step(r"(?P<var_name>{Variable}) = convert base 64 (?P<value>{Str}) to bytes")
def step_impl(context, var_name, value):
    var_name = StepTools.evaluate_variable_name(var_name)
    value = StepTools.evaluate_scenario_parameter(value)
    if not isinstance(value, str):
        raise TechnicalException(f"Unexpected value type {Typing.get_object_class_fullname(value)} (allowed types: string)")
    res = base64.b64decode(value)
    __get_variable_manager().register_variable(var_name, res)
    
