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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_sftp.tools.sftp.sftp_client import SFTPClient
from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter

logger = logging.getLogger(__name__)


if SFTPClient.is_available():

    def __get_session_context():
        return SessionContext.instance()
    
    def __get_scenario_context():
        return __get_session_context().get_scenario_context()
    
    def __get_variable_manager():
        return __get_scenario_context().get_variable_manager()
    
        
    @Given(r"(?P<var_name>{Variable}) = new sFTP client")
    def step_impl(context, var_name):
        """
        Create a new sFTP client.
        
        Note: Parameter 'private_key' can be a string with private key file path, 
              or a variable name that contains private key file content.
              When working with private key file content, it is important to pass it through a variable,
              otherwise strange errors can appear.
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        
        try:
            client = SFTPClient()
            client.connect(**kwargs)
        except Exception as exc:
            raise FunctionalException(str(exc)) from exc

        __get_variable_manager().register_variable(var_name, client)
        
    @Step(r"execute \[(?P<command>{Any})\] \(sFTP client: (?P<var_client>{Variable})\)")
    def step_impl(context, command, var_client):
        """
        Execute any method in class pysftp.Connection (cf https://pysftp.readthedocs.io/en/release_0.2.9/pysftp.html).
        An exception is raised if the method returns a result.
        """
        # command = StepTools.evaluate_scenario_parameter(command)
        command = StepTools.evaluate_string_parameter(command)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable
        
        result = eval("client.connection." + command)
        if result:
            raise TechnicalException(f"Unexpected result to command [{command}]: {result}")
        
    @Step(r"(?P<var_name>{Variable}) = result of \[(?P<command>{Any})\] \(sFTP client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, command, var_client):
        """
        Execute any method in class pysftp.Connection (cf https://pysftp.readthedocs.io/en/release_0.2.9/pysftp.html).
        The result is stored in given variable.
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        # command = StepTools.evaluate_scenario_parameter(command)
        command = StepTools.evaluate_string_parameter(command)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable
        
        result = eval("client.connection." + command)
        
        __get_variable_manager().register_variable(var_name, result)
        


    
