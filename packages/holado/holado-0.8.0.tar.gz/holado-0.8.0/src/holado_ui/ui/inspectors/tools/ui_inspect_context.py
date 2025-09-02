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

import copy
from holado_core.common.inspectors.tools.inspect_context import InspectContext
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_ui.ui.handlers.ui_context import UIContext


class UIInspectContext(InspectContext):
    """ UI inspect context
    """
    
    __instance_default = None
    
    def __init__(self, find_type=None, inspect_context=None, ui_context=None):
        super().__init__(find_type, inspect_context)
        self.__ui_context = ui_context
    
    @property
    def ui_context(self) -> UIContext:
        """
        @return UI context
        """
        return self.__ui_context
    
    @ui_context.setter
    def ui_context(self, ui_context:UIContext):
        self.__ui_context = ui_context
    
    def with_ui_context(self, ui_context):
        """
        Note: if wanted UI context is the same, self instance is returned, else a new one is returned
        @param ui_context UI context
        @return Same context but with given UI context
        """
        if ui_context == self.ui_context:
            return self
        else:
            res = copy.deepcopy(self)
            res.ui_context = ui_context
            return res

    def without_ui_context(self):
        """
        @return Same context but without UI context
        """
        return self.with_ui_context(self, None)
    
    def with_previous_ui_context(self):
        """
        @return Same context but with previous UI context
        """
        if self.ui_context is not None:
            return self.with_ui_context(self.__ui_context.get_previous_context())
        else:
            raise TechnicalException("UI context is not defined")
    
    @staticmethod
    def default():
        """
        @return Default UI inspect context
        """
        if InspectContext.__instance_default is None:
            InspectContext.__instance_default = InspectContext()
        return InspectContext.__instance_default
    
    
    
    
    
    