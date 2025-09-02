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
from holado_sftp.tools.sftp.sftp_server import SFTPServer
from holado_core.common.exceptions.functional_exception import FunctionalException
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_test.scenario.step_tools import StepTools

logger = logging.getLogger(__name__)

if SFTPServer.is_available():

    def __get_session_context():
        return SessionContext.instance()
    
    def __get_scenario_context():
        return __get_session_context().get_scenario_context()
    
    def __get_text_interpreter():
        return __get_scenario_context().get_text_interpreter()
    
    def __get_variable_manager():
        return __get_scenario_context().get_variable_manager()
    
    
    @Given(r"(?P<var_name>{Variable}) = new sFTP server")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        
        sftpserver_params = ""
        if "host" in kwargs:
            sftpserver_params += f" --host {kwargs.pop('host')}"
        if "port" in kwargs:
            sftpserver_params += f" --port {kwargs.pop('port')}"
        if "level" in kwargs:
            sftpserver_params += f" --level {kwargs.pop('level')}"
        if "keyfile" in kwargs:
            sftpserver_params += f" --keyfile {kwargs.pop('keyfile')}"
        sftpserver_params = sftpserver_params.strip()
  
        if "name" in kwargs:
            name = kwargs.pop("name")
        else:
            name = f"sftpserver {sftpserver_params}" 
        
        if "root_path" in kwargs:
            root_path = kwargs.pop("root_path")
            __get_session_context().path_manager.makedirs(root_path, is_directory = True)
        else:
            raise FunctionalException(f"The parameter 'root_path' is mandatory")
            
        if kwargs:
            raise FunctionalException(f"Unknown parameters: {kwargs}")
        
        server = SFTPServer(name, root_path, sftpserver_params)
        
        __get_variable_manager().register_variable(var_name, server)
    
    @Step(r"start sFTP server (?P<var_server>{Variable})")
    def step_impl(context, var_server):
        server = StepTools.evaluate_variable_value(var_server)
        server.start()
    
    
