
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
from holado_system.system.command.command_result import CommandResult
from holado_core.common.tools.converters.converter import Converter
import re

logger = logging.getLogger(__name__)


class CurlCommandResult(CommandResult):
    """
    Result of a cURL command
    """
    __regex_error = None
    
    def __init__(self, command, output=None, error=None, previous_command_result=None):
        super().__init__(command, output, CurlCommandResult.__extract_error(error), previous_command_result)
        self.__statistics = None

        self.__statistics = self.__extract_statistics(output, error)
        if previous_command_result is not None:
            if self.__statistics is not None and previous_command_result.statistics is not None:
                self.__statistics = previous_command_result.statistics + self.__statistics
            elif self.__statistics is None:
                self.__statistics = previous_command_result.statistics
    
    @property
    def statistics(self):
        """
        @return Command statistics
        """
        return self.__statistics
    
    @classmethod
    def __get_regex_error(cls):
        if cls.__regex_error is None:
            cls.__regex_error = re.compile(r"curl:\s+\((\d+)\)\s+(.*)")
        return cls.__regex_error
    
    @classmethod
    def __extract_error(cls, error):
        res = None
        
        if error is not None:
            m = cls.__get_regex_error().search(error)
            if m:
                res = m.group()
        
        return res

    def __extract_statistics(self, output, error):
        res = error
        
        if (output is None or len(output) == 0) and error is not None:
            m = self.__get_regex_error().search(error)
            if m:
                res = error[:m.start()]
        
        return res
    
    @property
    def error_code(self):
        """
        @return Error code if an error occurred, else -1
        """
        res = -1
        
        if self.has_error:
            m = self.__get_regex_error().search(self.error)
            if m:
                res = Converter.to_integer(m.group(1))
        
        return res
    
    @property
    def error_message(self):
        """
        @return Error message if an error occurred, else None
        """
        res = None
        
        if self.has_error:
            m = self.__get_regex_error().search(self.error)
            if m:
                res = m.group(2)
        
        return res
    
    