
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from builtins import super
from holado_core.common.tables.table_cell import TableCell
import logging
from holado_ui_selenium.ui.gui.selenium.drivers.selenium_driver import SeleniumDriver
from holado_ui_selenium.ui.gui.selenium.handlers.selenium_holder import SeleniumHolder

logger = logging.getLogger(__name__)


class SeleniumTableCell(TableCell):
    
    def __init__(self, selenium_driver:SeleniumDriver, cell_content:SeleniumHolder):
        """
        @summary: Constructor
        @param cell_content: String - Selenium cell content
        """
        super().__init__(cell_content)
        self.__selenium_driver = selenium_driver
        self.__element_text = None
        
    @property
    def driver(self):
        return self.__selenium_driver
    
    @property
    def internal_api(self):
        return self.driver.internal_api
    
    @TableCell.string_content.getter  # @UndefinedVariable
    def string_content(self):
        if self.content is not None:
            return self.get_element_text()
        else:
            return None
    
    def get_element_text(self):
        """
        Get element text.
        Notes: 
          - the found text is stored internally to accelerate algorithms
          - if needed, the element is scrolled to visible in order to get text
        @return Element text
        """
        if self.__element_text is None:
            text_find_parameters = self.content.find_info.find_parameters.with_visibility(True)
            text = self.internal_api.get_element_text(self.content, self.content.find_info.find_context, text_find_parameters)
            if len(text) == 0 and not self.internal_api.is_displayed(self.content):
                self.internal_api.scroll_into_view(self.content, 0)
                text = self.internal_api.get_element_text(self.content, self.content.find_info.findContext, text_find_parameters)
            self.__element_text = text
        
        return self.__element_text
    
    
    
    
