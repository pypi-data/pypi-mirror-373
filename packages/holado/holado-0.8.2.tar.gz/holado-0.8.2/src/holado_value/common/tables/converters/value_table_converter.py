
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



from holado_value.common.tables.value_table import ValueTable
from holado_value.common.tables.value_table_with_header import ValueTableWithHeader
from holado_core.common.tables.table_row import TableRow
from holado_core.common.tables.converters.table_converter import TableConverter
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.tables.table import Table
import copy
import logging
from holado_value.common.tables.value_table_manager import ValueTableManager
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_value.common.tools.value_types import ValueTypes
from holado_core.common.tools.tools import Tools
from holado_json.ipc.json_converter import JsonConverter
from holado_python.standard_library.typing import Typing
from holado_data.data.generator.base import BaseGenerator

logger = logging.getLogger(__name__)


class ValueTableConverter(TableConverter):
    
    @classmethod
    def convert_table_2_value_table(cls, table, do_eval_once=True):
        if isinstance(table, TableWithHeader):
            res = ValueTableWithHeader()
            res.header = copy.copy(table.header)
        else:
            res = ValueTable()
        for row in table:
            cells_content = [f"'{cc}'" if isinstance(cc, str) else f"{cc}" for cc in row.cells_content]
            res.add_row(cells_content=cells_content, do_eval_once=do_eval_once)
        return res
    
    @classmethod
    def convert_value_table_2_table(cls, table):
        ValueTableManager.verify_is_value_table(table)
        
        if isinstance(table, ValueTableWithHeader):
            res = TableWithHeader()
            res.header = copy.copy(table.header)
        else:
            res = Table()
        for row in table:
            cells_content = row.cells_value
            res.add_row(cells_content=cells_content)
        return res
    
    @classmethod
    def convert_table_with_header_to_dict_list(cls, table, as_generator=False):
        if not ValueTableManager.is_value_table(table):
            return TableConverter.convert_table_with_header_to_dict_list(table, as_generator=as_generator)
        
        if as_generator:
            class TableWithHeader2DictGenerator(BaseGenerator):
                def __init__(self, table):
                    super().__init__(name="table with header to dict generator")
                    self.__table = table
                    self.__index_by_name = table.get_column_indexes_by_string_content()
                    self.__table_rows_iter = iter(self.__table.rows)
                
                def __next__(self):
                    row = next(self.__table_rows_iter)
                    return {name: row.get_cell(index).value for name, index in self.__index_by_name.items()}
            
            return TableWithHeader2DictGenerator(table)
        else:
            # index_by_name = table.get_column_indexes_by_string_content()
            #
            # res = []
            # for row in table.rows:
            #     new_dict = {name: row.get_cell(index).value for name, index in index_by_name.items()}
            #     res.append(new_dict)
            #
            # return res
            gen = cls.convert_table_with_header_to_dict_list(table, as_generator=True)
            return [e for e in gen]
    
    @classmethod
    def convert_table_2_list_of_tuples(cls, table, as_generator=False):
        if not ValueTableManager.is_value_table(table):
            return TableConverter.convert_table_2_list_of_tuples(table, as_generator=as_generator)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Converting table to a list of tuples...")
        if as_generator:
            class Table2TupleGenerator(BaseGenerator):
                def __init__(self, table):
                    super().__init__(name="table with header to dict generator")
                    self.__table = table
                    self.__table_rows_iter = iter(self.__table.rows)
                
                def __next__(self):
                    row = next(self.__table_rows_iter)
                    return tuple((cell.value for cell in row.cells))
            
            return Table2TupleGenerator(table)
        else:
            # return [tuple((cell.content for cell in row.cells)) for row in table.rows]
            gen = cls.convert_table_2_list_of_tuples(table, as_generator=True)
            return [e for e in gen]
    
    @classmethod
    def convert_name_value_table_2_dict(cls, table, with_original_value_content = False):
        if not ValueTableManager.is_value_table(table):
            return TableConverter.convert_name_value_table_2_dict(table)
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting Name/Value table to dict (table = {table})")
        
        res = {}
        if table is not None:
            # Verify table structure
            ValueTableManager.verify_table_is_name_value_table(table)
            ValueTableManager.verify_is_value_table(table)
            
            for row in table.rows:
                if row.get_cell(1).value_type not in [ValueTypes.NotApplicable]:
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace("Converting row (%s)", row)
                    
                    name = row.get_cell(0).value
                    if with_original_value_content:
                        value = row.get_cell(1).content
                    else:
                        value = row.get_cell(1).value
                    
                    if name in res:
                        raise FunctionalException("Name '{}' appears several times in table".format(name))
                    else:
                        res[name] = value
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting Name/Value table to dict (table = {table}) => {res}")
        return res
        
    @classmethod
    def convert_name_value_table_2_list_and_dict(cls, table, with_original_value_content = False):
        # if not ValueTableManager.is_value_table(table):
        #     return TableConverter.convert_name_value_table_2_list_and_dict(table)
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting Name/Value table to list and dict (table = {table})")

        # Verify table structure
        ValueTableManager.verify_table_is_name_value_table(table)
        ValueTableManager.verify_is_value_table(table)
        
        res_list = []
        res_dict = {}
        for row in table.rows:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace("Converting row (%s)", row)
            
            name = row.get_cell(0).value
            if with_original_value_content:
                value = row.get_cell(1).content
            else:
                value = row.get_cell(1).value
            
            if name and len(name) > 0:
                if name in res_dict:
                    raise FunctionalException("Name '{}' appears several times in table".format(name))
                else:
                    res_dict[name] = value
            else:
                res_list.append(value)
                
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting Name/Value table to list and dict (table = {table}) => {res_list} ; {res_dict}")
        return [res_list, res_dict]
 
    @classmethod
    def convert_name_value_table_2_json_object(cls, table, converter=None):
        if not ValueTableManager.is_value_table(table):
            return TableConverter.convert_name_value_table_2_json_object(table, converter=converter)
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting Name/Value table to json object (table = {table})")
        if converter is None:
            converter = JsonConverter()
        
        # Verify table structure
        ValueTableManager.verify_table_is_name_value_table(table)
        ValueTableManager.verify_is_value_table(table)
        
        res = {}
        for row in table.rows:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace("Converting row (%s)", row)
            
            if row.get_cell(1).value_type in [ValueTypes.NotApplicable, ValueTypes.Merged]:
                pass
            elif ValueTypes.is_string(row.get_cell(1).value_type):
                name = row.get_cell(0).value
                value = row.get_cell(1).value
                
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                
                    logger.trace(f"Adding for name '{name}' string value [{value}] (type: {Typing.get_object_class_fullname(value)})")
                cls._fill_json_dict(res, name, value)
            else:
                name = row.get_cell(0).value
                value = row.get_cell(1).value
                value = converter.to_json(value)
                
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                
                    logger.trace(f"Adding for name '{name}' json value [{value}] (type: {Typing.get_object_class_fullname(value)})")
                cls._fill_json_dict(res, name, value)
                
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting Name/Value table to json object (table = {table}) => {res}")
        return res

    @classmethod
    def convert_x_name_value_table_2_list_x_values(cls, table, x_name, with_original_value_content = False):
        # if not ValueTableManager.is_value_table(table):
        #     return TableConverter.convert_x_name_value_table_2_list_x_values(table, x_name)
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting {x_name}/Name/Value table to list of {x_name} and values dict (table = {table})")

        # Verify table structure
        ValueTableManager.verify_table_is_x_name_value_table(table, x_name)
        
        x_list = []
        res_dict = {}
        for row in table.rows:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace("Converting row (%s)", row)

            x = row.get_cell(0).value
            name = row.get_cell(1).value
            if with_original_value_content:
                value = row.get_cell(2).content
            else:
                value = row.get_cell(2).value
            
            if x not in res_dict:
                res_dict[x] = {}
                x_list.append(x)
            res_dict[x][name] = value
                
        res = [{x_name:x, 'values':res_dict[x]} for x in x_list]
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting {x_name}/Name/Value table to list of {x_name} and values dict (table = {table}) => {res}")
        return res
        
    
    
        