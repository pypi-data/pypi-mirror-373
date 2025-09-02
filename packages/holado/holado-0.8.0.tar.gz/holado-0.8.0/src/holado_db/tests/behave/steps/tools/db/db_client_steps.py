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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_scripting.text.interpreter.text_interpreter import TextInterpreter
from holado_scripting.common.tools.variable_manager import VariableManager
from holado_test.common.context.scenario_context import ScenarioContext
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter

logger = logging.getLogger(__name__)


def __get_session_context() -> SessionContext:
    return SessionContext.instance()

def __get_scenario_context() -> ScenarioContext:
    return __get_session_context().get_scenario_context()

def __get_text_interpreter() -> TextInterpreter:
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager() -> VariableManager:
    return __get_scenario_context().get_variable_manager()



@Step(r"execute \[(?P<command>{Any})\] \(DB client: (?P<var_client>{Variable})\)")
def step_impl(context, command, var_client):
    """
    Execute a SQL request that doesn't return a result.
    An exception is raised if the method returns a result.
    """
    command = StepTools.evaluate_scenario_parameter(command)
    client = StepTools.evaluate_variable_value(var_client)
    
    result = client.execute(command)
    if result:
        raise TechnicalException(f"Unexpected result to command [{command}]: {result}")
    
@Step(r"(?P<var_name>{Variable}) = result of \[(?P<command>{Any})\] \(DB client: (?P<var_client>{Variable})\)")
def step_impl(context, var_name, command, var_client):
    """
    Execute a SQL request.
    The result is stored in given variable as a TableWithHeader.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    command = StepTools.evaluate_scenario_parameter(command)
    client = StepTools.evaluate_variable_value(var_client)
    
    result = client.execute(command)
    
    __get_variable_manager().register_variable(var_name, result)

@Step(r"execute \[(?P<command>{Any})\] with parameters (?P<parameters>{Any}) \(DB client: (?P<var_client>{Variable})\)")
def step_impl(context, command, parameters, var_client):
    """
    Execute a SQL request with given parameters that doesn't return a result.
    An exception is raised if the method returns a result.
    """
    command = StepTools.evaluate_scenario_parameter(command)
    parameters = StepTools.evaluate_scenario_parameter(parameters)
    client = StepTools.evaluate_variable_value(var_client)
    
    result = client.execute(command, *parameters)
    if result:
        raise TechnicalException(f"Unexpected result to command [{command}]: {result}")
    
@Step(r"(?P<var_name>{Variable}) = result of \[(?P<command>{Any})\] with parameters (?P<parameters>{Any}) \(DB client: (?P<var_client>{Variable})\)")
def step_impl(context, var_name, command, parameters, var_client):
    """
    Execute a SQL request with given parameters.
    The result is stored in given variable as a TableWithHeader.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    command = StepTools.evaluate_scenario_parameter(command)
    parameters = StepTools.evaluate_scenario_parameter(parameters)
    client = StepTools.evaluate_variable_value(var_client)
    
    result = client.execute(command, *parameters)
    
    __get_variable_manager().register_variable(var_name, result)
    

@Step(r"execute \[(?P<command>{Any})\] with parameters \(DB client: (?P<var_client>{Variable})\)")
def step_impl(context, command, var_client):
    """
    Execute a SQL request with given parameters that doesn't return a result.
    An exception is raised if the method returns a result.
    """
    command = StepTools.evaluate_scenario_parameter(command)
    client = StepTools.evaluate_variable_value(var_client)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    parameters_kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
    
    result = client.execute(command, **parameters_kwargs)
    if result:
        raise TechnicalException(f"Unexpected result to command [{command}]: {result}")
    
@Step(r"(?P<var_name>{Variable}) = result of \[(?P<command>{Any})\] with parameters \(DB client: (?P<var_client>{Variable})\)")
def step_impl(context, var_name, command, var_client):
    """
    Execute a SQL request with given parameters.
    The result is stored in given variable as a TableWithHeader.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    command = StepTools.evaluate_scenario_parameter(command)
    client = StepTools.evaluate_variable_value(var_client)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    parameters_kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
    
    result = client.execute(command, **parameters_kwargs)
    
    __get_variable_manager().register_variable(var_name, result)
    
    
    
    
