
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
from holado_core.common.exceptions.functional_exception import FunctionalException

class CommandException(FunctionalException):
    """
    Exception during command execution
    """
    
    def __init__(self, message=None, command=None, error=None):
        """
        @param message Exception message
        @param command Command
        @param error Command error message
        """
        super().__init__(message if message else f"Command '{command}' failed with error: {error}")
        self.__command = command
        self.__error = error
    
    @property
    def command(self):
        """
        @return Command
        """
        return self.__command
    
    @property
    def error(self):
        """
        @return Command error
        """
        return self.__error
        
    
class CommandError(FunctionalException):
    """
    Error returned by given command
    """
    
    def __init__(self, command, error):
        """
        @param command Command
        @param error Command error message
        """
        super().__init__(command=command, error=error)
        
    
