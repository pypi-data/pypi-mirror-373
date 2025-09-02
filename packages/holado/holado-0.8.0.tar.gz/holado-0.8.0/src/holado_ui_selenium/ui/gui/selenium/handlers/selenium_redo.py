
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
import abc
from holado_core.common.handlers.redo import Redo
from selenium.common.exceptions import WebDriverException,\
    StaleElementReferenceException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class SeleniumRedo(Redo):
    """ Redo on Selenium actions.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, selenium_driver):
        super().__init__(name)
        
        self.__selenium_driver = selenium_driver
        
        # Manage iteration on scroll_by_y
        self.__with_scroll_by_y = False
        self.__scroll_by_y = 0
        
        # Ignore stale exception
        self.ignoring(StaleElementReferenceException)
        # self.ignoring(UnreachableBrowserException)
        
        # Reduce process timeout, in order to execute several retries
        self.with_process_timeout_for_retry(3)
        
        # Deactivate polling to reduce stale exceptions
        self.polling_every(0)
        
        # Manage selenium freeze
        self.with_nb_successive_failure_before_error(3)
        
        # Manage element that is under change (WebDriverException with message "unknown error")
        self.ignoring(WebDriverException)
    
    @property
    def internal_api(self):
        return self.__selenium_driver.internal_api
    
    @property
    def scroll_by_y(self):
        return self.__scroll_by_y
    
    def with_iteration_on_scroll_by_y(self):
        """
        Activate detection of not clickable element exception and iterate on scroll_by_y
        @return self
        """
        self.__with_scroll_by_y = True
        return self
    
    def _execute_after_ignored(self, exception):
        # If element is not clickable, increase scroll by y after scroll_into_visible
        if self.__with_scroll_by_y and isinstance(exception, WebDriverException) and " is not clickable at point " in str(exception):
            old_scroll_by_y = self.__scroll_by_y
            self.__scroll_by_y = self.__scroll_by_y * 5 // 4 - 10
            logger.warning(f"Element was not clickable ; update scroll_by_y : {old_scroll_by_y} -> {self.__scroll_by_y}")
            return
        
        # Only ignore WebDriverException containing "unknown error" in message
        if type(exception) == WebDriverException and "unknown error" not in str(exception):
            Tools.raise_same_exception_type(exception, str(exception))
    
    
    
    
    
    
