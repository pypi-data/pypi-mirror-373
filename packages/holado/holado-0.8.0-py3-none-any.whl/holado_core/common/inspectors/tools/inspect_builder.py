#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.inspectors.tools.inspect_context import InspectContext
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters


class InspectBuilder(object):
    """ Inspect builder, used to create new InspectContext and InspectParameters.
    
    It is used to store available modules and finder types with Inspector.default_inspect_builder,
    and activated modules and finder types with Inspector.inspect_builder (or for GUI, GUIWindow.inspect_builder).
    By default all available modules are activated  it can be modified by overriding inspect_builder property in a new sub-class.
    """
    
    def __init__(self):
        self.__inspector = None
        
        self.__module_names = []
        self.__inspect_builder_by_module_name = {}
        
        self.__default_context = None
        self.__default_parameters = None
    
    def initialize(self, inspector):
        """
        @param inspector Inspector
        """
        self.__inspector = inspector
    
    @property
    def inspector(self):
        return self.__inspector
        
    @property
    def module_names(self):
        """
        @return Module names in order of priority
        """
        return self.__module_names
    
    def add_module(self, module_name, module_inspect_builder = None):
        """
        Add given module in list of managed modules, with given inspect builder
        @param module_name Module name
        @param module_inspect_builder Inspect builder to use with given module
        """
        if module_name in self.__module_names:
            raise TechnicalException(f"Module '{module_name}' already exists")
            
        if module_inspect_builder is None:
            module_inspector = self.__inspector.get_inspector_for_module(module_name)
            module_inspect_builder = module_inspector.default_inspect_builder
            
        self.__module_names.append(module_name)
        self.__inspect_builder_by_module_name[module_name] = module_inspect_builder
    
    def remove_module(self, module_name):
        """
        Remove given module from managed modules
        @param module_name Module name
        """
        if module_name not in self.__module_names:
            raise TechnicalException(f"Module '{module_name}' doesn't exist")
        self.__module_names.remove(module_name)
        self.__inspect_builder_by_module_name.remove(module_name)
    
    def remove_all_modules(self):
        """
        Remove all modules from managed modules
        """
        self.__module_names.clear()
        self.__inspect_builder_by_module_name.clear()
    
    def get_inspect_builder_for_module(self, module_name):
        """
        @param module_name Module name
        @return Inspect builder for given module name
        """
        if module_name not in self.__inspect_builder_by_module_name:
            raise TechnicalException(f"Module '{module_name}' doesn't exist")
        return self.__inspect_builder_by_module_name[module_name]
    
    def get_parameters_for_module(self, module_name, inspect_parameters):
        """
        @param module_name Module name
        @param inspect_parameters Current inspect parameters
        @return Module inspect parameters updated with current inspect parameter
        """
        return self.get_inspect_builder_for_module(module_name).parameters().get_module_parameters(inspect_parameters)
    
    @property
    def default_context(self):
        """
        Get or create default context.
        This method is usually used to build the default context.
        @return Default inspect context
        """
        if self.__default_context is None:
            self.__default_context = self._initialize_default_context()
        return self.__default_context
    
    def _initialize_default_context(self):
        return InspectContext.default()
        
    def context(self, inspect_context=None):
        """
        @param inspect_context Inspect context to update
        @return Updated inspect context
        """
        res = inspect_context
        if res is None:
            res = self.default_context
        return res
    
    @property
    def default_parameters(self):
        """
        Get or create default parameters.
        This method is usually used to build the default parameters.
        @return Default inspect parameters
        """
        if self.__default_parameters is None:
            self.__default_parameters = self.initialize_default_parameters()
        return self.__default_parameters
    
    def initialize_default_parameters(self):
        return InspectParameters.default_with_raise()
        
    def parameters(self, inspect_parameters=None, raise_exception=None):
        """
        @param inspect_parameters Inspect parameters to update
        @param raise_exception Whether raise exceptions or not
        @return Find parameters
        """
        res = inspect_parameters
        if res is None:
            res = self.default_parameters
            
        if raise_exception is not None:
            res = res.with_raise(raise_exception)
            
        return res
    
    def parameters_with_raise(self):
        """
        @return Default inspect parameters with raises
        """
        return self.parameters(True)
    
    def parameters_without_raise(self):
        """
        @return Default inspect parameters without any raise
        """
        return self.parameters(False)
    
    
    
    