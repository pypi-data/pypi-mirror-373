
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_system.system.command.exceptions import CommandError

logger = logging.getLogger(__name__)


class CommandResult(object):
    """
    Result of a command
    """

    def __init__(self, command, output=None, error=None, previous_command_result=None):
        self.__command = command
        self.__output = output
        self.__error = error

        if previous_command_result is not None:
            # Verify command is the same
            if previous_command_result.command != command:
                raise TechnicalException(f"Commands are not the same:\n    current:  [{command}]\n    previous: [{previous_command_result.command}]")
            
            if output is not None and previous_command_result.output is not None:
                self.__output = previous_command_result.output + output
            elif output is not None:
                self.__output = output
            else:
                self.__output = previous_command_result.output
            
            if error is not None and previous_command_result.error is not None:
                self.__error = previous_command_result.error + error
            elif error is not None:
                self.__error = error
            else:
                self.__error = previous_command_result.error
    
    @property
    def command(self):
        """
        @return Command
        """
        return self.__command
    
    @property
    def output(self):
        """
        @return Command output
        """
        return self.__output
 
    @output.setter
    def output(self, output):
        """
        @param output Command output
        """
        self.__output = output
    
    @property
    def error(self):
        """
        @return Command error
        """
        return self.__error
 
    @error.setter
    def error(self, error):
        """
        @param error Command error
        """
        self.__error = error

    @property
    def has_error(self):
        """
        @return True if error exists
        """
        return (self.error is not None and len(self.error) > 0)
    
    @property
    def has_output(self):
        """
        @return True if output exists
        """
        return (self.output is not None and len(self.output) > 0)
    
    def log_if_error(self):
        """
        Log an error if command resulted with an error.
        """
        if self.has_error:
            logger.error(f"Error during command '{self.command}': {self.error}")
    
    def raise_if_error(self):
        """
        Raise a CommandError if command resulted with an error.
        """
        if self.has_error:
            raise CommandError(self.command, self.error)
    
    def __eq__(self, obj:object)->bool:
        if obj is None or not isinstance(obj, type(self)):
            return False
        
        res = self.command is None and obj.command is None \
                or self.command is not None and self.command == obj.command
        
        res &= self.output is None and obj.output is None \
                or self.output is not None and self.output == obj.output
        
        res &= self.error is None and obj.error is None \
                or self.error is not None and self.error == obj.error
        
        return res
    
    