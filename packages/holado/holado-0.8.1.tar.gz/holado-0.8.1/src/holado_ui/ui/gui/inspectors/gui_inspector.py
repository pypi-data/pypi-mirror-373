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
from holado_ui.ui.inspectors.ui_inspector import UIInspector
import weakref
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_multitask.multithreading.reflection.sys import get_current_function_name
from holado_ui.ui.gui.windows.gui_window import GUIWindow
from holado_ui.ui.gui.handlers.zone_gui_context import ZoneGUIContext,\
    InformationTypes
import abc
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters
from holado_ui.ui.inspectors.tools.ui_inspect_context import UIInspectContext
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class GUIInspector(UIInspector):
    """ Base class for GUI inspector.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        super().__init__(module_name)
        
        self.__window_weakref = weakref.ref(None)
    
    def initialize(self, window:GUIWindow):
        if window is None:
            raise TechnicalException("Window is mandatory")
        super().initialize(window.driver)
        
        self.__window_weakref = weakref.ref(window)
        
    @property
    def window(self):
        res = self.__window_weakref()
        if res is None:
            raise TechnicalException("Window has been cleared")
        return res
        
    @UIInspector.inspect_builder.getter  # @UndefinedVariable
    def inspect_builder(self):
        """
        Prior inspect builder in window than in inspector
        @return Inspect builder instance
        """
        # Priors window one if existing 
        return self.get_inspect_builder(False)

    def get_inspect_builder(self, from_window):
        """
        Used internally to prior inspect builder in window than in inspector
        @param from_window If request comes from window
        @return Inspect builder instance
        """
        res = None
        
        if not from_window:
            res = self.window.get_inspect_builder(True)
        
        if res is None:
            res = super().inspect_builder
        
        return res

    @UIInspector.find_builder.getter  # @UndefinedVariable
    def find_builder(self):
        """
        Prior find builder in window than in inspector
        @return Find builder instance
        """
        # Priors window one if existing 
        return self.get_find_builder(False)

    def get_find_builder(self, from_window):
        """
        Used internally to prior find builder in window than in inspector
        @param from_window If request comes from window
        @return Find builder instance
        """
        res = None
        
        if not from_window:
            res = self.window.get_find_builder(True)
        
        if res is None:
            res = super().find_builder
        
        return res
    
    def _get_finder_ui_context_element(self, ui_context, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        if ui_context is None:
            return None
        
        if isinstance(ui_context, ZoneGUIContext):
            if ui_context.information_type == InformationTypes.Label:
                return self.get_finder_zone(ui_context.information, inspect_context, inspect_parameters)
            else:
                raise TechnicalException(f"Unmanaged zone information: type='{ui_context.information_type.name}'  information='{ui_context.information}'")
        else:
            raise TechnicalException(f"Unmanaged UI context type '{Typing.get_object_class_fullname(ui_context)}'")
    
    def get_finder_label(self, label, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param label Text
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for an element with given label text.
        """
        return self._get_finder_from_modules(get_current_function_name(), [label], None, inspect_context, inspect_parameters)

    def get_finder_popup(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder for a popup
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        return self._get_finder_from_modules(get_current_function_name(), None, None, inspect_context, inspect_parameters)
    
    def get_finder_popup_title(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder for a popup title
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        return self._get_finder_from_modules(get_current_function_name(), None, None, inspect_context, inspect_parameters)
    
    def get_finder_symbol(self, expected_symbol, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param expected_symbol Symbol as string
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for element corresponding to given symbol
        """
        return self._get_finder_from_modules(get_current_function_name(), [expected_symbol], None, inspect_context, inspect_parameters)
    
    def get_finder_table(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for a table element
        """
        return self._get_finder_from_modules(get_current_function_name(), None, None, inspect_context, inspect_parameters)
    
    def get_finder_table_row(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for a table row
        """
        return self._get_finder_from_modules(get_current_function_name(), None, None, inspect_context, inspect_parameters)
    
    def get_finder_table_cell(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for a table cell
        """
        return self._get_finder_from_modules(get_current_function_name(), None, None, inspect_context, inspect_parameters)
    
    def get_finder_text(self, text, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param text Text to find
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder of element with given text
        """
        return self._get_finder_from_modules(get_current_function_name(), [text], None, inspect_context, inspect_parameters)
    
    def get_finder_text_containing(self, text, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param text Text
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for element with content containing given text
        """
        return self._get_finder_from_modules(get_current_function_name(), [text], None, inspect_context, inspect_parameters)
    
    def get_finder_text_element(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder of element displaying text
        """
        return self._get_finder_from_modules(get_current_function_name(), None, None, inspect_context, inspect_parameters)
    
    def get_finder_zone(self, zone_name, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder of zone element for a given zone name.
        @param zone_name Zone name
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        return self._get_finder_from_modules(get_current_function_name(), [zone_name], None, inspect_context, inspect_parameters)
    
    
    
    