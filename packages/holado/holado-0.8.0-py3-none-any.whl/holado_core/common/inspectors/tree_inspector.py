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
from holado_core.common.finders.then_finder import ThenFinder
from holado_core.common.inspectors.element_inspector import ElementInspector
from holado_core.common.finders.after_in_tree_finder import AfterInTreeFinder
import abc
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters
from holado_core.common.inspectors.tools.inspect_context import InspectContext

logger = logging.getLogger(__name__)



class TreeInspector(ElementInspector):
    """ Base class for inspector on tree elements.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        super().__init__(module_name)
    
    """
    Find element with given finder, after element in tree found with given finder
    @param finder_first Finder for first element
    @param finder_after_first Finder for element to find after first one
    @param inspect_context Inspect context
    @param inspect_parameters Inspect parameters
    @return Finder
    """
    def get_finder_element_after(self, finder_first, finder_after_first, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None):
        description = f"{finder_after_first.element_description} after {finder_first.element_description} in tree"
        res = ThenFinder(description)
        
        # Find first element
        res.set_next_finder(finder_first)
        
        # Then find in tree
        res.set_next_finder( AfterInTreeFinder(finder_after_first, description) )
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_parent(self, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder for parent
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        raise NotImplementedError
    
    def get_finder_children(self, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder for children
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        raise NotImplementedError
    
    
    
    