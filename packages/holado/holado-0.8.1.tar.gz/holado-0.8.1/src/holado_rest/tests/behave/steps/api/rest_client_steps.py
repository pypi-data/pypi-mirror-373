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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_rest.api.rest.rest_client import RestClient
import json
import logging
from holado_rest.api.rest.rest_manager import RestManager
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_core.common.tables.table_manager import TableManager
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


if RestClient.is_available():

    def __get_session_context():
        return SessionContext.instance()
    
    def __get_scenario_context():
        return __get_session_context().get_scenario_context()
    
    def __get_text_interpreter():
        return __get_scenario_context().get_text_interpreter()
    
    def __get_variable_manager():
        return __get_scenario_context().get_variable_manager()
    
        
    @Given(r"(?P<var_name>{Variable}) = new REST client")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        
        if 'name' not in kwargs:
            kwargs['name'] = None
        
        manager = RestManager()
        client = manager.new_client(**kwargs)
    
        __get_variable_manager().register_variable(var_name, client)
    
    @Step(r"(?P<var_name>{Variable}) = response of (?P<request_method>delete|get|patch|post|put) (?P<path>{Str}) \(REST client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, request_method, path, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        path = StepTools.evaluate_scenario_parameter(path)
        client = StepTools.evaluate_variable_value(var_client)
        
        # Manage request arguments as step table
        request_kwargs = {}
        if hasattr(context, "table") and context.table is not None:
            table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
            request_kwargs = ValueTableConverter.convert_name_value_table_2_json_object(table)
        
        # Manage request arguments as json text
        # Manage data as json text
        text = BehaveStepTools.get_step_multiline_text(context, raise_exception_if_none=False)
        if text is not None:
            if len(request_kwargs) > 0:
                raise TechnicalException(f"Request kwargs are already set to {request_kwargs}")
            request_kwargs = json.loads(text)
        
        # Process request
        res = client.request(request_method, path, **request_kwargs)
        
        # Store result
        if Tools.do_log(logger, logging.DEBUG):
            res_table = TableManager.convert_object_attributes_2_name_value_table(res)
            logger.debug(f"Response of {request_method} {path}:\n{res_table.represent(4)}")
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = (?P<request_method>delete|get|patch|post|put) (?P<path>{Str}) \(REST client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, request_method, path, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        client = StepTools.evaluate_variable_value(var_client)

        execute_steps(format_step_with_context(context, 
                u"__RESPONSE__@ = response of {request_method} {path} (REST client: {var_client})"
                    .format(request_method=request_method, path=path, var_client=var_client) ))
        
        response = __get_variable_manager().get_variable_value("__RESPONSE__@")
        res = client.response_result(response)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = response of (?P<request_method>delete|get|patch|post|put) (?P<path>{Str}) with data \(REST client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, request_method, path, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        path = StepTools.evaluate_scenario_parameter(path)
        client = StepTools.evaluate_variable_value(var_client)
        
        data = None
        
        # Manage request arguments as step table
        if hasattr(context, "table") and context.table is not None:
            table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
            data = ValueTableConverter.convert_name_value_table_2_json_object(table)
        
        # Manage request arguments as json text
        # Manage data as json text
        text = BehaveStepTools.get_step_multiline_text(context, raise_exception_if_none=False)
        if text is not None:
            if data is not None:
                raise TechnicalException(f"Data is already set to [{data}]")
            data = text
        
        # Process request
        res = client.request(request_method, path, data=data)
        
        # Store result
        if Tools.do_log(logger, logging.DEBUG):
            res_table = TableManager.convert_object_attributes_2_name_value_table(res)
            logger.debug(f"Response of {request_method} {path}:\n{res_table.represent(4)}")
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = (?P<request_method>delete|get|patch|post|put) (?P<path>{Str}) with data \(REST client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, request_method, path, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        client = StepTools.evaluate_variable_value(var_client)

        execute_steps(format_step_with_context(context, 
                u"__RESPONSE__@ = response of {request_method} {path} with data (REST client: {var_client})"
                    .format(request_method=request_method, path=path, var_client=var_client) ))
        
        response = __get_variable_manager().get_variable_value("__RESPONSE__@")
        res = client.response_result(response)
        
        __get_variable_manager().register_variable(var_name, res)
    
    
    @Step(r"(?P<var_name>{Variable}) = response of (?P<request_method>delete|get|patch|post|put) (?P<path>{Str}) with content of CSV file (?P<file_path>{Str}) \(REST client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, request_method, path, file_path, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        path = StepTools.evaluate_scenario_parameter(path)
        file_path = StepTools.evaluate_scenario_parameter(file_path)
        client = StepTools.evaluate_variable_value(var_client)
        
        # Request with file object as data
        with open(file_path, "rb") as data:
            res = client.request(request_method, path, data=data, headers={'Content-Type':'text/csv'})
        
        # Store result
        if Tools.do_log(logger, logging.DEBUG):
            res_table = TableManager.convert_object_attributes_2_name_value_table(res)
            logger.debug(f"Response of {request_method} {path}:\n{res_table.represent(4)}")
        __get_variable_manager().register_variable(var_name, res)
    
    @When(r"(?P<var_name>{Variable}) = (?P<request_method>delete|get|patch|post|put) (?P<path>{Str}) with content of CSV file (?P<file_path>{Str}) \(REST client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, request_method, path, file_path, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        client = StepTools.evaluate_variable_value(var_client)

        execute_steps(format_step_with_context(context, 
                u"__RESPONSE__@ = response of {request_method} {path} with content of CSV file {file_path} (REST client: {var_client})"
                    .format(request_method=request_method, path=path, file_path=file_path, var_client=var_client) ))
        
        response = __get_variable_manager().get_variable_value("__RESPONSE__@")
        res = client.response_result(response)
        
        __get_variable_manager().register_variable(var_name, res)
    
    
    
