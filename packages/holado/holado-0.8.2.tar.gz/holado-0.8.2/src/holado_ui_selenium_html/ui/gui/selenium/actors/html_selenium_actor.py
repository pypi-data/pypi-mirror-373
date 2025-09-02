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
from holado_ui_selenium.ui.gui.selenium.actors.selenium_actor import SeleniumActor
from holado_core.common.exceptions.technical_exception import TechnicalException
from selenium.webdriver.support.select import Select

logger = logging.getLogger(__name__)



class HtmlSeleniumActor(SeleniumActor):
    """ HTML Selenium actor.
    """
    
    def __init__(self):
        super().__init__("html")
    
    def select_value(self, element, value):
        finder_info = element.find_info.finder.info
        if finder_info.finder_type is None:
            raise TechnicalException("Finder type is not set in finder info")
        
        if finder_info.finder_type == "select":
            drop_down = Select(element.element)
            drop_down.select_by_visible_text(value)
        else:
            raise TechnicalException(f"Unmanaged finder type '{finder_info.finder_type}'")
    
    
    
    