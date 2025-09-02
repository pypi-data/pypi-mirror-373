
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

import pprint
import sys
import threading
import subprocess
import logging
import time
from enum import IntEnum
from holado_core.common.exceptions.functional_exception import FunctionalException
import copy
import signal
from holado_core.common.tools.tools import Tools
from holado_multitask.multitasking.multitask_manager import MultitaskManager

logger = logging.getLogger(__name__)


class CommandStates(IntEnum):
    """States of a command."""
    Ready = 1
    Running = 2
    Success = 3
    Error = 4


class Command(threading.Thread):
    """
    Execute a command in a thread.
    """

    def __init__(self, cmd, do_log_output = False, do_raise_on_stderr = False, **subprocess_kwargs):
        """
        'cmd' argument can be a list or a str. If the global command should contain a '"' in any argument, it is recommanded to pass 'cmd' as a str.
        """
        super().__init__()

        # Put thread as daemon
        self.daemon = True
        
        self.cmd = cmd
        self.__do_log_output = do_log_output
        self.__do_raise_on_stderr = do_raise_on_stderr
        
        self.__process = None
        self.__state = CommandStates.Ready
        self.__stdout = None
        self.__stderr = None
        self.__error = None
        self.__callback = None
        self.__callback_delay_ms = None
        self.__external_parameters = {}
        self.__subprocess_kwargs = subprocess_kwargs
        self.__stop_signal = signal.SIGTERM

 
    @property
    def stdout(self):
        return self.__stdout
 
    @property
    def stderr(self):
        return self.__stderr
 
    @property
    def error(self):
        return self.__error
 
    @error.setter
    def error(self, err):
        """Set error (an exception)."""
        if not isinstance(err, Exception):
            raise Exception("An exception is expected")
        self.__error = err
        self.__state = CommandStates.Error

    @property
    def _internal_process(self):
        return self.__process
    
    @property
    def state(self):
        return self.__state
    
    @property
    def return_code(self):
        if self.__process:
            return self.__process.returncode
        else:
            return None
    
    @property
    def callback(self):
        return self.__callback
    
    @callback.setter
    def callback(self, callback):
        """Set callback called when execution end."""
        self.__callback = callback
    
    @property
    def callback_delay_ms(self):
        return self.__callback_delay_ms
    
    @callback_delay_ms.setter
    def callback_delay_ms(self, delay_ms):
        """Set callback delay in ms."""
        self.__callback_delay_ms = delay_ms
    
    @property
    def external_parameters(self):
        return self.__external_parameters
    
    @property
    def stop_signal(self):
        return self.__stop_signal
    
    @stop_signal.setter
    def stop_signal(self, stop_signal):
        """Set stop signal."""
        self.__stop_signal = stop_signal
    
    def run(self):
        logger.debug("Call command: {}".format(self.cmd))
        try:
            self.__state = CommandStates.Running
            
            kwargs = copy.copy(self.__subprocess_kwargs)
            kwargs['universal_newlines'] = True
            if isinstance(self.cmd, str):
                self.__process = subprocess.Popen(self.cmd,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  shell=True,
                                                  **kwargs)
            else:
                self.__process = subprocess.Popen(self.cmd,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  shell=False,
                                                  **kwargs)
            
            self.__stdout = ""
            self.__stderr = ""
            while self.__process.returncode is None:
                # Wait a small time and in same time yield this thread
                time.sleep(0.001)
                
                self.__process.poll()
                self.__read_stdout_stderr()
            
            # Manage end status
            if self.return_code == 0:
                self.__state = CommandStates.Success
            else:
                self.__state = CommandStates.Error
            
            # Manage error
            if self.__do_raise_on_stderr:
                self.__raise_exception_if_stderr()

            # Print result
            if self.__do_log_output:
                msg = "Output of command {}:\n{}\n{}\n{}".format(self.cmd, '<'*10, self.stdout, '>'*10)
                logger.debug(msg)

        except Exception as exc:
            self.error = exc
            
        finally:
            if self.callback:
                if self.callback_delay_ms:
                    delay_s = self.callback_delay_ms / 1000.
                    logger.debug(f"Command [{self.cmd}] has finished, call callback in {delay_s} seconds")
                    t = threading.Timer(delay_s, self.callback, [self])
                    t.start()
                else:
                    logger.debug(f"Command [{self.cmd}] has finished, calling callback...")
                    self.callback(self)
            elif self.error is not None:
                logger.error(f"Command [{self.cmd}] has finished on error: {self.error}")
            elif self.state == CommandStates.Error:
                logger.error(f"Command [{self.cmd}] has finished on error code {self.return_code} and stderr: {self.stderr}")
            elif self.state != CommandStates.Success:
                logger.warning(f"Command [{self.cmd}] has finished with status {self.state.name}")
            else:
                logger.debug(f"Command [{self.cmd}] has succeeded")
    
    def __read_stdout_stderr(self):
        # Get results
        out = self.__process.stdout.read()
        if len(out) > 0:
            if sys.version_info < (3,0):
                self.__stdout += out.decode('utf-8')
            else:
                self.__stdout += out
#                     logger.debug("[CMD OUT] | " + out)
        err = self.__process.stderr.read()
        if len(err) > 0:
            if sys.version_info < (3,0):
                self.__stderr += err.decode('utf-8')
            else:
                self.__stderr += err
#                     logger.error("[CMD ERR] | " + out)
                
    def __raise_exception_if_stderr(self):
        if len(self.stderr) > 0:
            msg = "Standard Error:\n{}\n{}\n{}".format('<'*7, self.stderr, '>'*7)
            if len(self.stdout) > 0:
                msg += "\nStandard Output:\n{}\n{}\n{}".format('<'*7, self.stdout, '>'*7)
            raise FunctionalException(msg)
        
    def kill(self):
        # Note: kill is equivalent to terminate in subprocess implementation
        if self.state == CommandStates.Running:
            self.__process.kill() 
                       
    def terminate(self):
        if self.state == CommandStates.Running:
            self.__process.terminate()
    
    def stop(self):
        if self.state == CommandStates.Running:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Stopping command [{self.cmd}] with signal {self.__stop_signal} and PID {self.__process.pid}")
            
            MultitaskManager.kill_process(self.__process.pid, sig=self.__stop_signal, do_kill_children=True, recursively=True)
    
    def __repr__(self):
        return pprint.pformat({'cmd' : self.cmd,
                               'is alive' : self.is_alive() })
            