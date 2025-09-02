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
import tempfile
import logging
import os
from holado_system.system.global_system import GlobalSystem, OSTypes
import time
from holado_core.common.exceptions.functional_exception import FunctionalException

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

def __get_report_manager():
    return SessionContext.instance().report_manager

def __get_path_manager():
    return SessionContext.instance().path_manager


@Given(r"(?P<var_name>{Variable}) = new temporary directory with prefix (?P<prefix>{Str})")
def step_impl(context, var_name, prefix):
    var_name = StepTools.evaluate_variable_name(var_name)
    pref = StepTools.evaluate_scenario_parameter(prefix)
    tmp_dir = tempfile.mkdtemp(prefix=pref)
    __get_variable_manager().register_variable(var_name, tmp_dir)
    
@Given(r"(?P<var_name>{Variable}) = scenario report directory (?P<path>{Str})")
def step_impl(context, var_name, path):
    var_name = StepTools.evaluate_variable_name(var_name)
    path = StepTools.evaluate_scenario_parameter(path)
    rd_path = __get_report_manager().current_scenario_report.get_path(path)
    __get_variable_manager().register_variable(var_name, rd_path)
    

@Given(r"(?P<var_name>{Variable}) = value of environment variable (?P<env_var_name>{Str})")
def step_impl(context, var_name, env_var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    env_var_name = StepTools.evaluate_scenario_parameter(env_var_name)
    res = os.getenv(env_var_name)
    if res is None:
        raise EnvironmentError(f"Environment variable {env_var_name} is not defined")
    __get_variable_manager().register_variable(var_name, res)

@Step(r"yield processor")
def step_impl(context):
    GlobalSystem.yield_processor()

@Step(r"(?P<var_name>{Variable}) = first available anonymous port")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    
    res = GlobalSystem.get_first_available_anonymous_port()
    
    if res is None:
        raise FunctionalException(f"No port is available")
    __get_variable_manager().register_variable(var_name, res)



