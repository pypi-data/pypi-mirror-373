
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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools
from typing import NamedTuple
import threading
from holado.common.handlers.object import DeleteableObject, Object
from holado.common.handlers.enums import ObjectStates
from holado_multitask.multithreading.functionthreaded import FunctionThreaded
from holado_core.common.handlers.redo import Redo
from holado_system.system.filesystem.file import File
from holado_core.common.exceptions.verify_exception import VerifyException
import abc
from holado_multitask.multithreading.loopfunctionthreaded import LoopFunctionThreaded
from holado_multitask.multitasking.multitask_manager import MultitaskManager


logger = logging.getLogger(__name__)

try:
    import pika  # @UnresolvedImport @UnusedImport
    from pika.exceptions import ConnectionWrongStateError, StreamLostError
    with_pika = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"RMQClient is not available. Initialization failed on error: {exc}")
    with_pika = False



class RMQClient(DeleteableObject):
    __metaclass__ = abc.ABCMeta
    
    @classmethod
    def is_available(cls):
        return with_pika
    
    def __init__(self, name):
        super().__init__(name)
        
        self.__connection_kwargs = None
        self.__publisher_and_kwargs = []
        self.__consumer_and_kwargs = []
        self.__buffer_consumer_and_kwargs = []
        
        self.__connection = None
        self.__connection_thread_id = None
        
        self.__is_consuming = False
        self.__is_stopping_consuming = False
        self.__rapid_close = False
        
        self.__process_data_events_thread = None
        self.__is_processing_data_events = False
        self.__is_stopping_processing_data_events = False
    
    def _delete_object(self):
        try:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Deleting RabbitMQ client...")
            self.close()
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Finished to delete RabbitMQ client")
        except StreamLostError as exc:
            if self.object_state == ObjectStates.Deleting:
                pass
            else:
                raise exc
        
    @property
    def connection(self):
        return self.__connection
    
    @property
    def _connection_kwargs(self):
        return self.__connection_kwargs
    
    @property
    def is_in_connection_thread(self):
        return MultitaskManager.get_thread_id() == self.__connection_thread_id
    
    @property
    def is_consuming(self):
        return self.__is_consuming
    
    @property
    def is_processing_data_events(self):
        return self.__is_processing_data_events
    
    @property
    def rapid_close(self):
        return self.__rapid_close
    
    @rapid_close.setter
    def rapid_close(self, rapid_close):
        self.__rapid_close = rapid_close
    
    @property
    def has_consumer(self):
        return len(self.__consumer_and_kwargs) > 0
    
    @property
    def _consumer_and_kwargs(self):
        return self.__consumer_and_kwargs
    
    @property
    def has_buffer_consumer(self):
        return len(self.__buffer_consumer_and_kwargs) > 0
    
    @property
    def _buffer_consumer_and_kwargs(self):
        return self.__buffer_consumer_and_kwargs
    
    @property
    def has_publisher(self):
        return len(self.__publisher_and_kwargs) > 0
    
    @property
    def _publisher_and_kwargs(self):
        return self.__publisher_and_kwargs
    
    def _set_connection(self, connection):
        self.__connection = connection
        self.__connection_thread_id = MultitaskManager.get_thread_id()
        
    def _build_and_save_connection_parameters_kwargs(self, **connection_parameters_kwargs):
        if Tools.has_sub_kwargs(connection_parameters_kwargs, "authentication."):
            authentication = Tools.pop_sub_kwargs(connection_parameters_kwargs, "authentication.")
            if 'user' in authentication:
                if type(authentication['user']) is tuple:
                    connection_parameters_kwargs['credentials'] = pika.PlainCredentials(authentication['user'][0], authentication['user'][1])
                else:
                    raise FunctionalException(f"[{self.name}]When authenticating by user, the value has to be in format: ('{{USER}}', '{{PASSWORD}}')  (obtained: {authentication['user']})")
            else:
                raise TechnicalException(f"[{self.name}]Unmanaged authentication type '{authentication.keys()}' (possible authentication types: 'user'")

        self.__connection_kwargs = connection_parameters_kwargs
        
    def _new_connection_parameters(self):
        return pika.ConnectionParameters(**self._connection_kwargs)
    
    @abc.abstractmethod
    def _new_connection(self):
        raise NotImplementedError()
    
    def connect(self, **connection_parameters_kwargs):
        """Connect with client appropriate connection"""
        self._build_and_save_connection_parameters_kwargs(**connection_parameters_kwargs)
        connection = self._new_connection()
        self._set_connection(connection)
    
    def close(self):
        # Stop consuming
        if self.is_consuming:
            self.stop_consuming()
            
        # Stop processing data events
        if self.is_processing_data_events:
            self.stop_process_data_events()
            
        # Close connection
        if self.__connection and self.__connection.is_open:
            self._close_connection()
        
    def _close_connection(self, connection=None):
        if connection is None:
            connection = self.connection
            
        if connection is None or not connection.is_open:
            raise TechnicalException(f"[{self.name}] Connection is not opened")
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Closing connection ({id(connection)})...")
        
        try:
            self.__connection.close()
        except (StreamLostError, ConnectionWrongStateError):
            pass
        except Exception as exc:  # @UnusedVariable
            #TODO: When this warning is logged during self.__del__, the log is cleared before, thus it is commented
            # logger.warn(f"Error catched while closing RabbitMQ client connection:\n{Tools.represent_exception(exc)}")
            # pass
            raise exc
        
    def __new_object_kwargs(self, obj, **kwargs):
        res = NamedTuple('ObjectKwargs', object=object, kwargs=dict)
        res.object = obj
        res.kwargs = kwargs
        return res

    def new_publisher(self, queue, queue_args=None, exchange="", exchange_args=None, routing_key=None, nb_runners=None):
        return self._new_publisher_with_connection(self.connection, queue, queue_args, exchange, exchange_args, routing_key, nb_runners)

    def _new_publisher_with_connection(self, connection, queue, queue_args=None, exchange="", exchange_args=None, routing_key=None, nb_runners=None):
        pub_channel = connection.channel()
        
        queue_name = self._prepare_queue(pub_channel, queue, queue_args, exchange, exchange_args, bind_args=None)
        if self.connection.publisher_confirms:
            pub_channel.set_confirm_delivery()
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Connection doesn't support publisher confirms")

        if routing_key:
            res = self._new_publisher(connection, pub_channel, exchange, routing_key, nb_runners)
        else:
            # TODO EKL: verify this case is functional
            res = self._new_publisher(connection, pub_channel, exchange, queue_name, nb_runners)
            
        self.__publisher_and_kwargs.append( self.__new_object_kwargs(res, queue=queue, queue_args=queue_args, exchange=exchange, exchange_args=exchange_args, routing_key=routing_key, nb_runners=nb_runners) )
        return res
    
    def _new_publisher(self, connection, channel, exchange, routing_key, nb_runners):
        raise NotImplementedError
        
    def new_consumer(self, queue, message_callback, queue_args=None, exchange="", exchange_args=None, bind_args=None):
        return self._new_consumer_with_connection(self.connection, queue, message_callback, queue_args, exchange, exchange_args, bind_args)
        
    def _new_consumer_with_connection(self, connection, queue, message_callback, queue_args=None, exchange="", exchange_args=None, bind_args=None):
        con_channel = connection.channel()
        
        if self.is_consuming:
            raise FunctionalException(f"[{self.name}] Not allowed to create a new consumer while consuming is started")
        queue_name = self._prepare_queue(con_channel, queue, queue_args, exchange, exchange_args, bind_args)
        res = RMQConsumer(self, connection, con_channel, queue_name, message_callback)
        self.__consumer_and_kwargs.append( self.__new_object_kwargs(res, queue=queue, message_callback=message_callback, queue_args=queue_args, exchange=exchange, exchange_args=exchange_args, bind_args=bind_args) )
        return res
        
    def new_buffer_consumer(self, queue, queue_args=None, exchange="", exchange_args=None, bind_args=None):
        return self._new_buffer_consumer_with_connection(self.connection, queue, queue_args, exchange, exchange_args, bind_args)
        
    def _new_buffer_consumer_with_connection(self, connection, queue, queue_args=None, exchange="", exchange_args=None, bind_args=None):
        con_channel = connection.channel()
        
        if self.is_consuming:
            raise FunctionalException(f"[{self.name}] Not allowed to create a new consumer while consuming is started")
        queue_name = self._prepare_queue(con_channel, queue, queue_args, exchange, exchange_args, bind_args)
        res = RMQBufferConsumer(self, connection, con_channel, queue_name)
        self.__buffer_consumer_and_kwargs.append( self.__new_object_kwargs(res, queue=queue, queue_args=queue_args, exchange=exchange, exchange_args=exchange_args, bind_args=bind_args) )
        return res
        
    def start_consuming(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Start consuming...")
        self.__is_consuming = True
        
        for obj_kwargs in self.__consumer_and_kwargs:
            obj_kwargs.object.start_consuming_in_thread()
            
        for obj_kwargs in self.__buffer_consumer_and_kwargs:
            obj_kwargs.object.start_consuming_in_thread()
        
    def stop_consuming(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Beginning stop consuming...")
        self.__is_stopping_consuming = True
        consumers_exceptions = []
        try:
            for obj_kwargs in self.__consumer_and_kwargs:
                try:
                    obj_kwargs.object.stop_consuming()
                except Exception as exc:
                    consumers_exceptions.append( (obj_kwargs.object, exc) )
            for obj_kwargs in self.__buffer_consumer_and_kwargs:
                try:
                    obj_kwargs.object.stop_consuming()
                except Exception as exc:
                    consumers_exceptions.append( (obj_kwargs.object, exc) )
        finally:
            self.__is_stopping_consuming = False
            self.__is_consuming = False
            
            if consumers_exceptions:
                logger.error(f"[{self.name}] Errors while stopping consuming on consumers: { {o.name:e for o,e in consumers_exceptions} }")
            elif Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Finished stop consuming")

    def start_process_data_events(self, raise_if_already_started=True):
        if self.__process_data_events_thread is not None and self.__process_data_events_thread.is_alive():
            if raise_if_already_started:
                raise TechnicalException(f"[{self.name}] Thread processing data events is already running")
            else:
                return
            
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Start processing data events...")
        self.__is_processing_data_events = True
        
        self.__process_data_events_thread = LoopFunctionThreaded(self.connection.process_data_events, kwargs={'time_limit':1}, register_thread=True, delay_before_run_sec=None)
        self.__process_data_events_thread.start()

    def stop_process_data_events(self):
        if not self.__is_processing_data_events:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Client is not processing data events")
            return
        if self.__is_stopping_processing_data_events:
            raise TechnicalException(f"[{self.name}] Data events processing is already under stop")
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Beginning stop data events processing...")
        self.__is_stopping_processing_data_events = True
        try:
            self.__process_data_events_thread.interrupt()
            self.__process_data_events_thread.join()
        finally:
            self.__is_stopping_processing_data_events = False
            self.__is_processing_data_events = False
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Finished stop data events processing")

    def _prepare_queue(self, channel, queue, queue_args=None, exchange="", exchange_args=None, bind_args=None):
        if exchange is not None and exchange != "":
            self._exchange_declare(channel, exchange, exchange_args)
        
        if queue is not None and queue != "":
            self._queue_declare(channel, queue, queue_args)
            queue_name = queue
        else:
            q_args = dict(queue_args) if queue_args else {}
            q_args['exclusive'] = True
            result = self._queue_declare(channel, queue, q_args)
            queue_name = result.method.queue
            
        if exchange is not None and exchange != "":
            self._queue_bind(channel, queue_name, exchange, bind_args)
            
        return queue_name
    
    def delete_queue(self, queue):
        self.connection.channel().queue_delete(queue=queue)
    
    def purge_queue(self, queue):
        self.connection.channel().queue_purge(queue)
        
    def _exchange_declare(self, channel, exchange, exchange_args=None):
        kwargs = {}
        arguments = None
        if exchange_args:
            arguments = dict(exchange_args)
            for name in ['exchange_type', 'passive', 'durable', 'auto_delete', 'internal']:
                if name in arguments:
                    kwargs[name] = arguments.pop(name)
        return channel.exchange_declare(exchange, arguments=arguments, **kwargs)
        
    def _queue_declare(self, channel, queue, queue_args=None):
        kwargs = {}
        arguments = None
        if queue_args:
            arguments = dict(queue_args)
            for name in ['passive', 'durable', 'exclusive', 'auto_delete']:
                if name in arguments:
                    kwargs[name] = arguments.pop(name)
        return channel.queue_declare(queue, arguments=arguments, **kwargs)
        
    def _queue_bind(self, channel, queue, exchange, bind_args=None):
        kwargs = {}
        arguments = None
        if bind_args:
            arguments = dict(bind_args)
            for name in ['routing_key']:
                if name in arguments:
                    kwargs[name] = arguments.pop(name)
        return channel.queue_bind(queue, exchange, arguments=arguments, **kwargs)
    
    def get_queue_message_count(self, queue):
        channel = self.connection.channel()
        status = self._queue_declare(channel, queue, {'passive':True})
        return status.method.message_count
    
    def is_queue_empty(self, queue, raise_exception=False):
        nb = self.get_queue_message_count(queue)
        res = (nb == 0)
        
        if not res and raise_exception:
            raise VerifyException(f"[{self.name}] Queue '{queue}' is not empty, it contains {nb} messages.")
        return res
    
    def flush(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Flushing...")
        for obj_kwargs in self._publisher_and_kwargs:
            obj_kwargs.object.flush()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Flushed")
    
    
    
class RMQPublisher(Object):
    def __init__(self, client, connection, channel, exchange, routing_key):
        super().__init__(f"RMQPublisher({routing_key})")
        self.__client = client
        self.__connection = connection
        self.__channel = channel
        self.__exchange = exchange
        self.__routing_key = routing_key
        
    @property
    def client(self):
        return self.__client
    
    @property
    def connection(self):
        return self.__connection
    
    @property
    def channel(self):
        return self.__channel
    
    def publish(self, body, **kwargs):
        kwargs['properties'] = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Transient)
        # kwargs['properties'] = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)
        # if self.__channel.has_confirm_delivery:
        #     kwargs['mandatory'] = True
        self.__channel.basic_publish(exchange=self.__exchange, routing_key=self.__routing_key, body=body, **kwargs)
        
        
class RMQConsumer(DeleteableObject):
    def __init__(self, client, connection, channel, queue, message_callback):
        super().__init__(f"RMQConsumer({queue})")
        
        self.__client = client
        self.__connection = connection
        self.__channel = channel
        self.__queue = queue
        self.__message_callback = message_callback
        
        # self.__consuming_thread_id = None
        self.__is_consuming = False
        self.__is_stopping_consuming = False
        
        self.__consumer_tag = self.__channel.basic_consume(queue=self.__queue, on_message_callback=self.__message_callback, auto_ack=True)
    
    @property
    def connection(self):
        return self.__connection
    
    @property
    def channel(self):
        return self.__channel
    
    @property
    def queue(self):
        return self.__queue
    
    @property
    def consumer_tag(self):
        return self.__consumer_tag
    
    # @property
    # def consuming_thread_id(self):
    #     return self.__consuming_thread_id
    #
    # @consuming_thread_id.setter
    # def consuming_thread_id(self, thread_id):
    #     self.__consuming_thread_id = thread_id
    
    @property
    def is_consuming(self):
        return self.__is_consuming
    
    def _delete_object(self):
        try:
            # Cancel consumer
            # self.__channel.basic_cancel(self.consumer_tag)
            
            # Stop consuming
            if self.is_consuming:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"[{self.name}] Deleting RabbitMQClient: Stopping consuming...")
                self.stop_consuming()
            
            # Close channel
            if self.__channel.is_open:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"[{self.name}] Deleting RabbitMQClient: Closing channel...")
                self.__channel.close()
        except StreamLostError as exc:
            if self.object_state == ObjectStates.Deleting:
                pass
            else:
                raise exc
    
    def start_consuming_in_thread(self):
        func = FunctionThreaded(self.start_consuming, register_thread=True, delay_before_run_sec=None)
        func.start()
        # self.consuming_thread_id = MultitaskManager.get_thread_id(thread=func)
        
    def start_consuming(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Beginning start consuming...")
        
        # Workaround: 
        #    Sometimes "When start consuming" is called rather than "Then client is consuming" 
        #    cf implementation of step @Given(r"start consuming in a thread \(RMQ client: (?P<var_client>\w+)\)")
        #    Workaround: register the thread_id allowed to start consuming.
        #    Note: A possible reason is that execute_steps is not thread safe. If it's true, the new implementation
        #          of the step with the wait of 0.01 seconds has resolved the problem, and thus this workaround is not needed anymore.
        # if self.consuming_thread_id is not None:
        #     thread_id = MultitaskManager.get_thread_id()
        #     if thread_id != self.consuming_thread_id:
        #         logger.error(f"Only thread {self.consuming_thread_id} is allowed to start consuming. Tried to start consuming in thread {thread_id} with traceback:\n{traceback.represent_stack(indent=4)}")
        #         return
        
        self.__is_consuming = True
        try:
            self.channel.start_consuming()
        except Exception as exc:
            if self.__is_stopping_consuming:
                if isinstance(exc, pika.exceptions.StreamLostError) \
                        or isinstance(exc, AttributeError) and "NoneType' object has no attribute 'clear'" in str(exc) \
                        or isinstance(exc, AssertionError):
                    logger.info(f"[{self.name}] Caught exception in consuming thread while stopping consuming: {exc}")
                else:
                    logger.warn(f"[{self.name}] Caught unexpected exception in consuming thread while stopping consuming: {Tools.represent_exception(exc)}")
            else:
                raise TechnicalException(f"[{self.name}] Failed to start consuming: {str(exc)}") from exc
        finally:
            # In all cases, self.__is_consuming must began False, otherwise stopping processing is broken in case of "raise exc"
            self.__is_consuming = False
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Finished start consuming")
    
    def stop_consuming(self):
        if not self.__is_consuming:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Consumer is not consuming")
            return
        if self.__is_stopping_consuming:
            raise TechnicalException(f"[{self.name}] Consuming is already under stop")
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Beginning stop consuming...")
        self.__is_stopping_consuming = True
        try:
            self.__stop_consuming_by_channel_stop_consuming()
            # self.__stop_consuming_by_deleting_channel_consumer_infos()
            
            # gc.collect()
            
            # Wait end of consuming
            if self.__is_consuming:
                logger.info(f"[{self.name}] Waiting consuming thread is stopped...")
                
                class StopRedo(Redo):
                    def __init__(self2):  # @NoSelf
                        super().__init__(f"[{self.name}] Stop consuming on consumer {self.consumer_tag}")
                        
                    def _process(self2):  # @NoSelf
                        return self.is_consuming
                redo = StopRedo()
                redo.redo_while(True)
                redo.with_timeout(30*60)    # Timeout of 30 min
                redo.polling_every(0.01)     # Wait 0.1 s beetween each try
                redo.with_process_in_thread(False)      # Run process in thread is not needed
                redo.execute()
                
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"[{self.name}] Finished waiting consuming thread is stopped")
        finally:
            self.__is_stopping_consuming = False
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Finished stop consuming")
            
    def __stop_consuming_by_channel_stop_consuming(self):
        try:
            self.channel.stop_consuming()
        except Exception as exc:
            if isinstance(exc, pika.exceptions.StreamLostError) \
                    or isinstance(exc, AttributeError) and "NoneType' object has no attribute 'clear'" in str(exc) \
                    or isinstance(exc, AssertionError):
                logger.info(f"[{self.name}] Caught exception while executing consuming stopping method: {exc}")
            else:
                logger.warn(f"[{self.name}] Caught exception while executing consuming stopping method: {Tools.represent_exception(exc)}")

    def __stop_consuming_by_deleting_channel_consumer_infos(self):
        del self.channel._consumer_infos[self.consumer_tag]
        # Schedule termination of connection.process_data_events using a
        # negative channel number
#                self.connection._request_channel_dispatch(-self.channel.channel_number)
        self.client.connection._request_channel_dispatch(-self.channel.channel_number)
    
    
    
class RMQBufferConsumer(Object):
    def __init__(self, client, connection, channel, queue):
        super().__init__(f"RMQBufferConsumer({queue})")
        self.__consumer = RMQConsumer(client, connection, channel, queue, self.__message_callback)
        
        self.__messages = []
        self.__messages_lock = threading.Lock()
    
    @property
    def connection(self):
        return self.__consumer.connection
    
    @property
    def nb_messages(self):
        with self.__messages_lock:
            return len(self.__messages)
    
    @property
    def messages(self):
        with self.__messages_lock:
            return list(self.__messages)
    
    @property
    def consumer_tag(self):
        return self.__consumer.consumer_tag
    
    # @property
    # def consuming_thread_id(self):
    #     return self.__consumer.consuming_thread_id
    #
    # @consuming_thread_id.setter
    # def consuming_thread_id(self, thread_id):
    #     self.__consumer.consuming_thread_id = thread_id
        
    def start_consuming_in_thread(self):
        self.__consumer.start_consuming_in_thread()
        
    def start_consuming(self):
        self.__consumer.start_consuming()
    
    def stop_consuming(self):
        self.__consumer.stop_consuming()
        
    def __message_callback(self, channel, method, properties, body):
        with self.__messages_lock:
            self.__messages.append( (channel, method, properties, body) )
            # logger.debug(f"[Consumer '{self.__consumer.queue}'] New message (total: {len(self.__messages)}): {channel=} ; {method=} ; {properties=} ; {body=}")
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"[{self.name}] New message (total: {len(self.__messages)}): {body}")
            elif Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] New message (total: {len(self.__messages)})")
    
    def reset_messages(self):
        with self.__messages_lock:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Reset messages (delete {len(self.__messages)} messages)")
            self.__messages.clear()
        
    def pop_first_message(self):
        with self.__messages_lock:
            res = self.__messages.pop(0)
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Pop first message (remaining: {len(self.__messages)}): {res}")
            return res
        
    def pop_and_save_messages(self, file:File, max_messages=None):
        res = 0
        
        nb_messages = self.nb_messages
        while nb_messages > 0 and (max_messages is None or res < nb_messages):
            msg = self.pop_first_message()
            file.writelines([msg[3].hex()])
            res += 1
            
            nb_messages = self.nb_messages
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Saved a message (nb saved: {res} ; remaining: {nb_messages})")
            
        return res
    
    