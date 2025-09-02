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
import os.path
import logging
from holado_test.scenario.step_tools import StepTools

logger = logging.getLogger(__name__)


def __get_session_context():
    return SessionContext.instance()

def __get_scenario_context():
    return __get_session_context().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


    
@Given(r"(?P<var_name>{Variable}) = start internal REST server")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    
    here = os.path.abspath(os.path.dirname(__file__))
    django_project_path = os.path.normpath(os.path.join(here, "..", "..", "..", "..", "..", "..", "..", "tests", "behave", "test_holado", "tools", "django", "api_rest"))
    
    execute_steps(u"""
        Given {var_name} = new Django server
            | Name                   | Value                          |
            | 'name'                 | 'REST server for holado tests' |
            | 'django_project_path'  | '{django_project_path}'        |
            | 'port'                 | 8000                           |
        When start (Django server: {var_name})
        """.format(var_name=var_name, django_project_path=django_project_path))
    


@Given(r"(?P<var_name>{Variable}) = new internal REST client")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    execute_steps(u"""
        Given {var_name} = new REST client
            | Name                      | Value                   |
            | 'url'                     | 'http://localhost:8000' |
            | 'headers.Content-Type'    | 'application/json'      |
            | 'authentication.user'     | ('admin', 'admin')      |
        """.format(var_name=var_name))
        
    
