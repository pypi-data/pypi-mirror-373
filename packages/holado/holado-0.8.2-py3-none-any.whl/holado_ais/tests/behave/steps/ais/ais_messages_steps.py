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
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_ais.ais.ais_messages import AISMessages
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_ais.ais.enums import AISMessageType
from holado_core.common.tools.string_tools import StrTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

def __get_ais_messages():
    return SessionContext.instance().ais_messages


if AISMessages.is_available():
    @Step(r"(?P<var_name>{Variable}) = decode AIS message of type (?P<msg_type>{Str}) from bitarray (?P<msg_bitarray>{Str})")
    def step_impl(context, var_name, msg_type, msg_bitarray):
        var_name = StepTools.evaluate_variable_name(var_name)
        msg_type = StepTools.evaluate_scenario_parameter(msg_type)
        msg_bitarray = StepTools.evaluate_scenario_parameter(msg_bitarray)
        
        res = __get_ais_messages().decode_message(msg_type, msg_bitarray)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = encode AIS message")
    def step_impl(context, var_name):
        """
        Encode an AIS message to NMEA format
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.get_step_table(context)
        
        res = __get_ais_messages().encode(table)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = encode AIS message (?P<message>{Any})")
    def step_impl(context, var_name, message):
        """
        Encode an AIS message to NMEA format
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        msg = StepTools.evaluate_scenario_parameter(message)
        table = BehaveStepTools.get_step_table(context)
        
        if table is not None:
            kwargs = ValueTableConverter.convert_table_with_header_to_dict(table)
        else:
            kwargs = {}
        res = __get_ais_messages().encode(msg, **kwargs)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = encode AIS raw payload (?P<raw_payload>{Any}) to NMEA")
    def step_impl(context, var_name, raw_payload):
        """
        Encode an AIS message to NMEA format
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        raw_payload = StepTools.evaluate_scenario_parameter(raw_payload)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        
        if table is not None:
            kwargs = ValueTableConverter.convert_table_with_header_to_dict(table)
        else:
            kwargs = {}
        res = __get_ais_messages().encode_raw_payload(raw_payload, **kwargs)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = new AIS message of type (?P<ais_message_type>{Str}) as bitarray bytes")
    def step_impl(context, var_name, ais_message_type):
        var_name = StepTools.evaluate_variable_name(var_name)
        msg_type = StepTools.evaluate_scenario_parameter(ais_message_type)
        
        if hasattr(context, 'table') and context.table is not None:
            table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        else:
            table = {}
        
        res = __get_ais_messages().new_message_as_bitarray_bytes(msg_type, table)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @Step(r"(?P<var_name>{Variable}) = new AIS message of type (?P<msg_type>{Int})")
    def step_impl(context, var_name, msg_type:int):
        var_name = StepTools.evaluate_variable_name(var_name)
        msg_type = StepTools.evaluate_scenario_parameter(msg_type)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        
        res = __get_ais_messages().new_message(msg_type, table)
        
        __get_variable_manager().register_variable(var_name, res)

    @Step(r"(?P<var_name>{Variable}) = convert AIS message (?P<msg>{Str}) to binary string")
    def step_impl(context, var_name, msg):
        var_name = StepTools.evaluate_variable_name(var_name)
        msg = StepTools.evaluate_scenario_parameter(msg)
        
        res = __get_ais_messages().convert_message_to_binary_str(msg)
        
        __get_variable_manager().register_variable(var_name, res)

    @Step(r"(?P<var_name>{Variable}) = convert AIS message (?P<msg>{Str}) to bytes")
    def step_impl(context, var_name, msg):
        var_name = StepTools.evaluate_variable_name(var_name)
        msg = StepTools.evaluate_scenario_parameter(msg)
        
        res = __get_ais_messages().convert_message_to_bytes(msg)
        
        __get_variable_manager().register_variable(var_name, res)

    @Step(r"(?P<var_name>{Variable}) = convert AIS message (?P<msg>{Str}) to hexadecimal string")
    def step_impl(context, var_name, msg):
        var_name = StepTools.evaluate_variable_name(var_name)
        msg = StepTools.evaluate_scenario_parameter(msg)
        
        res = __get_ais_messages().convert_message_to_bytes(msg)
        res = StrTools.to_hex(res)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = decode NMEA AIS message (?P<encoded_ais_message>{Str})(?P<dictionnary_str> as dictionnary)?")
    def step_impl(context, var_name, encoded_ais_message, dictionnary_str):
        var_name = StepTools.evaluate_variable_name(var_name)
        encoded_ais_message = StepTools.evaluate_scenario_parameter(encoded_ais_message)
        
        if isinstance(encoded_ais_message, list):
            res = __get_ais_messages().decode(*encoded_ais_message)
        else:
            res = __get_ais_messages().decode(encoded_msg=encoded_ais_message)
            
        if dictionnary_str is not None:
            res = res.asdict()
            
        __get_variable_manager().register_variable(var_name, res)
    
    #TODO EKL: rename step
    @Given(r"(?P<var_name>{Variable}) = split NMEA AIS message (?P<ais_message>{Bytes}|{Str}) to fields")
    def step_impl(context, var_name, ais_message):
        var_name = StepTools.evaluate_variable_name(var_name)
        ais_message = StepTools.evaluate_scenario_parameter(ais_message)
        
        res = __get_ais_messages().split_message_to_fields(ais_message)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Given(r"(?P<var_name>{Variable}) = split (?P<ais_raw>{Bytes}|{Str}) to NMEA AIS sentences")
    def step_impl(context, var_name, ais_raw):
        var_name = StepTools.evaluate_variable_name(var_name)
        ais_raw = StepTools.evaluate_scenario_parameter(ais_raw)
        
        res = __get_ais_messages().split_raw_to_sentences(ais_raw)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @Given(r"(?P<tb_var_name>{Variable}), (?P<msg_var_name>{Variable}) = split NMEA AIS sentence (?P<ais_sentence>{Bytes}|{Str}) to tag block and message")
    def step_impl(context, tb_var_name, msg_var_name, ais_sentence):
        tb_var_name = StepTools.evaluate_variable_name(tb_var_name)
        msg_var_name = StepTools.evaluate_variable_name(msg_var_name)
        ais_sentence = StepTools.evaluate_scenario_parameter(ais_sentence)
        
        tb, msg = __get_ais_messages().split_sentence_to_tab_block_and_message(ais_sentence)
        
        __get_variable_manager().register_variable(tb_var_name, tb)
        __get_variable_manager().register_variable(msg_var_name, msg)
        
    @Given(r"(?P<var_name>{Variable}) = split NMEA AIS Tag Block (?P<tag_block>{Bytes}|{Str}) to dict")
    def step_impl(context, var_name, tag_block):
        var_name = StepTools.evaluate_variable_name(var_name)
        tag_block = StepTools.evaluate_scenario_parameter(tag_block)
        
        res = __get_ais_messages().convert_tag_block_to_dict(tag_block)
        
        __get_variable_manager().register_variable(var_name, res)
        
    @Given(r"(?P<var_name>{Variable}) = NMEA AIS message (?P<ais_message>{Bytes}|{Str}) with message ID replaced by (?P<replacement_id>{Bytes}|{Str})")
    def step_impl(context, var_name, ais_message, replacement_id):
        var_name = StepTools.evaluate_variable_name(var_name)
        ais_message = StepTools.evaluate_scenario_parameter(ais_message)
        replacement_id = StepTools.evaluate_scenario_parameter(replacement_id)
        
        res = __get_ais_messages().replace_message_id_in_message(ais_message, replacement_id)
        
        __get_variable_manager().register_variable(var_name, res)
    
    


