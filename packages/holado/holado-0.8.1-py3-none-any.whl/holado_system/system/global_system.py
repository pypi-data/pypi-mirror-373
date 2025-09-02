
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
from holado.common.handlers.enums import AutoNumber
import platform
from holado_core.common.exceptions.technical_exception import TechnicalException
import time
import os
from holado_core.common.tools.tools import Tools
import threading
from holado_core.common.tools.converters.converter import Converter

logger = logging.getLogger(__name__)



class OSTypes(AutoNumber):
    """
    Types of operating systems.
    """
    Windows = ()
    MacOS = ()
    Linux = ()
    Other = ()


class GlobalSystem(object):
    """
    System methods.
    """
    __detected_os_type:OSTypes = None
    __detected_os_version = None

    @classmethod
    def get_os_type(cls):
        """
        Detect the operating system from the os.name System property and cache
        the result
        @return the operating system detected
        """
        if cls.__detected_os_type is None:
            os_ = platform.system()
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Detected OS: {os_}")
            if os_ == 'Darwin':
                cls.__detected_os_type = OSTypes.MacOS
            elif os_ == 'Windows':
                cls.__detected_os_type = OSTypes.Windows
            elif os_ == 'Linux':
                cls.__detected_os_type = OSTypes.Linux
            else:
                cls.__detected_os_type = OSTypes.Other
            logger.info(f"Detected OS type: {cls.__detected_os_type.name}")
        return cls.__detected_os_type

    @classmethod
    def get_os_version(cls):
        """
        Detect the operating system from the os.name System property and cache
        the result
        @return the operating system detected
        """
        if cls.__detected_os_version is None:
            cls.__detected_os_version = platform.release()
            if '-' in cls.__detected_os_version:
                cls.__detected_os_version = cls.__detected_os_version[:cls.__detected_os_version.index('-')]
            logger.info(f"Detected OS version: {cls.__detected_os_version}")
        return cls.__detected_os_version

    @classmethod
    def execute_curl(cls, curl_parameters, do_log_output=False):
        cmd = f"curl {curl_parameters}"
        return cls.execute_command(cmd, do_log_output=do_log_output, do_raise_on_stderr=False)

    @classmethod
    def execute_command(cls, cmd, do_log_output=False, do_raise_on_stderr=False):
        from holado_system.system.command.command import Command, CommandStates
        from holado_system.system.command.command_result import CommandResult
        
        command = Command(cmd, do_log_output=do_log_output, do_raise_on_stderr=do_raise_on_stderr)
        command.start()
        command.join()
        
        if command.state == CommandStates.Error:
            raise TechnicalException(f"Error while executing command [{cmd}]: [{command.error if command.error else command.stderr}]")
        return CommandResult(cmd, command.stdout, command.stderr)
    
    @classmethod
    def log_resource_usage(cls, prefix=None, level=logging.DEBUG, logger_=None):
        # cls.log_memory_usage(prefix, level, logger_)
        
        # Log all resources usage of this process and children processes
        if cls.get_os_type() == OSTypes.Linux:
            import resource
            cls.__log_resource_usage(resource.RUSAGE_SELF, None, None, prefix, level, logger_)
            cls.__log_resource_usage(resource.RUSAGE_CHILDREN, None, None, prefix, level, logger_)
        else:
            raise NotImplementedError(f"Not implemented for OS type '{cls.get_os_type().name}'")
        
        # Log threads
        cls.__log_threads(prefix, level, logger_)
    
    @classmethod
    def log_memory_usage(cls, prefix=None, level=logging.DEBUG, logger_=None):
        if cls.get_os_type() == OSTypes.Linux:
            import resource
            cls.__log_resource_usage(resource.RUSAGE_SELF, 'maxrss', 'maximum resident set size', prefix, level, logger_)
            cls.__log_resource_usage(resource.RUSAGE_CHILDREN, 'maxrss', 'maximum resident set size', prefix, level, logger_)
        else:
            raise NotImplementedError(f"Not implemented for OS type '{cls.get_os_type().name}'")
    
    @classmethod
    def __log_resource_usage(cls, which_process=None, resource_attr_name=None, resource_description=None, prefix=None, level=logging.DEBUG, logger_=None):
        if logger_ is None:
            logger_ = logger
        if not logger_.isEnabledFor(level):
            return
        
        if cls.get_os_type() == OSTypes.Linux:
            import resource
            if which_process is None:
                which_process = resource.RUSAGE_SELF
            
            ru = resource.getrusage(which_process)
            field_names = ['utime', 'stime', 'maxrss', 'minflt', 'majflt', 'inblock', 'oublock', 'nvcsw', 'nivcsw']
            resource_usage = {fn:getattr(ru, f'ru_{fn}') for fn in field_names}
            
            if which_process == resource.RUSAGE_SELF:
                usage_descr = "Process resource usage"
            elif which_process == resource.RUSAGE_CHILDREN:
                usage_descr = "Child processes resource usage"
            else:
                usage_descr = "Other resource usage"
            if resource_attr_name is not None:
                logger_.log(level, f"{prefix if prefix else ''}{usage_descr}: {resource_description} = {getattr(resource_usage, resource_attr_name)}")
            else:
                logger_.log(level, f"{prefix if prefix else ''}{usage_descr}: {resource_usage}")
        else:
            raise NotImplementedError(f"Not implemented for OS type '{cls.get_os_type().name}'")
    
    @classmethod
    def __log_threads(cls, prefix=None, level=logging.DEBUG, logger_=None):
        if logger_ is None:
            logger_ = logger
        if not logger_.isEnabledFor(level):
            return
        
        thread_names = [t.name for t in threading.enumerate()]
        logger_.log(level, f"{prefix if prefix else ''}Process has {len(thread_names)} threads: {thread_names}")
        
    @classmethod
    def yield_processor(cls):
        if cls.get_os_type() == OSTypes.Windows:
            time.sleep(0.0001)
        else:
            os.sched_yield()
    
    @classmethod
    def get_used_ports(cls):
        if cls.get_os_type() == OSTypes.Linux:
            cmd = "netstat -tunlep | grep LISTEN | awk '{print $4}' | awk '{gsub(\".*:\",\"\");print}'"
            result = cls.execute_command(cmd, do_log_output=False, do_raise_on_stderr=False)
            res = [Converter.to_integer(v) for v in result.output.split('\n') if len(v) > 0]
            return res
        else:
            raise NotImplementedError(f"Not implemented for OS type '{cls.get_os_type().name}'")
    
    @classmethod
    def get_first_available_anonymous_port(cls):
        used_ports = cls.get_used_ports()
        for port in range(32768, 65536):
            if port not in used_ports:
                return port
        return None
    
    