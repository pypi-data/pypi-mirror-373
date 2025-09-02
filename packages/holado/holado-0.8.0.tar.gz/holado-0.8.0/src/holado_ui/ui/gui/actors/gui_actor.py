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
import abc
import weakref
from holado_ui.ui.actors.ui_actor import UIActor
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.actors.actions import FindAction, Action
from holado_python.common.tools.comparators.string_comparator import StringComparator
from holado_core.common.actors.find_actor import FindActor

logger = logging.getLogger(__name__)



class GUIActor(UIActor):
    """ Base class for GUI actor dedicated to a GUI window.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        super().__init__(module_name)
        self.__window_weakref = None
        
        # Define some behaviors
        self.__do_write_to_element_key_by_key = False        # By default, write to element all keys in the same time
        self.__do_mouse_over_before_click = False            # By default, don't mouse over before click
    
    def initialize(self, window):
        super().initialize(window.driver)
        self.__window_weakref = weakref.ref(window)
    
    @property
    def window(self):
        res = self.__window_weakref()
        if res is None:
            raise TechnicalException("Window has been cleared")
        return res
    
    @property
    def inspector(self):
        return self.window.inspector
    
    @FindActor.default_find_builder.getter  # @UndefinedVariable
    def default_find_builder(self):
        return self.inspector.default_find_builder
    
    @FindActor.find_builder.getter  # @UndefinedVariable
    def find_builder(self):
        """
        @return Find builder from window
        """
        return self.window.find_builder
    
    @property
    def do_mouse_over_before_click(self):
        return self.__do_mouse_over_before_click
    
    @do_mouse_over_before_click.setter
    def do_mouse_over_before_click(self, mouse_over):
        """
        @param mouseOver True if mouse must be moved over the element before click on
        """
        self.__do_mouse_over_before_click = mouse_over
    
    @property
    def do_write_to_element_key_by_key(self):
        return self.__do_write_to_element_key_by_key
    
    @do_write_to_element_key_by_key.setter
    def do_write_to_element_key_by_key(self, key_by_key):
        """
        @param key_by_key True if write to element must be processed key by key
        """
        self.__do_write_to_element_key_by_key = key_by_key
    
    def click_on_element(self, element, scroll_by_x=0, scroll_by_y=0):
        """
        Click on element after having scrolled view.
        It is usually used when element is hidden by another element like a notification.
        @param element
        @param scroll_by_x
        @param scroll_by_y
        """
        raise NotImplementedError

    def write_to_element(self, element, value):
        """
        Write a text to element
        @param element Element
        @param value Text
        """
        raise NotImplementedError
    
    def act_click_on(self, scroll_by_x=0, scroll_by_y=0):
        """
        Action that click on an element
        @return Action
        @param scroll_by_x
        @param scroll_by_y
        """
        return Action("click on", lambda x: self.click_on_element(x, scroll_by_x, scroll_by_y))
        
    def act_find_and_click_on(self, finder, find_type):
        """
        Action that find element with finder and click on
        @param finder Finder
        @param find_type Find type
        @return Action
        """
        return self.act_then(self.act_find(finder, find_type), self.act_click_on())
    
    def act_find_popup(self, popup_title, redo=True):
        """
        @param popup_title Popup title
        @param redo If True, redo action
        @return Action that find popup
        """
        def func(container, candidates, find_context, find_parameters):
            return self.window.find_popup(popup_title, find_parameters.raise_no_such_element)
        res = FindAction(f"find popup '{popup_title}'", self.find_builder, func)
        return self._act_with_redo(res) if redo else res
    
    def act_check_text_is_displayed(self, ui_context, expected_str, redo=True):
        """
        Verify information displayed
        @param ui_context UI context
        @param expected_str Expected text
        @return Verify result
        """
        def func(container, candidates, find_context, find_parameters):
            # If expected doesn't contain interpret, firstly try to find directly text associated to label
            if not self.text_verifier.contains_interpret(expected_str):
                parameters_without_raise = find_parameters.without_raise()
                element = self.inspector.get_finder_text(expected_str, self.inspector.inspect_builder.context(ui_context), None).find_in(container, candidates, find_context, parameters_without_raise)
                if element is not None:
                    return True
            
            # Find text element
            element = self.inspector.get_finder_text_element(self.inspector.inspect_builder.context(ui_context), None).find_in(container, candidates, find_context, find_parameters)
            if element is None:
                # Return False in case find is done without throw
                return False
            
            
            # Verify text
            text = self.internal_api.get_element_text(element)
            comparator = StringComparator()
            return comparator.equals(text, expected_str, find_parameters.raise_no_such_element)
        
        res = FindAction(f"is displayed '{expected_str}'", self.find_builder, func)
        return self._act_with_redo(res) if redo else res

    """
    Verify information displayed
    @param ui_context UI context
    @param expected_str Expected text
    @return Verify result
    """
    def act_check_text_containing_is_displayed(self, ui_context, expected_str, redo=True):
        def func(container, candidates, find_context, find_parameters):
            element = self.inspector.get_finder_text_containing(expected_str, self.inspector.inspect_builder.context(ui_context), None).find_in(container, candidates, find_context, find_parameters)
            return element is not None
        
        res = FindAction(f"is displayed '{expected_str}'", self.find_builder, func)
        return self._act_with_redo(res) if redo else res
    
    
    
    
    