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
from holado_scripting.common.tools.variable_manager import VariableManager
import logging
from holado_test.scenario.step_tools import StepTools

logger = logging.getLogger(__name__)


def __get_session_context():
    return SessionContext.instance()

def __get_scenario_context():
    return __get_session_context().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager() -> VariableManager:
    return __get_scenario_context().get_variable_manager()

@Given(r"(?P<var_name>{Variable}) = start internal S3 server")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    execute_steps(u"""
        Given {var_name} = new moto S3 server
            | Name         | Value     |
            | 'name'       | None      |
            | 'ip_address' | '0.0.0.0' |
            | 'port'       | 5000      |
            | 'verbose'    | False     |
            | 'auto_stop'  | True      |
        When start S3 server {var_name}
        """.format(var_name=var_name) )
    
@Given(r"(?P<var_name>{Variable}) = new internal Minio S3 client")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    execute_steps(u"""
        Given {var_name} = new Minio S3 client
            | Name            | Value            |
            | 'endpoint'      | 'localhost:5000' |
            | 'access_key'    | None             |
            | 'secret_key'    | None             |
            | 'session_token' | None             |
            | 'secure'        | False            |
            | 'region'        | None             |
            | 'http_client'   | None             |
            | 'credentials'   | None             |
            | 'trace'         | True             |
        """.format(var_name=var_name) )
    
@Given(r"(?P<var_name>{Variable}) = new internal Boto3 S3 client")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    from botocore import UNSIGNED
    from botocore.client import Config
    
    __get_variable_manager().register_variable("__CONFIG__@", Config(signature_version=UNSIGNED))
    execute_steps(u"""
        Given {var_name} = new Boto3 S3 client
            | Name                    | Value                   |
            | 'region_name'           | None                    |
            | 'api_version'           | None                    |
            | 'use_ssl'               | False                   |
            | 'verify'                | None                    |
            | 'endpoint_url'          | 'http://localhost:5000' |
            | 'aws_access_key_id'     | None                    |
            | 'aws_secret_access_key' | None                    |
            | 'aws_session_token'     | None                    |
            | 'config'                | __CONFIG__@              |
        """.format(var_name=var_name) )
    

