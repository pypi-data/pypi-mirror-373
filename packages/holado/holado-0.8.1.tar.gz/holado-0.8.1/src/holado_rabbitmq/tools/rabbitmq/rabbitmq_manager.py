# -*- coding: utf-8 -*-

import logging
from holado_core.common.tools.tools import Tools
from holado_rabbitmq.tools.rabbitmq.rabbitmq_client import RMQBufferConsumer
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.typing import Typing
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.handlers.wait import WaitEndChange, WaitChange

logger = logging.getLogger(__name__)


class RMQManager:

    def __init__(self):
        self.__protobuf_messages = None
        
    def initialize(self, protobuf_messages):
        self.__protobuf_messages = protobuf_messages
    
    
    def received_messages_as_protobuf_objects(self, consumer, message_type_fullname):
        """Unserialize messages received by a buffer consumer to given Protobuf message type"""
        
        if not isinstance(consumer, RMQBufferConsumer):
            raise TechnicalException(f"Consumer has to be a buffer consumer (obtained type: {Typing.get_object_class_fullname(consumer)})")
        
        res = []
        for ind, m in enumerate(consumer.messages):
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Received message [{ind}]: {m[3]}")
            msg = self.__protobuf_messages.new_message(message_type_fullname, serialized_string=m[3])
            res.append(msg)
            # logger.debug(f"+++++ New message: type={Typing.get_object_class_fullname(msg)} ; dir={dir(msg)}")
        return res
    
        
    def await_message_reception(self, consumers, timeout_seconds=None, polling_seconds=None, raise_exception=True):
        """Wait until one of the buffer consumers has received a message.
        @param consumers: list of buffer consumers
        @param timeout_seconds: wait timeout
        @param polling_seconds: time to wait between pollings of received messages of all consumers
        """
        if raise_exception is None:
            raise_exception = True
        
        wait = WaitChange(f"Wait message reception by consumers",
                          lambda: sum([c.nb_messages for c in consumers if c.nb_messages > 0]),
                          do_process_in_thread = False,
                          result_reference = 0,
                          timeout_seconds=timeout_seconds, polling_seconds=polling_seconds)
        # On timeout, we will have res==0 and raise is managed before return
        wait.without_raise_on_timeout()
        
        res = wait.execute()
        
        if res == 0 and raise_exception:
            names = ",".join([c.name for c in consumers])
            raise FunctionalException(f"[{names}] No message was received (timeout: {timeout_seconds} seconds)")
        return res
    

    #TODO EKL: add a first_accepted_seconds and a accepted_window_seconds to be able to raise an exception that first or next message arrived but too late
    #TODO EKL: change use of polling_seconds to something like a timer, rather than waiting polling_seconds
    def await_messages_reception(self, consumers, first_timeout_seconds=None, window_seconds=None, polling_seconds=None, raise_exception=True):
        """Wait until buffer consumers stop to receive messages.
        It begins by waiting a first message in any consumer, since their creation or last reset.
        If no consumer receives a first message during first_timeout_seconds period, wait stops.
        Then after each message received by any consumer, a window duration of window_seconds is waited for a new message.
        When no new message is received by any consumer during the window period, wait stops.
        @param consumers: list of buffer consumers
        @param first_timeout_seconds: reception timeout of a first message
        @param window_seconds: time window for wait of a new message since last received message
        @param polling_seconds: time to wait between pollings of received messages of all consumers
        """
        # res = 0
        #
        # if window_seconds is None:
        #     if first_timeout_seconds is not None and first_timeout_seconds > 0:
        #         window_seconds = first_timeout_seconds / 10
        #     else:
        #         window_seconds = 1
        #     if window_seconds < 0.01:
        #         window_seconds = 0.01       # a window period below 10 ms is usually not efficient in testing context
        # if polling_seconds is None:
        #     min_window = min(first_timeout_seconds, window_seconds) if first_timeout_seconds is not None else window_seconds
        #     polling_seconds = min_window / 100       # 1% of error on window detection
        #     if polling_seconds > 0.1:
        #         polling_seconds = 0.1       # a polling period over 100 ms is usually not efficient in testing context
        #     elif polling_seconds < 0.001:
        #         polling_seconds = 0.001       # a polling period below 1 ms is usually not efficient in testing context
        #
        # # Wait first message is needed
        # dt_begin = datetime.now()
        # dt_last_poll = dt_begin
        # if first_timeout_seconds is not None:
        #     while (dt_last_poll - dt_begin).total_seconds() < first_timeout_seconds:
        #         nb_msg_by_consumer = {c.name: c.nb_messages for c in consumers if c.nb_messages > 0}
        #         dt_last_poll = datetime.now()
        #         if len(nb_msg_by_consumer) > 0:
        #             res = sum(nb_msg_by_consumer.values())
        #             if Tools.do_log(logger, logging.DEBUG):
        #                 logger.debug(f"Received first messages: total={res} ; " + " ; ".join(f"{k}:{v}" for k,v in nb_msg_by_consumer.items()))
        #             break
        #         time.sleep(polling_seconds)
        #     if res == 0:
        #         if raise_exception:
        #             names = ",".join([c.name for c in consumers])
        #             raise FunctionalException(f"[{names}] No message was received (timeout: {first_timeout_seconds} seconds)")
        #         return res
        #
        # # Wait end of reception
        # dt_last_receive = dt_last_poll
        # while (dt_last_poll - dt_last_receive).total_seconds() < window_seconds:
        #     nb_msg_by_consumer = {c.name: c.nb_messages for c in consumers if c.nb_messages > 0}
        #     nb = sum(nb_msg_by_consumer.values())
        #     dt_last_poll = datetime.now()
        #     if nb > res:
        #         res = nb
        #         if Tools.do_log(logger, logging.DEBUG):
        #             logger.debug(f"Received messages: total={res} ; " + " ; ".join(f"{k}:{v}" for k,v in nb_msg_by_consumer.items()))
        #         dt_last_receive = dt_last_poll
        #     time.sleep(polling_seconds)
        #
        # return res
        if raise_exception is None:
            raise_exception = True
        
        wait = WaitEndChange(f"Wait end of message reception by consumers",
                             lambda: sum([c.nb_messages for c in consumers if c.nb_messages > 0]),
                             do_process_in_thread = False,
                             result_reference = 0,
                             first_timeout_seconds=first_timeout_seconds, window_seconds=window_seconds, polling_seconds=polling_seconds)
        # On timeout, we will have res==0 and raise is managed before return
        wait.without_raise_on_timeout()
        
        res = wait.execute()
        
        if res == 0 and raise_exception:
            names = ",".join([c.name for c in consumers])
            raise FunctionalException(f"[{names}] No message was received (timeout: {first_timeout_seconds} seconds)")
        return res
    
    
    