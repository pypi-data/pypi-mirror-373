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
from holado_core.common.inspectors.tree_inspector import TreeInspector
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters
from holado_ui.ui.handlers.ui_context import UIContext
from holado_ui.ui.inspectors.tools.ui_inspect_context import UIInspectContext
import abc

logger = logging.getLogger(__name__)



class UIInspector(TreeInspector):
    """ Base class for inspector on UI elements.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        super().__init__(module_name)
        
        self.__driver = None
    
    def initialize(self, driver):
        self.__driver = driver
        
    @property
    def driver(self):
        return self.__driver
        
    @property
    def internal_driver(self):
        return self.driver.internal_driver
    
    def _build_result_finder(self, finder, inspect_context, inspect_parameters):
        ui_context = inspect_context.ui_context()
        if ui_context is not None:
            return self.get_finder_element_in_ui_context(ui_context, finder, inspect_context.without_ui_context(), inspect_parameters)
        else:
            return super()._build_result_finder(finder, inspect_context, inspect_parameters)

    def get_finder_ui_context(self, ui_context:UIContext, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder of UI context.
        @param ui_context Context
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        if ui_context is None:
            return self._build_result_finder(None, inspect_context, inspect_parameters)
        else:
            return self.get_finder_element_in_ui_context(ui_context.get_previous_context(),
                self._get_finder_ui_context_element(ui_context, inspect_context.without_ui_context(), inspect_parameters), 
                inspect_context, inspect_parameters)
    
    def _get_finder_ui_context_element(self, ui_context:UIContext, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        
        @param context UI context
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder of given UI context, without consideration of previous UI context
        """
        raise NotImplementedError

    def get_finder_element_in_ui_context(self, ui_context:UIContext, finder_element, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Find element with given finder, in given context
        @param ui_context Context
        @param finder_element Finder for element to find
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        return self.get_finder_element_in(
            self.get_finder_ui_context(ui_context, inspect_context.without_ui_context(), inspect_parameters), 
            finder_element, inspect_context, inspect_parameters)
    
    
    
    