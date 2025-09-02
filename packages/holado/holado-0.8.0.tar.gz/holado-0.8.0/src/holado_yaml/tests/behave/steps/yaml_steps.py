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
from holado_yaml.yaml.yaml_manager import YAMLManager
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools

logger = logging.getLogger(__name__)


if YAMLManager.is_available():
    
    def __get_scenario_context():
        return SessionContext.instance().get_scenario_context()
    
    def __get_variable_manager():
        return __get_scenario_context().get_variable_manager()
    
    def __get_path_manager():
        return SessionContext.instance().path_manager
    
    def __get_client(client_type, client):
        client_type = StepTools.evaluate_scenario_parameter(client_type)
        client = StepTools.evaluate_variable_name(client)
        
        if client is None:
            return YAMLManager.get_client(client_type)
        else:
            return client
    
    
    @Step(r"(?P<var_name>{Variable}) = new YAML client(?: \(client type: (?P<client_type>{Str})\))?")
    def step_impl(context, var_name, client_type):
        var_name = StepTools.evaluate_variable_name(var_name)
        client_type = StepTools.evaluate_scenario_parameter(client_type)
        
        res = YAMLManager.get_client(client_type)
        
        __get_variable_manager().register_variable(var_name, res)
    
    
    # Manage YAML objects
    
    @Step(r"(?P<var_name>{Variable}) = YAML object(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?\))?")
    def step_impl(context, var_name, client_type, client):
        var_name = StepTools.evaluate_variable_name(var_name)
        client = __get_client(client_type, client)
        text = BehaveStepTools.get_step_multiline_text(context)
        
        res = client.load_string(text)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"update YAML object (?P<obj>{Variable}) with data (?P<data>{Variable})(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?\))?")
    def step_impl(context, obj, data, client_type, client):  # @DuplicatedSignature
        obj = StepTools.evaluate_scenario_parameter(obj)
        data = StepTools.evaluate_scenario_parameter(data)
        client = __get_client(client_type, client)
        
        client.update_data(obj, data)
    
    @Step(r"(?P<var_name>{Variable}) = convert YAML object (?P<obj>{Variable}) to string(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?\))?")
    def step_impl(context, var_name, obj, client_type, client):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        obj = StepTools.evaluate_scenario_parameter(obj)
        client = __get_client(client_type, client)
        
        res = client.save_in_string(obj)
        
        __get_variable_manager().register_variable(var_name, res)
    
    
    # Manage YAML strings
    
    @Step(r"(?P<var_name>{Variable}) = load YAML string (?P<text>{Str})(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?\))?")
    def step_impl(context, var_name, text, client_type, client):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        text = StepTools.evaluate_scenario_parameter(text)
        client = __get_client(client_type, client)
        
        res = YAMLManager.load_string(text, client_type=client_type)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = update YAML string (?P<text>{Str}) with data (?P<data>{Variable})(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?\))?")
    def step_impl(context, var_name, text, data, client_type, client):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        text = StepTools.evaluate_scenario_parameter(text)
        data = StepTools.evaluate_scenario_parameter(data)
        client = __get_client(client_type, client)
        
        res = YAMLManager.update_string(text, data, client=client)
        
        __get_variable_manager().register_variable(var_name, res)
    
    
    # Manage YAML files
    
    @Step(r"(?P<var_name>{Variable}) = load YAML file (?P<path>{Str})(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?\))?")
    def step_impl(context, var_name, path, client_type, client):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        path = StepTools.evaluate_scenario_parameter(path)
        client = __get_client(client_type, client)
        
        res = YAMLManager.load_file(path, client=client)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = load multiple documents YAML file (?P<path>{Str})(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?\))?")
    def step_impl(context, var_name, path, client_type, client):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        path = StepTools.evaluate_scenario_parameter(path)
        client = __get_client(client_type, client)
        
        res = YAMLManager.load_multiple_documents_file(path, client=client)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"save (?P<data>{Variable}) in YAML file (?P<path>{Str})(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?\))?")
    def step_impl(context, data, path, client_type, client):  # @DuplicatedSignature
        data = StepTools.evaluate_scenario_parameter(data)
        path = StepTools.evaluate_scenario_parameter(path)
        client = __get_client(client_type, client)
        
        YAMLManager.save_in_file(path, data, client=client)
    
    @Step(r"update YAML file (?P<path>{Str}) with data (?P<data>{Variable})(?: \((?:client type: (?P<client_type>{Str}))?(?: ; )?(?:client: (?P<client>{Variable}))?(?: ; )?(?:(?P<with_backup_str>with backup))?(?: ; )?(?:backup extension: (?P<backup_extension>{Str}))?\))?")
    def step_impl(context, path, data, client_type, client, with_backup_str, backup_extension):  # @DuplicatedSignature
        path = StepTools.evaluate_scenario_parameter(path)
        data = StepTools.evaluate_scenario_parameter(data)
        client = __get_client(client_type, client)
        with_backup = with_backup_str is not None
        backup_extension = StepTools.evaluate_scenario_parameter(backup_extension)
        
        YAMLManager.update_file(path, data, client=client, with_backup=with_backup, backup_extension=backup_extension)
    
    @Step(r"restore YAML file (?P<path>{Str})(?: \((?:backup extension: (?P<backup_extension>{Str}))?\))?")
    def step_impl(context, path, backup_extension):  # @DuplicatedSignature
        path = StepTools.evaluate_scenario_parameter(path)
        backup_extension = StepTools.evaluate_scenario_parameter(backup_extension)
        
        YAMLManager.restore_file(path, backup_extension=backup_extension)




