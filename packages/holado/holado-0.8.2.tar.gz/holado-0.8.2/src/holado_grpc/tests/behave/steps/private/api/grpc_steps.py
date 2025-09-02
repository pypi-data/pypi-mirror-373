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
from holado_core.tools.abstracts.blocking_command_service import BlockingCommandService
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


@Given(r"(?P<var_name>{Variable}) = start internal gRPC server")
def step_impl(context, var_name):
    """
    This step runs the api_grpc/api1 gRPC server available in testing tools.
    
    It was written with djangogrpcframework that is not maintained anymore.
    Version 0.2.1 of djangogrpcframework is not compatible as is with Django>=4.1.4.
    A workaround working currently is to comment line 20 "requires_system_checks = False" in file "django_grpc_framework/management/commands/grpcrunserver.py".
    TODO: update tools by using library https://github.com/socotecio/django-socio-grpc instead of djangogrpcframework
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    
    here = os.path.abspath(os.path.dirname(__file__))
    django_project_path = os.path.normpath(os.path.join(here, "..", "..", "..", "..", "..", "..", "..", "tests", "behave", "test_holado", "tools", "django", "api_grpc"))
    
    execute_steps(u"""
        Given {var_name} = new gRPC Django server
            | Name                   | Value                          |
            | 'name'                 | 'gRPC server for holado tests' |
            | 'django_project_path'  | '{django_project_path}'        |
        When start (Django server: {var_name})
        """.format(var_name=var_name, django_project_path=django_project_path))
    
    # Update imported grpc messages and services
    proto_path = os.path.join(django_project_path, "api_grpc", "api1", "proto")
    __get_session_context().protobuf_messages.import_all_compiled_proto(proto_path)
    __get_session_context().grpc_services.import_all_compiled_proto(proto_path)
    
    
@Given(r"(?P<var_name>{Variable}) = new internal gRPC client on service (?P<service_name>{Str})")
def step_impl(context, var_name, service_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    
    execute_steps(u"""
        Given {var_name} = new gRPC client
            | Name                      | Value           |
            | 'endpoint'                | '0.0.0.0:50051' |
            | 'service'                 | {service_name}  |
        """.format(var_name=var_name, service_name=service_name))
