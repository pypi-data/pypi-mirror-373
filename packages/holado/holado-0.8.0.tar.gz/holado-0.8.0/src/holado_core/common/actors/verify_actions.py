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
import abc
from holado_core.common.actors.actions import ActionOnInput
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.verify_exception import VerifyException

logger = logging.getLogger(__name__)



class VerifyInput(ActionOnInput):
    """ Generic verify of input.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, raise_exception):
        super().__init__(name)
        self.__raise_exception = raise_exception
        
    @property
    def name(self):
        return self.__name
    
    def execute(self, input_):
        res = None
        try:
            res = self._verify(input_)
        except Exception as exc:
            if self.__raise_exception:
                raise exc
            else:
                res = False
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Verify [{self.name}] has failed: {Tools.represent_exception(exc)}")
                
        if not res and self.__raise_exception:
            self._raise_verify_exception()
        return res

    def _verify(self, input_):
        """
        @param input_ Input
        @return Result of verify
        """
        raise NotImplementedError

    def _raise_verify_exception(self):
        """
        Raise verify exception
        """
        raise VerifyException(f"Verify [{self.name}] has failed")
    
    
    
    
    
    