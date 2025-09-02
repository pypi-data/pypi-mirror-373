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
from holado_core.common.actors.actions import FindAction
from holado_ui.ui.gui.actors.gui_actor import GUIActor
from holado_ui_selenium.ui.gui.selenium.handlers.selenium_redo import SeleniumRedo
from holado_multitask.multithreading.reflection.sys import get_current_function_name
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class SeleniumActor(GUIActor):
    """ Selenium actor.
    """
    
    def __init__(self, module_name):
        super().__init__(module_name)
        
        self.__click_with_javascript = False
    
    @property
    def click_with_javascript(self):
        return self.__click_with_javascript
    
    @click_with_javascript.setter
    def click_with_javascript(self, with_javascript):
        """
        @param with_javascript True if click must be processed with Javascript rather than with Selenium
        """
        self.__click_with_javascript = with_javascript
    
    def click_on_element(self, element, scroll_by_x=0, scroll_by_y=0):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Clicking on element with scrollBy ({scroll_by_x}, {scroll_by_y})...")
        
        # Scroll to element, so that click action is visible on screenshot after an error
        if scroll_by_x != 0 or scroll_by_y != 0:
            self.internal_api.scroll_into_view(element, 0)
            self.internal_api.scroll_by(scroll_by_x, scroll_by_y, 100)
        else:
            self.internal_api.scroll_into_view(element)
        
        # Move mouse over
        if self.do_mouse_over_before_click:
            self.internal_api.moveMouseOver(element)
        
        # Click on element
        if self.click_with_javascript:
            self.internal_api.click_on_element_with_javascript(element)
        else:
            self.internal_api.click_on_element_with_selenium(element)
        
        self.internal_api.wait_until_window_is_loaded()
    
    def select_value(self, element, value):
        """
        Select a value in element
        @param element Element
        @param value Text
        @throws FunctionalException
        """
        finder_info = element.find_info.finder.info
        self._call_action_from_module(finder_info, get_current_function_name(), element, value)
    
    def write_to_element(self, element, value):
        if self.do_write_to_element_key_by_key:
            self.internal_api.write_to_element_key_by_key(element, value)
        else:
            self.internal_api.write_to_element_all_keys(element, value)
    
    def act_find_and_click_on(self, finder, find_type):
        def func(container, candidates, find_context, find_parameters):
            new_parameters = find_parameters.with_redo(False)
            
            class ActRedo(SeleniumRedo):
                def __init__(self_redo):  # @NoSelf
                    super().__init__(f"find and click on {finder.get_element_description()}", self.driver)
                    
                def _process(self_redo):  # @NoSelf
                    element = finder.find(find_type, container, candidates, find_context, new_parameters)
                    self.click_on_element(element, 0, self_redo.scroll_by_y)
                    return None
            
            redo = ActRedo()
            redo.with_iteration_on_scroll_by_y()
            redo.ignore_all(find_parameters.redo_ignored_exceptions)
            redo.execute()
            return None
        
        return FindAction(f"find {finder.get_element_description()} and click on", self.find_builder, func)
    
    def _get_redo(self, action, *args, **kwargs):
        """
        Redo an action
        @param action Action
        """
        class ActionRedo(SeleniumRedo):
            def __init__(self):
                super().__init__(f"redo {action.name}")
                
            def _process(self):
                return action.execute(*args, **kwargs)
            
            def _get_waited_description(self):
                return action.name
            
        return ActionRedo()
    
    
    
    
    
    