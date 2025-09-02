
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
import selectors
from holado_python.standard_library.socket.non_blocking_socket import TCPNonBlockingSocketClient
import copy
import threading
from holado_python.standard_library.socket.blocking_socket import TCPBlockingSocketClient
from holado_core.common.tools.tools import Tools
from holado.common.handlers.undefined import undefined_argument

logger = logging.getLogger(__name__)


##########################################################################
## Clients
##########################################################################


class MessageSocketClient(object):
    """
    Base class for message socket client.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, separator=b'\n'):
        super().__init__()
        
        self.__separator = separator
        self.__messages_lock = threading.Lock()
        self.__messages = []

    @property
    def messages(self):
        with self.__messages_lock:
            return copy.copy(self.__messages)
    
    @property
    def nb_messages(self):
        with self.__messages_lock:
            return len(self.__messages)
    
    def _extract_messages_from_data(self, data):
        while True:
            ind = data.in_bytes.find(self.__separator)
            if ind >=0:
                msg = data.in_bytes[:ind]
                self._add_message(msg)
                data.in_bytes = data.in_bytes[ind+len(self.__separator):]
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[{self.name}] New message (total: {self.nb_messages}): {msg}")
                elif Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"[{self.name}] New message (total: {self.nb_messages})")
            else:
                break
        
    def _add_message(self, msg):
        with self.__messages_lock:
            self.__messages.append(msg)
    
    def reset_received_messages(self):
        with self.__messages_lock:
            self.__messages.clear()
        
    def read_message(self):
        res = None
        with self.__messages_lock:
            if len(self.__messages) > 0:
                res = self.__messages.pop(0)
        return res
    
    def read_messages(self):
        with self.__messages_lock:
            res = copy.copy(self.__messages)
            self.__messages.clear()
        return res
    
    def write_message(self, msg_bytes):
        self.write(msg_bytes + self.__separator)



class MessageTCPBlockingSocketClient(TCPBlockingSocketClient, MessageSocketClient):
    """
    Message socket client with TCP blocking socket.
    """
    def __init__(self, separator=b'\n', *, name=None, create_ipv4_socket_kwargs=None, idle_sleep_delay=undefined_argument):
        MessageSocketClient.__init__(self, separator)
        TCPBlockingSocketClient.__init__(self, name=name, create_ipv4_socket_kwargs=create_ipv4_socket_kwargs, idle_sleep_delay=idle_sleep_delay)

    def _process_recv_send(self, *, read_bufsize=1024, read_kwargs=None, write_kwargs=None):
        # Read from socket & write in socket
        super()._process_recv_send(read_bufsize=read_bufsize, read_kwargs=read_kwargs, write_kwargs=write_kwargs)
        
        # Extract messages from received data
        if self.is_run_with_recv:
            with self._data_lock:
                self._extract_messages_from_data(self._data)



class MessageTCPNonBlockingSocketClient(TCPNonBlockingSocketClient, MessageSocketClient):
    """
    Message socket client with TCP non-blocking socket.
    """
    def __init__(self, separator=b'\n', *, name=None, create_ipv4_socket_kwargs=None, idle_sleep_delay=undefined_argument):
        MessageSocketClient.__init__(self, separator)
        TCPNonBlockingSocketClient.__init__(self, name=name, create_ipv4_socket_kwargs=create_ipv4_socket_kwargs, idle_sleep_delay=idle_sleep_delay)

    def _service_connection(self, key, mask, *, read_bufsize=1024, read_kwargs=None, write_kwargs=None):
        # Read from socket & write in socket
        res = super()._service_connection(key, mask, read_bufsize=read_bufsize, read_kwargs=read_kwargs, write_kwargs=write_kwargs)
        
        # Extract messages from received data
        if mask & selectors.EVENT_READ:
            with self._data_lock:
                self._extract_messages_from_data(self._data)
        
        return res







