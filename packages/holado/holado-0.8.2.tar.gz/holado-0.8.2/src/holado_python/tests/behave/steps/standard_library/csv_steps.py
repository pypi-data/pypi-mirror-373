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
from holado_test.behave.behave import render_step_table
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_system.system.filesystem.file import File
import base64
import csv
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.tables.table_row import TableRow
import os.path
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.csv import CsvManager

logger = logging.getLogger(__name__)



def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

def __get_report_manager():
    return SessionContext.instance().report_manager

def __get_path_manager():
    return SessionContext.instance().path_manager


@Given(r"(?P<var_name>{Variable}) = table with CSV content (?P<content>{Str})")
def step_impl(context, var_name, content):
    var_name = StepTools.evaluate_variable_name(var_name)
    execute_steps(u"""
        Given __FILE_CSV__@ = create CSV file with prefix 'csv_content' and content {content}
        Given {var_name} = table with content of CSV file __FILE_CSV__@
        """.format(var_name=var_name, content=content) )

@Given(r"(?P<var_name>{Variable}) = table with content of CSV file (?P<path>{Str})(?: \((?:encoding: (?P<encoding>{Str}))?(?: ; )?(?:dialect: (?P<dialect>{Str}))?(?: ; )?(?:delimiter: (?P<delimiter>{Str}))?(?: ; )?(?:quotechar: (?P<quotechar>{Str}))?(?: ; )?(?:quoting: (?P<quoting_str>ALL|MINIMAL|NONE|NONNUMERIC))?\))?")
def step_impl(context, var_name, path, encoding, dialect, delimiter, quotechar, quoting_str):
    var_name = StepTools.evaluate_variable_name(var_name)
    file_path = StepTools.evaluate_scenario_parameter(path)
    encoding = StepTools.evaluate_scenario_parameter(encoding)
    dialect = StepTools.evaluate_scenario_parameter(dialect)
    delimiter = StepTools.evaluate_scenario_parameter(delimiter)
    quotechar = StepTools.evaluate_scenario_parameter(quotechar)
    quoting_str = StepTools.evaluate_scenario_parameter(quoting_str)
    quoting = getattr(csv, f"QUOTE_{quoting_str}") if quoting_str is not None else None
    
    res = CsvManager.table_with_content_of_CSV_file(file_path, encoding, dialect, delimiter, quotechar, quoting)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = create CSV file with prefix (?P<path_prefix>{Str})")
def step_impl(context, var_name, path_prefix):
    var_name = StepTools.evaluate_variable_name(var_name)
    rendered_table = render_step_table(context.table, "    ")

    execute_steps(u"""
        Given __FILENAME__@ = path to timestamped file with prefix {path_prefix} and extension 'csv'
        Given {var_name} = create CSV file with name __FILENAME__@
        {table}
        """.format(path_prefix=path_prefix, var_name=var_name, table=rendered_table))

@Given(r"(?P<var_name>{Variable}) = create CSV file with name (?P<filename>{Str})")
def step_impl(context, var_name, filename):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.get_step_table(context)
    
    __get_variable_manager().register_variable("__TABLE_CONTENT__@", table)
    execute_steps(u"""
        Given {var_name} = create CSV file with name {filename} and table content __TABLE_CONTENT__@
        """.format(var_name=var_name, filename=filename) )

@Given(r"(?P<var_name>{Variable}) = create CSV file with name (?P<filename>{Str}) and table content (?P<table_content>{Variable})")
def step_impl(context, var_name, filename, table_content):
    var_name = StepTools.evaluate_variable_name(var_name)
    filename = StepTools.evaluate_scenario_parameter(filename)
    
    dest_path = __get_report_manager().current_scenario_report.get_path("files")
    file_path = os.path.join(dest_path, filename)
    __get_variable_manager().register_variable("__FILE_PATH__@", file_path)
    
    execute_steps(u"""
        Given create CSV file with path __FILE_PATH__@ and table content {table_content}
        """.format(table_content=table_content) )

    __get_path_manager().makedirs(file_path)
    
    __get_variable_manager().register_variable(var_name, file_path)

@Given(r"create CSV file with path (?P<file_path>{Str}) and table content (?P<table_content>{Variable})(?: \((?:encoding: (?P<encoding>{Str}))?(?: ; )?(?:dialect: (?P<dialect>{Str}))?(?: ; )?(?:delimiter: (?P<delimiter>{Str}))?(?: ; )?(?:quotechar: (?P<quotechar>{Str}))?(?: ; )?(?:quoting: (?P<quoting_str>ALL|MINIMAL|NONE|NONNUMERIC))?\))?")
def step_impl(context, file_path, table_content, encoding, dialect, delimiter, quotechar, quoting_str):
    file_path = StepTools.evaluate_scenario_parameter(file_path)
    table = StepTools.evaluate_variable_value(table_content)
    encoding = StepTools.evaluate_scenario_parameter(encoding)
    dialect = StepTools.evaluate_scenario_parameter(dialect)
    delimiter = StepTools.evaluate_scenario_parameter(delimiter)
    quotechar = StepTools.evaluate_scenario_parameter(quotechar)
    quoting_str = StepTools.evaluate_scenario_parameter(quoting_str)
    quoting = getattr(csv, f"QUOTE_{quoting_str}") if quoting_str is not None else None
    
    CsvManager.create_csv_file(file_path, table, encoding, dialect, delimiter, quotechar, quoting)

@Given(r"(?P<var_name>{Variable}) = create CSV file with prefix (?P<path_prefix>{Str}) and content (?P<content>{Str})")
def step_impl(context, var_name, path_prefix, content):
    var_name = StepTools.evaluate_variable_name(var_name)
    execute_steps(u"""
        Given {var_name} = create file with prefix {path_prefix} and extension 'csv' and content {content}
        """.format(var_name=var_name, path_prefix=path_prefix, content=content) )



