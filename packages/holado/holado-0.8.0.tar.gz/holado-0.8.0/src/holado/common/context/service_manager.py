
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
from builtins import object

logger = None

def initialize_logger():
    global logger
    logger = logging.getLogger(__name__)


class ServiceManager(object):
    """
    Manage services in context types
    """
    
    def __init__(self, default_context_type):
        """Create service manager with given default context type.
        Default context type is usually SessionContext.
        """
        self.__default_context_type = default_context_type
        self.__services = {}
    
    @property
    def default_context_type(self):
        return self.__default_context_type
    
    def has_service(self, name):
        return name in self.__services
    
    def register_service_instance(self, name, service_instance, context, raise_if_service_exist=True, raise_if_object_exist=True):
        """
        Register a new service in a context with an existing instance.
        
        A property with service name is automatically added to context.
        
        Notes:
            It is possible to override an already registered service by passing "raise_if_service_exist=False, raise_if_object_exist=False".
            It is possible to replace an existing property by service property by passing "raise_if_service_exist=False".
        """
        from holado_core.common.exceptions.technical_exception import TechnicalException
        logger_ = logger if logger else logging
        
        logger_.trace(f"Registering service '{name}' in context {context}...")
        
        if raise_if_object_exist and context.has_object(name):
            raise TechnicalException(f"Context contains already an object '{name}'")
        if raise_if_service_exist and hasattr(context, name):
            raise TechnicalException(f"Context contains already an attribute '{name}'")
        
        # Register the service
        if context.has_object(name):
            context.remove_object(name)
        context.set_object(name, service_instance)
        
        # Add dedicated property in context
        self.add_context_property(name, type(context), raise_if_service_exist=False)
        
        logger_.debug(f"Registered service '{name}' instance {service_instance} in context {context}")
    
    def register_service_type(self, name, type_service, initialize_service=None, raise_if_exist=True, 
                              context_types=None, context_raise_if_service_exist=True, context_raise_if_object_exist=True, 
                              shortcut_in_types=None):
        """
        Register a new service type in service manager, and in defines context types.
        
        After this registration, it is possible to:
            - use the service by calling service manager property (the service instance is stored in service manager context)
            - register service in another context type with method register_service_type_in_context
        A property with service name is automatically added to context of given types.
        If shortcut_in_types is defined, a shortcut property is added in these types to access directly the context service
        (this feature currently works only for ProcessContext, ThreadContext, FeatureContext and ScenarioContext)
        
        When the context property is called the first time, the service is instantiated by calling "m = type_service()".
        After instantiation, it will be initialized by calling "initialize_service(m)".
        Initialization is typically used to inject dependencies, and process initialize actions needing these dependencies.
        
        Notes:
            If context_types=None, default context type is used
            Use lambda to define "type_service" when service "__init__" method has arguments.
            Use lambda to define "initialize_service" when service "initialize" method has arguments.
            It is possible to replace an existing attribute/property by service property by passing "raise_if_exist=False".
        """
        from holado_core.common.exceptions.technical_exception import TechnicalException
        logger_ = logger if logger else logging
        
        logger_.trace(f"Registering service '{name}'...")
        
        if shortcut_in_types and context_types and len(context_types) > 1:
            from holado_core.common.exceptions.functional_exception import FunctionalException
            raise FunctionalException(
                f"Impossible to define to which context type service the shortcuts must be linked to. \
                Please define only one context type when creating shortcuts")
        if raise_if_exist and name in self.__services:
            raise TechnicalException(f"A service '{name}' is already registered")
        if raise_if_exist and hasattr(self, name):
            raise TechnicalException(f"Service manager has already an attribute '{name}'")
        
        # Register the service
        self.__services[name] = (type_service, initialize_service, context_raise_if_service_exist, context_raise_if_object_exist)
        
        # Add dedicated property in service manager
        self.__add_service_manager_property(name)
        
        # Add property in context types
        _context_types = context_types
        if _context_types is None:
            _context_types = [self.__default_context_type]
        for context_type in _context_types:
            self.add_context_property(name, context_type, raise_if_exist)
        
        # Add shortcut property in given types
        if context_types and len(context_types) == 1:
            for type_ in shortcut_in_types:
                self.add_shortcut_property_to_context_service(name, type_, context_types[0], raise_if_exist)
        
        logger_.debug(f"Registered service '{name}'")
        # print(f"Registered service '{name}'")
    
    def register_service_type_in_context(self, name, context, raise_if_service_exist=None, raise_if_object_exist=None):
        logger_ = logger if logger else logging
        
        logger_.trace(f"Registering service '{name}' in context {context}...")
        
        self.__verify_object_doesnt_exist(name, context, raise_if_object_exist)
        
        if context.has_object(name):
            context.remove_object(name)
        self.add_context_property(name, type(context), raise_if_service_exist)
        
        logger_.trace(f"Registered service '{name}' in context {context}")
    
    def _get_context_service(self, name, context):
        """
        Get a service instance.
        If not already created, the instance is created according its registration and stored in context.
        """
        from holado_core.common.exceptions.technical_exception import TechnicalException
        logger_ = logger if logger else logging
        
        logger_.trace(f"Getting service '{name}' from {context}...")
        if not context.has_object(name):
            logger_.debug(f"Creating service '{name}'...")
            if name in self.__services:
                service = self.__services[name]
            else:
                raise TechnicalException(f"Unregistered service '{name}'")
            
            logger_.trace(f"Instantiating service '{name}'...")
            service_inst = service[0]()
            context.set_object(name, service_inst)
            logger_.debug(f"Service '{name}' is instantiated and stored in context {context}")
            
            if service[1] is not None:
                logger_.trace(f"Initializing service '{name}'...")
                service[1](service_inst)
            logger_.debug(f"Created service '{name}' for context {context}")
        return context.get_object(name)
    
    def add_context_property(self, name, context_type, raise_if_service_exist=None):
        # Note: next lines are commented, to allow to set again the service in context type
        # if raise_if_service_exist is None or raise_if_service_exist:
        #     self.__verify_service_doesnt_exist(name, context_type, raise_if_service_exist)
        if hasattr(context_type, name):
            logger.debug(f"Set again the property '{name}' in context type {context_type}")
        
        @property
        def context_service_property(self_context):
            return self._get_context_service(name, self_context)
        setattr(context_type, name, context_service_property)
        
        @property
        def context_has_service_property(self_context):
            return self_context.has_object(name)
        setattr(context_type, 'has_' + name, context_has_service_property)
    
    def add_shortcut_property_to_context_service(self, name, dst_type, context_type, raise_if_service_exist=None):
        from holado_multitask.multiprocessing.context.process_context import ProcessContext
        from holado.common.context.session_context import SessionContext
        from holado_multitask.multithreading.context.thread_context import ThreadContext
        from holado_test.common.context.feature_context import FeatureContext
        from holado_test.common.context.scenario_context import ScenarioContext
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        if issubclass(context_type, ProcessContext):
            self.__add_shortcut_property_to_context_service(name, dst_type, 
                                                            SessionContext.instance().multitask_manager.get_process_context,
                                                            raise_if_service_exist)
        elif issubclass(context_type, ThreadContext):
            self.__add_shortcut_property_to_context_service(name, dst_type, 
                                                            SessionContext.instance().multitask_manager.get_thread_context,
                                                            raise_if_service_exist)
        elif issubclass(context_type, FeatureContext):
            self.__add_shortcut_property_to_context_service(name, dst_type, 
                                                            SessionContext.instance().get_feature_context,
                                                            raise_if_service_exist)
        elif issubclass(context_type, ScenarioContext):
            self.__add_shortcut_property_to_context_service(name, dst_type, 
                                                            SessionContext.instance().get_scenario_context,
                                                            raise_if_service_exist)
        else:
            raise TechnicalException(f"Unmanaged context of type {context_type}")
    
    def __add_shortcut_property_to_context_service(self, name, dst_type, context_getter, raise_if_service_exist=None):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        self.__verify_service_doesnt_exist(name, dst_type, raise_if_service_exist)
        
        @property
        def context_service_property(self_context):  # @UnusedVariable
            context = context_getter()
            if not hasattr(context, name):
                raise TechnicalException(f"Service '{name}' doesn't exist in context {context}")
            return getattr(context, name)
        setattr(dst_type, name, context_service_property)
    
    def __add_service_manager_property(self, name):
        @property
        def manager_service_property(self_manager):
            return self_manager._get_context_service(name, self_manager.context)
        setattr(self.__class__, name, manager_service_property)
    
    def __verify_service_exist(self, name):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        if name not in self.__services:
            raise TechnicalException(f"Unregistered service '{name}'")
        
    def __verify_object_doesnt_exist(self, name, context, raise_if_object_exist=None):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        if raise_if_object_exist is None:
            self.__verify_service_exist(name)
            raise_if_object_exist = self.__services[name][3]
        
        if raise_if_object_exist and context.has_object(name):
            raise TechnicalException(f"Context contains already an object '{name}'")
    
    def __verify_service_doesnt_exist(self, name, obj_inst_or_type, raise_if_service_exist=None):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        if raise_if_service_exist is None:
            self.__verify_service_exist(name)
            raise_if_service_exist = self.__services[name][2]
            
        if raise_if_service_exist and hasattr(obj_inst_or_type, name):
            raise TechnicalException(f"Context contains already an attribute '{name}'")
        


