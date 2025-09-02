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
from holado_test.behave.behave import *  # @UnusedWildImport
import logging
from holado_test.scenario.step_tools import StepTools
from holado_core.common.exceptions.technical_exception import TechnicalException

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


def __get_context(context_name):
    context_name = context_name.capitalize()
    if context_name == SessionContext.instance().name:
        return SessionContext.instance()
    elif context_name == __get_scenario_context().name:
        return __get_scenario_context()
    else:
        raise TechnicalException(f"Not found context of name '{context_name}'")

@Step(r"execute post processes of (?P<context_name>{Str}) context")
def step_impl(context, context_name):
    context_name = StepTools.evaluate_scenario_parameter(context_name)
    
    context = __get_context(context_name)
    context.do_post_processes()

@Step(r"execute persisted post processes of (?P<context_name>{Str}) context")
def step_impl(context, context_name):
    context_name = StepTools.evaluate_scenario_parameter(context_name)
    
    context = __get_context(context_name)
    context.do_persisted_post_processes()

@Step(r"(?P<var_name>{Variable}) = number of persisted post processes to perform for (?P<context_name>{Str}) context")
def step_impl(context, var_name, context_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    context_name = StepTools.evaluate_scenario_parameter(context_name)
    
    context = __get_context(context_name)
    res = context.get_number_of_persisted_post_processes_to_perform()
    
    __get_variable_manager().register_variable(var_name, res)


