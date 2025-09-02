# -*- coding: utf-8 -*-

import logging
from holado.common.context.session_context import SessionContext
from holado_system.system.command.command import Command, CommandStates
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_test.scenario.step_tools import StepTools
from holado_core.tools.abstracts.blocking_command_service import BlockingCommandService
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)

def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

@Given(r"(?P<var_name>{Variable}) = new command (?P<cmd>{AnyStr})(?<! with)")
def step_impl(context, var_name, cmd):
    var_name = StepTools.evaluate_variable_name(var_name)
    cmd = StepTools.evaluate_string_parameter(cmd)
    obj_cmd = Command(cmd)
    __get_variable_manager().register_variable(var_name, obj_cmd)

@Given(r"(?P<var_name>{Variable}) = new command (?P<cmd>{AnyStr}) with")
def step_impl(context, var_name, cmd):
    var_name = StepTools.evaluate_variable_name(var_name)
    cmd = StepTools.evaluate_scenario_parameter(cmd)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    arguments_dict = ValueTableConverter.convert_name_value_table_2_dict(table)
    
    
    blocking = False
    auto_stop = False
    do_log_output = False
    do_raise_on_stderr = False
    name = ''
    
    if 'blocking' in arguments_dict:
        blocking = arguments_dict['blocking']
        if 'name' in arguments_dict:
            name = arguments_dict['name']
        if 'auto_stop' in arguments_dict:
            auto_stop = arguments_dict['auto_stop']
    else:
        if 'name' in arguments_dict:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("Argument 'name' is useless for non-blocking commands")
        if 'auto_stop' in arguments_dict:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("Argument 'auto_stop' is useless for non-blocking commands")
    if 'do_log_output' in arguments_dict:
        do_log_output = arguments_dict['do_log_output']
    if 'do_raise_on_stderr' in arguments_dict:
        do_raise_on_stderr = arguments_dict['do_raise_on_stderr']
    
    if blocking:
        obj_cmd = BlockingCommandService(name, cmd, do_log_output=do_log_output, do_raise_on_stderr=do_raise_on_stderr)
        obj_cmd.auto_stop = auto_stop
    else:
        obj_cmd = Command(cmd, do_log_output=do_log_output, do_raise_on_stderr=do_raise_on_stderr)
    
    __get_variable_manager().register_variable(var_name, obj_cmd)

@Then(r"command (?P<var_name>{Variable}) has status (?P<expected_status>Ready|Running|Success|Error)")
def step_impl(context, var_name, expected_status):
    obj_cmd =  StepTools.evaluate_variable_value(var_name)
    
    if isinstance(obj_cmd, Command):
        state = obj_cmd.state
    elif isinstance(obj_cmd, BlockingCommandService):
        state = obj_cmd.status
    else:
        raise TechnicalException(f"Variable {var_name} is not a command")
        
    if state is not CommandStates[expected_status]:
        raise FunctionalException(f"Command state error : expected {expected_status} found {state.name}")
    
@Given(r"run command (?P<var_name>{Variable})")
def step_impl(context, var_name):
    obj_cmd =  StepTools.evaluate_variable_value(var_name)
    obj_cmd.start()
    
    