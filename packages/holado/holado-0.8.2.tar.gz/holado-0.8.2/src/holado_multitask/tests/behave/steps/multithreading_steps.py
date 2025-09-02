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


from holado.common.context.session_context import SessionContext
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_multitask.multithreading.functionthreaded import FunctionThreaded
from holado_core.common.block.function import Function
from holado_test.scenario.step_tools import StepTools
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_scripting.common.tools.evaluate_parameters import EvaluateParameters
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_multitask.multithreading.periodicfunctionthreaded import PeriodicFunctionThreaded
from holado.common.handlers.undefined import undefined_argument


logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_threads_manager():
    return SessionContext.instance().threads_manager

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()




@Given(r"(?P<var_name>{Variable}) = new thread that calls steps(?P<is_periodic_str> periodically)?(?: \((?:delay before: (?P<delay_before_str>{Float}) s)?(?: ; )?(?:period: (?P<period_str>{Float}) s(?: ; nb times: (?P<nb_times_str>{Int}))?)?(?: ; )?(?:format with: (?P<format_with>{Variable}(?:, {Variable})*))?\))?")
def step_impl(context, var_name, is_periodic_str, delay_before_str, period_str, nb_times_str, format_with):
    var_name = StepTools.evaluate_variable_name(var_name)
    delay_before_sec = StepTools.evaluate_scenario_parameter(delay_before_str)
    period_sec = StepTools.evaluate_scenario_parameter(period_str)
    nb_times = StepTools.evaluate_scenario_parameter(nb_times_str)
    format_with = StepTools.evaluate_variable_name(format_with)
    steps = BehaveStepTools.get_step_multiline_text(context, eval_params=EvaluateParameters.nothing())
    
    if is_periodic_str is not None and period_sec is None:
        raise FunctionalException(f"Period must be defined for periodic steps")
    if format_with is not None:
        steps = StepTools.format_steps_with(steps, format_with.split(', '))
    
    if period_sec is not None:
        thread_name = f"CALL_STEPS_PERIODICALLY[{var_name};{period_sec}]"
        func = PeriodicFunctionThreaded(period_sec, execute_steps, args=[steps], name=thread_name, delay_before_run_sec=delay_before_sec, nb_times=nb_times)
        res = func.unique_name
    else:
        thread_name = f"CALL_STEPS[{var_name}]"
        func = FunctionThreaded(execute_steps, args=[steps], name=thread_name, delay_before_run_sec=delay_before_sec)
        res = func.unique_name
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = call steps in a thread(?: \((?:delay before: (?P<delay_before_str>{Float}) s)?(?: ; )?(?:format with: (?P<format_with>{Variable}(?:, {Variable})*))?\))?")
def step_impl(context, var_name, delay_before_str, format_with):
    var_name = StepTools.evaluate_variable_name(var_name)
    delay_before_sec = StepTools.evaluate_scenario_parameter(delay_before_str)
    format_with = StepTools.evaluate_variable_name(format_with)
    steps = BehaveStepTools.get_step_multiline_text(context, eval_params=EvaluateParameters.nothing())
    
    step_params_list = []
    if delay_before_sec is not None:
        step_params_list.append(f"delay before: {delay_before_sec} s")
    if format_with is not None:
        step_params_list.append(f"format with: {format_with} s")
    step_params = " (" + " ; ".join(step_params_list) + ")" if len(step_params_list) > 0 else ""
    
    execute_steps(u"""
        Given {var_name} = new thread that calls steps{step_params}
            \"""{steps}\"""
        Given start thread {var_name}
        """.format(var_name=var_name, step_params=step_params, steps=BehaveStepTools.format_steps_as_parameter(steps, 12)))

@Given(r"for thread (?P<var_name>{Variable}), call steps for interrupt(?: \(format with: (?P<format_with>{Variable}(?:, {Variable})*)\))?")
def step_impl(context, var_name, format_with):
    thread_id = StepTools.evaluate_variable_value(var_name)
    format_with = StepTools.evaluate_variable_name(format_with)
    steps = BehaveStepTools.get_step_multiline_text(context, eval_params=EvaluateParameters.nothing())
    
    if format_with is not None:
        steps = StepTools.format_steps_with(steps, format_with.split(', '))
        
    interrupt_func = Function(execute_steps, steps)
    
    func = __get_threads_manager().get_thread(thread_id)
    if hasattr(func, "interrupt_function"):
        func.interrupt_function = interrupt_func
    else:
        raise FunctionalException("Thread '{}' is not interruptable by a function".format(var_name))

@Step(r'start thread (?P<var_name>{Variable})')
def step_impl(context, var_name):
    thread_id = StepTools.evaluate_variable_value(var_name)
    
    thread = __get_threads_manager().get_thread(thread_id)
    thread.start()

@Step(r'join thread (?P<var_name>{Variable})(?: \(timeout: (?P<timeout_str>{Variable}) s\))?')
def step_impl(context, var_name, timeout_str):
    thread_id = StepTools.evaluate_variable_value(var_name)
    timeout = StepTools.evaluate_variable_value(timeout_str) if timeout_str is not None else undefined_argument
    
    __get_threads_manager().join_thread(thread_id, timeout=timeout)

@Step(r'stop thread (?P<var_name>{Variable})')
def step_impl(context, var_name):
    thread_id = StepTools.evaluate_variable_value(var_name)
    
    thread = __get_threads_manager().get_thread(thread_id)
    thread.interrupt()




