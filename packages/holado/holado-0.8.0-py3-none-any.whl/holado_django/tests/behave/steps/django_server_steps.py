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
from holado_django.server.django_server import DjangoServer
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_django.server.grpc_django_server import GrpcDjangoServer

logger = logging.getLogger(__name__)


def __get_session_context():
    return SessionContext.instance()

def __get_scenario_context():
    return __get_session_context().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()



@Given(r"(?P<var_name>{Variable}) = new Django server")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.get_step_table(context)
    
    kwargs = ValueTableConverter.convert_name_value_table_2_json_object(table)
    if 'django_project_path' not in kwargs:
        raise TechnicalException("Parameter 'django_project_path' is required")
    if 'name' not in kwargs:
        kwargs['name'] = f"Django server ({kwargs['django_project_path']})"
    
    server = DjangoServer(**kwargs)
    
    __get_variable_manager().register_variable(var_name, server)
    
@Given(r"(?P<var_name>{Variable}) = new gRPC Django server")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.get_step_table(context)
    
    kwargs = ValueTableConverter.convert_name_value_table_2_json_object(table)
    if 'django_project_path' not in kwargs:
        raise TechnicalException("Parameter 'django_project_path' is required")
    if 'name' not in kwargs:
        kwargs['name'] = f"Django server ({kwargs['django_project_path']})"
    
    server = GrpcDjangoServer(**kwargs)
    
    __get_variable_manager().register_variable(var_name, server)
    

@Step(r"start \(Django server: (?P<var_server>{Variable})\)")
def step_impl(context, var_server):
    server = StepTools.evaluate_variable_value(var_server)
    server.start()

@Step(r"stop \(Django server: (?P<var_server>{Variable})\)")
def step_impl(context, var_server):
    server = StepTools.evaluate_variable_value(var_server)
    server.stop()

    
