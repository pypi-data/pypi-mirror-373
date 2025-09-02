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
from holado_python.standard_library.typing import Typing


class SeleniumHolder(ElementHolder):
    """ Information on a Selenium element.
    """
    
    def __init__(self, parent, element, selenium_driver, description=None):
        """
        @param parent Parent
        @param element Element instance
        @param selenium_driver Selenium driver
        @param description Element description
        """
        super().__init__(parent, element, description)
        self.__selenium_driver = selenium_driver

    @property
    def driver(self):
        """
        @return Selenium driver
        """
        return self.__selenium_driver
    
    @property
    def is_alert(self):
        """
        @return If is an alert
        """
        return isinstance(self.element, Alert)
    
    @property
    def is_web_driver(self):
        """
        @return If is a web driver
        """
        return isinstance(self.element, WebDriver)
    
    @property
    def is_web_element(self):
        """
        @return If is a web element
        """
        return isinstance(self.element, WebElement) and not self.is_popup
    
    @property
    def is_popup(self):
        """
        @return If is a popup
        """
        return False

    @ElementHolder.complete_description_and_details.getter  # @UndefinedVariable
    def complete_description_and_details(self):
        if self.is_alert:
            return f"{self.complete_description} (element: {{ALERT}})"
        elif self.is_web_driver:
            return f"{self.complete_description} (element: {{PAGE}})"
        elif self.is_web_element:
            return f"{self.complete_description} (element: {self.driver.internal_api.get_element_description(self.element)})"
        else:
            return super().complete_description_and_details

    def get_holder_for(self, element, description):
        """
        @param element New element instance.
        @param description New element description.
        @return Element holder for given element instance
        """
        if isinstance(element, WebElement):
            return SeleniumHolder(self, element, self.driver, description)
        else:
            raise TechnicalException(f"Unexpected element type {Typing.get_object_class_fullname(element)}")
    
    def get_popup_holder_for(self, element, title, description):
        """
        @param element Popup element
        @param title Popup title
        @param description Popup description
        @return Popup holder for given popup element
        """
        if isinstance(element, WebElement):
            return PopupHolder(self, element, self.driver, title, description)
        else:
            raise TechnicalException(f"Unexpected element type {Typing.get_object_class_fullname(element)}")
    
    
    
class PopupHolder(SeleniumHolder):
    """ Information on a popup element.
    """
    
    def __init__(self, parent, element, selenium_driver, title=None, description=None):
        """
        @param parent Parent
        @param element Popup element instance
        @param selenium_driver Selenium driver
        @param title Popup title (None means no title)
        @param description Element description
        """
        super().__init__(parent, element, selenium_driver, description)
        self.__title = title
        
    @SeleniumHolder.is_popup.getter
    def is_popup(self):
        return True

    @property
    def title(self):
        """
        @return Popup title
        """
        return self.__title
    
    @ElementHolder.complete_description_and_details.getter  # @UndefinedVariable
    def complete_description_and_details(self):
        if self.is_popup:
            if self.title is not None:
                return f"{self.complete_description} (popup '{self.title}' element: {self.driver.internal_api.get_element_description(self.element)})"
            else:
                return f"{self.complete_description} (popup element: {self.driver.internal_api.get_element_description(self.element)})"
        else:
            return super().complete_description_and_details
    
    
    
    
    
    