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
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.tools.converters.converter import Converter
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_python.standard_library.hashlib import HashTools

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


@Given(r"(?P<var_name>{Variable}) = code associated to content (?P<content>{AnyLazy})(?: \((?:size: (?P<code_size>{Int}))?(?: ; )?(?:prefix: (?P<prefix>{Str}))?\))?")
def step_impl(context, var_name, code_size, content, prefix):
    """Return a code computed with content as input.
    Dynamic part of the code is computed with blake2b hash algorithm.
    If code_size (minus length of prefix if defined) is not a multiple of 2, it is rounded to the multiple of 2 just below.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    code_size = StepTools.evaluate_scenario_parameter(code_size)
    content = StepTools.evaluate_scenario_parameter(content)
    prefix = StepTools.evaluate_scenario_parameter(prefix)
    
    res = HashTools.code(content, code_size, prefix)
    
    __get_variable_manager().register_variable(var_name, res)





