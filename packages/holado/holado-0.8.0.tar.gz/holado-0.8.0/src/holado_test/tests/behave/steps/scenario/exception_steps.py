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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_test.scenario.step_tools import StepTools
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_test.behave.behave import enter_expected_exception_step
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_block_manager():
    return __get_scenario_context().block_manager

def __get_scope_manager():
    return __get_scenario_context().scope_manager

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

def __get_expression_evaluator():
    return __get_scenario_context().get_expression_evaluator()



def __verify_context_doesnt_already_expect_an_exception(context):
    if context.expected_exception_str:
        msg = 'Already expecting failure on exception {}'.format(context.expected_exception_str)
        raise FunctionalException(msg)
    elif context.expected_exception_pattern:
        msg = "Already expecting failure on exception matching '{}'".format(context.expected_exception_pattern)
        raise FunctionalException(msg)

@Given(r"next step shall fail on exception (?!matching)(?P<exc_str>{Any})")
def step_impl(context, exc_str):
    exc_str = StepTools.evaluate_string_parameter(exc_str)
    
    __verify_context_doesnt_already_expect_an_exception(context)
    enter_expected_exception_step(context, expected_exception_str = exc_str)

@Given(r"next step shall fail on exception matching (?P<exc_str>{AnyStr})")
def step_impl(context, exc_str):
    exc_str = StepTools.evaluate_string_parameter(exc_str)
    exc_str_unescaped = StepTools.unescape_string(exc_str)
    
    __verify_context_doesnt_already_expect_an_exception(context)
    enter_expected_exception_step(context, expected_exception_pattern = exc_str_unescaped)

@Given(r"next step shall fail on following exception(?! matching)")
def step_impl(context):
    exc_str = BehaveStepTools.get_step_multiline_text(context)
    
    __verify_context_doesnt_already_expect_an_exception(context)
    enter_expected_exception_step(context, expected_exception_str = exc_str)

@Given(r"next step shall fail on following exception matching")
def step_impl(context):
    exc_str = BehaveStepTools.get_step_multiline_text(context)
    exc_str_unescaped = StepTools.unescape_string(exc_str)
    
    __verify_context_doesnt_already_expect_an_exception(context)
    enter_expected_exception_step(context, expected_exception_pattern = exc_str_unescaped)





