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


import logging
from holado_core.common.tools.tools import Tools
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_value.common.tables.comparators.table_2_value_table_comparator import Table2ValueTable_Comparator
from holado_core.common.tables.table_manager import TableManager
from holado_value.common.tables.value_table_manager import ValueTableManager
from holado.common.context.session_context import SessionContext
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_test.scenario.step_tools import StepTools
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


# Configure module to use internally
try:
    from suds.sudsobject import Printer, Object, Facade  # @UnresolvedImport @UnusedImport
    import suds.client  # @UnresolvedImport
    from suds.cache import NoCache  # @UnresolvedImport
    with_suds = True
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug("Module 'suds' will be used in web service steps")
except Exception as exc:
    with_suds_exception = exc
    with_suds = False

if not with_suds:
    try:
        import zeep  # @UnresolvedImport
        from zeep.transports import Transport  # @UnresolvedImport
        with_zeep = True
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Module 'zeep' will be used in web service steps")
    except Exception as exc:
        with_zeep_exception = exc
        with_zeep = False

if not with_suds and not with_zeep:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Web service module is not available. No package was found to manage web service steps (managed packages: suds, zeep).\nInitialization failed with suds on error: {with_suds_exception}\nInitialization failed with zeep on error: {with_zeep_exception}")


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

@Given(r"open web service client for WSDL (?P<wsdl_file>{Str})")
def step_impl(context, wsdl_file):
    wsdl_file = StepTools.evaluate_scenario_parameter(wsdl_file)
    
    if with_suds:
        context.ws_client = suds.client.Client(wsdl_file, cache=NoCache())
    elif with_zeep:
        transport = Transport(cache=None)
        context.ws_client = zeep.Client(wsdl_file, transport=transport)
    else:
        raise TechnicalException("No module was found to manage web service steps (managed modules: suds, zeep)")

@Given(r"open (?P<ws_name>{Str}) web service client")
def step_impl(context, ws_name):  # @DuplicatedSignature
    ws_name = StepTools.evaluate_scenario_parameter(ws_name)
    
    wsdl_file = 'http://10.0.3.247/{}/?wsdl'.format(ws_name)
    step = u"Given open web service client for WSDL '{}'".format(wsdl_file)
    execute_steps(step)

@Given(r'close web service client')
def step_impl(context):  # @DuplicatedSignature
    del context.ws_client

@When(r"(?P<var_name>{Variable}) = call web service (?P<method_name>{Str}) with parameters")
def step_impl(context, var_name, method_name):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    method_name = StepTools.evaluate_scenario_parameter(method_name)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    parameters = ValueTableConverter.convert_name_value_table_2_dict(table)
    logger.info("call web service '{}' with parameters [{}]".format(method_name, parameters))
    
    # Verify web service method
    if not hasattr(context, 'ws_client') or context.ws_client is None:
        raise FunctionalException("No web service is opened")
    try:
        method = getattr(context.ws_client.service, method_name)
    except:
        raise FunctionalException("Method '{}' doesn't exist in web service".format(method_name))
    
    # Call web service method
    result = method(**parameters)

    # Store result in variable
    logger.info("result of web service '{}': [{}]".format(method_name, result))
    __get_variable_manager().register_variable(var_name, result)


@Given(r"(?P<var_name>{Variable}) = new (?P<type_name>{Str}) from web service")
def step_impl(context, var_name, type_name):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    type_name = StepTools.evaluate_string_parameter(type_name)
    # Verify web service
    if not hasattr(context, 'ws_client') or context.ws_client is None:
        raise FunctionalException("No web service is opened")

    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    
    # Create object instance
    if with_suds:
        obj = context.ws_client.factory.create(type_name)
    elif with_zeep:
        obj = getattr(context.ws_client.type_factory('asgard.api_reseaux.tns'), type_name)()
    else:
        raise TechnicalException("No module was found to manage web service steps (managed modules: suds, zeep)")
    
    # Fill object
    if type_name == "stringArray":
        # Verify table structure
        ValueTableManager.verify_table_is_value_table(table)
        
        # Fill stringArray
        for row in table.rows:
            obj.string.append(row.get_cell(0).value)
    else:
        ValueTableManager.set_object_attributes_according_name_value_table(obj, table)
    
    # Store in variable
    __get_variable_manager().register_variable(var_name, obj)

@Then(r"(?P<object_string>{Str}) is (?P<type_name>{Str}) from web service")
def step_impl(context, object_string, type_name):  # @DuplicatedSignature
    obj = StepTools.evaluate_scenario_parameter(object_string)
    type_name = StepTools.evaluate_string_parameter(type_name)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    
    # Verify web service
    if not hasattr(context, 'ws_client') or context.ws_client is None:
        raise FunctionalException("No web service is opened")
    
    if with_suds:
        ws_obj = context.ws_client.factory.create(type_name)
    elif with_zeep:
        ws_obj = getattr(context.ws_client.type_factory('asgard.api_reseaux.tns'), type_name)()
    else:
        raise TechnicalException("No module was found to manage web service steps (managed modules: suds, zeep)")
        
    if isinstance(obj, Typing.get_object_class(ws_obj)):
        if type_name == "stringArray":
            # Convert stringArray to table
            obj_table = TableWithHeader()
            obj_table.header.add_cells_from_contents(["Value"])
            for obj_str in obj.string:
                obj_table.add_row(cells_content=[obj_str])
            
            # Compare tables
            comparator = Table2ValueTable_Comparator()
            comparator.equals(obj_table, table)
        else:
            # Convert object to table
            obj_table = TableManager.convert_object_attributes_2_name_value_table(obj)
            
            # Compare tables
            comparator = Table2ValueTable_Comparator()
            comparator.equals(obj_table, table)
    else:
        raise FunctionalException("Object is of type '{}' (expected type: '{}' ; type_name: '{}')".format(Typing.get_object_class_fullname(obj), Typing.get_object_class_fullname(ws_obj), type_name))


