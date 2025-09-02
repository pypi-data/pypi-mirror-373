
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

import threading
import logging
import sys
import os.path
from pathlib import Path
import configparser
from holado_logging.common.logging.log_config import LogConfig
from holado_core.common.tools.tools import Tools


logger = logging.getLogger(__name__)

def filter_thread_native_id(record):
    """Inject thread_native_id to log records"""
    from holado_multitask.multitasking.multitask_manager import MultitaskManager
    record.thread_native_id = MultitaskManager.get_thread_id(native=True)
    return record

class LogManager(object):

    def __init__(self):
        self.__loggers_levels = []
        
        self.__config_file_path = None
        
        self.on_console = False
        self.__console_handler = None
        
        self.in_file = True
        self.__files_lock = threading.Lock()
        self.__file_names = []
        self.__file_handlers = {}
        self.__root_file_name = None
        self.__root_file_handler = None
        self.__root_file_handler_active = False
        
        # Initialize format according python version
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        if MultitaskManager.has_thread_native_id():
            # Exists since python 3.8
            # self.format = '{asctime:s} | {thread_native_id:-5d} | {levelname:5s} | {name:50s} | {message:s}'
            self.format = '{asctime:s} | {process:-5d}-{thread_native_id:-5d} | {levelname:5s} | {name:50s} | {message:s}'
            self.style = '{'
        else:
            if sys.version_info > (3, 2):
                # self.format = '{asctime:s} | {thread:-5d} | {levelname:5s} | {module:35s} | {message:s}'
                self.format = '{asctime:s} | {process:-5d}-{thread:-5d} | {levelname:5s} | {name:50s} | {message:s}'
                self.style = '{'
            else: 
                self.format = '%(asctime)s | %(process)-5d-%(thread)-5d | %(levelname)5s | %(module)35s | %(message)s'
                self.style = '%'
        
    def configure(self):
        self.__config_file_path = LogConfig.config_file_path
        
        if self.__config_file_path:
            config = configparser.ConfigParser()
            config.read(self.__config_file_path)
            
            if config.has_section("loggers_levels"):
                self.__loggers_levels = config.items(section="loggers_levels")
    
    def initialize(self):
        """
        Initialize log manager.
        If log_on_console is True, logs are published on console until a new configuration by calling method set_config
        """
        handlers = []
        if LogConfig.log_on_console:
            self.on_console = True
            self.__console_handler = self.__new_console_handler()
            handlers.append(self.__console_handler)
        
        logging.basicConfig(format=self.format, style=self.style, level=LogConfig.default_level, handlers=handlers)
    
    def has_log_file(self, file_name):
        with self.__files_lock:
            return file_name in self.__file_names or file_name == self.__root_file_name
    
    def set_root_log_file(self, file_name):
        with self.__files_lock:
            if file_name is not None and len(file_name) > 0:
                self.__root_file_name = file_name
                
    def reset_log_files(self):
        with self.__files_lock:
            self.__file_names.clear()
                
    def add_log_file(self, file_name):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        if file_name is not None and len(file_name) > 0:
            if file_name == self.__root_file_name:
                raise TechnicalException(f"Log file '{file_name}' is already set as root log file")
            with self.__files_lock:
                if file_name in self.__file_names:
                    raise TechnicalException(f"Log file '{file_name}' is already set")
                self.__file_names.append(file_name)
    
    def remove_log_file(self, file_name):
        with self.__files_lock:
            if file_name is not None and len(file_name) > 0 and file_name in self.__file_names:
                self.__file_names.remove(file_name)
        
    def __new_console_handler(self):
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        
        res = logging.StreamHandler()
        res.setFormatter(logging.Formatter(fmt=self.format, style=self.style))
        if MultitaskManager.has_thread_native_id():
            res.addFilter(filter_thread_native_id)
        return res
    
    def set_config(self):
        # print(f"Set logging config: {LogConfig.default_level=} ; {self.on_console=} ; {self.in_file=} ; {self.__root_file_name=}")
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Set logging config: {LogConfig.default_level=} ; {self.on_console=} ; {self.in_file=} ; {self.__root_file_name=}")

        # if self.__config_file_path is not None:
        #     logging.config.fileConfig(self.__config_file_path, defaults=None, disable_existing_loggers=False)
        
        logger_ = logging.getLogger()

        # Update log destination to console
        if self.on_console:
            if self.__console_handler is not None:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug("Log destination already set to console.")
            else:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug("Adding log destination to console.")
                self.__console_handler = self.__new_console_handler()
                logger_.addHandler(self.__console_handler)
        else:
            if self.__console_handler is not None:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug("Removing log destination to console.")
                logger_.removeHandler(self.__console_handler)
                self.__console_handler = None
                
        # Update log destination to files
        with self.__files_lock:
            # Remove old log files
            # Note: root file is not removed if it is configured
            for file_name in list(self.__file_handlers.keys()):
                if file_name not in self.__file_names:
                    self.remove_file_handler(file_name, do_remove_log_file=False)
            
            # Add new log files
            if self.__root_file_name and not self.__root_file_handler:
                self.add_root_file_handler()
            for file_name in self.__file_names:
                if file_name not in list(self.__file_handlers.keys()):
                    self.add_file_handler(file_name)
        
        # level
        if logger_.getEffectiveLevel() != LogConfig.default_level:
            logger_.setLevel(LogConfig.default_level)
    
        # Loggers levels
        for name, level in self.__loggers_levels:
            if not name.startswith("#"):
                logging.getLogger(name).setLevel(level)
        
        # WARNING: For local debug only
        # logging.getLogger("holado_logging.common.logging.log_manager").setLevel(logging.DEBUG)
        
    def set_level(self, log_level, do_set_config=True):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        if isinstance(log_level, str):
            if hasattr(logging, log_level):
                log_level = getattr(logging, log_level)
            else:
                raise TechnicalException(f"Unexpected log level string '{log_level}'")
            
        LogConfig.default_level = log_level
        if do_set_config:
            self.set_config()
        
    def add_root_file_handler(self):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        
        logger_ = logging.getLogger()
            
        if not self.__root_file_name:
            raise TechnicalException("Root log file is not defined")
            
        if self.__root_file_handler is None:
            logger_.info("Creating file handler to root file '{}'.".format(self.__root_file_name))
            Path(os.path.dirname(self.__root_file_name)).mkdir(parents=True, exist_ok=True)
            
            self.__root_file_handler = logging.FileHandler(self.__root_file_name, mode='w', encoding='utf8')
            self.__root_file_handler.setFormatter(logging.Formatter(fmt=self.format, style=self.style))
            if MultitaskManager.has_thread_native_id():
                self.__root_file_handler.addFilter(filter_thread_native_id)
            
        logger_.addHandler(self.__root_file_handler)
        self.__root_file_handler_active = True
        
    def remove_root_file_handler(self, do_reset=False):
        logger_ = logging.getLogger()
        if self.__root_file_handler:
            logger_.info(f"Removing log destination to root file '{self.__root_file_name}'.")
            logger_.removeHandler(self.__root_file_handler)
            self.__root_file_handler_active = False
            if do_reset:
                self.__root_file_handler = None
        
    def add_file_handler(self, file_name, logger_=None):
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        
        if logger_ is None:
            logger_ = logging.getLogger()
            
        # In case this method is called outside "set_config" method, add file_name as a configured log_file
        if not self.has_log_file(file_name):
            self.add_log_file(file_name)
            
        if file_name in self.__file_handlers:
            logger_.debug("Log destination already set to file '{}'.".format(file_name))
        else:
            logger_.info("Adding log destination to file '{}'.".format(file_name))
            Path(os.path.dirname(file_name)).mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(file_name, mode='w', encoding='utf8')
            file_handler.setFormatter(logging.Formatter(fmt=self.format, style=self.style))
            if MultitaskManager.has_thread_native_id():
                file_handler.addFilter(filter_thread_native_id)
            
            self.__file_handlers[file_name] = file_handler
            logger_.addHandler(file_handler)
                
    def remove_file_handler(self, file_name, logger_=None, do_remove_log_file=True):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        if logger_ is None:
            logger_ = logging.getLogger()
            
        if file_name not in self.__file_handlers:
            raise TechnicalException(f"Not set log destination to file '{file_name}'")
        
        logger_.info("Removing log destination to file '{}'.".format(file_name))
        logger_.removeHandler(self.__file_handlers[file_name])
        del self.__file_handlers[file_name]
        
        if do_remove_log_file:
            self.remove_log_file(file_name)
    
    def __remove_existing_file_handlers(self, log_level_if_exists=None):
        with self.__files_lock:
            if len(self.__file_names) > 0:
                if log_level_if_exists is not None:
                    logger_ = logging.getLogger()
                    logger_.log(log_level_if_exists, f"Removing existing file handlers: {self.__file_names}")
                file_names = list(self.__file_names)
            else:
                file_names = []
        
        # Note: removes are done outside lock to avoid a deadlock
        for fn in file_names:
            self.remove_file_handler(fn)
    
    def enter_log_file(self, file_name, do_remove_root_file_handler=True, do_remove_other_file_handlers=True):
        if do_remove_other_file_handlers:
            self.__remove_existing_file_handlers(log_level_if_exists=logging.ERROR)
        
        self.add_file_handler(file_name)
        
        if do_remove_root_file_handler:
            self.remove_root_file_handler(do_reset=False)
            
    def leave_log_file(self, file_name, do_remove_log_file=True):
        if not self.__root_file_handler_active:
            self.add_root_file_handler()
        self.remove_file_handler(file_name, do_remove_log_file=do_remove_log_file)
    
    
    