
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
from holado_core.common.handlers.abstracts.base_redo import BaseRedo

logger = logging.getLogger(__name__)


class Redo(BaseRedo):
    """ Redo a process until timeout.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        super().__init__(name)
        self.__is_redo_while_null = False
        self.__is_redo_while_not_null = False
        self.__redo_while_values = []
        self.__is_redo_until_none = False
        self.__is_redo_until_not_none = False
        self.__redo_until_values = []
    
    def _is_redo_needed(self, result):
        if self.__is_redo_while_null and result is None:
            return True
        if self.__is_redo_until_none and result is None:
            return False
        
        if self.__is_redo_while_not_null and result is not None:
            return True
        if self.__is_redo_until_not_none and result is not None:
            return False
        
        if len(self.__redo_while_values) > 0 and result is not None:
            for value in self.__redo_while_values:
                if result == value:
                    return True
        
        if len(self.__redo_until_values) > 0:
            if result is None:
                return True
            else:
                for value in self.__redo_until_values:
                    if result == value:
                        return False
        
        # If redo until something, then return True, else return False
        return self.__is_redo_until_none or self.__is_redo_until_not_none or len(self.__redo_until_values) > 0
    
    def redo_while_none(self):
        """
        Redo while result is None
        Note: can be combined with any other redo_XXX method
        @return self
        """
        self.__is_redo_while_null = True
        return self
    
    def redo_while_not_none(self):
        """
        Redo while result is not None
        Note: can be combined with any other redo_XXX method
        @return self
        """
        self.__is_redo_while_not_null = True
        return self
    
    def redo_while(self, value):
        """
        Redo while result is equal to given value
        Note: can be combined with any other redo_XXX method
        @param value Value
        @return self
        """
        self.__redo_while_values.append(value)
        return self
    
    def redo_until_none(self):
        """
        Redo until result is None
        Note: can be combined with any other redo_XXX method
        @return self
        """
        self.__is_redo_until_none = True
        return self
    
    def redo_until_not_none(self):
        """
        Redo until result is not None
        Note: can be combined with any other redo_XXX method
        @return self
        """
        self.__is_redo_until_not_none = True
        return self
    
    def redo_until(self, value):
        """
        Redo until result is equal to given value
        Note: can be combined with any other redo_XXX method
        @param value Value
        @return self
        """
        self.__redo_until_values.append(value)
        return self
        
        
        
