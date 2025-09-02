
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

import time
import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_rabbitmq.tools.rabbitmq.rabbitmq_client import RMQClient,\
    RMQPublisher
import threading
import queue
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing


logger = logging.getLogger(__name__)


if RMQClient.is_available():
    import pika
    from pika import exceptions
    from pika.adapters.blocking_connection import _CallbackResult
    
    class RMQBlockingChannel(pika.adapters.blocking_connection.BlockingChannel):
        """
        Add features to pika.adapters.blocking_connection.BlockingChannel:
          - Rapid close: possibility to rapidly close connection without data consistency verification.
                         It is useful when using consumers for monitoring, like in testing context.
          - Add time_limit parameter to start_consuming method.
        """
        def __init__(self, channel_impl, connection, rapid_close=False):
            super().__init__(channel_impl, connection)
            self.__rapid_close = rapid_close
            self.__is_closing = False
            self.__confirm_delivery = False
            self.__is_consuming = False
            self.__is_stopping_consuming = False
        
        def close(self, reply_code=0, reply_text="Normal shutdown"):
            self.__is_closing = True
            try:
                super().close(reply_code=reply_code, reply_text=reply_text)
            except ValueError as exc:
                if self.__rapid_close and "file descriptor cannot be a negative integer" in str(exc):
                    # This exception can appear during channel close with rapid close option
                    pass
                else:
                    raise exc
        
        def _flush_output(self, *waiters):
            if self.__rapid_close and self.__is_closing:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Channel is closing, bypass output flush for rapid close")
            else:
                super()._flush_output(*waiters)
            
        def start_consuming(self, time_limit=None, time_limit_on_stop=None):
            """
            Override start_consuming method to add time_limit parameter.
            """
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self}] Start consuming...")
            self.__is_consuming = True
            try:
                if not self.__rapid_close and time_limit is None and time_limit_on_stop is None:
                    # Use pika implementation
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"[{self}] Start consuming with Pika implementation")
                    return super().start_consuming()
                else:
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"[{self}] Start consuming with HolAdo implementation")
                    
                # Check if called from the scope of an event dispatch callback
                with self.connection._acquire_event_dispatch() as dispatch_allowed:
                    if not dispatch_allowed:
                        raise exceptions.ReentrancyError(
                            'start_consuming may not be called from the scope of '
                            'another BlockingConnection or BlockingChannel callback')
                
                self._impl._raise_if_not_open()
                
                # Process events as long as consumers exist on this channel
                while self._consumer_infos:
                    # This will raise ChannelClosed if channel is closed by broker
                    if self.__is_stopping_consuming:
                        t_limit = time_limit_on_stop
                        if self.__rapid_close and t_limit is None:
                            # To ensure a rapid close, time_limit shouldn't be None, set it to 0 while stopping consuming
                            t_limit = 0
                    else:
                        t_limit = time_limit
                    if t_limit is None and self.__rapid_close:
                        # To ensure a rapid close, time_limit shouldn't be None, set it to 0.1s as a compromise between rapidity and resource cost 
                        t_limit = 0.1
                    
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[{self}] Processing data events (time_limit={t_limit})")
                    self._process_data_events(time_limit=t_limit)
            finally:
                self.__is_consuming = False
                self.__is_stopping_consuming = False
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"[{self}] Finished start consuming")
        
        def stop_consuming(self, consumer_tag=None):
            self.__is_stopping_consuming = True
            super().stop_consuming(consumer_tag=consumer_tag)
        
        @property
        def has_confirm_delivery(self):
            return self._delivery_confirmation
        
        def set_confirm_delivery(self):
            self.confirm_delivery()
            


    class RMQBlockingConnection(pika.adapters.blocking_connection.BlockingConnection):
        """
        Add features to pika.adapters.blocking_connection.BlockingConnection:
          - Rapid close: possibility to rapidly close connection without data consistency verification.
                         It is useful when using consumers for monitoring, like in testing context.
        """
        def __init__(self, parameters=None, _impl_class=None, rapid_close=False):
            super().__init__(parameters, _impl_class)
            self.__rapid_close = rapid_close
            self.__is_closing = False

        def channel(self, channel_number=None):
            """
            Override channel method to use RMQBlockingChannel instead of BlockingChannel.
            The implementation is a copy of BlockingConnection.channel.
            """
            with _CallbackResult(self._OnChannelOpenedArgs) as opened_args:
                impl_channel = self._impl.channel(
                    channel_number=channel_number,
                    on_open_callback=opened_args.set_value_once)
    
                # Create our proxy channel
                channel = RMQBlockingChannel(impl_channel, self, rapid_close=self.__rapid_close)
    
                # Link implementation channel with our proxy channel
                impl_channel._set_cookie(channel)
    
                # Drive I/O until Channel.Open-ok
                channel._flush_output(opened_args.is_ready)
            
            return channel

        def close(self, reply_code=200, reply_text='Normal shutdown'):
            self.__is_closing = True
            super().close(reply_code=reply_code, reply_text=reply_text)
            
        def _flush_output(self, *waiters):
            if self.__rapid_close and self.__is_closing:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Connection is closing, bypass output flush for rapid close")
            else:
                super()._flush_output(*waiters)
                

class RMQBlockingClient(RMQClient):
    USE_RMQBlockingPublisher = True
    
    def __init__(self):
        super().__init__('RMQBlockingClient')
    
    def close(self):
        super().close()
        
        # Close all consumers connections
        for obj_kwargs in self._consumer_and_kwargs:
            connection = obj_kwargs.object.connection
            if connection and connection.is_open:
                self._close_connection(connection)
            
        for obj_kwargs in self._buffer_consumer_and_kwargs:
            connection = obj_kwargs.object.connection
            if connection and connection.is_open:
                self._close_connection(connection)
    
    def _new_connection(self):
        res = None
        connection_parameters = self._new_connection_parameters()
        
        last_exception = None
        for _ in range(300):
            try:
                res = RMQBlockingConnection(connection_parameters, rapid_close=self.rapid_close)
                break
            except pika.exceptions.IncompatibleProtocolError as exc:
                is_same_exception = str(last_exception) == str(exc) if last_exception else False
                if not last_exception or not is_same_exception:
                    logger.exception("Retry after possible temporary incompatible protocol errors while trying to connect with a blocking connection")
                    last_exception = exc
                elif is_same_exception:
                    logger.warning("Retry after same exception")
                time.sleep(0.1)
            except Exception as exc:
                is_same_exception = str(last_exception) == str(exc) if last_exception else False
                if not last_exception or not is_same_exception:
                    logger.exception("Retry after unexpected exception while trying to connect with a blocking connection")
                    last_exception = exc
                elif is_same_exception:
                    logger.warning("Retry after same exception")
                time.sleep(0.1)
                
        if res is None:
            raise TechnicalException(f"Failed to connect with a blocking connection and parameters [{connection_parameters}]. Last error was (more details in report): {last_exception} (type: {Typing.get_object_class_fullname(last_exception)})")
        return res
    
    def _new_publisher(self, connection, channel, exchange, routing_key, nb_runners):
        if self.USE_RMQBlockingPublisher:
            res = RMQBlockingPublisher(self, connection, channel, exchange, routing_key, nb_runners)
        else:
            res = RMQSimpleBlockingPublisher(self, connection, channel, exchange, routing_key)
        return res
        
    def new_consumer(self, queue, message_callback, queue_args=None, exchange="", exchange_args=None, bind_args=None):
        if not self.has_consumer and not self.has_buffer_consumer:
            # Use default connection for first consumer or buffer consumer
            return super().new_consumer(queue, message_callback, queue_args=queue_args, exchange=exchange, exchange_args=exchange_args, bind_args=bind_args)
        
        # Note: A new blocking connection is needed for each consumer due to multitasking possibilities of holado_rabbitmq.
        #       When a client hosts many consumers and start_consuming is called on it (RMQClient.start_consuming), 
        #       the method start_consuming is called in a separated thread for each consumer. But current implementation
        #       of BlockingChannel supposes that all pika methods are called in the same thread.
        connection = self._new_connection()
        return self._new_consumer_with_connection(connection, queue, message_callback, queue_args, exchange, exchange_args, bind_args)
    
    def new_buffer_consumer(self, queue, queue_args=None, exchange="", exchange_args=None, bind_args=None):
        if not self.has_consumer and not self.has_buffer_consumer:
            # Use default connection for first consumer or buffer consumer
            return super().new_buffer_consumer(queue, queue_args=queue_args, exchange=exchange, exchange_args=exchange_args, bind_args=bind_args)
        
        # Note: A new blocking connection is needed for each consumer due to multitasking possibilities of holado_rabbitmq.
        #       When a client hosts many consumers and start_consuming is called on it (RMQClient.start_consuming), 
        #       the method start_consuming is called in a separated thread for each consumer. But current implementation
        #       of BlockingChannel supposes that all pika methods are called in the same thread.
        connection = self._new_connection()
        return self._new_buffer_consumer_with_connection(connection, queue, queue_args=queue_args, exchange=exchange, exchange_args=exchange_args, bind_args=bind_args)
    
class RMQBlockingPublisher(RMQPublisher):
    """
    Implementation of a publisher for long and intensive publishes.
    """
    
    def __init__(self, client, connection, channel, exchange, routing_key, nb_runners=None):
        super().__init__(client, connection, channel, exchange, routing_key)

        self.__publish_lock = threading.Lock()
        self.__publish_nb_runners = nb_runners if nb_runners is not None else 10
        self.__publish_running_nb = 0
        self.__publish_queue = queue.Queue(maxsize=self.__publish_nb_runners * 2)
        self.__publish_counter = 0
        self.__published_counter = 0

    def flush(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] flushing...")
        self.__publish_queue.join()
        while self.__published_counter < self.__publish_counter:
            time.sleep(0.01)
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
        
        # Note: following code doesn't seem to be more efficient, thus it is commented
        # if self.client.is_in_connection_thread:
        #     self.client.connection.call_later(0, lambda: self.__publish_message(msg_item[0], **msg_item[1]))
        # else:
        #     self.client.connection.add_callback_threadsafe(
        #         lambda: self.__publish_message(msg_item[0], **msg_item[1])
        #         )
        self.client.connection.add_callback_threadsafe(
            lambda: self.__publish_message(msg_item[0], **msg_item[1]) )
        
        self.__publish_queue.task_done()

    def __publish_message(self, body, **kwargs):
        # Publish message
        RMQPublisher.publish(self, body, **kwargs)
        self.__published_counter += 1

        # Manage to publish next message
        self.__publish_next()

    def publish(self, body, **kwargs):
        # Start data events processing if needed
        self.client.start_process_data_events(raise_if_already_started=False)
        
        # Add message to publish in queue
        self.__publish_queue.put((body, kwargs))
        self.__publish_counter += 1

        # Start publishing if it is not already running
        self.__publish_start()

class RMQSimpleBlockingPublisher(RMQPublisher):
    """
    Simple implementation of a publisher
    """
    def __init__(self, client, connection, channel, exchange, routing_key):
        super().__init__(client, connection, channel, exchange, routing_key)
        


