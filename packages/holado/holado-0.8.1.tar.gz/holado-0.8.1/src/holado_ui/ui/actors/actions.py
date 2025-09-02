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
from holado_core.common.actors.actions import BaseAction
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException

logger = logging.getLogger(__name__)



class UIDriverAction(BaseAction):
    """ Generic action on an UI driver.
    """
    def __init__(self, name, ui_manager):
        super().__init__(name)
        self.__ui_manager = ui_manager
        
    @property
    def ui_manager(self):
        return self.__ui_manager
    
    def _get_driver(self, uid):
        return self.ui_manager.get_driver_info(uid).driver
    
    def execute(self, uid):
        raise NotImplementedError
    
    
class UIDriverCloser(UIDriverAction):
    """ Default UI driver closer.
    """
    def __init__(self, name, ui_manager):
        super().__init__(name, ui_manager)
        
    def execute(self, uid):
        driver = self._get_driver(uid)
        driver.close()
        
        # Pop driver if registered in focus
        try:
            if self.ui_manager.has_focused_driver(uid):
                self.ui_manager.pop_focused_driver(uid)
        except FunctionalException as exc:
            raise TechnicalException(exc)
        
        return True
    
    
    
    
    