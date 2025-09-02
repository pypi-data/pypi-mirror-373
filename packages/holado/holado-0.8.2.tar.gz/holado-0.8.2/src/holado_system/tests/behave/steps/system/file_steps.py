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
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_system.system.filesystem.file import File
import base64
import os.path
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.typing import Typing
from zipfile import ZipFile

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


@Then(r"file (?P<path>{Str}) (?P<exists_str>exists|doesn't exist)")
def step_impl(context, path, exists_str):  # @DuplicatedSignature
    path = StepTools.evaluate_scenario_parameter(path)
    exists = exists_str == "exists"
    
    __get_path_manager().check_file_exists(path, do_exist=exists, raise_exception=True)

@Given(r"(?P<var_name>{Variable}) = is path (?P<path>{Str}) an absolute file path")
def step_impl(context, var_name, path):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    path = StepTools.evaluate_scenario_parameter(path)
    res = os.path.isabs(path)
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = file name of path (?P<path>{Str})(?: \((?P<without_extension_str>without extension)\))?")
def step_impl(context, var_name, path, without_extension_str):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    path = StepTools.evaluate_scenario_parameter(path)
    
    res = os.path.basename(path)
    if without_extension_str is not None:
        res = os.path.splitext(res)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = open file (?P<path>{Str}) in mode (?P<mode>{Str})")
def step_impl(context, var_name, path, mode):
    var_name = StepTools.evaluate_variable_name(var_name)
    execute_steps(u"""
        Given {var_name} = open file {path}
            | Name    | Value  |
            | 'mode'  | {mode} |
        """.format(var_name=var_name, path=path, mode=mode))

@Given(r"(?P<var_name>{Variable}) = open file (?P<path>{Str})")
def step_impl(context, var_name, path):
    var_name = StepTools.evaluate_variable_name(var_name)
    path = StepTools.evaluate_scenario_parameter(path)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    open_kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
    
    __get_path_manager().makedirs(path)
    res = File(path, **open_kwargs)

    __get_variable_manager().register_variable(var_name, res)

@Given(r"close \(file: (?P<file>{Variable})\)")
def step_impl(context, file):
    file = StepTools.evaluate_scenario_parameter(file)
    file.close()

@When(r"write line (?P<line>{Str}) \(file: (?P<file>{Variable})\)")
def step_impl(context, line, file):
    line = StepTools.evaluate_scenario_parameter(line)
    file = StepTools.evaluate_scenario_parameter(file)
    
    file.writelines([line])
    
@When(r"write lines (?P<lines_list>{List}) \(file: (?P<file>{Variable})\)")
def step_impl(context, lines_list, file):
    lines_list = StepTools.evaluate_scenario_parameter(lines_list)
    file = StepTools.evaluate_scenario_parameter(file)
    
    file.writelines(lines_list)
    
@When(r"write (?P<data>{Str}) \(file: (?P<file>{Variable})\)")
def step_impl(context, data, file):
    data = StepTools.evaluate_scenario_parameter(data)
    file = StepTools.evaluate_scenario_parameter(file)
    
    file.write(data)

@Given(r"(?P<var_name>{Variable}) = content of(?:(?P<is_text_file_str> text))? file (?P<path>{Str})")
def step_impl(context, var_name, is_text_file_str, path):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    is_text_file = is_text_file_str is not None
    path = StepTools.evaluate_scenario_parameter(path)
    
    res = File.get_file_content(path, is_text_file)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = content of file (?P<path>{Str}) in base 64")
def step_impl(context, var_name, path):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    path = StepTools.evaluate_scenario_parameter(path)

    res = File.get_file_content_in_base64(path)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = lines of file (?P<path>{Str})")
def step_impl(context, var_name, path):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    path = StepTools.evaluate_scenario_parameter(path)

    with File(path, mode="r") as fin:
        lines = fin.readlines()
    res = list(map(lambda x: x.strip('\n'), lines))
    
    __get_variable_manager().register_variable(var_name, res)


@Given(r"(?P<var_name>{Variable}) = path to file with name (?P<filename>{Str})")
def step_impl(context, var_name, filename):
    var_name = StepTools.evaluate_variable_name(var_name)
    filename = StepTools.evaluate_scenario_parameter(filename)
    
    dest_path = __get_report_manager().current_scenario_report.get_path("files")
    res = os.path.join(dest_path, filename)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = path to timestamped file with prefix (?P<path_prefix>{Str}) and extension (?P<path_ext>{Str})")
def step_impl(context, var_name, path_prefix, path_ext):
    var_name = StepTools.evaluate_variable_name(var_name)
    prefix = StepTools.evaluate_scenario_parameter(path_prefix)
    ext = StepTools.evaluate_scenario_parameter(path_ext)

    res = __get_path_manager().get_timestamped_path(prefix, ext)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = create file with prefix (?P<path_prefix>{Str}) and extension (?P<path_ext>{Str}) and content (?P<content>{Str})")
def step_impl(context, var_name, path_prefix, path_ext, content):
    var_name = StepTools.evaluate_variable_name(var_name)
    execute_steps(u"""
        Given __FILENAME__@ = path to timestamped file with prefix {path_prefix} and extension {path_ext}
        Given {var_name} = create file with name __FILENAME__@ and content {content}
        """.format(path_prefix=path_prefix, path_ext=path_ext, var_name=var_name, content=content) )

@Given(r"(?P<var_name>{Variable}) = create file with name (?P<path_name>{Str}) and content (?P<content>{Str})")
def step_impl(context, var_name, path_name, content):
    var_name = StepTools.evaluate_variable_name(var_name)
    filename = StepTools.evaluate_scenario_parameter(path_name)
    content = StepTools.evaluate_scenario_parameter(content)
    
    dest_path = __get_report_manager().current_scenario_report.get_path("files")
    file_path = os.path.join(dest_path, filename)
    __get_path_manager().makedirs(file_path)
    
    File.create_file_with_content(file_path, content)

    __get_variable_manager().register_variable(var_name, file_path)


@Given(r"(?P<var_name>{Variable}) = create file with name (?P<path_name>{Str})")
def step_impl(context, var_name, path_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    content = BehaveStepTools.get_step_multiline_text(context, raise_exception_if_none=False)
    if content is None:
        content = ""
    __get_variable_manager().register_variable("__FILE_CONTENT__@", content)
    
    execute_steps(u"""
        Given {var_name} = create file with name {path_name} and content __FILE_CONTENT__@
        """.format(var_name=var_name, path_name=path_name) )


@Step(r"extract files from zip file (?P<zip_path>{Str}) in path (?P<dest_path>{Str})")
def step_impl(context, zip_path, dest_path):
    """
    extracts zip contents into the specified path.
    """
    zip_path = StepTools.evaluate_scenario_parameter(zip_path)
    dest_path = StepTools.evaluate_scenario_parameter(dest_path)
    
    __get_path_manager().makedirs(dest_path)
    
    # Extract files from the zip archive
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_path)
        logger.debug(f"Extracted files to {dest_path}")