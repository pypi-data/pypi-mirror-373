
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
from holado_core.tools.abstracts.service import Service
from holado_system.system.command.command import Command, CommandStates
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)

class BlockingCommandService(Service):
    """
    Manage a service launched by a blocking system command.
    """
    
    def __init__(self, name, cmd, **kwargs):
        super().__init__(name)
        
        self.__cmd_str = cmd
        self.__command = Command(self.__cmd_str, **kwargs)
    
    @property
    def internal_command(self):
        return self.__command
    
    @property
    def status(self):
        if self.__command is not None:
            return self.__command.state
        else:
            return None
    
    def start(self):
        """
        Start the service.
        """ 
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Starting service '{self.name}'")
        self.__command.start()

    def stop(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Stopping service '{self.name}'")
        status = self.__command.state
        if status == CommandStates.Running:
            # self.__command.terminate()
            self.__command.stop()
            self.__command.join()
        else:
            raise FunctionalException(f"Service '{self.name}' is not running (status: {status.name}")
    
    def join(self, timeout=None):
        self.__command.join(timeout)
