
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
import socket
from holado_python.standard_library.socket.socket import SocketClient
import abc
from holado_multitask.multithreading.loopfunctionthreaded import LoopFunctionThreaded
import selectors
from holado.common.handlers.undefined import undefined_argument
import time
import ssl

logger = logging.getLogger(__name__)


##########################################################################
## Clients
##########################################################################


class NonBlockingSocketClient(SocketClient):
    """
    Base class for blocking socket client.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, *, name=None, create_ipv4_socket_kwargs=None, idle_sleep_delay=undefined_argument, do_run_with_recv=True, do_run_with_send=True):
        self.__selector = selectors.DefaultSelector()
        
        # Note: __selector must be defined before, since Socket.__init__ can execute create_ipv4_socket
        super().__init__(name=name, create_ipv4_socket_kwargs=create_ipv4_socket_kwargs, idle_sleep_delay=idle_sleep_delay, do_run_with_recv=do_run_with_recv, do_run_with_send=do_run_with_send)

    def _delete_object(self):
        if self.internal_socket:
            # Note: stop must be done before unregistering selector
            self.stop()
            self.__selector.unregister(self.internal_socket)
        
        super()._delete_object()
    
    def _register_socket(self, sock):
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.__selector.register(sock, events, data=self._data)
    
    def start(self, *, read_bufsize=1024, read_kwargs=None, write_kwargs=None):
        """Start client event loop.
        """
        kwargs = {'read_bufsize':read_bufsize, 'read_kwargs':read_kwargs, 'write_kwargs':write_kwargs}
        thread = LoopFunctionThreaded(self._wait_and_process_events, kwargs=kwargs, register_thread=True, delay_before_run_sec=None)
        self._start_thread(thread)
    
    def _wait_and_process_events(self, *, read_bufsize=1024, read_kwargs=None, write_kwargs=None):
        has_activity = False
        events = self.__selector.select(timeout=None)
        for key, mask in events:
            has_activity |= self._service_connection(key, mask, read_bufsize=read_bufsize, read_kwargs=read_kwargs, write_kwargs=write_kwargs)
        
        # Wait before next loop if no data was exchanged
        if not has_activity and self._idle_sleep_delay is not None:
            time.sleep(self._idle_sleep_delay)

    def _service_connection(self, key, mask, *, read_bufsize=1024, read_kwargs=None, write_kwargs=None):
        has_activity = False
        read_kwargs = read_kwargs if read_kwargs is not None else {}
        write_kwargs = write_kwargs if write_kwargs is not None else {}
        
        sock = key.fileobj
        data = key.data
        if self.is_run_with_recv and mask & selectors.EVENT_READ:
            if self.is_with_ssl:
                # ssl doesn't suppôrt flags != 0
                flags = 0
            else:
                flags = read_kwargs.get('flags', 0)
            try:
                recv_data = sock.recv(read_bufsize, flags)
            except ssl.SSLWantReadError:
                recv_data = None
            if recv_data:
                has_activity = True
                with self._data_lock:      # data is self._data
                    data.in_bytes += recv_data
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[{self.name}] Received [{recv_data}] (type: {type(recv_data)} ; total: {len(data.in_bytes)})")
        
        if self.is_run_with_send and mask & selectors.EVENT_WRITE:
            with self._data_lock:      # data is self._data
                if data.out_bytes:
                    has_activity = True
                    try:
                        sent = sock.send(data.out_bytes)
                    except ssl.SSLWantWriteError:
                        sent = 0
                    if sent > 0:
                        data.out_bytes = data.out_bytes[sent:]
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"[{self.name}] Sent {sent} data (remaining to send: {len(data.out_bytes)})")
        
        return has_activity
    

class TCPNonBlockingSocketClient(NonBlockingSocketClient):
    """
    TCP socket client.
    """
    
    def __init__(self, *, name=None, create_ipv4_socket_kwargs=None, idle_sleep_delay=undefined_argument, do_run_with_recv=True, do_run_with_send=True):
        super().__init__(name=name, create_ipv4_socket_kwargs=create_ipv4_socket_kwargs, idle_sleep_delay=idle_sleep_delay, do_run_with_recv=do_run_with_recv, do_run_with_send=do_run_with_send)
    
    def create_ipv4_socket(self, host, port, **kwargs):
        socket_kwargs = self._new_ssl_context_if_required(**kwargs)
        
        if self.is_with_ssl:
            # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # sock = Socket.create_connection((host, port), do_connect=False, **socket_kwargs)
            sock = socket.create_connection((host, port), **socket_kwargs)
            sock.setblocking(False)
            
            wrap_socket_kwargs = self._ssl_wrap_socket_kwargs
            do_handshake_on_connect = wrap_socket_kwargs.pop('do_handshake_on_connect', False)
            sock = self._ssl_context.wrap_socket(sock, server_hostname=host, do_handshake_on_connect=do_handshake_on_connect, **wrap_socket_kwargs)
            self._set_internal_socket(sock, is_ssl_handshake_done_on_connect=do_handshake_on_connect)
            
            # sock.connect((host, port))
        else:
            sock = socket.create_connection((host, port), **socket_kwargs)
            sock.setblocking(False)
            self._set_internal_socket(sock)
        
        # Register socket
        self._register_socket(sock)







