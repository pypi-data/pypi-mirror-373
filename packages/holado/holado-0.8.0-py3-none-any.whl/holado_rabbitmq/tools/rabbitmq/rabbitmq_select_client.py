
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_multitask.multithreading.functionthreaded import FunctionThreaded
from holado_core.common.handlers.redo import Redo
from holado_core.common.exceptions.timeout_exception import TimeoutException
from holado_core.common.handlers.wait import WaitIsTrueOnEvent
from holado_rabbitmq.tools.rabbitmq.rabbitmq_client import RMQClient,\
    RMQPublisher
import queue
import threading
from holado_core.common.tools.tools import Tools


logger = logging.getLogger(__name__)


if RMQClient.is_available():
    import pika
    from pika.exceptions import ConnectionClosedByClient
    from pika.exchange_type import ExchangeType
    
    class RMQChannel(pika.channel.Channel):
        """
        Add features to pika.channel.Channel:
          - Confirm delivery
          - Automatically wait exchange, queue and bind are OK, like with a blocking connection
        """
        def __init__(self, connection, channel_number, on_open_callback):
            super().__init__(connection, channel_number, on_open_callback)
            self.__confirm_delivery = False
            self.__ack_nack_callback_func = None
            
        @property
        def has_confirm_delivery(self):
            return self.__confirm_delivery
        
        def set_confirm_delivery(self, wait_select_ok=True):
            if wait_select_ok:
                def callback_select_ok(method_frame):
                    if method_frame.method.NAME == 'Confirm.SelectOk':
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"[Channel {self.channel_number}] Confirm delivery mode is set")
                        return True
                    else:
                        raise TechnicalException(f"[Channel {self.channel_number}] Unexpected method frame {method_frame} (expected Confirm.SelectOk)")
                wait_declare_ok = WaitIsTrueOnEvent(f"wait confirm select is OK", callback_select_ok)
                
                self.confirm_delivery(self.__ack_nack_callback, wait_declare_ok.on_event)
                
                wait_declare_ok.execute()
            else:
                self.confirm_delivery(self.__ack_nack_callback)
                
            self.__confirm_delivery = True
            
        def set_ack_nack_callback(self, func):
            self.__ack_nack_callback_func = func
            
        def __ack_nack_callback(self, method_frame:pika.frame.Method):
            if self.__ack_nack_callback_func:
                self.__ack_nack_callback_func(method_frame)
        
        def exchange_declare(self, exchange, exchange_type=ExchangeType.direct, passive=False, durable=False, auto_delete=False, internal=False, arguments=None, wait_declare_ok=True):
            if wait_declare_ok:
                def callback_declare_ok(method_frame):
                    if method_frame.method.NAME == 'Exchange.DeclareOk':
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"[Channel {self.channel_number}] Exchange declare is OK")
                        return True
                    else:
                        raise TechnicalException(f"[Channel {self.channel_number}] Unexpected method frame {method_frame} (expected Exchange.DeclareOk)")
                wait_declare_ok = WaitIsTrueOnEvent(f"wait exchange declare is OK", callback_declare_ok)
                
                super().exchange_declare(exchange, exchange_type=exchange_type, passive=passive, durable=durable, auto_delete=auto_delete, internal=internal, arguments=arguments, callback=wait_declare_ok.on_event)
                
                wait_declare_ok.execute()
            else:
                return super().exchange_declare(exchange, exchange_type=exchange_type, passive=passive, durable=durable, auto_delete=auto_delete, internal=internal, arguments=arguments, callback=None)
        
        def queue_declare(self, queue, passive=False, durable=False, exclusive=False, auto_delete=False, arguments=None, wait_declare_ok=True):
            if wait_declare_ok:
                def callback_declare_ok(method_frame):
                    if method_frame.method.NAME == 'Queue.DeclareOk':
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"[Channel {self.channel_number}] Queue declare is OK")
                        return True
                    else:
                        raise TechnicalException(f"[Channel {self.channel_number}] Unexpected method frame {method_frame} (expected Queue.DeclareOk)")
                wait_declare_ok = WaitIsTrueOnEvent(f"wait queue declare is OK", callback_declare_ok)
                
                super().queue_declare(queue, passive=passive, durable=durable, exclusive=exclusive, auto_delete=auto_delete, arguments=arguments, callback=wait_declare_ok.on_event)
                
                wait_declare_ok.execute()
            else:
                return super().queue_declare(queue, passive=passive, durable=durable, exclusive=exclusive, auto_delete=auto_delete, arguments=arguments, callback=None)
        
        def queue_bind(self, queue, exchange, routing_key=None, arguments=None, wait_bind_ok=True):
            if wait_bind_ok:
                def callback_bind_ok(method_frame):
                    if method_frame.method.NAME == 'Queue.BindOk':
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"[Channel {self.channel_number}] Bind is OK")
                        return True
                    else:
                        raise TechnicalException(f"[Channel {self.channel_number}] Unexpected method frame {method_frame} (expected Queue.BindOk)")
                wait_bind_ok = WaitIsTrueOnEvent(f"wait bind is OK", callback_bind_ok)
                
                super().queue_bind(queue, exchange, routing_key=routing_key, arguments=arguments, callback=wait_bind_ok.on_event)
                
                wait_bind_ok.execute()
            else:
                return super().queue_bind(queue, exchange, routing_key=routing_key, arguments=arguments)


    class RMQSelectConnection(pika.adapters.select_connection.SelectConnection):
        """
        Add features to pika.adapters.select_connection.SelectConnection:
          - Be able to wait until connection is opened.
          - Be able to wait until channel is opened.
          - Use default on_xxx methods to raise on unexpected behaviour
        Note: start_ioloop is automatically started if wait_is_opened is True
        """
        def __init__(self, parameters=None,
                     on_open_callback=None,
                     on_open_error_callback=None,
                     on_close_callback=None,
                     custom_ioloop=None,
                     internal_connection_workflow=True, 
                     wait_is_opened=True):
            """
            Note: Parameters on_open_callback and on_open_error_callback are omitted if waiting until connection is opened.
            """
            # Declare first private variables in case of open error while closing
            self.__is_closing = False
            self.__on_close_callback = on_close_callback
            self.__ioloop_started = False
            self.__func_ioloop_start = None
            self.__channels = []
            
            if wait_is_opened:
                class WaitConnection(Redo):
                    def __init__(self):
                        super().__init__(f"redo connection is opened")
                        self.__connection = None
                        self.__exception = None
                        
                    def _process(self):
                        return (self.__connection, self.__exception)
                    
                    def on_open(self, connection):
                        self.__connection = connection
                    
                    def on_open_error(self, connection, exception):
                        self.__connection = connection
                        self.__exception = exception
                wait_connection = WaitConnection()
                wait_connection.redo_while( (None,None) )
                
                super().__init__(parameters=parameters,
                                 on_open_callback=wait_connection.on_open,
                                 on_open_error_callback=wait_connection.on_open_error,
                                 on_close_callback=self.__on_close,
                                 custom_ioloop=custom_ioloop,
                                 internal_connection_workflow=internal_connection_workflow)
                
                self.start_ioloop()
                conn, exc = wait_connection.execute()
                if exc is not None:
                    raise exc
                if conn is not self:
                    raise TechnicalException(f"Unexpected connection object after waiting open (obtained: {id(conn)} ; expected: {id(self)})")
            
            else:
                super().__init__(parameters=parameters,
                                 on_open_callback=on_open_callback,
                                 on_open_error_callback=on_open_error_callback,
                                 on_close_callback=self.__on_close,
                                 custom_ioloop=custom_ioloop,
                                 internal_connection_workflow=internal_connection_workflow)
        
        def __on_close(self, connection, exception):
            if not self.__is_closing and exception is not None:
                if isinstance(exception, ConnectionClosedByClient) and exception.reply_code != 200:
                    raise exception
            
            if self.__on_close_callback:
                self.__on_close_callback(connection, exception)
        
        def start_ioloop(self, in_thread=True, raise_if_already_started=True):
            if self.__ioloop_started and raise_if_already_started:
                raise TechnicalException(f"IO loop is already started")
            
            if in_thread:
                if self.__func_ioloop_start is not None and self.__func_ioloop_start.is_alive():
                    raise TechnicalException(f"IO loop is running in a thread")
                
                if self.__func_ioloop_start is None:
                    name = f"[Connection {id(self)}] start ioloop"
                    self.__func_ioloop_start = FunctionThreaded(self.start_ioloop, kwargs={'in_thread':False}, name=name)
                self.__func_ioloop_start.start()
            else:
                self.__ioloop_started = True
                self.ioloop.start()
                self.__ioloop_started = False
                
        def stop_ioloop(self):
            if self.__ioloop_started:
                # self.ioloop.stop()
                self.ioloop.add_callback_threadsafe(self.ioloop.stop)
                
        
        def channel(self, channel_number=None, on_open_callback=None, wait_is_opened=True):
            """
            Override channel method to enable waiting until channel is opened.
            Note: Parameter on_open_callback is omitted if waiting until channel is opened.
            """
            res = None
            
            if wait_is_opened:
                # Create wait redo
                class WaitChannel(Redo):
                    def __init__(self):
                        super().__init__(f"redo channel is opened")
                        self.__channel = None
                        
                    def _process(self):
                        return self.__channel
                    
                    def set_channel(self, channel):
                        self.__channel = channel
                        
                wait_channel = WaitChannel()
                wait_channel.with_timeout(3)
                wait_channel.redo_while_none()
                
                # Make maxium 3 retries
                nb_retries = 3
                for n in range(nb_retries):
                    # Call channel method
                    res = super().channel(channel_number=channel_number, on_open_callback=wait_channel.set_channel)
                    
                    try:
                        res = wait_channel.execute()
                    except TimeoutException as exc:
                        if n + 1 == nb_retries:
                            raise exc
                        else:
                            if Tools.do_log(logger, logging.DEBUG):
                                logger.debug("Channel was not open in time, retry")
                        continue
                    else:
                        break
            else:
                res = super().channel(channel_number=channel_number, on_open_callback=on_open_callback)
            
            if res is None:
                raise TechnicalException(f"Failed to get channel")
            self.__channels.append(res)
            
            return res

        def _create_channel(self, channel_number, on_open_callback):
            """Override _create_channel method to use RMQChannel instead of pika.channel.Channel"""
            return RMQChannel(self, channel_number, on_open_callback)


class RMQSelectClient(RMQClient):
    def __init__(self):
        super().__init__('RMQSelectClient')
    
    def _new_connection_parameters(self):
        connection_kwargs = self._connection_kwargs
        wait_connection = connection_kwargs.pop('wait_connection', True)
        return pika.ConnectionParameters(**connection_kwargs), wait_connection
    
    def _new_connection(self):
        if self.rapid_close:
            raise TechnicalException(f"Rapid close is not managed for select connection")
        connection_parameters, wait_connection = self._new_connection_parameters()
        return RMQSelectConnection(parameters=connection_parameters, wait_is_opened=wait_connection)
    
    def _close_connection(self, connection=None):
        if connection is None:
            connection = self.connection
        connection.stop_ioloop()
        super().stop_consuming()
    
    def _new_publisher(self, connection, channel, exchange, routing_key, nb_runners):
        res = RMQSelectPublisher(self, connection, channel, exchange, routing_key, nb_runners)
        return res
        

class RMQSelectPublisher(RMQPublisher):
    """
    Implementation of a publisher for long and intensive publishes.
    """
    
    def __init__(self, client, connection, channel, exchange, routing_key, nb_runners=None):
        super().__init__(client, connection, channel, exchange, routing_key)
        
        # Manage message publish
        self.__publish_lock = threading.Lock()
        self.__publish_nb_runners = nb_runners if nb_runners is not None else 100
        self.__publish_running_nb = 0
        self.__publish_queue = queue.Queue(maxsize=self.__publish_nb_runners * 2)
        self.__publish_counter = 0
        self.__published_counter = 0
        
        # Manage ack/nack
        self.__ack_counter = 0
        self.__nack_counter = 0
        self.__delivery_tag_counter = 0
        self.__ack_nack_lock = threading.Lock()
        # self.__ack_nack_queue = queue.Queue(maxsize=self.__publish_nb_runners * 2)
        self.__ack_nack_queue = queue.Queue()
        self.__last_log_index = 0
        
        # Set ack/nack callback
        channel.set_ack_nack_callback(self.__ack_nack_callback)

    def flush(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] flushing...")
        self.__publish_queue.join()
        self.__ack_nack_queue.join()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] flushed")

    def __publish_start(self):
        with self.__publish_lock:
            if self.__publish_running_nb < self.__publish_nb_runners:
                self.__publish_running_nb += 1
            else:
                return
        
        self.__publish_next()

    def __publish_next(self):
        try:
            msg_item = self.__publish_queue.get(block=False)
        except queue.Empty:
            with self.__publish_lock:
                self.__publish_running_nb -= 1
            return
        
        self.client.connection.ioloop.add_callback_threadsafe(
            lambda: self.__publish_message(msg_item[0], **msg_item[1]) )
        
        self.__publish_queue.task_done()

    def __publish_message(self, body, **kwargs):
        # Add delivery tag in queue
        with self.__ack_nack_lock:
            self.__delivery_tag_counter += 1
            del_tag = self.__delivery_tag_counter
        self.__ack_nack_queue.put(del_tag)
        
        # Publish message
        # RMQPublisher.publish(self, body, **kwargs)
        self.client.connection.ioloop.add_callback_threadsafe(
            lambda: RMQPublisher.publish(self, body, **kwargs) )
        self.__published_counter += 1

        # Manage to publish next message
        self.__publish_next()

    def publish(self, body, **kwargs):
        # Add message to publish in queue
        self.__publish_queue.put((body, kwargs))
        self.__publish_counter += 1

        # Start publishing if it is not already running
        self.__publish_start()
        
    def __ack_nack_callback(self, method_frame:pika.frame.Method):
        if method_frame.method.NAME == 'Basic.Ack':
            self.__ack_counter += 1
            del_tag_obtained = method_frame.method.delivery_tag
            del_tag_expected = self.__get_next_delivery_tag_from_ack_nack_queue()
            if method_frame.method.multiple:
                while del_tag_expected < del_tag_obtained:
                    del_tag_expected = self.__get_next_delivery_tag_from_ack_nack_queue()
                if del_tag_expected > del_tag_obtained:
                    raise TechnicalException(f"[{self.name}] Ack: inconsistent multiple delivery tags (obtained: {del_tag_obtained} ; expected: {del_tag_expected})")
            else:
                if del_tag_obtained != del_tag_expected:
                    raise TechnicalException(f"[{self.name}] Ack: inconsistent delivery tags (obtained: {del_tag_obtained} ; expected: {del_tag_expected})")
                
        elif method_frame.method.NAME == 'Basic.Nack':
            self.__nack_counter += 1
            del_tag_obtained = method_frame.method.delivery_tag
            del_tag_expected = self.__get_next_delivery_tag_from_ack_nack_queue()
            if del_tag_obtained != del_tag_expected:
                raise TechnicalException(f"[{self.name}] Nack: inconsistent delivery tags (obtained: {del_tag_obtained} ; expected: {del_tag_expected})")
            
        else:
            raise TechnicalException(f"Unexpected method frame {method_frame}")
        # if self.__delivery_tag_counter // 1000 != self.__last_log_index:
        #     logger.warning(f"++++++++++++++++++++++++++++++++++++++++ __ack_nack_callback: publish queue size: {self.__publish_queue.qsize()} ; delivery tag counter: {self.__delivery_tag_counter} ; ack/nack queue size: {self.__ack_nack_queue.qsize()}")
        #     self.__last_log_index = self.__delivery_tag_counter // 1000
            
    def __get_next_delivery_tag_from_ack_nack_queue(self):
        res = self.__ack_nack_queue.get(block=False)
        self.__ack_nack_queue.task_done()
        return res
    
    def _log_stats(self, level=logging.DEBUG):
        if Tools.do_log(logger, level):
            logger.log(level, f"[{self.name}] delivery tag: {self.__delivery_tag_counter} ; nack: {self.__nack_counter}")
        





