
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
import os
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
import sys
import importlib
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)

try:
    import grpc_requests  # @UnusedImport
    with_grpc_requests = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"GRpcServices is not available. Initialization failed on error: {exc}")
    with_grpc_requests = False


class GRpcServices(object):
    @classmethod
    def is_available(cls):
        return with_grpc_requests
    
    def __init__(self): 
        self.__service_descriptors_by_fullname = {}
        self.__services_by_fullname = {}
    
    def import_all_compiled_proto(self, compiled_proto_path, raise_if_not_exist=True):
        """Register a folder path containing compiled proto files. Usually it corresponds to the parameter '--python_out' passed to proto compiler."""
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[GRpcServices] Importing all compiled proto in '{compiled_proto_path}'...")
        if os.path.exists(compiled_proto_path):
            if os.path.isfile(compiled_proto_path):
                proto_path = os.path.dirname(compiled_proto_path)
                sys.path.append(proto_path)
                self.__import_compiled_proto(proto_path, compiled_proto_path)
            elif os.path.isdir(compiled_proto_path):
                sys.path.append(compiled_proto_path)
                self.__import_all_compiled_proto(compiled_proto_path, "")
            else:
                raise TechnicalException(f"Unmanaged path '{proto_path}'")
        else:
            msg = f"Path '{compiled_proto_path}' doesn't exist"
            if raise_if_not_exist:
                raise TechnicalException(msg)
            else:
                logger.warning(msg)
    
    def __import_all_compiled_proto(self, compiled_proto_path, package_name):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"[GRpcServices] Importing all compiled proto in '{compiled_proto_path}' (package: '{package_name}')...")
        if os.path.isdir(compiled_proto_path):
            lp = os.listdir(compiled_proto_path)
            for cp in lp:
                if not cp.startswith((".", "_")):
                    cur_proto_path = os.path.join(compiled_proto_path, cp)
                    
                    if os.path.isfile(cur_proto_path):
                        self.__import_compiled_proto(cur_proto_path, package_name)
                    elif os.path.isdir(cur_proto_path):
                        cur_package_name = f"{package_name}.{cp}" if package_name is not None and len(package_name) > 0 else cp
                        self.__import_all_compiled_proto(cur_proto_path, cur_package_name)
                    else:
                        raise TechnicalException(f"Unmanaged path '{cur_proto_path}'")
        else:
            raise TechnicalException(f"Unmanaged path '{compiled_proto_path}'")
    
    def __import_compiled_proto(self, compiled_proto_file_path, package_name):
        if not os.path.isfile(compiled_proto_file_path):
            raise TechnicalException(f"Compiled proto path '{compiled_proto_file_path}' is not a file")
        if not compiled_proto_file_path.endswith("_pb2.py"):
            return

        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"[GRpcServices] Importing compiled proto file '{compiled_proto_file_path}' (package: '{package_name}')...")
        
        filename = os.path.splitext(os.path.basename(compiled_proto_file_path))[0]
        module_name = f"{package_name}.{filename}" if package_name is not None and len(package_name) > 0 else filename
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"[GRpcServices] Importing module '{module_name}'")
        module = importlib.import_module(module_name)
        
        if hasattr(module.DESCRIPTOR, 'services_by_name'):
            service_package = module.DESCRIPTOR.package if hasattr(module.DESCRIPTOR, 'package') else package_name
            
            module_grpc_name = module_name + '_grpc'
            module_spec = importlib.util.find_spec(module_grpc_name)
            if module_spec is not None:
                module_grpc = importlib.import_module(module_grpc_name)
            
            for s_name in module.DESCRIPTOR.services_by_name:
                s_fullname = f"{service_package}.{s_name}" if service_package is not None and len(service_package) > 0 else s_name
                self.__service_descriptors_by_fullname[s_fullname] = module.DESCRIPTOR.services_by_name[s_name]
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"[GRpcServices] New managed service descriptor '{s_fullname}'")
                if module_grpc is not None:
                    self.__services_by_fullname[s_fullname] = getattr(module_grpc, s_name)
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"[GRpcServices] New managed service '{s_fullname}' (type: '{self.__services_by_fullname[s_fullname].__qualname__}')")

    def has_service(self, service_fullname):
        """Return if service fullname is known."""
        return service_fullname in self.__services_by_fullname

    def get_service(self, service_fullname):
        """Return service for given service fullname."""
        if self.has_service(service_fullname):
            return self.__services_by_fullname[service_fullname]
        else:
            raise FunctionalException(f"Unknown service '{service_fullname}' (existing services: {list(self.__services_by_fullname.keys())})")

    def has_service_descriptor(self, service_fullname):
        """Return if service descriptor fullname is known."""
        return service_fullname in self.__service_descriptors_by_fullname

    def get_service_descriptor(self, service_fullname):
        """Return service descriptor for given service fullname."""
        if self.has_service_descriptor(service_fullname):
            return self.__service_descriptors_by_fullname[service_fullname]
        else:
            raise FunctionalException(f"Unknown service '{service_fullname}' (existing services: {list(self.__service_descriptors_by_fullname.keys())})")

    def has_method_descriptor(self, service_fullname, method_name):
        """Return if method exists in service descriptor fullname."""
        service_descriptor = self.get_service_descriptor(service_fullname)
        return method_name in service_descriptor.methods_by_name

    def get_method_descriptor(self, service_fullname, method_name):
        """Return service method descriptor for given service fullname and method name."""
        # Get service descriptor to verify in same type that it exists
        service_descriptor = self.get_service_descriptor(service_fullname)
        
        # Get method descriptor
        if method_name in service_descriptor.methods_by_name:
            return service_descriptor.methods_by_name[method_name]
        else:
            raise FunctionalException(f"Unknown method '{method_name}' in service '{service_fullname}' (existing methods in service: {list(service_descriptor.methods_by_name.keys())})")
    
    def get_all_service_fullnames(self):
        return tuple(self.__service_descriptors_by_fullname.keys())
    
    def get_all_method_fullnames(self):
        res = []
        for service_fullname in self.get_all_service_fullnames():
            service_descriptor = self.get_service_descriptor(service_fullname)
            for method_name in service_descriptor.methods_by_name:
                res.append(f"{service_fullname}.{method_name}")
        return res
    
    
        