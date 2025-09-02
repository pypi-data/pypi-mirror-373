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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_test.behave.behave import *  # @UnusedWildImport
import time
import logging
import re
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.tools.tools import Tools
from holado_core.common.handlers.redo import Redo
from holado_test.common.exceptions.undefined_step_exception import UndefinedStepException
from holado.holado_config import Config
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_scripting.common.tools.evaluate_parameters import EvaluateParameters
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


@Step(r"wait (?P<nb_sec>{Float}) seconds")
def step_impl(context, nb_sec):
    nb_sec = StepTools.evaluate_scenario_parameter(nb_sec)
    time.sleep(nb_sec)

def _prepare_acceptable_times(accepted, timeout, polling_time):
    res_a, res_t, res_p = accepted, timeout, polling_time

    if res_t is None:
        if res_a is None:
            res_t = Config.timeout_seconds
        else:
            res_t = 10 * res_a
    if res_a is None:
        res_a = res_t
    if res_p is None:
        res_p = res_a / 100
        if res_p > 1:
            res_p = 1

    return res_a, res_t, res_p

@Step(r"wait until (?P<then_step>{AnyLazy})(?P<then_after_steps> after steps)?(?: \((?:accepted time: (?P<accepted>{Float}) s)?(?: ; )?(?:timeout: (?P<timeout>{Float}) s)?(?: ; )?(?:polling: (?P<polling>{Float}) s)?\))?")
def step_impl(context, then_step, then_after_steps, accepted, timeout, polling):
    accepted = StepTools.evaluate_scenario_parameter(accepted)
    timeout = StepTools.evaluate_scenario_parameter(timeout)
    polling = StepTools.evaluate_scenario_parameter(polling)

    before_steps = BehaveStepTools.get_step_multiline_text(context, eval_params=EvaluateParameters.nothing(), raise_exception_if_none=False)
    if then_after_steps is not None and before_steps is None:
        raise FunctionalException("Missing steps to execute before Then step")
    
    accepted, timeout, polling = _prepare_acceptable_times(accepted, timeout, polling)

    class StepRedo(Redo):
        def __init__(self, then_step, before_steps):
            super().__init__("wait until then step")
            self.__then_step = then_step
            self.__before_steps = before_steps
            self.__steps_text = format_step_with_context(context, u"Then {}".format(then_step), with_keyword=False)
            
            # Replace dynamic variable names
            self.__then_step = StepTools.replace_variable_names(self.__then_step)
            self.__before_steps = StepTools.replace_variable_names(self.__before_steps)
            self.__steps_text = StepTools.replace_variable_names(self.__steps_text)

            self.stop_retry_on(UndefinedStepException)
            self.ignoring(Exception)

        def _execute_before_process(self):
            if self.__before_steps is not None:
                execute_steps(self.__before_steps)

        def _process(self):
            execute_steps(self.__steps_text)

        def _execute_after_failure(self, exc):
            if 'UNDEFINED SUB-STEP' in str(exc):
                raise UndefinedStepException(f"A step doesn't exist in:\n{self.__steps_text}") from exc
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Following steps failed:\n{Tools.indent_string(4, self.__steps_text)}\n  Error: {Typing.get_object_class_fullname(exc)}({exc})")

        def _get_waited_description(self):
            return self.__then_step

    redo = StepRedo(then_step, before_steps)
    redo.with_accepted_time(accepted).with_timeout(timeout).polling_every(polling)
    redo.ignoring(VerifyException)
    redo.execute()

@Then(r"(?P<value>{Str}) matches pattern (?P<pattern_str>{RawStr})")
def step_impl(context, value, pattern_str):
    val = StepTools.evaluate_scenario_parameter(value)
    pattern_str = StepTools.evaluate_string_parameter(pattern_str)
    
    pattern = re.compile(pattern_str)

    if not pattern.search(val):
        raise VerifyException("Match failure, value doesn't match pattern:\n    value : {}\n  pattern : {}".format(val, pattern_str))

@Then(r"(?P<value>{Str}) doesn't match pattern (?P<pattern_str>{RawStr})")
def step_impl(context, value, pattern_str):
    val = StepTools.evaluate_scenario_parameter(value)
    pattern_str = StepTools.evaluate_string_parameter(pattern_str)
    
    pattern = re.compile(pattern_str)

    if pattern.search(val):
        raise VerifyException("Match failure, value matches pattern:\n    value : {}\n  pattern : {}".format(val, pattern_str))




