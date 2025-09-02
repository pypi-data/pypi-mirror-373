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
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_test.scenario.tester_tools import TesterTools

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


@Step(r"tester logs (?P<msg>{AnyStr})(?: \((?P<unlimited_str>unlimited)\))?")
def step_impl(context, msg, unlimited_str):
    msg = StepTools.evaluate_scenario_parameter(msg)
    
    # Add multiline text if present
    text = BehaveStepTools.get_step_multiline_text(context, raise_exception_if_none=False, log_level=logging.TRACE)  # @UndefinedVariable
    if text is not None:
        msg += '\n' + text
    
    # Add table if present
    table = BehaveStepTools.get_step_table(context)
    if table:
        msg += '\n' + table.represent(4)
    
    TesterTools.log(msg, unlimited_str is not None)
    
    
@Step(r"(?P<var_name>{Variable}) = tester represents (?P<param>{Any})")
def step_impl(context, var_name, param):
    var_name = StepTools.evaluate_variable_name(var_name)
    value = StepTools.evaluate_scenario_parameter(param)
    
    text = TesterTools.represent(value)
    
    __get_variable_manager().register_variable(var_name, text)
    

@Step(r"fail on error (?P<msg>{AnyStr})")
def step_impl(context, msg):
    msg = StepTools.evaluate_scenario_parameter(msg)
    raise FunctionalException(msg)

