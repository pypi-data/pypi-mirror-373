
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
from holado_core.common.exceptions.technical_exception import TechnicalException, TimeoutTechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_core.common.tools.tools import Tools
import time
from holado.holado_config import Config
from holado.common.handlers.object import Object
from holado.common.handlers.undefined import undefined_argument, undefined_value

logger = logging.getLogger(__name__)

try:
    import grpc_requests
    import grpc
    with_grpc_requests = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"GRpcClient is not available. Initialization failed on error: {exc}")
    with_grpc_requests = False

# Activation of logs in gRPC library (activated logs are thrown in stdout, it doesn't follow logging settings)
# os.environ["GRPC_VERBOSITY"] = "DEBUG"
# os.environ["GRPC_TRACE"] = "http"
# os.environ["GRPC_TRACE"] = "all"


class GRpcClient(Object):
    """
    gRPC client
    
    It is implemented internally with grpc_requests, that manages reflection clients and stub clients.
    """
    
    @classmethod
    def is_available(cls):
        return with_grpc_requests
    
    if with_grpc_requests:
        def __init__(self, name, endpoint, **kwargs):
            super().__init__(name)
            self.__endpoint = endpoint
            self.__kwargs = kwargs
            self.__client = grpc_requests.client.get_by_endpoint(endpoint, **kwargs)
            
            self.__func_grpc_services = None
            self.__func_protobuf_converter = None
            self.__func_protobuf_messages = None
            
            self.__request_log_level = Config.log_level_grpc_request
        
        def initialize(self, func_grpc_services, func_protobuf_converter, func_protobuf_messages):
            self.__func_grpc_services = func_grpc_services
            self.__func_protobuf_converter = func_protobuf_converter
            self.__func_protobuf_messages = func_protobuf_messages
            
        @property
        def __grpc_services(self):
            return self.__func_grpc_services()
    
        @property
        def __protobuf_converter(self):
            return self.__func_protobuf_converter()
    
        @property
        def __protobuf_messages(self):
            return self.__func_protobuf_messages()
        
        @property    
        def internal_client(self) -> grpc_requests.client.Client:
            return self.__client
        
        @property
        def request_log_level(self):
            return self.__request_log_level
        
        @request_log_level.setter
        def request_log_level(self, log_level):
            self.__request_log_level = log_level
        
        def request(self, service, method, request, raw_output=False, result_on_statuses=undefined_argument, **kwargs):
            """
            :param request: request data in json or proto format
            :param raw_output: if method should return a proto object or a json oject (default: False)
            :param kwargs: other arguments for underlying grpc_requests method, or further underlying grpc method (ex: 'timeout')
            :returns: if raw_output==True, returns a proto object, else returns a json object with proto data
            """
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Requesting {service}.{method} with data [{request}] (raw_output: {raw_output} ; kwargs:{kwargs})")
            res = undefined_value
            
            # Set a default timeout
            raise_on_timeout = False
            if kwargs is None:
                kwargs = {}
            if 'timeout' not in kwargs:
                kwargs['timeout'] = Config.join_timeout_seconds
                raise_on_timeout = True
            timeout = kwargs['timeout'] if 'timeout' in kwargs else None
            
            success = False
            last_exc = None
            for try_nb in range(1,4):
                try:
                    # Ask always raw_output=True, so that we get a Protobuf instance, and then conversion is done if needed
                    res_proto = self.internal_client.request(service, method, request, raw_output=True, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    exc_str = str(exc)
                    
                    # Manage result on statuses
                    if result_on_statuses is not undefined_argument:
                        for status, status_result in result_on_statuses.items():
                            if f"status = StatusCode.{status.name}" in exc_str:
                                res = status_result
                                break
                        if res is not undefined_value:
                            success = True
                            break
                    
                    msg_list = [
                        f"Request failed (try {try_nb}):",
                        f"    method: {service}.{method}",
                        f"    data:",
                        Tools.indent_string(8, str(request)),
                        f"    raw_output: {raw_output}",
                        f"    kwargs: {kwargs}",
                        f"    error:",
                        Tools.indent_string(8, exc_str) ]
                    exc_msg = "\n".join(msg_list)
                    if "status = StatusCode.UNAVAILABLE" in exc_str:
                        logger.warning("Service temporarily unavailable:\n" + exc_msg)
                        time.sleep(1)
                        continue
                    elif "status = StatusCode.DEADLINE_EXCEEDED" in exc_str:
                        if raise_on_timeout:
                            raise TimeoutTechnicalException(exc_msg)
                        else:
                            logger.warning(f"Timeout ({timeout} s) occured while requesting:\n" + exc_msg)
                            time.sleep(1)
                            continue
                    elif "status = " in exc_str:
                        raise FunctionalException(exc_msg) from exc
                    else:
                        raise TechnicalException(exc_msg) from exc
                else:
                    success = True
                    break
            
            # If still in error after all tries, raise an exception with last exception message
            if not success:
                if "status = " in exc_msg:
                    raise FunctionalException(exc_msg) from last_exc
                else:
                    raise TechnicalException(exc_msg) from last_exc
                
            # Manage result conversion if needed
            # Note: this step is done manually since grpc_requests has some limitations when raw_output=False:
            #     - Field with default values are not set in json result
            #     - Some field types are badly managed (ex: uint64 fields appear as string in json)
            if res is undefined_value:
                if raw_output == True:
                    if isinstance(res_proto, grpc._channel._MultiThreadedRendezvous):
                        res = list(res_proto)
                    else:
                        res = res_proto
                else:
                    if isinstance(res_proto, grpc._channel._MultiThreadedRendezvous):
                        res = [self.__protobuf_converter.convert_protobuf_object_to_json_object(cur_res) for cur_res in res_proto]
                    else:
                        res = self.__protobuf_converter.convert_protobuf_object_to_json_object(res_proto)
            if Tools.do_log(logger, self.request_log_level):
                logger.log(self.request_log_level, f"Request {service}.{method} with data [{request}] (raw_output: {raw_output} ; kwargs:{kwargs})  => {res}")
            return res
                
        def get_request_data_type_fullname(self, service, method):
            method_descriptor = self.__grpc_services.get_method_descriptor(service, method)
            return method_descriptor.input_type.full_name
            
        def build_request_data(self, service, method, params_table=None, params_dict=None, as_proto=False):
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Building request data for service method '{service}.{method}'")
            if as_proto is not None and as_proto:
                method_descriptor = self.__grpc_services.get_method_descriptor(service, method)
                res = self.__protobuf_messages.new_message(method_descriptor.input_type.full_name, fields_table=params_table, fields_dict=params_dict)
            else:
                if params_table is not None:
                    res = ValueTableConverter.convert_name_value_table_2_json_object(params_table)
                elif params_dict is not None:
                    res = params_dict
                else:
                    res = {}
            
            return res
        
        
        