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


from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
import logging
from holado_test.scenario.step_tools import StepTools
import os

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

def __get_resource_manager():
    return SessionContext.instance().resource_manager


@Given(r"(?P<var_name>{Variable}) = path to local resource file (?P<filename>{Str})")
def step_impl(context, var_name, filename):
    var_name = StepTools.evaluate_variable_name(var_name)
    filename = StepTools.evaluate_scenario_parameter(filename)
    
    if os.path.isabs(filename):
        res = filename
    else:
        res = __get_resource_manager().get_path(filename)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = lines of local resource file (?P<filename>{Str})(?: \(offset: (?P<offset>{Int}) ; size: (?P<size>{Int})\))?")
def step_impl(context, var_name, filename, offset, size):
    execute_steps(u"""
        Given __FILE_PATH__@ = path to local resource file {filename}
        Given __LINES__@ = lines of file __FILE_PATH__@
        Given {var_name} = __LINES__@[{offset}:{offset}+{size}]
        """.format(var_name=var_name, filename=filename, offset=offset, size=size))

@Given(r"(?P<var_name>{Variable}) = open local resource file (?P<filename>{Str})")
def step_impl(context, var_name, filename):
    execute_steps(u"""
        Given __FILE_PATH__@ = path to local resource file {filename}
        Given {var_name} = open file __FILE_PATH__@ in mode 'r'
        """.format(var_name=var_name, filename=filename))


