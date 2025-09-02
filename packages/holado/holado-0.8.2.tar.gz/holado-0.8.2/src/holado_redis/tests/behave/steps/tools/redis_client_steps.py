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
from holado_redis.tools.redis.redis_client import RedisClient
from holado_redis.tools.redis.redis_manager import RedisManager
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


if RedisClient.is_available():

    @Given(r"(?P<var_name>{Variable}) = new Redis client")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        
        manager = RedisManager()
        client = manager.new_client(**kwargs)
        
        __get_variable_manager().register_variable(var_name, client)
        
    @Step(r"execute \[(?P<command>{Any})\] \(Redis client: (?P<var_client>{Variable})\)")
    def step_impl(context, command, var_client):
        """
        Execute any method in class Redis (cf https://redis.readthedocs.io/en/stable/commands.html).
        An exception is raised if the method returns a result.
        """
        # command = StepTools.evaluate_scenario_parameter(command)
        command = StepTools.evaluate_string_parameter(command)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable
        
        result = eval("client.internal_client." + command)
        if result:
            raise TechnicalException(f"Unexpected result to command [{command}]: {result}")
        
    @Step(r"(?P<var_name>{Variable}) = result of \[(?P<command>{Any})\] \(Redis client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, command, var_client):
        """
        Execute any method in class Redis (cf https://redis.readthedocs.io/en/stable/commands.html).
        The result is stored in given variable.
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        # command = StepTools.evaluate_scenario_parameter(command)
        command = StepTools.evaluate_string_parameter(command)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable
        
        result = eval("client.internal_client." + command)
        
        __get_variable_manager().register_variable(var_name, result)
        
    @Step(r"delete keys matching (?P<match_>{RawStr})' \(Redis client: (?P<var_client>{Variable})\)")
    def step_impl(context, match_, var_client):
        """
        Delete keys matching given glob-style pattern.
        An exception is raised if a delete fails. 
        """
        match_ = StepTools.evaluate_scenario_parameter(match_)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable
        
        client.delete_keys_matching(match_)


    
    
