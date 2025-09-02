
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

import logging
import abc
from holado_system.system.command.command import CommandStates
from holado.common.handlers.object import DeleteableObject

logger = logging.getLogger(__name__)

class Service(DeleteableObject):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        super().__init__(name)

        self.__auto_stop = False
        
    def _delete_object(self):
        if self.auto_stop and self.status == CommandStates.Running:
            self.stop()

    @property
    def status(self):
        raise NotImplementedError()
        
    @property
    def auto_stop(self):
        self.__auto_stop
        
    @auto_stop.setter
    def auto_stop(self, auto_stop):
        self.__auto_stop = auto_stop
    
    @abc.abstractmethod
    def stop(self):
        """Stop service"""
        raise NotImplementedError()
