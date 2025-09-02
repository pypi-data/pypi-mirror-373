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
from holado_json.ipc.json import create_name_value_table_from_json,\
    create_table_with_header_from_json
import logging
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_core.common.tools.tools import Tools
from holado_json.ipc.json_converter import JsonConverter
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


@Step(r"(?P<var_name>{Variable}) = convert json (?P<json_value>{Str}) to name/value table")
def step_impl(context, var_name, json_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    json_value = StepTools.evaluate_scenario_parameter(json_value)
        
    res = create_name_value_table_from_json(json_value, recursive=False, uncollapse_list=False)

    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Convertion result:\n{res.represent(4)}\nsource: {json_value}")
    __get_variable_manager().register_variable(var_name, res)


@Step(r"(?P<var_name>{Variable}) = convert json (?P<json_value>{Str}) to name/value table with names uncollapsed")
def step_impl(context, var_name, json_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    json_value = StepTools.evaluate_scenario_parameter(json_value)
        
    res = create_name_value_table_from_json(json_value, recursive=True, uncollapse_list=False)

    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Convertion result:\n{res.represent(4)}\nsource: {json_value}")
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = convert json (?P<json_value>{Str}) to name/value table with names and list uncollapsed")
def step_impl(context, var_name, json_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    json_value = StepTools.evaluate_scenario_parameter(json_value)
        
    res = create_name_value_table_from_json(json_value, recursive=True, uncollapse_list=True)

    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Convertion result:\n{res.represent(4)}\nsource: {json_value}")
    __get_variable_manager().register_variable(var_name, res)


@Step(r"(?P<var_name>{Variable}) = convert json (?P<json_object>{Str}) to table with names as columns recursively")
def step_impl(context, var_name, json_object):
    var_name = StepTools.evaluate_variable_name(var_name)
    json_object = StepTools.evaluate_scenario_parameter(json_object)
    
    res = create_table_with_header_from_json(json_object, recursive=True, uncollapse_list=False)

    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Convertion result:\n{res.represent(4)}\nsource: {json_object}")
    __get_variable_manager().register_variable(var_name, res)


@Step(r"(?P<var_name>{Variable}) = convert json (?P<json_object>{Str}) to table with names as columns")
def step_impl(context, var_name, json_object):
    var_name = StepTools.evaluate_variable_name(var_name)
    json_object = StepTools.evaluate_scenario_parameter(json_object)
    
    res = create_table_with_header_from_json(json_object, recursive=False, uncollapse_list=False)
    
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Convertion result:\n{res.represent(4)}\nsource: {json_object}")
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = convert text (?P<json_text>{Str}) to json")
def step_impl(context, var_name, json_text):
    var_name = StepTools.evaluate_variable_name(var_name)
    json_text = StepTools.evaluate_scenario_parameter(json_text)
    
    if isinstance(json_text, bytes):
        json_text = json_text.decode('utf-8')
    
    converter = JsonConverter()
    json_object = converter.to_json(json_text)
    
    __get_variable_manager().register_variable(var_name, json_object)
    
@Step(r"(?P<var_name>{Variable}) = json object")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    json_text = BehaveStepTools.get_step_multiline_text(context)
    
    converter = JsonConverter()
    json_object = converter.to_json(json_text)
    
    __get_variable_manager().register_variable(var_name, json_object)
    
@Step(r"(?P<var_name>{Variable}) = convert name/value table (?P<table_varname>{Variable}) to json")
def step_impl(context, var_name, table_varname):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
        
    res = ValueTableConverter.convert_name_value_table_2_json_object(table)

    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Convertion result:\n{res}\nsource: {table.represent(4)}")
    __get_variable_manager().register_variable(var_name, res)

