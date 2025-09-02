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
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_docker.tools.docker_controller.docker_controller_manager import DockerControllerManager

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


@Given(r"(?P<var_name>{Variable}) = new Docker Controller client")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.get_step_table(context)
    if table is not None:
        kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
    else:
        kwargs = {}
    
    res = DockerControllerManager.new_client(**kwargs)

    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = list containers \(Docker Controller client: (?P<var_client>{Variable})\)")
def step_impl(context, var_name, var_client):
    var_name = StepTools.evaluate_variable_name(var_name)
    client = StepTools.evaluate_variable_value(var_client)
    
    res = client.get_containers_status()
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = get information on container (?P<name>{Str}) \(Docker Controller client: (?P<var_client>{Variable})\)")
def step_impl(context, var_name, name, var_client):
    var_name = StepTools.evaluate_variable_name(var_name)
    name = StepTools.evaluate_scenario_parameter(name)
    client = StepTools.evaluate_variable_value(var_client)
    
    res = client.get_container_info(name)
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?:(?P<or_start_str>start or ))?restart container (?P<name>{Str}) \(Docker Controller client: (?P<var_client>{Variable})\)")
def step_impl(context, or_start_str, name, var_client):
    or_start = or_start_str is not None
    name = StepTools.evaluate_scenario_parameter(name)
    client = StepTools.evaluate_variable_value(var_client)
    
    client.restart_container(name, start_if_gone=or_start)

@Step(r"start container (?P<name>{Str}) \(Docker Controller client: (?P<var_client>{Variable})\)")
def step_impl(context, name, var_client):
    name = StepTools.evaluate_scenario_parameter(name)
    client = StepTools.evaluate_variable_value(var_client)
    
    client.start_container(name)

@Step(r"stop container (?P<name>{Str})(?:(?P<if_started_str> if started))? \(Docker Controller client: (?P<var_client>{Variable})\)")
def step_impl(context, name, if_started_str, var_client):
    name = StepTools.evaluate_scenario_parameter(name)
    if_started = if_started_str is not None
    client = StepTools.evaluate_variable_value(var_client)
    
    client.stop_container(name, raise_if_gone=not if_started)

@Step(r"wait container (?P<name>{Str})(?:(?P<if_started_str> if started))? \(Docker Controller client: (?P<var_client>{Variable})\)")
def step_impl(context, name, if_started_str, var_client):
    name = StepTools.evaluate_scenario_parameter(name)
    if_started = if_started_str is not None
    client = StepTools.evaluate_variable_value(var_client)
    
    client.wait_container(name, raise_if_gone=not if_started)


