#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import copy
from holado_core.common.finders.else_finder import ElseFinder
from holado_core.common.exceptions.technical_exception import TechnicalException


class InspectParameters(object):
    """ Inspect parameters
    """
    
    __instance_default = None
    __instance_default_without_raise = None
    
    def __init__(self, raise_no_such_finder=True, finder_types=None, result_finder_type=None):
        """
        Constructor
        @param raise_no_such_finder If True, raise NoSuchElementException, else return None, when no element is found.
        @param finder_types Finder types to use
        @param result_finder_type Type of finder result when multiple finders are possible
        """
        self.raise_no_such_finder = raise_no_such_finder
        self.finder_types = [] if finder_types is None else finder_types
        self.result_finder_type = ElseFinder if result_finder_type is None else result_finder_type
    
    def get_module_parameters(self, inspect_parameters):
        """
        @param inspect_parameters Current inspect parameters
        @return Module inspect parameters updated with current inspect parameter
        """
        return self.with_result_finder_type(inspect_parameters.result_finder_type) \
            .with_raise(inspect_parameters.raise_no_such_finder)
    
    def set_raise(self, raise_exception):
        """
        @param raise_exception Whether raise exceptions or not
        """
        self.raise_no_such_finder = raise_exception
    
    def with_raise(self, raise_exception=True):
        """
        Note: if raise booleans are same, self instance is returned, else a new one is returned
        @param raise_exception Whether raise exceptions or not
        @return Same parameters but with raise
        """
        if self.raise_no_such_finder == raise_exception:
            return self
        else:
            res = copy.deepcopy(self)
            res.raise_no_such_finder = raise_exception
            return res
        
    def without_raise(self):
        """
        Note: if raise booleans are already False, self instance is returned, else a new one is returned
        @return Same parameters but without raise
        """
        return self.with_raise(False)
    
    def add_finder_type(self, finder_type):
        """
        @param finder_type Finder type to add
        """
        if finder_type in self.finder_types:
            raise TechnicalException(f"Finder type '{finder_type}' already exists")
        self.finder_types.append(finder_type)
    
    def add_finder_types(self, finder_types):
        """
        @param finder_types Finder types to add
        """
        for finder_type in finder_types:
            self.add_finder_type(finder_type)
    
    def remove_finder_type(self, finder_type):
        """
        @param finder_type Finder type to remove
        """
        if finder_type not in self.finder_types:
            raise TechnicalException(f"Finder type '{finder_type}' doesn't exist")
        self.finder_types.remove(finder_type)
    
    def remove_finder_types(self, finder_types):
        """
        @param finder_types Finder types to remove
        """
        for finder_type in finder_types:
            self.remove_finder_type(finder_type)
    
    def remove_all_finder_types(self):
        """
        Remove all finder types
        """
        self.finder_types.clear()
    
    def with_finder_type(self, finder_type):
        """
        Note: if wanted finder type is already set, this instance is returned, else a new one is returned
        @param finder_type Finder type
        @return Same parameters but with given finder type
        """
        if finder_type in self.finder_types:
            return self
        else:
            res = copy.deepcopy(self)
            res.finder_types.append(finder_type)
            return res
        
    def with_finder_types(self, finder_types):
        """
        Note: if wanted finder types are already set, this instance is returned, else a new one is returned
        @param finder_types Finder types
        @return Same parameters but with given finder types
        """
        res = self
        for finder_type in finder_types:
            res = res.with_find_type(finder_type)
        return res
        
    def set_result_finder_type(self, result_finder_type):
        """
        @param result_finder_type Result finder type
        """
        self.result_finder_type = result_finder_type
    
    def with_result_finder_type(self, result_finder_type):
        """
        Note: if given result finder class is already set, this instance is returned, else a new one is returned
        @param result_finder_type Result finder class
        @return Same parameters but with given result finder class
        """
        if self.result_finder_type == result_finder_type:
            return self
        else:
            res = copy.deepcopy(self)
            res.result_finder_type = result_finder_type
            return res
        
    @staticmethod
    def default(raise_exception=True):
        """
        @param raise_exception Whether raise exceptions or not
        @return Default inspect parameters with given raiseability
        """
        if raise_exception:
            return InspectParameters.default_with_raise()
        else:
            return InspectParameters.default_without_raise()
    
    @staticmethod
    def default_with_raise():
        """
        @return Default find parameters with raises
        """
        if InspectParameters.__instance_default is None:
            InspectParameters.__instance_default = InspectParameters()
        return InspectParameters.__instance_default
    
    @staticmethod
    def default_without_raise():
        """
        @return Default find parameters without any raise
        """
        if InspectParameters.__instance_default_without_raise is None:
            InspectParameters.__instance_default_without_raise = InspectParameters(raise_no_such_finder=False)
        return InspectParameters.__instance_default_without_raise
    

    
    
    