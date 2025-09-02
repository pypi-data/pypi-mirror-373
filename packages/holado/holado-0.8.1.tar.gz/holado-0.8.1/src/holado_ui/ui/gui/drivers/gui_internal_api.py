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
from holado_ui.ui.drivers.ui_internal_api import UIInternalAPI
from holado_core.common.finders.tools.find_parameters import FindParameters
from datetime import datetime
import os

logger = logging.getLogger(__name__)



class GUIInternalAPI(UIInternalAPI):
    """ Base class for GUI internal API.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, driver):
        super().__init__(driver)
        
        self.__activate_wait_until_window_is_loaded = True
    
    @property
    def activate_wait_until_window_is_loaded(self):
        return self.__activate_wait_until_window_is_loaded
    
    @activate_wait_until_window_is_loaded.setter
    def activate_wait_until_window_is_loaded(self, activate_wait_until_window_is_loaded):
        """
        @param activate_wait_until_window_is_loaded True/false for respectively activation/deactivation of wait until window is loaded
        """
        self.__activate_wait_until_window_is_loaded = activate_wait_until_window_is_loaded
    
    def get_element_coordinates(self, element):
        """
        @param element Element
        @return Element coordinates
        """
        raise NotImplementedError

    def get_element_description(self, element, with_text=True):
        """
        @param element Element
        @param with_text If true add the text of the element
        @return Element description
        """
        raise NotImplementedError
    
    def get_element_location(self, element):
        """
        @param element Element
        @return Element location
        """
        raise NotImplementedError
    
    def get_element_rectangle(self, element):
        """
        @param element Element
        @return Element rectangle
        """
        raise NotImplementedError
    
    def get_element_size(self, element):
        """
        @param element Element
        @return Element size
        """
        raise NotImplementedError

    def get_element_text(self, element):
        """
        @param element Element
        @return Text of given element
        """
        find_context = self.driver.find_builder.context()
        find_parameters = FindParameters.default_with_raise().with_visibility(True)
        return self._get_element_text(element, find_context, find_parameters)

    def _get_element_text(self, element, find_context, find_parameters):
        """
        @param element Element
        @param find_context Find context
        @param find_parameters Find parameters
        @return Text of given element
        """
        raise NotImplementedError
    
    def clear_element(self, element):
        """
        Clear content of editable element
        @param element Element
        """
        raise NotImplementedError
    
    def make_screenshot(self, destination_path, context_description):
        """
        Make a screenshot of current window.
        @param destination_path Destination path
        @param context_description Context description that will be inserted in file names
        """
        # Create file name
        date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
        file_name = f"{date_str}-{context_description}-screenshot.png"
        screenshot_path = os.path.join(destination_path, file_name)
        
        # Take screenshot
        self.get_screenshot_file(screenshot_path)
    
    def get_screenshot_file(self, screenshot_path, element=None, margin_around_element=0):
        """
        Make a screenshot and return image file instance.
        @param screenshot_path Screenshot path
        @param element Element to screenshot (if not defined, a screenshot of whole page is done)
        @param margin_around_element Size of the marge around element to include in screenshot  
        @return File containing screenshot
        """
        raise NotImplementedError
    
    def get_screenshot_file_in_destination(self, destination_path, element=None, margin_around_element=0):
        """
        Make a screenshot of given element and return image file instance.
        @param destination_path Destination path
        @param element Element to screenshot (if not defined, a screenshot of whole page is done)
        @param margin_around_element Size of the marge around element to include in screenshot  
        @return File containing screenshot
        """
        # Format now datetime
        date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
        if element is not None:
            file_name = f"{date_str}-element-margin{margin_around_element}.png"
        else:
            file_name = f"{date_str}-page.png"
        screenshot_path = os.path.join(destination_path, file_name)
        
        return self.get_screenshot_file(screenshot_path, element, margin_around_element)
    
    def is_displayed(self, element):
        """
        @param element An element.
        @return True if given element is displayed.
        """
        raise NotImplementedError
    
    def is_visible(self, element, find_context, find_parameters):
        """
        Return if element visibility corresponds to the one defined in find parameters.
        Note: If find_parameters.visibility is null, always return true
        @param element An element.
        @param find_context Find context
        @param find_parameters Find parameters
        @return True if given element is visible.
        """
        if find_parameters.visibility is None:
            return True
        
        return (find_parameters.visibility == self.is_displayed(element))
    
    def move_mouse_over(self, element):
        """
        Move mouse over a given element
        @param element Element 
        """
        raise NotImplementedError

    def scroll_by(self, x, y, sleep_after_scroll_ms=100):
        """
        Scroll by given number of pixels
        @param x X number of pixels
        @param y Y number of pixels
        @param sleep_after_scroll_ms Number of milliseconds to wait after scroll
        """
        raise NotImplementedError
    
    def scroll_into_view(self, element, sleep_after_scroll_ms=100):
        """
        Scroll so that given element is entirely visible
        @param element Element to view
        @param sleep_after_scroll_ms Number of milliseconds to wait after scroll
        """
        raise NotImplementedError
    
    def scroll_to(self, x, y, sleep_after_scroll_ms=100):
        """
        Scroll to given coordinates
        @param x X coordinate (pixel number) in top left corner
        @param y y coordinate (pixel number) in top left corner
        @param sleep_after_scroll_ms Number of milliseconds to wait after scroll
        """
        raise NotImplementedError
    
    def wait_until_window_is_loaded(self, timeout_seconds=None):
        """
        Wait until window is loaded with default timeout
        @param timeout_seconds Timeout in seconds
        """
        raise NotImplementedError
    
    
    
    
    