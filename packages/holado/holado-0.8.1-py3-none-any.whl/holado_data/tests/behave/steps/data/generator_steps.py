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
from holado_scripting.text.interpreter.text_interpreter import TextInterpreter
from holado_scripting.common.tools.variable_manager import VariableManager
from holado_test.common.context.scenario_context import ScenarioContext
import logging
from holado_data.data.generator.python_generator import PythonGenerator

logger = logging.getLogger(__name__)


def __get_session_context() -> SessionContext:
    return SessionContext.instance()

def __get_scenario_context() -> ScenarioContext:
    return __get_session_context().get_scenario_context()

def __get_text_interpreter() -> TextInterpreter:
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager() -> VariableManager:
    return __get_scenario_context().get_variable_manager()



@Step(r"(?P<var_name>{Variable}) = generator with expression \[(?P<generator_expression>{Any})\]")
def step_impl(context, var_name, generator_expression):
    """
    Create new generator with given expression.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    generator_expression = StepTools.evaluate_scenario_parameter(generator_expression)
    
    result = PythonGenerator(generator_expression)
    
    __get_variable_manager().register_variable(var_name, result)

@Step(r"set batch size to (?P<batch_size>{Int}) \(Generator: (?P<var_gen>{Variable})\)")
def step_impl(context, batch_size, var_gen):
    """
    Set generator batch size.
    """
    batch_size = StepTools.evaluate_scenario_parameter(batch_size)
    gen = StepTools.evaluate_variable_value(var_gen)
    
    gen.batch_size = batch_size
    
@Step(r"(?P<var_name>{Variable}) = next \(Generator: (?P<var_gen>{Variable})\)")
def step_impl(context, var_name, var_gen):
    """
    Get next element.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    gen = StepTools.evaluate_variable_value(var_gen)
    
    result = next(gen)
    
    __get_variable_manager().register_variable(var_name, result)
    
@Step(r"(?P<var_name>{Variable}) = next batch \(Generator: (?P<var_gen>{Variable})\)")
def step_impl(context, var_name, var_gen):
    """
    Get next batch.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    gen = StepTools.evaluate_variable_value(var_gen)
    
    result = gen.next_batch()
    
    __get_variable_manager().register_variable(var_name, result)
    
    
    
    
    
