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

from holado_core.common.handlers.element_holder import ElementHolder
from holado_core.common.exceptions.technical_exception import TechnicalException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By


class SeleniumBy(object):
    """ Information on a Selenium By.
    """
    
    def __init__(self, by:By, value=None):
        """
        @param by Selenium locator strategy
        @param value Selenium locator value
        """
        self.__by = by
        self.__value = value

    @property
    def by(self):
        """
        @return Selenium locator strategy
        """
        return self.__by
    
    @property
    def value(self):
        """
        @return Selenium locator value
        """
        return self.__value
    
    def __repr__(self)->str:
        return f"{self.by.replace(' ', '_')}({self.value})"
    
    
    
    
    