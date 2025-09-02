
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


# logger = logging.getLogger(__name__)


class LogConfig(object):
    TLogger = None
    TManager = None
    config_file_path = None
    default_level = logging.INFO
    log_on_console=False
    log_in_file=True
    __is_configured = False
    
    @classmethod
    def configure(cls, use_holado_logger=True, config_file_path=None, log_level=None, log_on_console=False, log_in_file=True):
        if cls.__is_configured:
            logging.warning(f"Logging was already configured, it is not possible to configure it twice. This new configuration is skipped.")
            return
        
        # Use holado loggers
        if use_holado_logger:
            cls.__set_holado_loggers()
        
        # HolAdo needs at least to add logging level TRACE and PRINT
        cls.add_logging_level_trace()
        cls.add_logging_level_print()
        
        cls.config_file_path = config_file_path
        if config_file_path:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_file_path)
            log_level = config.get("holado", "level")
            log_on_console = config.get("holado", "log_on_console")
            log_in_file = config.get("holado", "log_in_file")
        
        if log_level:
            if isinstance(log_level, str):
                log_level = logging._nameToLevel[log_level]
            cls.default_level = log_level
        if log_on_console:
            if isinstance(log_on_console, str):
                log_on_console = True if log_on_console == "True" else False
            cls.log_on_console = log_on_console
        if log_in_file:
            if isinstance(log_in_file, str):
                log_in_file = True if log_in_file == "True" else False
            cls.log_in_file = log_in_file
        
        cls.__is_configured = True
    
    @classmethod
    def __set_holado_loggers(cls):
        from holado_logging.common.logging.holado_logger import HALogger
        
        # Configure loggers to use
        HALogger.default_message_size_limit = 10000
        cls.TLogger = HALogger
        cls.TManager = logging.Manager
        
        # Set loggers in logging
        from holado_logging.common.logging.holado_logger import HARootLogger
        logging.root = HARootLogger(cls.default_level)
        logging.Logger.root = logging.root
        logging.Logger.manager = cls.TManager(cls.TLogger.root)
        
        logging.setLoggerClass(cls.TLogger)
        
    
    @classmethod
    def add_logging_level_print(cls):
        if not cls.has_logging_level("PRINT"):
            cls.add_logging_level("PRINT", 45, None)
    
    @classmethod
    def add_logging_level_trace(cls):
        if not cls.has_logging_level("TRACE"):
            cls.add_logging_level("TRACE", 5, None)
        
    
    @classmethod
    def has_logging_level(cls, levelName):
        return hasattr(logging, levelName)
    
    @classmethod
    def add_logging_level(cls, levelName, levelNum, methodName=None):
        """
        This method was implemented and shared by the author of library haggis (https://haggis.readthedocs.io).
        
        Comprehensively adds a new logging level to the `logging` module and the
        currently configured logging class.
    
        `levelName` becomes an attribute of the `logging` module with the value
        `levelNum`. `methodName` becomes a convenience method for both `logging`
        itself and the class returned by `logging.getLoggerClass()` (usually just
        `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
        used.
    
        To avoid accidental clobberings of existing attributes, this method will
        raise an `AttributeError` if the level name is already an attribute of the
        `logging` module or if the method name is already present 
    
        Example
        -------
        >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
        >>> logging.getLogger(__name__).setLevel("TRACE")
        >>> logging.getLogger(__name__).trace('that worked')
        >>> logging.trace('so did this')
        >>> logging.TRACE
        5
    
        """
        if not methodName:
            methodName = levelName.lower()
    
        if hasattr(logging, levelName):
            raise AttributeError('{} already defined in logging module'.format(levelName))
        if hasattr(logging, methodName):
            raise AttributeError('{} already defined in logging module'.format(methodName))
        if hasattr(logging.getLoggerClass(), methodName):
            raise AttributeError('{} already defined in logger class'.format(methodName))
    
        # This method was inspired by the answers to Stack Overflow post
        # http://stackoverflow.com/q/2183233/2988730, especially
        # http://stackoverflow.com/a/13638084/2988730
        def logForLevel(self, message, *args, **kwargs):
            if self.isEnabledFor(levelNum):
                self._log(levelNum, message, args, **kwargs)
        def logToRoot(message, *args, **kwargs):
            logging.log(levelNum, message, *args, **kwargs)
    
        logging.addLevelName(levelNum, levelName)
        setattr(logging, levelName, levelNum)
        setattr(logging.getLoggerClass(), methodName, logForLevel)
        setattr(logging, methodName, logToRoot)
    
    
    
    