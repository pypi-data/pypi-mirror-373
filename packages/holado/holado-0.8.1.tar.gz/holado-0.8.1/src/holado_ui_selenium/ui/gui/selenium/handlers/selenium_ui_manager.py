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
from holado.common.context.context import Context
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_ui.ui.exceptions.focus_driver_exception import FocusDriverException
from holado_ui_selenium.ui.gui.selenium.handlers.enums import BrowserTypes
from holado_ui_selenium.ui.gui.selenium.drivers.selenium_driver import SeleniumDriver

logger = logging.getLogger(__name__)



class SeleniumUIManager(Context):
    """ Tools to manage existing web browsers.
    It adds features to UIManager.
    """
    
    def __init__(self, ui_manager, path_manager):
        super().__init__("SeleniumUIManager")
        
        self.__ui_manager = ui_manager
        self.__path_manager = path_manager
    
    @property
    def current_browser(self):
        """
        @return Current browser instance
        """
        # Create browser if needed
        if not self.has_current_browser():
            #TODO: add default browser type in a config file
            browser_type = BrowserTypes.Chrome
            
            # If not already set, set browser with configured version
            if not self.has_browser(browser_type):
                self.set_browser(browser_type)
            
            # Update current browser ID
            self.set_current_browser_id(self.get_browser_id(browser_type))
        
        # When last page of a browser is closed, the browser is removed from registered driver, since it is not visible anymore.
        # Thus, if current browser is not anymore in registered drivers, push it again
        browser_id = self.current_browser_id
        if not self.__ui_manager.has_driver(browser_id):
            self.__ui_manager.push_driver(browser_id, self.get_browser_of_id(browser_id), False)
        
        # Verify that active driver is expected browser
        try:
            self.__ui_manager.verify_driver_is_in_focus(self.get_current_browser_id())
        except FocusDriverException as exc:
            raise FocusDriverException(f"Current active UI is not expected browser (usually it is solved by switching into the browser before): expected: '{self.get_current_browser_id()}' ; current active: '{self.__ui_manager.in_focus_driver_info.uid}'") from exc
        
        return self.__ui_manager.in_focus_driver_info.driver
    
    @property
    def current_browser_id(self):
        """
        @return Current browser ID
        """
        return self.get_object("current_browser_id")

    @current_browser_id.setter
    def current_browser_id(self, browser_id):
        """
        Set current browser ID
        @param browser_id Browser ID
        """
        self.set_object("current_browser_id", browser_id, False)

    @property
    def has_current_browser(self):
        """
        @return True if context contains current browser instance
        """
        return self.has_object("current_browser_id")

    def set_current_browser_type(self, browser_type):
        """
        Set current browser type
        @param browser_type Browser type
        """
        self.current_browser_id = self.get_browser_id(browser_type)

    def get_browser(self, browser_type):
        """
        @param browser_type Browser type
        @return Browser instance of given type
        """
        if not self.has_browser(browser_type):
            self.set_browser(browser_type)
        return self.get_object(self.get_browser_id(browser_type))

    def get_browser_of_id(self, browser_id):
        """
        @param browser_id Browser ID
        @return Browser instance of given ID
        """
        return self.get_object(browser_id)

    def get_browser_id(self, browser_type):
        """
        @param browser_type Browser type
        @return Browser ID of given type
        """
        return f"{browser_type.name}_browser"

    def has_browser(self, browser_type):
        """
        @param browser_type Browser type
        @return True if context contains browser instance of given type
        """
        return self.has_object(self.get_browser_id(browser_type))

    def set_browser(self, browser_type):
        """
        @param browser_type Browser type
        """
        if self.has_Browser(browser_type):
            logger.info(f"setting a new browser of type '{browser_type.name}'")
            
            uid = self.get_browser_id(browser_type)
            
            # Create and initialize new browser
            selenium_driver = SeleniumDriver(browser_type, self.__path_manager)
            self.__ui_manager.initialize_ui_driver(uid, selenium_driver)
            
            # Add driver in UI manager
            self.__ui_manager.push_driver(self.get_browser_id(browser_type), self.get_browser(browser_type), False)
        else:
            raise TechnicalException(f"Browser of type '{browser_type.name}' is already set")

    def set_browser_lifetime_to(self, lifetime_context, browser_type):
        """
        Set browser lifetime to given context
        @param lifetime_context Lifetime context
        @param browser_type Browser type
        """
        if self.has_browser(browser_type):
            browser_id = self.get_browser_id(browser_type)
            self.__ui_manager.set_driver_lifetime_to(lifetime_context, browser_id)
        else:
            raise TechnicalException(f"No browser of type '{browser_type.name}' is set")

    def switch_to_browser(self, browser_type):
        """
        Make given browser type as active UI driver
        @param browser_type Browser type
        """
        # Set current browser type
        self.set_current_browser_type(browser_type)
        
        browser_id = self.get_browser_id(browser_type)
        if not self.__ui_manager.has_driver(browser_id):
            if not self.has_browser(browser_type):
                self.set_browser(browser_type)
            else:
                self.__ui_manager.push_driver(browser_id, self.get_browser_of_id(browser_id), False)
        else:
            self.__ui_manager.switch_to_driver(browser_id)
        
        # If browser has already an opened window, focus on it
        if self.current_browser.is_opened:
            handle = self.current_browser.internal_driver.get_window_handle()
            
            # Use an alert to force focus
            self.current_browser.internal_driver.execute_script("alert('Test')")
            self.current_browser.internal_driver.swith_to.alert.accept()
            
            self.current_browser.internal_driver.swith_to.window(handle)

    def switch_to_browser(self, browser_id):
        """
        Make browser of given ID as active UI driver
        @param browser_id ID of already opened browser
        """
        # Repush browser
        self.__ui_manager.switch_to_driver(browser_id)
        
        # If browser has already an opened window, focus on it
        if self.current_browser.is_opened:
            handle = self.current_browser.internal_driver.get_window_handle()
            self.current_browser.internal_driver.switchTo().window(handle)
    
    def close_browser(self, browser_type, lifetime_context=None):
        """
        Close given browser type
        @param browser_type Browser type
        @param lifetime_context Lifetime context
        @return True if a driver was closed
        """
        res = False
        
        if self.has_browser(browser_type) and self.get_browser(browser_type).is_opened:
            # Close browser
            browser_id = self.get_browser_id(browser_type)
            res = self.__ui_manager.close_driver(browser_id, lifetime_context)
        
        return res
    
    
    
    
    
    