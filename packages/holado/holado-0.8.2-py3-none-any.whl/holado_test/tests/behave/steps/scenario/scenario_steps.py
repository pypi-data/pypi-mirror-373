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


import logging
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_core.common.block.function import Function
from holado_test.common.context.scenario_context import ScenarioContext
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_scripting.common.tools.evaluate_parameters import EvaluateParameters
from holado_test.scenario.step_tools import StepTools
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


def __get_scenario_context() -> ScenarioContext:
    return SessionContext.instance().get_scenario_context()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()



@Given(r"at end of scenario, call steps(?: \(format with: (?P<format_with>{Variable}(?:, {Variable})*)\))?")
def step_impl(context, format_with):
    format_with = StepTools.evaluate_variable_name(format_with)
    steps = BehaveStepTools.get_step_multiline_text(context, eval_params=EvaluateParameters.nothing())
    
    if format_with is not None:
        steps = StepTools.format_steps_with(steps, format_with.split(', '))
    
    func = Function(execute_steps, steps)
    __get_scenario_context().add_post_process(func)


@Given(r"(?P<var_name>{Variable}) = last step duration")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    
    step_context = __get_scenario_context().get_step(-2)
    res = step_context.duration
    if res is None:
        raise TechnicalException(f"Failed to get last step duration: {step_context}")
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = last step start datetime")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    
    step_context = __get_scenario_context().get_step(-2)
    res = step_context.start_datetime
    if res is None:
        raise TechnicalException(f"Failed to get last step start datetime: {step_context}")
    
    __get_variable_manager().register_variable(var_name, res)
    
    __get_variable_manager().register_variable(var_name, step_context.start_datetime)

@Given(r"(?P<var_name>{Variable}) = last step end datetime")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    
    step_context = __get_scenario_context().get_step(-2)
    res = step_context.end_datetime
    if res is None:
        raise TechnicalException(f"Failed to get last step end datetime: {step_context}")
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = defined user data (?P<user_data_name>{Str})(?: \(default: (?P<default_value>{Any})\))?")
def step_impl(context, var_name, user_data_name, default_value):
    var_name = StepTools.evaluate_variable_name(var_name)
    user_data_name = StepTools.evaluate_scenario_parameter(user_data_name)
    default_value = StepTools.evaluate_scenario_parameter(default_value)
    
    if user_data_name in context.config.userdata:
        res = context.config.userdata[user_data_name]
    else:
        res = default_value
    
    __get_variable_manager().register_variable(var_name, res)
    
    



