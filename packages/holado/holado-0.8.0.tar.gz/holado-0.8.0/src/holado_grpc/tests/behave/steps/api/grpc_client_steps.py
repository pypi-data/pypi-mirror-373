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
from holado_grpc.api.rpc.grpc_client import GRpcClient
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_core.common.tools.tools import Tools
from holado_system.system.global_system import GlobalSystem
import queue
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


if GRpcClient.is_available():

    def __get_session_context():
        return SessionContext.instance()
    
    def __get_scenario_context():
        return __get_session_context().get_scenario_context()
    
    def __get_text_interpreter():
        return __get_scenario_context().get_text_interpreter()
    
    def __get_variable_manager():
        return __get_scenario_context().get_variable_manager()
    
    def __get_grpc_services():
        return __get_session_context().grpc_services

        
    @Given(r"(?P<var_name>{Variable}) = new gRPC client")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        
        client = __get_session_context().grpc_manager.new_client(None, **kwargs)
        
        __get_variable_manager().register_variable(var_name, client)
        
    @Given(r"(?P<var_name>{Variable}) = service names \(gRPC client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        client = StepTools.evaluate_variable_value(var_client)
        
        service_names = client.internal_client.service_names
        
        __get_variable_manager().register_variable(var_name, service_names)
        
    @Step(r"(?P<var_name>{Variable}) = input type fullname of request (?P<service_method>{Str}) \(gRPC client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, service_method, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        service_method = StepTools.evaluate_scenario_parameter(service_method)
        client = StepTools.evaluate_variable_value(var_client)
        
        service_name, method_name = service_method.rsplit('.', 1)
        res = client.get_request_data_type_fullname(service_name, method_name)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @When(r"(?P<var_name>{Variable}) = request (?P<service_method>{Str}) \(gRPC client: (?P<var_client>{Variable})(?: ; with Protobuf (?P<with_proto_request>request)?(?: & )?(?P<with_proto_response>response)?)?\)")
    def step_impl(context, var_name, service_method, var_client, with_proto_request, with_proto_response):
        var_name = StepTools.evaluate_variable_name(var_name)
        service_method = StepTools.evaluate_scenario_parameter(service_method)
        client = StepTools.evaluate_variable_value(var_client)
        table = BehaveStepTools.get_step_table(context)
        
        service_name, method_name = service_method.rsplit('.', 1)
        request_data = client.build_request_data(service_name, method_name, params_table=table, as_proto=with_proto_request is not None)
        res = client.request(service_name, method_name, request_data, raw_output=with_proto_response is not None)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @When(r"(?P<var_name>{Variable}) = request (?P<service_method>{Str}) with data (?P<request_data>{Str}) \(gRPC client: (?P<var_client>{Variable})(?: ; with Protobuf (?P<with_proto_response>response)?)?\)")
    def step_impl(context, var_name, service_method, request_data, var_client, with_proto_response):
        var_name = StepTools.evaluate_variable_name(var_name)
        service_method = StepTools.evaluate_scenario_parameter(service_method)
        request_data = StepTools.evaluate_scenario_parameter(request_data)
        client = StepTools.evaluate_variable_value(var_client)
        
        service_name, method_name = service_method.rsplit('.', 1)
        res = client.request(service_name, method_name, request_data, raw_output=with_proto_response is not None)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @Step(r"(?P<var_name>{Variable}) = data for request (?P<service_method>{Str}) \(gRPC client: (?P<var_client>{Variable})(?P<as_proto> ; as Protobuf)?\)")
    def step_impl(context, var_name, service_method, var_client, as_proto):
        var_name = StepTools.evaluate_variable_name(var_name)
        service_method = StepTools.evaluate_scenario_parameter(service_method)
        client = StepTools.evaluate_variable_value(var_client)
        table = BehaveStepTools.get_step_table(context)
        
        service_name, method_name = service_method.rsplit('.', 1)
        res = client.build_request_data(service_name, method_name, params_table=table, as_proto=as_proto is not None)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @When(r"request (?P<service_method>{Str}) for all of queue (?P<var_queue>{Variable}) \(gRPC client: (?P<var_client>{Variable})(?: ; rate log period: (?P<rate_period_s>{Int}) s)?\)")
    def step_impl(context, service_method, var_queue, var_client, rate_period_s):
        service_method = StepTools.evaluate_scenario_parameter(service_method)
        q = StepTools.evaluate_variable_value(var_queue)
        q_name = StepTools.evaluate_variable_name(var_queue)
        client = StepTools.evaluate_variable_value(var_client)
        client_name = StepTools.evaluate_variable_name(var_client)
        rate_period_s = StepTools.evaluate_scenario_parameter(rate_period_s)
        
        counter = 0
        beg = Tools.timer_s()
        c_beg, t_beg = counter, beg
        log_counter = 0
        service_name, method_name = service_method.rsplit('.', 1)
        
        try:
            while True:
                # Get next message and publish
                request_data = q.get()
                if q.is_sentinel(request_data):
                    break
                counter += 1
                
                try:
                    # Note: according internal library implementation, less actions are done with raw_output=True
                    client.request(service_name, method_name, request_data, raw_output=True)
                except Exception as exc:
                    logger.warning(f"[Queue {q_name} -> Client {client_name}] Failed to request data {counter}: [{Typing.get_object_class_fullname(exc)}] {str(exc)}")
                    # logger.warning(f"[Queue {q_name} -> Publisher {pub_name}] Failed to publish message {counter}: [{Typing.get_object_class_fullname(exc)}] {Tools.represent_exception(exc)}")
                finally:
                    q.task_done()
                
                # Log rate if needed
                if rate_period_s and counter % 10 == 0:
                    t_end = Tools.timer_s()
                    if t_end > t_beg + rate_period_s:
                        c_end, s_end = counter, q.qsize()
                        rate = (c_end - c_beg) / (t_end - t_beg)
                        log_counter += 1
                        logger.print(f"[Queue {q_name} -> Client {client_name}] Rate: {int(rate)} msg/s ; Nb messages: {counter} ; Queue size: {s_end}")
                        c_beg, t_beg = c_end, t_end
                        
                # Yield processor in case of multithreading
                if counter % 10 == 0:
                    GlobalSystem.yield_processor()
        except queue.Empty:
            # Without block, or with timeout, this exception occurs when queue is empty
            pass
        
        if rate_period_s:
            end = Tools.timer_s()
            rate = counter / (end - beg)
            logger.print(f"[Queue {q_name} -> Client {client_name}] Mean rate: {int(rate)} msg/s ; Nb messages: {counter}")




    
