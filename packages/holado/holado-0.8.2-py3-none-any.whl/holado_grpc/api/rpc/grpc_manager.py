
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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado.common.context.session_context import SessionContext
from holado_grpc.api.rpc.grpc_client import GRpcClient


logger = logging.getLogger(__name__)

# Activation of logs in gRPC library (activated logs are thrown in stdout, it doesn't follow logging settings)
# os.environ["GRPC_VERBOSITY"] = "DEBUG"
# os.environ["GRPC_TRACE"] = "http"
# os.environ["GRPC_TRACE"] = "all"


class GRpcManager(object):
    """
    Manage gRPC features, agnostic to internal gRPC library.
    """
    
    def __init__(self):
        self.__func_grpc_services = None
        self.__func_protobuf_converter = None
        self.__func_protobuf_messages = None
    
    def initialize(self, func_grpc_services, func_protobuf_converter, func_protobuf_messages):
        self.__func_grpc_services = func_grpc_services
        self.__func_protobuf_converter = func_protobuf_converter
        self.__func_protobuf_messages = func_protobuf_messages
        
    @property
    def __grpc_services(self):
        return self.__func_grpc_services()
        
    def new_client(self, name, **kwargs):
        if name is None:
            name = "Undefined"
        endpoint = kwargs.pop("endpoint")
        
        service_fullname = kwargs.pop("service") if "service" in kwargs else None
        services_fullnames = kwargs.pop("services") if "services" in kwargs else None
        if service_fullname is not None:
            service_descriptors = [self.__grpc_services.get_service_descriptor(service_fullname)]
        elif services_fullnames is not None:
            service_descriptors = [self.__grpc_services.get_service_descriptor(sfn) for sfn in services_fullnames]
        else:
            service_descriptors = None
    
        # Proxy settings
        #kwargs['channel_options'] = (('grpc.enable_http_proxy', 0),('grpc.enable_https_proxy', 0),)
        
        if service_descriptors is not None:
            res = GRpcClient(name, endpoint=endpoint, service_descriptors=service_descriptors, **kwargs)
        else:
            import grpc
            try:
                res = GRpcClient(name, endpoint=endpoint, **kwargs)
            except grpc.RpcError as exc:
                if hasattr(exc, "details"):
                    details = str(exc.details)
                    if "status = StatusCode.UNIMPLEMENTED" in details and 'details = "Method not found: grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo"' in details:
                        raise FunctionalException(f"Endpoint '{endpoint}' doesn't manage reflection, thus step parameter 'service' or 'services' has to be specified")
                raise exc
        
        res.initialize(self.__func_grpc_services, self.__func_protobuf_converter, self.__func_protobuf_messages)
        
        return res
        
            