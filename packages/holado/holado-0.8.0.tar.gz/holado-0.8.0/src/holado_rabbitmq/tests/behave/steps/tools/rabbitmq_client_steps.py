# -*- coding: utf-8 -*-

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


from holado_value.common.tables.comparators.table_2_value_table_comparator import Table2ValueTable_Comparator
from holado_test.scenario.step_tools import StepTools
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_rabbitmq.tools.rabbitmq import rabbitmq_client
from holado_core.common.tables.table_manager import TableManager
from holado_core.common.exceptions.functional_exception import FunctionalException
import logging
from holado_core.common.tools.tools import Tools
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
import queue
from holado_system.system.global_system import GlobalSystem
from holado_core.common.exceptions.technical_exception import TechnicalException
import pika
from holado_rabbitmq.tools.rabbitmq.rabbitmq_blocking_client import RMQBlockingClient
from holado_rabbitmq.tools.rabbitmq.rabbitmq_select_client import RMQSelectClient
from holado_python.standard_library.typing import Typing


logger = logging.getLogger(__name__)


if rabbitmq_client.RMQClient.is_available():

    def __get_session_context():
        return SessionContext.instance()
    
    def __get_scenario_context():
        return __get_session_context().get_scenario_context()
    
    def __get_text_interpreter():
        return __get_scenario_context().get_text_interpreter()
    
    def __get_variable_manager():
        return __get_scenario_context().get_variable_manager()
    
    def __get_protobuf_messages():
        return SessionContext.instance().protobuf_messages
    
    def __get_rabbitmq_manager():
        return SessionContext.instance().rabbitmq_manager
    
    
    def __convert_step_args_2_RabbitMQClient_kwargs(step_args):
        res = {}
        args = dict(step_args)
        if 'queue.name' in args:
            res['queue'] = args.pop('queue.name')
        if Tools.has_sub_kwargs(args, 'queue.'):
            res['queue_args'] = Tools.pop_sub_kwargs(args, 'queue.')
        if 'exchange.name' in args:
            res['exchange'] = args.pop('exchange.name')
        if Tools.has_sub_kwargs(args, 'exchange.'):
            res['exchange_args'] = Tools.pop_sub_kwargs(args, 'exchange.')
        if Tools.has_sub_kwargs(args, 'bind.'):
            res['bind_args'] = Tools.pop_sub_kwargs(args, 'bind.')
        res.update(args)
        return res
    
    
    @Given(r"(?P<var_name>{Variable}) = new RabbitMQ client")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        obj = RMQBlockingClient()
        __get_variable_manager().register_variable(var_name, obj)
    
    @Given(r"(?P<var_name>{Variable}) = new RabbitMQ client with rapid close")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        obj = RMQBlockingClient()
        obj.rapid_close = True
        __get_variable_manager().register_variable(var_name, obj)
    
    @Given(r"(?P<var_name>{Variable}) = new asynchronous RabbitMQ client")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        obj = RMQSelectClient()
        __get_variable_manager().register_variable(var_name, obj)
    
    @When(r"connect \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        """
        Create a new connection to RabbitMQ Client. Connection parameters are defined in a table.
        The connection is a select connection for asynchronous client else a blocking connection.
        Credentials:
            To define connection credentials, define username and password values
        """

        if hasattr(context, "table"):
            table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
            connection_parameters_kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        else:
            connection_parameters_kwargs = {}
        
        client = StepTools.evaluate_variable_value(var_client)
        client.connect(**connection_parameters_kwargs)
    
    @When(r"connect with a blocking connection \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        """
        Create a new blocking connection to RabbitMQ Client. Connection parameters are defined in a table.
        Credentials:
            To define connection credentials, define username and password values
        """
        if hasattr(context, "table"):
            table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
            connection_parameters_kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        else:
            connection_parameters_kwargs = {}
        
        client = StepTools.evaluate_variable_value(var_client)
        if not isinstance(client, RMQBlockingClient):
            raise FunctionalException(f"A blocking connection is only possible with a blocking client")
        client.connect(**connection_parameters_kwargs)
    
    @When(r"connect with a select connection \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        """
        Create a new select connection to RabbitMQ Client. 
        Connection parameters are defined in a table.
        A parameter 'wait_connection' can be set to wait connection before step end (default).
        Credentials:
            To define connection credentials, define username and password values
        """

        if hasattr(context, "table"):
            table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
            connection_parameters_kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        else:
            connection_parameters_kwargs = {}
        
        client = StepTools.evaluate_variable_value(var_client)
        if not isinstance(client, RMQBlockingClient):
            raise FunctionalException(f"A select connection is only possible with a select client")
        client.connect(**connection_parameters_kwargs)
    
    @Step(r"flush \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        """
        Flush connection of RabbitMQ Client
        """
        client = StepTools.evaluate_variable_value(var_client)
        client.flush()
    
    @Step(r"close \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        """
        Close connection to RabbitMQ Client
        """
        client = StepTools.evaluate_variable_value(var_client)
        client.close()
    
    @Given(r"(?P<var_name>{Variable}) = new publisher on queue (?P<queue>{Str}) \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, queue, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        queue = StepTools.evaluate_scenario_parameter(queue)
        
        execute_steps("""
            Given {} = new publisher (RMQ client: {})
                | Name         | Value |
                | 'queue.name' | '{}'  |
            """.format(var_name, var_client, queue) )
    
    @Given(r"(?P<var_name>{Variable}) = new publisher \(RMQ client: (?P<var_client>{Variable})(?: ; nb of runners: (?P<nb_runners>{Int}))?\)")
    def step_impl(context, var_name, var_client, nb_runners):
        var_name = StepTools.evaluate_variable_name(var_name)
        nb_runners = StepTools.evaluate_scenario_parameter(nb_runners)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        
        args = ValueTableConverter.convert_name_value_table_2_dict(table)
        kwargs = __convert_step_args_2_RabbitMQClient_kwargs(args)
        if nb_runners is not None and 'nb_runners' not in kwargs:
            kwargs['nb_runners'] = nb_runners
        
        client = StepTools.evaluate_variable_value(var_client)
        pub = client.new_publisher(**kwargs)
        
        __get_variable_manager().register_variable(var_name, pub)
    
    @Given(r"(?P<var_name>{Variable}) = new buffer consumer on queue (?P<queue>{Str}) \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, queue, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        queue = StepTools.evaluate_scenario_parameter(queue)
        
        execute_steps("""
            Given {} = new buffer consumer (RMQ client: {})
                | Name         | Value |
                | 'queue.name' | '{}'  |
            """.format(var_name, var_client, queue) )
    
    @Given(r"(?P<var_name>{Variable}) = new buffer consumer \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        args = ValueTableConverter.convert_name_value_table_2_dict(table)
        kwargs = __convert_step_args_2_RabbitMQClient_kwargs(args)
        
        client = StepTools.evaluate_variable_value(var_client)
        con = client.new_buffer_consumer(**kwargs)
        
        __get_variable_manager().register_variable(var_name, con)
    
    # @Given(r"start consuming in a thread \(RMQ client: (?P<var_client>{Variable})\)")
    # def step_impl(context, var_client):
    #     # execute_steps(u"""
    #     #     Given __THREAD_ID_CONSUMING__@ = start consuming in a thread (RMQ client: {var_client})
    #     #     Given wait until client is consuming (RMQ client: {var_client}) (accepted time: 20 s)
    #     #     Given for thread __THREAD_ID_CONSUMING__@, call steps for interrupt
    #     #         \"""
    #     #         When stop consuming (RMQ client: {var_client})
    #     #         \"""
    #     #     """.format(var_client=var_client))
    #
    #     # The wait of 0.01 seconds is done to avoid the case where two execute_steps are done in the same time in two different threads
    #     execute_steps(u"""
    #         Given __THREAD_ID_CONSUMING__@ = start consuming in a thread (RMQ client: {var_client})
    #         Given wait 0.01 seconds
    #         Given wait until client is consuming (RMQ client: {var_client}) (accepted time: 5 s)
    #         """.format(var_client=var_client))
    #
    # @Given(r"(?P<var_name>{Variable}) = start consuming in a thread \(RMQ client: (?P<var_client>{Variable})\)")
    # def step_impl(context, var_name, var_client):
    #     var_name = StepTools.evaluate_variable_name(var_name)
    #     var_client = StepTools.evaluate_variable_name(var_client)
    #
    #     # Start consuming in a small delay
    #     execute_steps(u"""
    #         Given {var_name} = call steps in a thread
    #             \"""
    #             When start consuming (RMQ client: {var_client})
    #             \"""
    #         """.format(var_name=var_name, var_client=var_client))
    #
    #     # Register the thread allowed to start consuming 
    #     thread_name = __get_variable_manager().get_variable_value(var_name)
    #     thread = SessionContext.instance().threads_manager.get_thread(thread_name)
    #     thread_id = MultitaskManager.get_thread_id(thread=thread)
    #
    #     client = StepTools.evaluate_variable_value(var_client)
    #     client.consuming_thread_id = thread_id
    
    @Step(r"start consuming \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        client = StepTools.evaluate_variable_value(var_client)
        client.start_consuming()
    
    @Then(r"client is consuming \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        client = StepTools.evaluate_variable_value(var_client)
        if not client.is_consuming:
            raise FunctionalException(f"RMQ client is not consuming")
        
    @Step(r"stop consuming \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        client = StepTools.evaluate_variable_value(var_client)
        client.stop_consuming()
    
    @Step(r"start data events processing \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        """
        Usually this step is not needed, as data events processing is automatically started at first publish.
        """
        client = StepTools.evaluate_variable_value(var_client)
        client.start_process_data_events()
    
    @Step(r"stop data events processing \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_client):
        """
        Usually this step is not needed, as data events processing is automatically stopped when closing client.
        """
        client = StepTools.evaluate_variable_value(var_client)
        client.stop_process_data_events()
    
    @When(r"publish (?P<msg>{Str}) \(RMQ publisher: (?P<var_pub>{Variable})\)")
    def step_impl(context, msg, var_pub):
        msg = StepTools.evaluate_scenario_parameter(msg)
        pub = StepTools.evaluate_variable_value(var_pub)
        pub.publish(msg)
    
    @When(r"publish all of (?P<iterable_str>{Any}) \(RMQ publisher: (?P<var_pub>{Variable})\)")
    def step_impl(context, iterable_str, var_pub):
        iterable = StepTools.evaluate_scenario_parameter(iterable_str)
        pub = StepTools.evaluate_variable_value(var_pub)
        pub_name = StepTools.evaluate_variable_name(var_pub)
        
        counter = 0
        
        for msg in iterable:
            counter += 1
            
            try:
                pub.publish(msg)
            except pika.exceptions.ChannelWrongStateError as exc:
                raise TechnicalException(f"[Publisher {pub_name}] Stop publishing after error on message {counter}: [{Typing.get_object_class_fullname(exc)}] {str(exc)}") from exc
            except Exception as exc:
                raise TechnicalException(f"[Publisher {pub_name}] Failed to publish message {counter}: [{Typing.get_object_class_fullname(exc)}] {str(exc)}") from exc
                
            # Yield processor in case of multithreading
            if counter % 10 == 0:
                GlobalSystem.yield_processor()
    
    @When(r"publish all of queue (?P<var_queue>{Variable}) \(RMQ publisher: (?P<var_pub>{Variable})(?: ; rate log period: (?P<rate_period_s>{Int}) s)?\)")
    def step_impl(context, var_queue, var_pub, rate_period_s):
        q = StepTools.evaluate_variable_value(var_queue)
        q_name = StepTools.evaluate_variable_name(var_queue)
        pub = StepTools.evaluate_variable_value(var_pub)
        pub_name = StepTools.evaluate_variable_name(var_pub)
        rate_period_s = StepTools.evaluate_scenario_parameter(rate_period_s)
        
        counter = 0
        beg = Tools.timer_s()
        c_beg, t_beg = counter, beg
        log_counter = 0
        
        try:
            while True:
                # Get next message and publish
                msg = q.get()
                if q.is_sentinel(msg):
                    break
                counter += 1
                
                try:
                    pub.publish(msg)
                except pika.exceptions.ChannelWrongStateError as exc:
                    logger.error(f"[Queue {q_name} -> Publisher {pub_name}] Stop publishing after error on message {counter}: [{Typing.get_object_class_fullname(exc)}] {str(exc)}")
                    break
                except Exception as exc:
                    logger.warning(f"[Queue {q_name} -> Publisher {pub_name}] Failed to publish message {counter}: [{Typing.get_object_class_fullname(exc)}] {str(exc)}")
                    # logger.warning(f"[Queue {q_name} -> Publisher {pub_name}] Failed to publish message {counter}: [{Typing.get_object_class_fullname(exc)}] {Tools.represent_exception(exc)}")
                finally:
                    q.task_done()
                
                # Log rate if needed
                if rate_period_s and counter % 10 == 0:
                    t_end = Tools.timer_s()
                    if t_end > t_beg + rate_period_s:
                        c_end, s_end = counter, q.qsize()
                        rate = (c_end - c_beg) / (t_end - t_beg)
                        log_counter += 1
                        logger.print(f"[Queue {q_name} -> Publisher {pub_name}] Rate: {int(rate)} msg/s ; Nb messages: {counter} ; Queue size: {s_end}")
                        c_beg, t_beg = c_end, t_end
                        
                # Yield processor in case of multithreading
                if counter % 10 == 0:
                    GlobalSystem.yield_processor()
        except queue.Empty:
            # Without block, or with timeout, this exception occurs when queue is empty
            pass
        
        if rate_period_s:
            end = Tools.timer_s()
            rate = counter / (end - beg)
            logger.print(f"[Queue {q_name} -> Publisher {pub_name}] Mean rate: {int(rate)} msg/s ; Nb messages: {counter}")
    
    @When(r"await consumer (?P<var_con>{Variable}) receives a message(?: \(timeout: (?P<timeout_sec>{Float}) s(?: ; polling: (?P<polling_sec>{Float}) s)?\))?")
    def step_impl(context, var_con, timeout_sec, polling_sec):
        con = StepTools.evaluate_variable_value(var_con)
        timeout_sec = StepTools.evaluate_scenario_parameter(timeout_sec)
        polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
        
        __get_rabbitmq_manager().await_message_reception([con], timeout_seconds=timeout_sec, polling_seconds=polling_sec)
    
    @When(r"await consumers (?P<list_consumers>{List}) receive a message(?: \(timeout: (?P<timeout_sec>{Float}) s(?: ; polling: (?P<polling_sec>{Float}) s)?\))?")
    def step_impl(context, list_consumers, timeout_sec, polling_sec):
        consumers = StepTools.evaluate_list_scenario_parameter(list_consumers, "list_consumers")
        timeout_sec = StepTools.evaluate_scenario_parameter(timeout_sec)
        polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
        
        __get_rabbitmq_manager().await_message_reception(consumers, timeout_seconds=timeout_sec, polling_seconds=polling_sec)
    
    @When(r"await consumer (?P<var_con>{Variable}) receives (?:(?P<no_str>no) )?messages(?: \((?:first timeout: (?P<first_timeout_sec>{Float}) s)?(?: ; )?(?:window: (?P<window_sec>{Float}) s)?(?: ; )?(?:polling: (?P<polling_sec>{Float}) s)?\))?")
    def step_impl(context, var_con, no_str, first_timeout_sec, window_sec, polling_sec):
        con = StepTools.evaluate_variable_value(var_con)
        first_timeout_sec = StepTools.evaluate_scenario_parameter(first_timeout_sec)
        window_sec = StepTools.evaluate_scenario_parameter(window_sec)
        polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
        do_raise = no_str is None
        
        __get_rabbitmq_manager().await_messages_reception([con], first_timeout_seconds=first_timeout_sec, window_seconds=window_sec, polling_seconds=polling_sec, raise_exception=do_raise)
    
    @When(r"await consumers (?P<list_consumers>{List}) receive (?:(?P<no_str>no) )?messages(?: \((?:first timeout: (?P<first_timeout_sec>{Float}) s)?(?: ; )?(?:window: (?P<window_sec>{Float}) s)?(?: ; )?(?:polling: (?P<polling_sec>{Float}) s)?\))?")
    def step_impl(context, list_consumers, no_str, first_timeout_sec, window_sec, polling_sec):
        consumers = StepTools.evaluate_list_scenario_parameter(list_consumers, "list_consumers")
        first_timeout_sec = StepTools.evaluate_scenario_parameter(first_timeout_sec)
        window_sec = StepTools.evaluate_scenario_parameter(window_sec)
        polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
        do_raise = no_str is None
        
        __get_rabbitmq_manager().await_messages_reception(consumers, first_timeout_seconds=first_timeout_sec, window_seconds=window_sec, polling_seconds=polling_sec, raise_exception=do_raise)
    
    @Then(r"consumer (?P<var_con>{Variable}) doesn't receive any message \(timeout: (?P<timeout_sec>{Float}) s ; polling: (?P<polling_sec>{Float}) s\)")
    def step_impl(context, var_con, timeout_sec, polling_sec):
        con = StepTools.evaluate_variable_value(var_con)
        timeout_sec = StepTools.evaluate_scenario_parameter(timeout_sec)
        polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
        
        nb = __get_rabbitmq_manager().await_message_reception([con], timeout_seconds=timeout_sec, polling_seconds=polling_sec, raise_exception=False)
        if nb > 0:
            raise FunctionalException(f"Consumer has received {nb} messages")
    
    @Then(r"consumers (?P<list_consumers>{List}) don't receive any message \(timeout: (?P<timeout_sec>{Float}) s ; polling: (?P<polling_sec>{Float}) s\)")
    def step_impl(context, list_consumers, timeout_sec, polling_sec):
        consumers = StepTools.evaluate_list_scenario_parameter(list_consumers, "list_consumers")
        timeout_sec = StepTools.evaluate_scenario_parameter(timeout_sec)
        polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
        
        nb = __get_rabbitmq_manager().await_message_reception(consumers, timeout_seconds=timeout_sec, polling_seconds=polling_sec, raise_exception=False)
        if nb > 0:
            raise FunctionalException(f"Consumer has received {nb} messages")
    
    @Then(r"consumer (?P<var_con>{Variable}) received (?P<nb_msg>{Int}) messages")
    def step_impl(context, var_con, nb_msg):
        con = StepTools.evaluate_variable_value(var_con)
        nb_msg = StepTools.evaluate_scenario_parameter(nb_msg)
    
        if len(con.messages) != nb_msg:
            raise FunctionalException(f"The number of received messages is {len(con.messages)} (expected: {nb_msg}). Received messages:\n    {(chr(10)+'    ').join((str(m[3]) for m in con.messages))}")
    
    @Then(r"consumer (?P<var_con>{Variable}) received(?: (?P<nb_msg>{Int}))? string messages:")
    def step_impl(context, var_con, nb_msg):
        con = StepTools.evaluate_variable_value(var_con)
        nb_msg = StepTools.evaluate_scenario_parameter(nb_msg)
        table = BehaveStepTools.convert_step_table_2_value_table(context.table)
        
        # Verify number of messages
        if nb_msg:
            if len(con.messages) != nb_msg:
                raise FunctionalException(f"The number of received messages is {len(con.messages)} (expected: {nb_msg}). Received messages:\n    {(chr(10)+'    ').join((str(m[3]) for m in con.messages))}")
        
        # Verify messages
        messages = [m[3].decode('utf-8') for m in con.messages]
        obtained = TableManager.convert_list_2_column_table(messages)
        comparator = Table2ValueTable_Comparator()
        comparator.equals(obtained, table)
    
    @Step(r"(?P<var_name>{Variable}) = number of received messages \(RMQ consumer: (?P<var_con>{Variable})\)")
    def step_impl(context, var_name, var_con):
        var_name = StepTools.evaluate_variable_name(var_name)
        con = StepTools.evaluate_variable_value(var_con)
        
        res = len(con.messages)

        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = received messages \(RMQ consumer: (?P<var_con>{Variable})\)")
    def step_impl(context, var_name, var_con):
        var_name = StepTools.evaluate_variable_name(var_name)
        con = StepTools.evaluate_variable_value(var_con)
        
        res = [m[3] for m in con.messages]
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Received {len(res)} messages")

        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = received messages as (?P<proto_type_str>{Str}) Protobuf objects \(RMQ consumer: (?P<var_con>{Variable})\)")
    def step_impl(context, var_name, proto_type_str, var_con):
        var_name = StepTools.evaluate_variable_name(var_name)
        proto_type_str = StepTools.evaluate_scenario_parameter(proto_type_str)
        con = StepTools.evaluate_variable_value(var_con)
        
        res = __get_rabbitmq_manager().received_messages_as_protobuf_objects(con, proto_type_str)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @Step(r"(?P<var_name>{Variable}) = pop first received message \(RMQ consumer: (?P<var_con>{Variable})\)")
    def step_impl(context, var_name, var_con):
        var_name = StepTools.evaluate_variable_name(var_name)
        con = StepTools.evaluate_variable_value(var_con)
        
        message = con.pop_first_message()
        res = message[3]
        
        __get_variable_manager().register_variable(var_name, res)
        
    @Step(r"(?P<var_name>{Variable}) = pop first received message as (?P<proto_type_str>{Str}) Protobuf object \(RMQ consumer: (?P<var_con>{Variable})\)")
    def step_impl(context, var_name, proto_type_str, var_con):
        var_name = StepTools.evaluate_variable_name(var_name)
        con = StepTools.evaluate_variable_value(var_con)
        
        proto_type_str = StepTools.evaluate_scenario_parameter(proto_type_str)
        
        message = con.pop_first_message()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Pop first message: {message[3]}")
        res = __get_session_context().protobuf_messages.new_message(proto_type_str, serialized_string=message[3])
        # logger.debug(f"+++++ New message: type={Typing.get_object_class_fullname(msg)} ; dir={dir(msg)}")
        
        __get_variable_manager().register_variable(var_name, res)
        
    @When(r"(?P<var_name>{Variable}) = pop and save received messages \(RMQ consumer: (?P<var_con>{Variable}) ; file: (?P<var_file>{Variable})(?: ; max messages: (?P<max_messages>{Int}))?\)")
    def step_impl(context, var_name, var_con, var_file, max_messages):
        var_name = StepTools.evaluate_variable_name(var_name)
        con = StepTools.evaluate_variable_value(var_con)
        file = StepTools.evaluate_variable_value(var_file)
        max_messages = int(max_messages) if max_messages else None
        
        res = con.pop_and_save_messages(file, max_messages)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @Given(r"reset stored messages in consumer (?P<var_con>{Variable})")
    def step_impl(context, var_con):
        con = StepTools.evaluate_variable_value(var_con)
        con.reset_messages()
        
    @Given(r"reset stored messages in consumers (?P<list_consumers>{List})")
    def step_impl(context, list_consumers):
        consumers = StepTools.evaluate_list_scenario_parameter(list_consumers, "list_consumers")
        for con in consumers:
            con.reset_messages()
        
    @When(r"purge queue (?P<queue>{Str}) \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, queue, var_client):
        queue = StepTools.evaluate_scenario_parameter(queue)
        client = StepTools.evaluate_variable_value(var_client)
        client.purge_queue(queue)
        
    @Step(r"delete and recreate stream queue (?P<queue>{Str}) \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, queue, var_client):
        queue_name = StepTools.evaluate_scenario_parameter(queue)
        client = StepTools.evaluate_variable_value(var_client)
        client.delete_queue(queue_name)
        client._queue_declare(
            channel=client.connection.channel(),
            queue=queue_name,
            queue_args={
                'durable': True,
                "x-queue-type": "stream",
                "x-stream-max-segment-size-bytes": 100000000
            })
        
    @Step(r"bind queue (?P<queue>{Str}) to exchange (?P<exchange>{Str})(?: with routine key (?P<routine_key>{Str}))? \(RMQ client: (?P<var_client>{Variable})\)")
    def step_impl(context, queue, exchange, routine_key, var_client):
        queue_name = StepTools.evaluate_scenario_parameter(queue)
        exchange = StepTools.evaluate_scenario_parameter(exchange)
        routine_key = StepTools.evaluate_scenario_parameter(routine_key)
        client = StepTools.evaluate_variable_value(var_client)
        bind_args={
            'routing_key': routine_key
            }
        client._queue_bind(
            channel=client.connection.channel(),
            queue=queue_name,
            exchange=exchange,
            bind_args=bind_args
        )
        