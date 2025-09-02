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

import logging
import abc
from holado_ui.ui.drivers.ui_driver import UIDriver
from queue import LifoQueue
from holado_core.common.exceptions.technical_exception import TechnicalException
import re
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class GUIDriver(UIDriver):
    """ Base class for GUI drivers.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name=None):
        super().__init__(name or "GUIDriver")
        
        # Information on opened pages
        self.__window_id_by_visible_order = LifoQueue()
        self.__window_info_by_id = {}
        
        # Settings used to implement the right GUIWindow instance when a new window is opened
        self.__window_type_by_name_pattern = {}
        self.__default_window_type = None
    
    def _close_driver(self):
        # Close each opened page before 
        while not self.__window_id_by_visible_order.empty():
            self._close_current_window()
    
    def _close_current_window(self):
        raise NotImplementedError

    def _has_window_info(self, window_id):
        return window_id in self.__window_info_by_id
    
    def _add_window_info(self, window_id, window_info):
        self.__window_info_by_id[window_id] = window_info
    
    def _get_window_info(self, window_id):
        res = self.__window_info_by_id[window_id]
        if res is None:
            msg = f"No descriptor exists for ID '{window_id}'. Currently known IDs: {list(self.__window_info_by_id.keys())}"
            raise TechnicalException(msg)
        return res
    
    def _update_window_info(self, window_id, window):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Updated window info: ID={window_id} ; window type={Typing.get_object_class_fullname(window)}")
        window_info = self._get_window_info(window_id)
        window_info.window = window
    
    def _clear_window_info(self):
        self.__window_id_by_visible_order.clear()
        self.__window_info_by_id.clear()
    
    @property
    def default_window_type(self):
        return self.__default_window_type
    
    @default_window_type.setter
    def default_window_type(self, default_type):
        """
        Set the type to use by default when a new window is opened.
        @param default_type Default window type
        """
        self.__default_window_type = default_type
    
    def _get_window_type(self, window_name):
        res = None
        
        # Get window type by name
        for name_pattern in self.__window_type_by_name_pattern:
            m = re.compile(name_pattern).match(window_name)
            if m:
                res = self.__window_type_by_name_pattern[name_pattern]
                break
        
        # Else get default window type
        if res is None:
            res = self.default_window_type
        
        return res

    def add_window_type(self, window_name_pattern, window_type):
        """
        Set the type to use for given window name pattern.
        Note: window name patterns are ordered  thus, if two patterns match a window name, the first added will be used
        @param window_namePattern Pattern of window name
        @param window_type Window type
        """
        self.__window_type_by_name_pattern[window_name_pattern] = window_type
    
    def _has_current_window(self):
        return not self.__window_id_by_visible_order.empty()
    
    def _nb_windows(self):
        return self.__window_id_by_visible_order.qsize()
    
    def _get_all_window_ids(self):
        return list(self.__window_id_by_visible_order.queue)
    
    def _get_current_window_id(self):
        if self.__window_id_by_visible_order.empty():
            raise FunctionalException("No window is currently opened.")
        return self.__window_id_by_visible_order.queue[-1]
    
    def _pop_current_window_id(self):
        if self.__window_id_by_visible_order.empty():
            raise FunctionalException("No window is currently opened.")
        return self.__window_id_by_visible_order.get()
    
    def _push_current_window_id(self, window_id):
        if self._has_window_info(window_id):
            logger.warning(f"Repush window {window_id} on top")
        self.__window_id_by_visible_order.put(window_id)
    
    @property
    def current_window(self):
        """
        @return current window.
        """
        return self._get_window_info(self._get_current_window_id()).window
    
    def update_current_window(self, window_name, window_id):
        """
        Update current window instance after a new window has been opened
        @param window_name Window name
        @param window_id Window ID (for verification)
        """
        # Verify that window ID is current window
        if self._get_current_window_id() != window_id:
            raise FunctionalException("A new window was opened.")
        
        # Find type specific to displayed window
        window = self.new_window_for_name(window_name)
        self._update_window_info(self.get_current_window_id(), window)
    
    def update_current_window_with_default(self, window_id):
        """
        Update current window instance after a new window has been opened, with default window
        @param window_id Window ID (for verification)
        """
        # Verify that window ID is current window
        if self.get_current_window_id() != window_id:
            raise FunctionalException("A new window was opened.")

        # Find type specific to displayed window
        window = self.new_default_window()
        self._update_window_info(self.get_current_window_id(), window)
    
    def new_default_window(self):
        """
        @return New instance of default window
        """
        specific_type = self.default_window_type
        if specific_type is not None:
            return self.__new_window_for_type(specific_type)
        else:
            raise TechnicalException("Unable to determine default window type")
        
    def _new_window_for_name(self, window_name):
        specific_type = self._get_window_type(window_name)
        if specific_type is not None:
            return self.__new_window_for_type(specific_type)
        else:
            raise TechnicalException(f"Unable to determine window type for window name '{window_name}'")
        
    def __new_window_for_type(self, specific_type):
        if specific_type is None:
            raise TechnicalException("Type is None")

        res = specific_type()
        res.initialize(self)

        return res
    
    def make_screenshots_for_debug(self, destination_path, context_description):
        """
        Make screenshots for debug.
        @param destination_path Destination path
        @param context_description Context description that will be inserted in file names
        """
        raise NotImplementedError
    
    