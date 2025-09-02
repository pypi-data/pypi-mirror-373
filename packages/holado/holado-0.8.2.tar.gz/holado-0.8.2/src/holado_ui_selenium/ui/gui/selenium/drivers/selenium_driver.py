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
from holado_core.common.exceptions.technical_exception import TechnicalException
import re
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_ui.ui.gui.drivers.gui_driver import GUIDriver
from urllib.parse import unquote
from holado_ui_selenium.ui.gui.selenium.handlers.enums import BrowserTypes
from holado_core.common.handlers.redo import Redo
from holado_ui.ui.gui.windows.gui_window_info import GUIWindowInfo
from selenium.common.exceptions import NoSuchWindowException
from holado.common.handlers.enums import ObjectStates
from holado_core.common.exceptions.timeout_exception import TimeoutException
from holado_ui_selenium.ui.gui.selenium.tools.selenium_path_manager import SeleniumPathManager
from holado_ui_selenium.ui.gui.selenium.drivers.selenium_internal_api import SeleniumInternalAPI
from holado_ui_selenium.ui.gui.selenium.drivers.web_driver_manager import WebDriverManager
import urllib
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class SeleniumDriver(GUIDriver):
    """ Selenium driver.
    """
    
    def __init__(self, browser_type, path_manager, name=None):
        super().__init__(name or "SeleniumDriver")
        
        self.__path_manager = SeleniumPathManager(path_manager)
        self.__web_driver_manager = WebDriverManager(browser_type, self.__path_manager)
        self.__current_host = None
    
    def _initialize_internal_api(self):
        return SeleniumInternalAPI(self)
    
    @property
    def current_host(self):
        """
        @return Current host
        """
        return self.__current_host
    
    @current_host.setter
    def current_host(self, host):
        """
        Update current host
        @param host New host
        """
        if host != self.__current_host:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"current host has changed ('{self.current_host}' -> '{host}')")
            self.__current_host = host
    
    @property
    def browser_type(self):
        """
        @return the browser type
        """
        return self.__web_driver_manager.browser_type
    
    @property
    def _selenium_path_manager(self):
        return self.__path_manager
    
    @property
    def _path_manager(self):
        return self.__path_manager.path_manager
    
    @property
    def current_url(self, ):
        """
        @return current URL (it is unescaped).
        """
        # Get URL from selenium
        res = self.internal_driver.current_url
        # Decode URL (for percent-encoded data like %20)
        try:
            res = unquote(res, encoding='utf-8', errors='strict')
        except UnicodeError as exc:
            raise TechnicalException(str(exc)) from exc
        return res
        
    def open_site(self, host):
        """
        Open a portal given a specific host
        @param host Name of remote host
        """
        self.current_host = host
        self.open_current_host()
    
    def open_new_window(self):
        """
        Open a new page
        """
        if not self.is_open:
            self.open()
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("Opening new window...")
            
            if self.has_current_window():
                self.internal_api.open_new_window()
            else:
                self.internal_api.focus()      # When entering in this case, close of last page was simulated, and the browser window has possibly lost focus
            
            self.check_new_browser_page_is_open()
            
    def open_current_host(self):
        """
        Open current host
        """
        # Build URL
        url = "http://" + self.current_host
        
        # Open URL
        # Note: use open_url rather than openSite in order to use same proxy settings
        self.open_url(url)
    
    def refresh(self):
        """
        Refresh current Html page
        """
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace("Refreshing current page...")
        self.internal_api.refresh_browser()
        self.internal_api.wait_until_window_is_loaded()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Refreshed current page")
        
    def open(self):
        """
        Open a WebDriver for configured browser.
        """
        self.__open_driver()
        
    def __open_driver(self):
        """
        Open a WebDriver for configured browser.
        """
        # Create web driver
        self.internal_driver = self.__web_driver_manager.create_web_driver()
        
        self.internal_api.maximize()
        
      
    def _close_driver(self):
        super()._close_driver()
        self.__close_browser(self.__browser_type)
        
    def __close_browser(self, browser_type):
        if self.has_internal_driver:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("close web driver")
                
            # Close browser
#          if (CommonSystem.getOSType() == OSType.Windows):
#              #WORKAROUND: scenario stops and displays an error window saying plugin container has stopped
#              driver.quit()
#              Tools.sleep(5000)
#          }    

            # Quit web driver
#          if (browser_type == BrowserTypes.Firefox):
#            if (browser_type == BrowserTypes.Chrome):
#                try:
#                    driver.quit()
#                except Exception e):
#                    logger.warn("exception catched when quiting web driver: {}", e.getMessage())
#                #                        setInternalDriver(None)
            
            # Remove opened pages information
            self._clear_window_info()
            
    def open_url(self, url):
        """
        Open given URL in current active browser.
        @param url URL to open.
        """
        # Open new browser if needed
        if not self.is_open:
            self.open()
            self.check_new_browser_page_is_open()
                
        # Go to url
        self.navigate_to_url(url)

        # Update current host
        current_url = self.current_url
        current_host = self.__get_host_from_url(current_url)
        if current_host is None:
            raise FunctionalException(f"Url '{current_url}' does not match expected formats")
        else:
            self.current_host = current_host
        
        # Update managed handle and page
        page_handle = self.internal_driver.current_window_handle
        if current_host is not None:
            page_name = self._get_page_name_from_url(current_url)
            selenium_window = self._new_window_for_name(page_name)
        else:
            page_name = None
            selenium_window = self.new_default_window()
            selenium_window.initialize(self)
        window_info = GUIWindowInfo(selenium_window, page_name, page_handle)
        self._add_window_info(page_handle, window_info)
        if not self.has_current_window or self._get_current_window_id() != page_handle:
            self._push_current_window_id(page_handle)
        
    def __navigate_to_url(self, url):
        self.internal_driver.get(url)
        
    def check_browser_displays_page(self, page_name, host=None, timeout_seconds=None):
        """
        Check that browser displays given page until given timeout, and update internal current page.
        @param page_name Page name
        @param host Host name
        @param timeout_seconds Timeout (if None, default timeout is used)
        """
        if host is None:
            host = "https?://" + self.current_host
            
        self.internal_api.wait_until_window_is_loaded()
        
        # Check if current url contains expected host and page name
        class PageRedo(Redo):
            def __init__(self, driver):
                super().__init__(f"check browser displays page '{page_name}'")
                self.__driver = driver
                
            def _process(self):
                res = None
                
                current_page_name = self.__driver._get_page_name_from_url(self.__driver.current_url, host)
                if current_page_name is not None:
                    if self.text_verifier.check(page_name, current_page_name):
                        res = current_page_name
                else:
                    logger.warning(f"browser page '{self.current_url}' doesn't match expected page '{page_name}'")
                
                return res
            
        redo = PageRedo(self)
        redo.redo_while_none()
        if timeout_seconds is not None:
            redo.with_timeout(timeout_seconds)
        redo.with_nb_successive_failure_before_error(3)
        try:
            current_page_name = redo.execute()
        except TimeoutException:
            raise FunctionalException(f"Page '{page_name}' is not displayed (current: '{self.current_url}')")
        
        self.update_current_window(current_page_name, self.internal_driver.current_window_handle)
        
    def is_browser_displaying_page(self, page_name, host=None):
        """
        @param page_name Page name
        @param host Host name
        @return True if browser displays given page
        """
        if host is None:
            host = "http://" + self.current_host
            
        self._verify_is_open()
        self.internal_api.wait_until_window_is_loaded()
        
        # Return if current url contains expected host and page name
        current_page_name = self._get_page_name_from_url(self.current_url, host)
        if current_page_name is not None:
            res = self.text_verifier.check(page_name, current_page_name)
        else:
            res = False
        
        return res
        
    def check_new_browser_page_is_open(self):
        """
        Checks and register a new opened browser.
        If more than one new browsers are detected, an exception is thrown 
        """
        class PageRedo(Redo):
            def __init__(self, driver):
                super().__init__(f"check new browser is open")
                self.__driver = driver
                
            def _process(self):
                res = None
                
                handles = self.internal_api.window_handles
                
                # Verify that one and only one new browser exists
                if len(handles) > self._nb_windows() + 1:
                    raise FunctionalException(f"More than one ({len(handles) - self._nb_windows()} new windows exist. Unable to determine which one is the last one.")
                elif len(handles) == self._nb_windows():
                    raise NoSuchWindowException("No new browser is open")
                
                # Find and register new browser handle
                for handle in handles:
                    # If new browser exists
                    if not self._has_window_info(handle):
                        # Move to new browser
                        self.switch_to_window(handle)
                        self._push_current_window_id(handle)
                        res = handle
                        break
                
                return res
            
        redo = PageRedo(self)
        redo.redo_while_none()
        redo.ignoring(NoSuchWindowException)
        redo.with_nb_successive_failure_before_error(3)
        new_handle = redo.execute()
        
        # Check new window is found
        if new_handle is None:
            raise FunctionalException("Unable to find new browser")
           
        # Update current host
        url = self.current_url
        self.current_host = self.__get_host_from_url(url)
        
        # update managed handle and page
        if self.current_host is not None:
            page_name = self._get_page_name_from_url(url)
            selenium_window = self._new_window_for_name(page_name)
        else:
            page_name = None
            selenium_window = self.new_default_window()
            selenium_window.initialize(self)
        self._add_window_info(new_handle, GUIWindowInfo(selenium_window, page_name, new_handle))
        
    def __get_host_from_url(self, str_url):
        split_result = urllib.parse.urlsplit(str_url)
        res_split = urllib.parse.SplitResult(scheme=split_result.scheme, netloc=split_result.netloc, path='', query='', fragment='')
        return res_split.geturl()
        
    def _get_page_name_from_url(self, url, host=None):
        if host is None:
            if self.current_host is None:
                raise TechnicalException("Hostname is not defined")
            host = self.current_host
            
        # Verify host
        url_host = self.__get_host_from_url(url)
        if url_host != host:
            raise FunctionalException(f"Unexpected host in url '{url}' (obtained: '{url_host}'  expected: '{host}')")
        
        # Get page name
        split_result = urllib.parse.urlsplit(url)
        return split_result.path
    
    def _close_current_window(self):
        """
        Close current window.
        If is under closing, close of last window, else simulate a close to keep browser and web driver connected
        """
        is_closing = (self.object_state == ObjectStates.Closing)
        self.__close_current_window(is_closing)
    
    """
    Close current window.
    @param close_last_window If True close last window, else simulate a close to keep browser and web driver connected
    """
    def __close_current_window(self, close_last_window):
        # Disactivate JS onbeforeunload
        self.internal_api.disactivate_js_onbeforeunload()

        # Close current browser page
        if self._nb_windows() > 1 or close_last_window:
            self.internal_driver.close()
        else:
            # Change page to default
            # Note: currently, pages that doesn't start with http are not managed
#          self.open_url("about:blank")
            self.open_url("https://www.lilo.org/fr/")
        
        # Leave handle internally
        handle = self._get_current_window_id()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Leaving window {handle}")
        
        # Close browser or move to previous page
        if self._nb_windows() == 0:
            if close_last_window:
                # No window exists anymore, close browser 
                if self.__browser_type == BrowserTypes.Firefox:
                    handles = self.internal_api.window_handles
                    if len(handles) == 0 or len(handles) == 1 and handle in handles:
                        self.close()
                else:
                    self.close()
        else:
            #  Move to previous page
            self.set_focus_on_current_page()
            self.current_host = self.__get_host_from_url(self.current_url)
        
    def set_focus_on_current_page(self):
        """
        Set focus on current registered page.
        It is used internally by pages when a popup is closed, or when a page is closed. 
        """
        self.__switch_to_window(self._get_current_window_id())
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"return into window {self._get_current_window_id()}")
        
    def __switch_to_window(self, handle):
        try:
            self.internal_driver.swith_to.window(handle)
        except NoSuchWindowException as exc:
            msg_list = [str(exc)]
            msg_list.append(f"    Known by framework: {self._get_all_window_ids()}")
            msg_list.append(f"    Known by selenium: {self.internal_api.window_handles}")
            raise NoSuchWindowException("\n".join(msg_list)) from exc
            
    def make_screenshots_for_debug(self, destination_path, context_description):
        # Screenshot of current window
        self.internal_api.make_screenshot(destination_path, context_description)
        
        # Backup of current window page source
        self.internal_api.makePageSourceBackup(destination_path, context_description)
    
    
    
    
    
    