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
import weakref
from holado_core.common.exceptions.technical_exception import TechnicalException
import queue
from holado_core.common.finders.tools.find_parameters import FindParameters
from holado_core.common.exceptions.element_exception import NoSuchElementException,\
    TooManyElementsException
from holado_core.common.finders.tools.enums import FindType
from holado_ui.ui.gui.handlers.label_gui_context import LabelGUIContext
from holado_ui.ui.gui.drivers.gui_driver import GUIDriver
from holado_ui.ui.gui.drivers.gui_internal_api import GUIInternalAPI
from holado_scripting.text.verifier.text_verifier import TextVerifier
import abc
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class GUIWindow(object):
    """ Base class for GUI windows.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        self.__driver_weakref = weakref.ref(None)
        
        self.__inspect_builder = None
        self.__find_builder = None
        
        self.__inspector = None
        self.__actor = None

        self.__current_container = None
        self.__popup_stack = queue.LifoQueue()
    
    def initialize(self, driver:GUIDriver):
        """
        Initialize window with given driver
        @param driver UI driver
        """
        self.__driver_weakref = weakref.ref(driver)
        
        self.__inspector = self._initialize_inspector()
        self.__actor = self._initialize_actor()

        # Must be after inspector initialize, so that default inspect builder is accessible throw inspector
        self.__inspect_builder = self._initialize_inspect_builder()

        self.__current_container = self.get_window_container()
    
    @property
    def driver(self) -> GUIDriver:
        """
        @return driver
        """
        res = self.__driver_weakref()
        if res is None:
            raise TechnicalException("Driver has been cleared")
        return res
    
    @property
    def internal_api(self) -> GUIInternalAPI:
        """
        @return Internal API
        """
        return self.driver.internal_api
    
    @property
    def inspect_builder(self):
        """
        @return Inspector builder
        """
        return self.get_inspect_builder(False)
    
    def get_inspect_builder(self, from_inspector):
        """
        Used internally to prior inspect builder in window than in inspector
        @param from_inspector If request comes from inspector
        @return Inspector instance
        """
        if self.__inspect_builder is not None:
            return self.__inspect_builder
        elif not from_inspector:
            return self.inspector.get_inspect_builder(True)
        else:
            return None
    
    def _initialize_inspect_builder(self):
        """
        This method is used internally at window creation, in order to instantiate the appropriate inspect builder.
        By default return None, in order to use the default one initialized in Inspector. 
        @return a new inspect builder
        """
        return None
    
    @property
    def find_builder(self):
        """
        @return Find builder
        """
        return self.get_find_builder(False)
    
    def get_find_builder(self, from_inspector):
        """
        Used internally to prior find builder in window than in inspector
        @param from_inspector If request comes from inspector
        @return Inspector instance
        """
        if self.__find_builder is not None:
            return self.__find_builder
        elif not from_inspector:
            return self.inspector.get_find_builder(True)
        else:
            return None
    
    def _initialize_find_builder(self):
        """
        This method is used internally at window creation, in order to instantiate the appropriate find builder.
        By default return None, in order to use the default one initialized in Inspector. 
        @return a new find builder
        """
        return None
    
    @property
    def inspector(self):
        """
        @return Inspector instance
        """
        return self.__inspector
    
    def _initialize_inspector(self):
        """
        This method is used internally at window creation, in order to instantiate the appropriate inspector type.
        @return a new inspector instance
        """
        raise NotImplementedError

    @property
    def actor(self):
        """
        @return Actor instance
        """
        return self.__actor
    
    def _initialize_actor(self):
        """
        This method is used internally at window creation, in order to instantiate the appropriate actor type.
        @return a new actor instance
        """
        raise NotImplementedError

    def _get_text_verifier(self) -> TextVerifier:
        return self.driver.text_verifier
    
    @property
    def current_container(self):
        return self.__current_container
    
    @current_container.setter
    def current_container(self, current_container):
        """
        @param current_container the current container to set
        """
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Set current container to [{current_container.get_complete_description()}]") 
        self.__current_container = current_container
    
    def update_current_container(self, raise_no_such_element=True):
        """
        Update current container, usually after a page refresh
        @param raise_no_such_element Raise if any expected element is not found
        """
        # If page behind popup (no popup in stack)
        if self.__popup_stack.empty():
            # Update current container
            self.current_container = self.get_window_container()
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("Updated current container with page container") 
        
        
        # If popup behind popup
        else:
            popup_name = self.__popup_stack.queue[-1]
            popup = self.find_popup(popup_name, raise_no_such_element)
            if popup is not None:
                self.current_container(self.get_popup_container(popup_name, popup))
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Updated current container with popup '{popup_name}' (popup stack: {self.__popup_stack.queue})")
            else:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Unable to update current container  unable to find popup '{popup_name}' (popup stack: {self.__popup_stack.queue})")
                    
    def get_zone_holder(self, zone, zone_name):
        """
        Create a holder with zone element
        @param zone element corresponding to zone
        """
        return self.current_container.get_holder_for(zone, f"zone '{zone_name}'")
    
    def _enter_popup(self, popup_name, popup_holder):
        """
        Enter in popup
        """
        # Update current container
        self.current_container = popup_holder
        
        # Add popup in stack
        self.__popup_stack.put(popup_name)
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Entered in popup '{popup_name}' -> Popup stack: {self.__popup_stack.queue}") 
    
    def _leave_popup(self, raise_no_such_element=True):
        """
        Go back to previous popup or page
        """
        # Remove closed popup from stack
        popup_name = self.__popup_stack.get()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Leaved popup '{popup_name}' -> Popup stack: {self.__popup_stack.queue}") 
        
        # Update current container
        self.update_current_container(raise_no_such_element)
    
    def is_any_popup_opened(self):
        """
        @return True if any popup is supposed to be opened
        """
        return not self.__popup_stack.empty()
    
    def wait_until_popup_is_closed(self, raise_no_such_element=True, timeout_seconds=None, popup_title=None):
        """
        Wait until popup is closed
        @param raise_no_such_element Raise if any expected element is not found
        @param timeout_seconds Timeout duration in seconds
        @param popup_title Popup title
        """
        # Define popup title
        if popup_title is None:
            popup_name = self.__popup_stack.queue[-1]
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Waiting until popup '{popup_name}' is closed (popup stack: {self.__popup_stack.queue})...")
                 
            if popup_name != "{EMPTY}":
                popup_title = popup_name
            
        # Wait popup is closed
        self.actor.redo_while_not_null(
                self.actor.act_find_popup(popup_title),
                timeout_seconds)
        
        # Leave popup
        self._leave_popup(raise_no_such_element)
    
    def get_window_container(self):
        """
        @return Window container
        """
        raise NotImplementedError

    def _get_popup_container(self, popup_title, popup_element):
        raise NotImplementedError
    
    def click_on_text(self, ui_context, text, redo_while_no_such_element):
        """
        Click on given text
        @param ui_context Context
        @param text Text
        @param redo_while_no_such_element If True, retry while catching exception NoSuchElementException
        """
        parameters = FindParameters.default_with_raise().with_redo(redo_while_no_such_element).ignoring(NoSuchElementException)
        act = self.actor.act_find_and_click_on(self.inspector.get_finder_text(text, self.inspector.inspect_builder.context(ui_context), None),
                                               FindType.In)
        act.execute(self.current_container, parameters)
    
    def for_label_is_displayed(self, ui_context, label, text, raise_exception):
        """
        Check the value associated to a label
        @param ui_context Context
        @param label Label
        @param text Text associated to label
        @param raise_exception If True, raise an exception rather than returning False
        @return Check result
        """
        ui_context_label = LabelGUIContext.for_label(ui_context, label)
        act = self.actor.act_check_text_is_displayed(ui_context_label, text)
        return act.execute(self.current_container, FindParameters.default(raise_exception))
    
    def check_table_contains(self, ui_context, expected, raise_exception):
        """
        Check that the table contains a sub-table
        @param ui_context Context
        @param expected Value table
        @param raise_exception If True, raise an exception when verification is False
        @return Check result
        """
        raise NotImplementedError
    
    def check_table_displays(self, ui_context, expected, raise_exception):
        """
        Check that the table is equal to given value table
        @param ui_context Context
        @param expected Value table
        @param raise_exception If True, raise an exception when verification is False
        @return Check result
        """
        raise NotImplementedError
    
    def check_text_containing_x_is_displayed(self, ui_context, text):
        """
        Verify that a text containing given text is displayed.
        @param ui_context Context
        @param text Text to find
        """
        act = self.actor.act_check_text_containing_is_displayed(ui_context, text)
        act.execute(self.current_container, FindParameters.default_with_raise())
    
    def check_text_x_is_displayed(self, ui_context, text):
        """
        Verify that given text is displayed.
        @param ui_context Context
        @param text Text to find
        """
        act = self.actor.act_number_of_occurrences(self.inspector.get_finder_text(text, self.inspector.inspect_builder.context(ui_context), None), FindType.In)
        nb = act.execute(self.current_container)
        if nb < 1:
            raise NoSuchElementException(f"Unable to find text '{text}'")
        elif nb > 1:
            raise TooManyElementsException(f"text '{text}' was found {nb} times")
    
    def is_text_displayed(self, ui_context, text):
        """
        @param ui_context Context
        @param text Text to find
        @return True if text was found
        """
        act = self.actor.act_number_of_occurrences(self.inspector.get_finder_text(text, self.inspector.inspect_builder.context(ui_context), None), FindType.In)
        nb = act.execute(self.current_container)
        return (nb >= 1)
    
    def check_new_popup_is_opened(self, expected_popup_title=None, raise_exception=True):
        """
        @param expected_popup_title Title of the popup
        @param raise_exception If True, raise an exception rather than returning False
        @return True if a popup has appeared with expected title
        """
        raise NotImplementedError

    """
    @param expected_popup_title Title of the popup
    @param raise_no_such_exception If True, raise an exception rather than returning None
    @return Popup element
    """
    def find_popup(self, expected_popup_title, raise_no_such_exception):
        # Find popup
        res = self.inspector.get_finder_popup().find_in(self.get_window_container(), FindParameters.default(raise_no_such_exception))
        if not raise_no_such_exception and res is None:
            return None
        
        # Find and verify the title
        if expected_popup_title is not None:
            title = self.inspector.get_finder_popup_title().findIn(res, FindParameters.default_without_raise())
            if title != None:
                obtained_popup_title = self.internal_api.get_element_text(title)
            else:
                obtained_popup_title = ""
            
            
            # Check popup title
            if not self._get_text_verifier().check(expected_popup_title, obtained_popup_title):
                if raise_no_such_exception:
                    raise NoSuchElementException(f"Current popup does not have the right title (obtained: '{obtained_popup_title}'  expected: '{expected_popup_title}')")
                else:
                    res = None
        
        return res
    
    
    
    