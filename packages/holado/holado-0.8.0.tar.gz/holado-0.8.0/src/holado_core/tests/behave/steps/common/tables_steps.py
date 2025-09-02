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


from holado_test.behave.behave import *  # @UnusedWildImport
from holado_test.behave.behave import render_step_table
import copy
from holado_value.common.tools.value_types import ValueTypes
from holado_core.common.tables.table_manager import TableManager
from holado_value.common.tables.comparators.table_2_value_table_comparator import Table2ValueTable_Comparator
from holado_core.common.tools.tools import reversed_enumerate
from holado_test.scenario.step_tools import StepTools
from holado_value.common.tables.comparators.table_2_value_table_with_header_comparator import Table2ValueTable_WithHeaderComparator
from holado_value.common.tables.comparators.table_2_value_table_cell_comparator import Table2ValueTable_CellComparator
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.tables.table import Table
from holado_core.common.tables.table_row import TableRow
from holado_core.common.tables.comparators.string_table_row_comparator import StringTableRowComparator
import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado.common.context.session_context import SessionContext
from holado_value.common.tables.value_table import ValueTable
from holado_value.common.tables.value_table_with_header import ValueTableWithHeader
from holado_core.common.tools.converters.converter import Converter
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_python.standard_library.typing import Typing
from holado_value.common.tables.value_table_manager import ValueTableManager
from holado_core.common.tables.converters.table_converter import TableConverter

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

@Given(r"(?P<var_name>{Variable}) = table")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    
    table = BehaveStepTools.convert_step_table_2_value_table(context.table)
    
    __get_variable_manager().register_variable(var_name, table)

@Given(r"(?P<var_name>{Variable}) = table with header")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    
    __get_variable_manager().register_variable(var_name, table)

@Given(r"(?P<var_name>{Variable}) = object table")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.convert_step_table_2_value_table(context.table)
    
    res = ValueTableConverter.convert_value_table_2_table(table)
    
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = object table with header")
def step_impl(context, var_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    
    res = ValueTableConverter.convert_value_table_2_table(table)
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r"(?P<var_name>{Variable}) = convert dictionary (?P<obj_str>{Str}) to name/value table")
def step_impl(context, var_name, obj_str):
    var_name = StepTools.evaluate_variable_name(var_name)
    obj = StepTools.evaluate_scenario_parameter(obj_str)
    if isinstance(obj, str):
        obj = eval(obj)
    if not isinstance(obj, dict):
        raise TechnicalException(f"Expecting dict, received {Typing.get_object_class_fullname(obj)}")
    
    table = TableManager.convert_dict_2_name_value_table(obj)
    
    __get_variable_manager().register_variable(var_name, table)

@Step(r"(?P<var_name>{Variable}) = convert dictionary (?P<obj_str>{Str}) to table with keys as columns")
def step_impl(context, var_name, obj_str):
    var_name = StepTools.evaluate_variable_name(var_name)
    obj = StepTools.evaluate_scenario_parameter(obj_str)
    if isinstance(obj, str):
        obj = eval(obj)
    if not isinstance(obj, dict):
        raise TechnicalException(f"Expecting dict, received {Typing.get_object_class_fullname(obj)}")
    
    table = TableManager.convert_dict_2_table_with_keys_as_column(obj)
    
    __get_variable_manager().register_variable(var_name, table)

@Step(r"(?P<var_name>{Variable}) = convert table with header (?P<table>{Variable}) to list of dictionary(?: \((?P<as_generator_str>as generator)\))?")
def step_impl(context, var_name, table, as_generator_str):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_scenario_parameter(table)
    as_generator = as_generator_str is not None
    if not TableManager.is_table_with_header(table):
        raise TechnicalException(f"Table must be a table with header (obtained type: {Typing.get_object_class_fullname(table)})")
    
    if ValueTableManager.is_value_table(table):
        res = ValueTableConverter.convert_table_with_header_to_dict_list(table, as_generator=as_generator)
    else:
        res = TableConverter.convert_table_with_header_to_dict_list(table, as_generator=as_generator)
    
    __get_variable_manager().register_variable(var_name, res)

@Step(r'(?P<var_name>{Variable}) = convert object (?P<obj_str>{Variable}) to name/value table')
def step_impl(context, var_name, obj_str):
    var_name = StepTools.evaluate_variable_name(var_name)
    obj = StepTools.evaluate_variable_value(obj_str)
    
    table = TableManager.convert_object_attributes_2_name_value_table(obj)
    
    __get_variable_manager().register_variable(var_name, table)
    
#TODO EKL: move step
@Step(r"(?P<var_name>{Variable}) = convert string (?P<list_obj_str>{Variable}) to list")
def step_impl(context, var_name, list_obj_str):
    var_name = StepTools.evaluate_variable_name(var_name)
    list_str = StepTools.evaluate_variable_value(list_obj_str)
    
    list_obj = eval(list_str)
    if not isinstance(list_obj, list):
        raise FunctionalException("Given string is not a string representation of a list")
    
    __get_variable_manager().register_variable(var_name, list_obj)

@Step(r'(?P<var_name>{Variable}) = convert list (?P<list_obj_str>{Variable}) to table with object attributes as columns')
def step_impl(context, var_name, list_obj_str):
    var_name = StepTools.evaluate_variable_name(var_name)
    list_obj = StepTools.evaluate_variable_value(list_obj_str)
    
    table = TableManager.convert_object_list_2_table_with_attributes_as_column(list_obj)
    
    __get_variable_manager().register_variable(var_name, table)

@Step(r'(?P<var_name>{Variable}) = convert list (?P<list_obj_str>{Variable}) to column table')
def step_impl(context, var_name, list_obj_str):
    var_name = StepTools.evaluate_variable_name(var_name)
    list_obj = StepTools.evaluate_variable_value(list_obj_str)
    
    table = TableManager.convert_object_list_2_column_table(list_obj)
    
    __get_variable_manager().register_variable(var_name, table)

@Then(r"compare table 1 (?P<table_1_str>{Variable}) to table 2 (?P<table_2_str>{Variable}) with(?: \(reorder columns table 1:(?P<reorder_table_1_str>true|false) ; reorder columns table 2:(?P<reorder_table_2_str>true|false)\))?")
def step_impl(context, table_1_str, table_2_str, reorder_table_1_str, reorder_table_2_str):
    table_1 = StepTools.evaluate_variable_value(table_1_str)
    table_2 = StepTools.evaluate_variable_value(table_2_str)
    compare_params_table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    reorder_columns_table_1 = Converter.to_boolean(reorder_table_1_str.capitalize()) if reorder_table_1_str is not None else True
    reorder_columns_table_2 = Converter.to_boolean(reorder_table_2_str.capitalize()) if reorder_table_2_str is not None else True
    
    TableManager.compare_tables(table_1, table_2, compare_params_table, reorder_columns_table_1, reorder_columns_table_2)

@Step(r"table (?P<table_varname>{Variable}) is")
def step_impl(context, table_varname):
    table_obtained = StepTools.evaluate_variable_value(table_varname)
    BehaveStepTools.then_table_is(table_obtained, context.table)

@Step(r"table (?P<table_varname>{Variable}) is empty")
def step_impl(context, table_varname):
    table = StepTools.evaluate_variable_value(table_varname)
    
    if not table.is_empty:
        raise FunctionalException(f"Table {table_varname} is not empty")

@Step(r"table (?P<table_varname>{Variable}) contains")
def step_impl(context, table_varname):
    table_obtained = StepTools.evaluate_variable_value(table_varname)
    BehaveStepTools.then_table_contains(table_obtained, context.table)

@Step(r"table (?P<table_1_varname>{Variable}) contains table (?P<table_2_varname>{Variable})")
def step_impl(context, table_1_varname, table_2_varname):
    table_1 = StepTools.evaluate_variable_value(table_1_varname)
    table_2 = StepTools.evaluate_variable_value(table_2_varname)
    BehaveStepTools.then_table_contains(table_1, table_2)

@Step(r"table (?P<table_varname>{Variable}) doesn't contain")
def step_impl(context, table_varname):
    table_obtained = StepTools.evaluate_variable_value(table_varname)
    BehaveStepTools.then_table_doesnt_contain(table_obtained, context.table)

@Step(r"table (?P<table_1_varname>{Variable}) doesn't contain table (?P<table_2_varname>{Variable})")
def step_impl(context, table_1_varname, table_2_varname):
    table_1 = StepTools.evaluate_variable_value(table_1_varname)
    table_2 = StepTools.evaluate_variable_value(table_2_varname)
    BehaveStepTools.then_table_doesnt_contain(table_1, table_2)
    
@Given(r'(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with columns ordered')
def step_impl(context, var_name, table_varname):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    table_columns = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)

    res_table = copy.copy(table)
    columns_ordered = table_columns.get_column_names()
    res_table.order_columns(names=columns_ordered)
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r"(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) without columns (?P<col_names>{List})")
def step_impl(context, var_name, table_varname, col_names):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    col_names = StepTools.evaluate_list_scenario_parameter(col_names, "col_names")
    
    res_table = copy.copy(table)
    for col_name in col_names:
        if res_table.has_column(col_name, raise_exception=False):
            res_table.remove_column(name=col_name)
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r'(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with only columns')
def step_impl(context, var_name, table_varname):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    table_columns = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)

    res_table = copy.copy(table)
    expected_colnames = table_columns.get_column_names()
    
    table_colnames = table.get_column_names()
    for col_index, col_name in reversed_enumerate(table_colnames):
        if col_name not in expected_colnames:
            res_table.remove_column(index=col_index)
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r'(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with only columns ordered')
def step_impl(context, var_name, table_varname):
    var_name = StepTools.evaluate_variable_name(var_name)
    rendered_table = render_step_table(context.table, "    ")

    execute_steps(u"""
        Given __TABLE_WITH_ONLY_COLUMNS__@ = table {table_varname} with only columns
        {table}
        """.format(table_varname=table_varname, table=rendered_table))
    
    execute_steps(u"""
        Given {var_name} = table __TABLE_WITH_ONLY_COLUMNS__@ with columns ordered
        {table}
        """.format(var_name=var_name, table=rendered_table))
    
@Given(r'(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with new columns')
def step_impl(context, var_name, table_varname):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    table_new_columns = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table, do_eval_once=False)

    res_table = copy.copy(table)
    is_res_value_table = ValueTableManager.is_value_table(res_table)
    
    res_col_indexes = res_table.get_column_indexes_by_string_content()
    
    tnc_indexes = table_new_columns.get_column_indexes_by_string_content()
    for row_new_column in table_new_columns.rows:
        new_colname_cell = row_new_column[tnc_indexes["Column Name"]]
        new_value_expr_cell = row_new_column[tnc_indexes["Value Expression"]]
        
        # Build new column
        new_col_cells_content = []
        for row in res_table.rows:
            # Add each existing column cells as variable
            for cn in res_col_indexes:
                if is_res_value_table:
                    __get_variable_manager().register_variable(f"Column({cn})", row.get_cell(res_col_indexes[cn]).value, accept_expression=False)
                else:
                    __get_variable_manager().register_variable(f"Column({cn})", row.get_cell(res_col_indexes[cn]).content, accept_expression=False)
                
            # Add new cell
            new_content = new_value_expr_cell.value
            if is_res_value_table and isinstance(new_content, str):
                new_content = f"'{new_content}'"
            new_col_cells_content.append(new_content)
                
        res_table.add_column(name=new_colname_cell.value, cells_content=new_col_cells_content)
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r'(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with new rows')
def step_impl(context, var_name, table_varname):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    table_new_rows = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)

    res_table = copy.copy(table)
    is_res_value_table = ValueTableManager.is_value_table(res_table)
    
    # Verify tables headers
    header_comp = StringTableRowComparator()
    header_comp.equals(table_new_rows.header, res_table.header)
    
    # Add rows
    for new_row in table_new_rows.rows:
        cells_value = new_row.cells_value
        if is_res_value_table:
            #TODO: add a test to verify if with this implementation the cells with variables are reevaluated after each compare
            res_table.add_row(cells_value=cells_value)
        else:
            res_table.add_row(cells_content=cells_value)
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r"(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with column (?P<col_name>{Str}) content replaced by")
def step_impl(context, var_name, table_varname, col_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    table_replace = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table, do_eval_once=False)
    col_name = StepTools.evaluate_scenario_parameter(col_name)

    res_table = copy.copy(table)
    is_value_table = ValueTableManager.is_value_table(res_table)
    col = res_table.get_column(name=col_name)
    
    tr_indexes = table_replace.get_column_indexes_by_string_content()
    tcell_comparator = Table2ValueTable_CellComparator() if "Condition Expression" in tr_indexes else None
    for cell in col:
        for row_replace in table_replace.rows:
            cell_cond_value = row_replace[tr_indexes["Condition Value"]] if "Condition Value" in tr_indexes else None
            cell_cond_expr = row_replace[tr_indexes["Condition Expression"]] if "Condition Expression" in tr_indexes else None
            cell_rep_value = row_replace[tr_indexes["Replace Value"]] if "Replace Value" in tr_indexes else None
            
            if cell_cond_value is not None:
                # If condition value is 'DEFAULT' or cell value is equal to condition value
                cond = (cell_cond_value.content_type == ValueTypes.Symbol and cell_cond_value.content == 'DEFAULT'
                        or cell_cond_value.value_type != ValueTypes.NotApplicable 
                            and (is_value_table and cell.value == cell_cond_value.value or not is_value_table and cell.content == cell_cond_value.value) )
            elif cell_cond_expr is not None:
                cond = tcell_comparator.equals(cell, cell_cond_expr, raise_exception = False)
            else:
                continue
                
            if cond:
                if cell_rep_value.value_type != ValueTypes.NotApplicable:
                    # Note: As 'col' is created with a copy of 'res_table' cells, 'cell' is also a 'res_table' cell.
                    #       Thus, modifying 'cell' is modifying the cell in 'res_table'
                    if is_value_table:
                        cell.value = cell_rep_value.value
                    else:
                        cell.content = cell_rep_value.value
                    break
                else:
                    continue
                
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r"(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with columns (?P<col_names>{List}) content replaced by")
def step_impl(context, var_name, table_varname, col_names):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    col_names = StepTools.evaluate_list_scenario_parameter(col_names, "col_names")
    
    rendered_table = render_step_table(context.table, "    ")

    __get_variable_manager().register_variable(var_name, copy.copy(table))
    
    for col_name in col_names:
        execute_steps(u"""
            Given {var_name} = table {var_name} with column '{col_name}' content replaced by
            {table}
            """.format(var_name=var_name, col_name=col_name, table=rendered_table))
    
@Given(r"(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with rows ordered by (?P<col_names>{List})")
def step_impl(context, var_name, table_varname, col_names):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    col_names = StepTools.evaluate_list_scenario_parameter(col_names, "col_names")

    res_table = copy.copy(table)
    res_table.sort(names=col_names)
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r"(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with rows verifying")
def step_impl(context, var_name, table_varname):
    """
    Keep only rows verifying at least one line of step table.
    
    If table table_varname is without header, step table can't have a header and must have same column number as 'table_varname'. 
    If table table_varname is with header, step table must be a table with header, but it can contain only some columns of 'table_varname'. 
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    is_with_header = TableManager.is_table_with_header(table)
    if is_with_header:
        table_remove = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    else:
        table_remove = BehaveStepTools.convert_step_table_2_value_table(context.table)
    
    if is_with_header:
        comparator = Table2ValueTable_WithHeaderComparator()
    else:
        comparator = Table2ValueTable_Comparator()

    res_table = copy.copy(table)
    if is_with_header and table_remove.nb_columns != table.nb_columns:
        res_table.remove_rows_only_verifying(table_remove, comparator, keep_rows=True)
    else:
        res_table.remove_rows_verifying(table_remove, comparator, keep_rows=True)
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r"(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) without rows verifying")
def step_impl(context, var_name, table_varname):
    """
    Remove rows verifying at least one line of step table.
    
    If table table_varname is without header, step table can't have a header and must have same column number as 'table_varname'. 
    If table table_varname is with header, step table must be a table with header, but it can contain only some columns of 'table_varname'. 
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    is_with_header = TableManager.is_table_with_header(table)
    if is_with_header:
        table_remove = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
    else:
        table_remove = BehaveStepTools.convert_step_table_2_value_table(context.table)
    
    if is_with_header:
        comparator = Table2ValueTable_WithHeaderComparator()
    else:
        comparator = Table2ValueTable_Comparator()

    res_table = copy.copy(table)
    if is_with_header and table_remove.nb_columns != table.nb_columns:
        res_table.remove_rows_only_verifying(table_remove, comparator)
    else:
        res_table.remove_rows_verifying(table_remove, comparator)
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r"(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) without duplicated rows")
def step_impl(context, var_name, table_varname):
    """
    Remove duplicated rows considering only column names in step table.
    """
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    table_columns = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)

    res_table = copy.copy(table)
    res_table.remove_rows_duplicated(column_names=table_columns.get_column_names())
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r"(?P<var_name>{Variable}) = extract column (?P<col_name>{Str}) from table (?P<table_varname>{Variable})")
def step_impl(context, var_name, table_varname, col_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    col_name = StepTools.evaluate_scenario_parameter(col_name)
    table = StepTools.evaluate_variable_value(table_varname)

    if isinstance(table, TableWithHeader):
        res_table = TableWithHeader()
        res = table.get_column(name=col_name)

        res_table.header = TableRow(cells_content={col_name})
        for c in res.cells:
            res_table.add_row(cells_content={c.content})
       
        __get_variable_manager().register_variable(var_name, res_table)
    else:
        raise TechnicalException(f"Table {table_varname} as no column {col_name}")
    
#TODO: return a list rather than a table
@Given(r"(?P<var_name>{Variable}) = extract column (?P<col_name>{Str}) cells from table (?P<table_varname>{Variable})")
def step_impl(context, var_name, table_varname, col_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    col_name = StepTools.evaluate_scenario_parameter(col_name)
    table = StepTools.evaluate_variable_value(table_varname)

    if isinstance(table, TableWithHeader):
        res_table = Table()
        res = table.get_column(name=col_name)

        for c in res.cells:
            res_table.add_row(cells_content={c.content})
       
        __get_variable_manager().register_variable(var_name, res_table)
    else:
        raise TechnicalException(f"Table {table_varname} as no column {col_name}")
    
#TODO: remove
@Given(r"(?P<var_name>{Variable}) = extract column (?P<col_name>{Str}) cells from table (?P<table_varname>{Variable}) as row")
def step_impl(context, var_name, table_varname, col_name):
    var_name = StepTools.evaluate_variable_name(var_name)
    col_name = StepTools.evaluate_scenario_parameter(col_name)
    table = StepTools.evaluate_variable_value(table_varname)

    if isinstance(table, TableWithHeader):
        res_table = Table()
        res = table.get_column(name=col_name)

        res_table.add_row()
        for c in res.cells:
            res_table.add_column(cells_content={c.content})
       
        __get_variable_manager().register_variable(var_name, res_table)
    else:
        raise TechnicalException(f"Table {table_varname} as no column {col_name}")
        

@Given(r"(?P<var_name>{Variable}) = table (?P<table_varname>{Variable}) with columns renamed")
def step_impl(context, var_name, table_varname):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    table_columns = BehaveStepTools.convert_step_table_2_value_table(context.table)
    
    col_index = table.get_column_indexes_by_string_content()
    
    res_table = copy.copy(table)
    header = res_table.header

    for row in table_columns.rows:
        old_name = row.get_cell(0).string_content
        new_name = row.get_cell(1).string_content
        
        if old_name in col_index:
            header.get_cell(col_index[old_name]).content = new_name
    res_table.header = header
    
    __get_variable_manager().register_variable(var_name, res_table)
    
@Given(r"(?P<var_name>{Variable}) = number of rows in table (?P<table_varname>{Variable})")
def step_impl(context, var_name, table_varname):
    var_name = StepTools.evaluate_variable_name(var_name)
    table = StepTools.evaluate_variable_value(table_varname)
    
    # print(table.represent())
    count_table = table.nb_rows
    
    # print(count_table)    
    __get_variable_manager().register_variable(var_name, count_table)
    
    
    