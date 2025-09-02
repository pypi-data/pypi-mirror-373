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

logger = logging.getLogger(__name__)



class DefaultSeleniumActor(SeleniumActor):
    """ Default Selenium actor.
    """
    __module_class_by_name = {}
    
    @classmethod
    def register_module(cls, name, class_):
        if name in cls.__module_class_by_name:
            raise TechnicalException(f"Module '{name}' is already registered with type '{cls.__module_class_by_name[name].__name__}'")
        cls.__module_class_by_name[name] = class_
    
    
    def __init__(self):
        super().__init__("selenium")
        
    def _initialize_module(self, name):
        if name in self.__module_class_by_name:
            res = self.__module_class_by_name[name]()
            res.initialize(self.window)
            return res
        else:
            return super()._initialize_module(name)
    
    
    