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
from holado_core.common.tools.string_tools import StrTools

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


@Given(r"(?P<var_name>{Variable}) = convert list (?P<hex_list>{List}) of hexadecimal strings to list of bytes")
def step_impl(context, var_name, hex_list):
    var_name = StepTools.evaluate_variable_name(var_name)
    hex_list = StepTools.evaluate_scenario_parameter(hex_list)
    
    res = []
    for hex_str in hex_list:
        res.append(StrTools.hex_to_bytes(hex_str))
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = convert list (?P<str_list>{List}) of (?:strings|bytes) to list of hexadecimal strings")
def step_impl(context, var_name, str_list):
    var_name = StepTools.evaluate_variable_name(var_name)
    str_list = StepTools.evaluate_scenario_parameter(str_list)
    
    res = []
    for str_el in str_list:
        res.append(StrTools.to_bytes(str_el).hex())
    
    __get_variable_manager().register_variable(var_name, res)
    
    
    
    