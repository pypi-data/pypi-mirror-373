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
from holado.common.context.session_context import SessionContext
from holado_test.scenario.step_tools import StepTools
import logging
import queue
from typing import Iterable
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools
from holado_system.system.global_system import GlobalSystem
from holado_system.system.filesystem.file import File
from holado_python.standard_library.queue import IterableQueue,\
    IterableLifoQueue
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_scripting.common.tools.evaluate_parameters import EvaluateParameters
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()



@Given(r"(?P<var_name>{Variable}) = new FIFO queue(?: of size (?P<size>{Int}))?(?: \((?:block on get: (?P<block_on_get>{Boolean}))?(?: ; )?(?:block on get timeout: (?P<block_on_get_timeout>{Float} s))?(?: ; )?(?:block on put: (?P<block_on_put>{Boolean}))?(?: ; )?(?:block on put timeout: (?P<block_on_put_timeout>{Float}) s)?\))?")
def step_impl(context, var_name, size, block_on_get, block_on_get_timeout, block_on_put, block_on_put_timeout):
    var_name = StepTools.evaluate_variable_name(var_name)
    size = StepTools.evaluate_scenario_parameter(size)
    block_on_get = StepTools.evaluate_scenario_parameter(block_on_get)
    block_on_get_timeout = StepTools.evaluate_scenario_parameter(block_on_get_timeout)
    block_on_put = StepTools.evaluate_scenario_parameter(block_on_put)
    block_on_put_timeout = StepTools.evaluate_scenario_parameter(block_on_put_timeout)
    
    res = IterableQueue(size, block_on_get, block_on_get_timeout, block_on_put, block_on_put_timeout)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = new LIFO queue(?: of size (?P<size>{Int}))?(?: \((?:block on get: (?P<block_on_get>{Boolean}))?(?: ; )?(?:block on get timeout: (?P<block_on_get_timeout>{Float} s))?(?: ; )?(?:block on put: (?P<block_on_put>{Boolean}))?(?: ; )?(?:block on put timeout: (?P<block_on_put_timeout>{Float}) s)?\))?")
def step_impl(context, var_name, size, block_on_get, block_on_get_timeout, block_on_put, block_on_put_timeout):
    var_name = StepTools.evaluate_variable_name(var_name)
    size = StepTools.evaluate_scenario_parameter(size)
    block_on_get = StepTools.evaluate_scenario_parameter(block_on_get)
    block_on_get_timeout = StepTools.evaluate_scenario_parameter(block_on_get_timeout)
    block_on_put = StepTools.evaluate_scenario_parameter(block_on_put)
    block_on_put_timeout = StepTools.evaluate_scenario_parameter(block_on_put_timeout)
        
    res = IterableLifoQueue(size, block_on_get, block_on_get_timeout, block_on_put, block_on_put_timeout)
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"put (?!all )(?P<value>{Any}) \(Queue: (?P<var_queue>{Variable})\)")
def step_impl(context, value, var_queue):
    value = StepTools.evaluate_scenario_parameter(value)
    q = StepTools.evaluate_variable_value(var_queue)
    
    q.put(value)

@Step(r"(?P<var_name>{Variable}) = get \(Queue: (?P<var_queue>{Variable})\)")
def step_impl(context, var_name, var_queue):
    var_name = StepTools.evaluate_variable_name(var_name)
    q = StepTools.evaluate_variable_value(var_queue)
    
    res = q.get()
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"task is done \(Queue: (?P<var_queue>{Variable})\)")
def step_impl(context, var_queue):
    q = StepTools.evaluate_variable_value(var_queue)
    
    q.task_done()

@Step(r"join \(Queue: (?P<var_queue>{Variable})\)")
def step_impl(context, var_queue):
    q = StepTools.evaluate_variable_value(var_queue)
    
    q.join()

@Step(r"(?P<var_name>{Variable}) = size \(Queue: (?P<var_queue>{Variable})\)")
def step_impl(context, var_name, var_queue):
    var_name = StepTools.evaluate_variable_name(var_name)
    q = StepTools.evaluate_variable_value(var_queue)
        
    res = q.qsize()
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"close queue \(Queue: (?P<var_queue>{Variable})\)")
def step_impl(context, var_queue):
    q = StepTools.evaluate_variable_value(var_queue)
    q.close()



@Step(r"put all of (?P<iterable_str>{Variable}) \(Queue: (?P<var_queue>{Variable})(?: ; nb of repeat: (?P<repeat_nb>{Int}))?(?: ; rate log period: (?P<rate_period_s>{Int}) s)?\)")
def step_impl(context, iterable_str, var_queue, repeat_nb, rate_period_s):
    iterable = StepTools.evaluate_scenario_parameter(iterable_str)
    it_name = StepTools.evaluate_variable_name(iterable_str)
    q = StepTools.evaluate_variable_value(var_queue)
    q_name = StepTools.evaluate_variable_name(var_queue)
    repeat_nb = StepTools.evaluate_scenario_parameter(repeat_nb)
    rate_period_s = StepTools.evaluate_scenario_parameter(rate_period_s)
    
    if not isinstance(iterable, Iterable):
        raise FunctionalException(f"Parameter [{iterable_str}] (type: {Typing.get_object_class_fullname(iterable)}) is not iterable")

    if repeat_nb is None:
        repeat_nb = 1
    nb_elements = len(iterable)
    
    beg = Tools.timer_s()
    s_end, t_end = 0, beg
    for num in range(1, repeat_nb+1):
        s_beg, t_beg = is_beg, it_beg = s_end, t_end
        ind_beg = 0
        
        for ind, value in enumerate(iterable):
            q.put(value)
            
            if rate_period_s and ind > 0 and ind % 10 == 0:
                it_end = Tools.timer_s()
                if it_end > it_beg + rate_period_s:
                    is_end = q.qsize()
                    rate = (is_beg + ind - ind_beg - is_end) / (it_end - it_beg)
                    logger.print(f"[{it_name} -> Queue {q_name} ; Iteration {num}] Current rate: {round(rate,2)} item/s ; Queue size: {is_end}")
                    ind_beg, is_beg, it_beg = ind, is_end, it_end
                    
            # Yield processor in case of multithreading
            if ind % 10 == 0:
                GlobalSystem.yield_processor()
            
        if rate_period_s:
            s_end, t_end = q.qsize(), Tools.timer_s()
            rate = (s_beg + nb_elements - s_end) / (t_end - t_beg)
            logger.print(f"[{it_name} -> Queue {q_name} ; Iteration {num}] Mean rate: {round(rate,2)} item/s ; Queue size: {s_end}")
        
    if rate_period_s:
        end, s_end = Tools.timer_s(), q.qsize()
        rate = (nb_elements * repeat_nb - s_end) / (end - beg)
        logger.print(f"[{it_name} -> Queue {q_name}] Mean rate: {round(rate,2)} item/s")

@Step(r"put all of (?P<iterable_str>{Variable}) by batch of (?P<batch_size>{Int}) items \(Queue: (?P<var_queue>{Variable})(?: ; nb of repeat: (?P<repeat_nb>{Int}))?(?: ; rate log period: (?P<rate_period_s>{Int}) s)?\)")
def step_impl(context, iterable_str, batch_size, var_queue, repeat_nb, rate_period_s):
    iterable = StepTools.evaluate_scenario_parameter(iterable_str)
    it_name = StepTools.evaluate_variable_name(iterable_str)
    batch_size = StepTools.evaluate_scenario_parameter(batch_size)
    q = StepTools.evaluate_variable_value(var_queue)
    q_name = StepTools.evaluate_variable_name(var_queue)
    repeat_nb = StepTools.evaluate_scenario_parameter(repeat_nb)
    rate_period_s = StepTools.evaluate_scenario_parameter(rate_period_s)
    
    if not isinstance(iterable, Iterable):
        raise FunctionalException(f"Parameter [{iterable_str}] (type: {Typing.get_object_class_fullname(iterable)}) is not iterable")

    if repeat_nb is None:
        repeat_nb = 1
    nb_elements = len(iterable)
    
    beg = Tools.timer_s()
    s_end, t_end = 0, beg
    for num in range(1, repeat_nb+1):
        s_beg, t_beg = is_beg, it_beg = s_end, t_end
        batch_counter_beg = batch_counter = 0
        batch = []
        
        for value in iterable:
            batch.append(value)
            if len(batch) >= batch_size:
                batch_counter += 1
                q.put(batch)
                batch = []
            
                if rate_period_s and batch_counter > 0 and batch_counter % 10 == 0:
                    it_end = Tools.timer_s()
                    if it_end > it_beg + rate_period_s:
                        is_end = q.qsize()
                        rate = (is_beg + batch_counter - batch_counter_beg - is_end) / (it_end - it_beg)
                        logger.print(f"[{it_name} -> Queue {q_name} ; Iteration {num}] Current rate: {round(rate,2)} item/s ; Queue size: {is_end}")
                        batch_counter_beg, is_beg, it_beg = batch_counter, is_end, it_end
                        
                # Yield processor in case of multithreading
                if batch_counter % 10 == 0:
                    GlobalSystem.yield_processor()
            
        if rate_period_s:
            s_end, t_end = q.qsize(), Tools.timer_s()
            rate = (s_beg + nb_elements - s_end) / (t_end - t_beg)
            logger.print(f"[{it_name} -> Queue {q_name} ; Iteration {num}] Mean rate: {round(rate,2)} item/s ; Queue size: {s_end}")
        
    if rate_period_s:
        end, s_end = Tools.timer_s(), q.qsize()
        rate = (nb_elements * repeat_nb - s_end) / (end - beg)
        logger.print(f"[{it_name} -> Queue {q_name}] Mean rate: {round(rate,2)} item/s")

@Step(r"put all lines of file (?P<file_str>{Variable})(?: \(offset: (?P<offset>{Int}) ; size: (?P<size>{Int})\))? \(Queue: (?P<var_queue>{Variable})(?: ; rate log period: (?P<rate_period_s>{Int}) s)?\)")
def step_impl(context, file_str, offset, size, var_queue, rate_period_s):
    file = StepTools.evaluate_scenario_parameter(file_str)
    file_name = StepTools.evaluate_variable_name(file_str)
    q = StepTools.evaluate_variable_value(var_queue)
    q_name = StepTools.evaluate_variable_name(var_queue)
    offset = StepTools.evaluate_scenario_parameter(offset)
    size = StepTools.evaluate_scenario_parameter(size)
    rate_period_s = StepTools.evaluate_scenario_parameter(rate_period_s)
    
    if not isinstance(file, File):
        raise FunctionalException(f"Parameter [{file_str}] is not a file object")

    beg = Tools.timer_s()
    s_beg, t_beg = s_end, t_end = 0, beg
    ind_beg = 0
    
    for ind, line in enumerate(file.internal_file):
        if ind < offset:
            continue
        elif size > 0 and ind >= offset + size:
            break
        
        q.put(line.strip('\n'))
        
        if rate_period_s and ind > 0 and ind % 10 == 0:
            t_end = Tools.timer_s()
            if t_end > t_beg + rate_period_s:
                s_end = q.qsize()
                rate = (s_beg + ind - ind_beg - s_end) / (t_end - t_beg)
                logger.print(f"[File {file_name} -> Queue {q_name}] Current rate: {round(rate,2)} item/s ; Queue size: {s_end}")
                ind_beg, s_beg, t_beg = ind, s_end, t_end
                
        # Yield processor in case of multithreading
        if ind > 0 and ind % 10 == 0:
            GlobalSystem.yield_processor()
        
    if rate_period_s:
        end, s_end = Tools.timer_s(), q.qsize()
        rate = (ind + 1 - s_end) / (end - beg)
        logger.print(f"[File {file_name} -> Queue {q_name}] Mean rate: {round(rate,2)} item/s")



@Step(r"for (?P<item_var_name>{VariableName}) in (?P<iterable_str>{Variable}), call steps, and put (?P<result_var_name>{VariableName}) \(Queue: (?P<var_queue>{Variable})(?: ; rate log period: (?P<rate_period_s>{Int}) s)?(?: ; format with: (?P<format_with>{Variable}(?:, {Variable})*))?\)")
def step_impl(context, item_var_name, iterable_str, result_var_name, var_queue, rate_period_s, format_with):
    item_var_name = StepTools.evaluate_variable_name(item_var_name)
    iterable = StepTools.evaluate_variable_value(iterable_str)
    it_name = StepTools.evaluate_variable_name(iterable_str)
    result_var_name = StepTools.evaluate_variable_name(result_var_name)
    q = StepTools.evaluate_variable_value(var_queue)
    q_name = StepTools.evaluate_variable_name(var_queue)
    rate_period_s = StepTools.evaluate_scenario_parameter(rate_period_s)
    format_with = StepTools.evaluate_variable_name(format_with)
    steps = BehaveStepTools.get_step_multiline_text(context, eval_params=EvaluateParameters.nothing())
    
    if format_with is not None:
        steps = StepTools.format_steps_with(steps, format_with.split(', '))
    
    beg = Tools.timer_s()
    t_beg = t_end = beg
    ind_beg = 0
    
    for ind, item in enumerate(iterable):
        __get_variable_manager().register_variable(item_var_name, item)
        execute_steps(steps)
        result = __get_variable_manager().get_variable_value(result_var_name)
        
        q.put(result)
        
        if rate_period_s and ind > 0 and ind % 10 == 0:
            t_end = Tools.timer_s()
            if t_end > t_beg + rate_period_s:
                s_end = q.qsize()
                rate = (ind - ind_beg) / (t_end - t_beg)
                logger.print(f"[{it_name} -> Queue {q_name}] Current rate: {round(rate,2)} item/s ; Queue size: {s_end}")
                ind_beg, t_beg = ind, t_end
                
        # Yield processor in case of multithreading
        if ind > 0 and ind % 10 == 0:
            GlobalSystem.yield_processor()
        
    if rate_period_s:
        end, s_end = Tools.timer_s(), q.qsize()
        rate = (ind + 1) / (end - beg)
        logger.print(f"[{it_name} -> Queue {q_name}] Mean rate: {round(rate,2)} item/s ; Queue size: {s_end}")


@Step(r"for (?P<item_var_name>{VariableName}) in queue, call steps \(Queue: (?P<var_queue>{Variable})(?: ; rate log period: (?P<rate_period_s>{Int}) s)?(?: ; format with: (?P<format_with>{Variable}(?:, {Variable})*))?\)")
def step_impl(context, item_var_name, var_queue, rate_period_s, format_with):
    item_var_name = StepTools.evaluate_variable_name(item_var_name)
    q = StepTools.evaluate_variable_value(var_queue)
    q_name = StepTools.evaluate_variable_name(var_queue)
    rate_period_s = StepTools.evaluate_scenario_parameter(rate_period_s)
    format_with = StepTools.evaluate_variable_name(format_with)
    steps = BehaveStepTools.get_step_multiline_text(context, eval_params=EvaluateParameters.nothing())
    
    if format_with is not None:
        steps = StepTools.format_steps_with(steps, format_with.split(', '))
    
    counter = 0
    beg = Tools.timer_s()
    c_beg, t_beg = counter, beg
    log_counter = 0
    
    try:
        while True:
            # Get next item
            item = q.get()
            if q.is_sentinel(item):
                break
            counter += 1
            
            __get_variable_manager().register_variable(item_var_name, item)
            try:
                execute_steps(steps)
            except Exception as exc:
                logger.warning(f"[Queue {q_name}] Failed to execute steps with {counter}'th item: [{Typing.get_object_class_fullname(exc)}] {str(exc)}")
            finally:
                q.task_done()
            
            # Log rate if needed
            if rate_period_s and counter % 10 == 0:
                t_end = Tools.timer_s()
                if t_end > t_beg + rate_period_s:
                    c_end, s_end = counter, q.qsize()
                    rate = (c_end - c_beg) / (t_end - t_beg)
                    log_counter += 1
                    logger.print(f"[Queue {q_name}] Rate: {int(rate)} msg/s ; Nb items: {counter} ; Queue size: {s_end}")
                    c_beg, t_beg = c_end, t_end
                    
            # Yield processor in case of multithreading
            if counter % 10 == 0:
                GlobalSystem.yield_processor()
    except queue.Empty:
        # Without block, or with timeout, this exception occurs when queue is empty
        pass
    
    if rate_period_s:
        end = Tools.timer_s()
        rate = counter / (end - beg)
        logger.print(f"[Queue {q_name}] Mean rate: {int(rate)} msg/s ; Nb messages: {counter}")




