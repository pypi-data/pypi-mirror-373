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

import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.finders.tools.find_builder import FindBuilder
from holado_core.common.inspectors.tools.inspect_builder import InspectBuilder
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters
from holado_core.common.inspectors.tools.inspect_context import InspectContext
import abc
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class Inspector(object):
    """ Base class for inspector.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        # Modules management
        self.__module_name = module_name
        self.__inspector_by_module_name = {}
    
        # Builders to use
        self.__inspect_builder = None
        self.__find_builder = None
    
    
    def initialize(self):
        """
        Initialize inspector
        """
        self.__inspect_builder = self.default_inspect_builder()
        self.__find_builder = self.default_find_builder()
    
    @property
    def find_builder(self):
        """
        @return Find builder defined for this inspector
        """
        return self.__find_builder
    
    @property
    def inspect_builder(self):
        """
        @return Inspect builder defined for this inspector
        """
        return self.__inspect_builder
    
    @property
    def module_name(self):
        return self.__module_name
    
    @property
    def default_inspect_builder(self):
        """
        @return New default inspect builder for this inspector
        """
        res = InspectBuilder()
        res.initialize(self)
        return res
    
    @property
    def default_find_builder(self):
        """
        @return New default find builder for this inspector
        """
        return FindBuilder()
    
    def _get_inspector_for_module(self, name):
        """
        @param name Module name
        @return Module inspector
        """
        if name not in self.__inspector_by_module_name:
            self.__inspector_by_module_name[name] = self._initialize_module(name)
        return self.__inspector_by_module_name[name]
    
    def _initialize_module(self, name):
        """
        Initialize a new instance of given module name
        @param name Module name
        @return New module instance
        """
        raise TechnicalException(f"Unmanaged module '{name}'")
    
    def _get_finder_from_modules(self, method_name, method_args=None, method_kwargs=None, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None):
        method_args = [] if method_args is None else method_args
        method_kwargs = {} if method_kwargs is None else method_kwargs
        inspect_context = self.inspect_builder.context() if inspect_context is None else inspect_context
        inspect_parameters = self.inspect_builder.parameters() if inspect_parameters is None else inspect_parameters
        
        finders = []
        for module_name in self.inspect_builder.module_names:
            module = self._get_inspector_for_module(module_name)
            if hasattr(module, method_name):
                method = getattr(module, method_name)
                module_parameters = self.inspect_builder.get_parameters_for_module(module_name, inspect_parameters)
                try:
                    finder = method(*method_args, **method_kwargs, inspect_context=inspect_context, inspect_parameters=module_parameters)
                except FunctionalException as e:
                    raise TechnicalException("Unexpected exception") from e
                
                if finder is not None:
                    self._add_finder_to_list(finders, finder, inspect_context, inspect_parameters)
        
        return self._build_result_finder_from_list(finders=finders, inspect_context=inspect_context, inspect_parameters=inspect_parameters)
    
    def _remove_none_from_list(self, list_):
        if list_ is None:
            return
        
        i = 0
        while i < len(list_):
            if list_[i] is None:
                del list_[i]
            else:
                i += 1
    
    def _build_result_finder(self, finder, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Build result finder, considering given inspect parameters.
        @param finder Finder to return
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Result finder
        """
        if finder is None:
            if inspect_parameters.raise_no_such_finder:
                raise TechnicalException(f"No such finder")
            else:
                return None
        
        if inspect_context.finder_type is not None and inspect_context.finder_type not in inspect_parameters.finder_types:
            return None
        
        finder.inspector = self
        if self.__module_name is not None:
            finder.info.module_name = self.__module_name
        if inspect_context.finder_type is not None:
            finder.info.finder_type = inspect_context.finder_type
        
        return finder
    
    
    def _build_result_finder_from_list(self, finders, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None, element_description=None):
        """
        Build result finder with description copied from first finder in list
        @param finders Finders list
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @param element_description Element description
        @return Result finder
        """
        if element_description is None and finders is not None and len(finders) > 0:
            element_description = finders[0].element_description
        
        self._remove_none_from_list(finders)
    
        if finders is None or len(finders) == 0:
            if inspect_parameters.raise_no_such_finder:
                raise TechnicalException(f"No such finder")
            else:
                return None
        elif finders.size() == 1:
            return self._build_result_finder(finders[0], inspect_context, inspect_parameters)
        else:
            res = inspect_parameters.result_finder_type(element_description)
            for finder in finders:
                if hasattr(res, "set_next_finder"):
                    res.set_next_finder(finder)
                elif hasattr(res, "add_finder"):
                    res.add_finder(finder)
                else:
                    raise TechnicalException(f"Unmanaged result finder type '{Typing.get_object_class_fullname(res)}'")
            return self._build_result_finder(res, inspect_context, inspect_parameters)
        
    def _merge_result_finders(self, result_finders, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Merge result finders to first result finder
        @param result_finders Finders list
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Result finder
        """
        self._remove_none_from_list(result_finders)
        
        if result_finders is None or len(result_finders) == 0:
            if inspect_parameters.raise_no_such_finder:
                raise TechnicalException(f"No such finder")
            else:
                return None
        else:
            res = result_finders[0]
            for result_finder in result_finders[1:]:
                if hasattr(res, "set_next_finder"):
                    res.set_next_finder(result_finder)
                elif hasattr(res, "add_finder"):
                    res.add_finder(result_finder)
                else:
                    raise TechnicalException(f"Unmanaged result finder type '{Typing.get_object_class_fullname(res)}'")
            return res
    
    def _add_finder_to_list(self, finders, finder, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None):
        if finder is not None:
            finders.add(self._build_result_finder(finder, inspect_context, inspect_parameters))
    
    