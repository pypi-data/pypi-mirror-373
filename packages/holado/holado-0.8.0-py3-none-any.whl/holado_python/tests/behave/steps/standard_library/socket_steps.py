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


from holado_test.scenario.step_tools import StepTools
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_python.standard_library.socket.blocking_socket import TCPBlockingSocketClient
from holado_python.standard_library.socket.echo_server import EchoTCPBlockingSocketServer
from holado_python.standard_library.socket.message_socket import MessageTCPNonBlockingSocketClient, MessageTCPBlockingSocketClient
from holado_core.common.handlers.wait import WaitEndChange, WaitChange
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_python.standard_library.socket.non_blocking_socket import TCPNonBlockingSocketClient

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()



################################################################
## Clients
################################################################


@Given(r"(?P<var_name>{Variable}) = new TCP socket client")
def step_impl(context, var_name):
    """Return a new TCP socket client.
    Note: Only IPv4 is managed for the moment
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)

    blocking = kwargs.pop('blocking') if 'blocking' in kwargs else True
    if blocking:
        res = TCPBlockingSocketClient(create_ipv4_socket_kwargs=kwargs)
    else:
        res = TCPNonBlockingSocketClient(create_ipv4_socket_kwargs=kwargs)
    
    __get_variable_manager().register_variable(var_name, res)


@Given(r"(?P<var_name>{Variable}) = new message TCP socket client")
def step_impl(context, var_name):
    """Return a new message TCP socket client.
    Parameter 'separator' specifies the separator at end of each message (default: b'\n')
    Note: Only IPv4 is managed for the moment
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
    
    separator = kwargs.pop('separator') if 'separator' in kwargs else '\n'
    blocking = kwargs.pop('blocking') if 'blocking' in kwargs else True
    if blocking:
        res = MessageTCPBlockingSocketClient(separator, create_ipv4_socket_kwargs=kwargs)
    else:
        res = MessageTCPNonBlockingSocketClient(separator, create_ipv4_socket_kwargs=kwargs)
    
    __get_variable_manager().register_variable(var_name, res)


@Step(r"start \(socket client: (?P<server_varname>{Variable})\)")
def step_impl(context, server_varname):
    """Start a socket client.
    It starts a thread listening incoming data.
    This step is needed for non blocking socket clients to manage incoming data.
    Note: current implementation uses 'start' method parameters default values.
    """
    server = StepTools.evaluate_scenario_parameter(server_varname)
    server.start()

@Step(r"stop \(socket client: (?P<server_varname>{Variable})\)")
def step_impl(context, server_varname):
    """Stop a non blocking socket client.
    """
    server = StepTools.evaluate_scenario_parameter(server_varname)
    server.stop()




################################################################
## Server
################################################################


@Given(r"(?P<var_name>{Variable}) = new echo TCP socket server")
def step_impl(context, var_name):
    """Return a new echo TCP socket server.
    When started, it waits connections, and for each connection it listen data and send them back
    Note: Only IPv4 is managed for the moment
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
    
    res = EchoTCPBlockingSocketServer(create_ipv4_socket_kwargs=kwargs)
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"start \(socket server: (?P<server_varname>{Variable})\)")
def step_impl(context, server_varname):
    """Start a socket server
    Note: current implementation uses 'start' method parameters default values.
    """
    server = StepTools.evaluate_scenario_parameter(server_varname)
    server.start()

@Step(r"stop \(socket server: (?P<server_varname>{Variable})\)")
def step_impl(context, server_varname):
    """Start a socket server
    Note: current implementation uses 'start' method parameters default values.
    """
    server = StepTools.evaluate_scenario_parameter(server_varname)
    server.stop()



################################################################
## Client and Server
################################################################


@Step(r"ensure SSL handshake is done \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, socket_varname):
    """Ensure SSL handshake is done.
    """
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    sock.ensure_ssl_handshake_is_done()

@Step(r"write (?P<data>{Bytes}) \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, data, socket_varname):
    """Send data
    This step do as many socket send as needed to send the whole data.
    """
    data = StepTools.evaluate_scenario_parameter(data)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    sock.write(data)

@Step(r"(?P<var_name>{Variable}) = read \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, var_name, socket_varname):
    """Read data
    This step do as many socket recv as needed to receive the whole data.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    res = sock.read()
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = received data \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, var_name, socket_varname):
    """Get currently received data
    This step works only with clients that are started, so that listening thread is started.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    res = sock.received_data
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = size of received data \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, var_name, socket_varname):
    """Get received messages without removing from socket
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    res = sock.received_data_size
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"socket (?P<socket_varname>{Variable}) doesn't receive any data(?: \((?:timeout: (?P<timeout_sec>{Float}) s)?(?: ; )?(?:polling: (?P<polling_sec>{Float}) s)?\))?")
def step_impl(context, socket_varname, timeout_sec, polling_sec):
    """Wait and verify socket doesn't receive any data
    """
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    timeout_sec = StepTools.evaluate_scenario_parameter(timeout_sec)
    polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
    
    if timeout_sec is None:
        timeout_sec = 10
    
    wait = WaitChange(f"Verify no data is received (socket: {sock})",
                      lambda: sock.received_data_size,
                      timeout_seconds=timeout_sec, polling_seconds=polling_sec)
    wait.without_raise_on_timeout()
    data_size = wait.execute()
    if data_size > 0:
        raise FunctionalException(f"[{sock.name}] Socket has received data of size {data_size}")

@Step(r"await socket (?P<socket_varname>{Variable}) receives a data(?: \((?:timeout: (?P<timeout_sec>{Float}) s)?(?: ; )?(?:polling: (?P<polling_sec>{Float}) s)?\))?")
def step_impl(context, socket_varname, timeout_sec, polling_sec):
    """Wait socket receives at least one data
    """
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    timeout_sec = StepTools.evaluate_scenario_parameter(timeout_sec)
    polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
    
    if timeout_sec is None:
        timeout_sec = 10
    
    wait = WaitChange(f"Wait data reception (socket: {sock})",
                      lambda: sock.received_data_size,
                      timeout_seconds=timeout_sec, polling_seconds=polling_sec)
    wait.without_raise_on_timeout()
    data_size = wait.execute()
    if data_size == 0:
        raise FunctionalException(f"[{sock.name}] No data was received (timeout: {wait.timeout} seconds)")

@Step(r"await socket (?P<socket_varname>{Variable}) receives data(?: \((?:first timeout: (?P<first_timeout_sec>{Float}) s)?(?: ; )?(?:window: (?P<window_sec>{Float}) s)?(?: ; )?(?:polling: (?P<polling_sec>{Float}) s)?\))?")
def step_impl(context, socket_varname, first_timeout_sec, window_sec, polling_sec):
    """Wait socket stop to receive data
    """
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    first_timeout_sec = StepTools.evaluate_scenario_parameter(first_timeout_sec)
    window_sec = StepTools.evaluate_scenario_parameter(window_sec)
    polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
    
    wait = WaitEndChange(f"Wait end of data reception (socket: {sock})",
                         lambda: sock.received_data_size,
                         first_timeout_seconds=first_timeout_sec, window_seconds=window_sec, polling_seconds=polling_sec)
    wait.without_raise_on_timeout()
    data_size = wait.execute()
    if data_size == 0:
        raise FunctionalException(f"[{sock.name}] No data was received (timeout: {wait.timeout} seconds)")

@Given(r"reset stored received data in socket (?P<socket_varname>{Variable})")
def step_impl(context, socket_varname):
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    sock.reset_received_data()



# For client and servers managing messages

@Step(r"write message (?P<data>{Bytes}) \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, data, socket_varname):
    """Send message
    """
    data = StepTools.evaluate_scenario_parameter(data)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    sock.write_message(data)

@Step(r"(?P<var_name>{Variable}) = read message \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, var_name, socket_varname):
    """Read a received message.
    If no message is in socket, None is returned.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    res = sock.read_message()
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = read messages \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, var_name, socket_varname):
    """Read all received messages.
    If no message is in socket, an empty list is returned.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    res = sock.read_messages()
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = received messages \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, var_name, socket_varname):
    """Get received messages without removing from socket
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    res = sock.messages
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = number of received messages \(socket: (?P<socket_varname>{Variable})\)")
def step_impl(context, var_name, socket_varname):
    """Get received messages without removing from socket
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    
    res = sock.nb_messages
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"socket (?P<socket_varname>{Variable}) doesn't receive any message(?: \((?:timeout: (?P<timeout_sec>{Float}) s)?(?: ; )?(?:polling: (?P<polling_sec>{Float}) s)?\))?")
def step_impl(context, socket_varname, timeout_sec, polling_sec):
    """Wait and verify socket doesn't receive any message
    """
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    timeout_sec = StepTools.evaluate_scenario_parameter(timeout_sec)
    polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
    
    if timeout_sec is None:
        timeout_sec = 10
    
    wait = WaitChange(f"Wait end of message reception (socket: {sock})",
                      lambda: sock.nb_messages,
                      timeout_seconds=timeout_sec, polling_seconds=polling_sec)
    wait.without_raise_on_timeout()
    nb_messages = wait.execute()
    if nb_messages > 0:
        raise FunctionalException(f"[{sock.name}] Socket has received {nb_messages} messages (timeout: {wait.timeout} seconds)")

@Step(r"await socket (?P<socket_varname>{Variable}) receives (?:(?P<no_str>no) )?messages(?: \((?:first timeout: (?P<first_timeout_sec>{Float}) s)?(?: ; )?(?:window: (?P<window_sec>{Float}) s)?(?: ; )?(?:polling: (?P<polling_sec>{Float}) s)?\))?")
def step_impl(context, socket_varname, no_str, first_timeout_sec, window_sec, polling_sec):
    """Wait until socket receives messages or no messages.
    Wait during max first_timeout_sec duration for a first message, then, and after each new message, wait during max window_sec duration for a new message.
    If no message is received during first_timeout_sec duration, an error is raised only if messages are waited (ie 'no ' is not added when calling step).
    """
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    no_messages = no_str is not None
    first_timeout_sec = StepTools.evaluate_scenario_parameter(first_timeout_sec)
    window_sec = StepTools.evaluate_scenario_parameter(window_sec)
    polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
    
    wait = WaitEndChange(f"Wait until socket receives {no_str if no_str is not None else ''}messages (socket: {sock})",
                         lambda: sock.nb_messages,
                         first_timeout_seconds=first_timeout_sec, window_seconds=window_sec, polling_seconds=polling_sec)
    wait.without_raise_on_timeout()
    nb_messages = wait.execute()
    if not no_messages and nb_messages == 0:
        raise FunctionalException(f"[{sock.name}] No message was received (timeout: {wait.timeout} seconds)")

@Step(r"await socket (?P<socket_varname>{Variable}) receives a message(?: \((?:timeout: (?P<timeout_sec>{Float}) s)?(?: ; )?(?:polling: (?P<polling_sec>{Float}) s)?\))?")
def step_impl(context, socket_varname, timeout_sec, polling_sec):
    """Get received messages without removing from socket
    """
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    timeout_sec = StepTools.evaluate_scenario_parameter(timeout_sec)
    polling_sec = StepTools.evaluate_scenario_parameter(polling_sec)
    
    if timeout_sec is None:
        timeout_sec = 10
    
    wait = WaitChange(f"Wait a message reception (socket: {sock})",
                      lambda: sock.nb_messages,
                      timeout_seconds=timeout_sec, polling_seconds=polling_sec)
    wait.without_raise_on_timeout()
    nb_messages = wait.execute()
    if nb_messages == 0:
        raise FunctionalException(f"[{sock.name}] No message was received (timeout: {wait.timeout} seconds)")

@Given(r"reset stored received messages in socket (?P<socket_varname>{Variable})")
def step_impl(context, socket_varname):
    sock = StepTools.evaluate_scenario_parameter(socket_varname)
    sock.reset_received_messages()
    


