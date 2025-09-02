#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.tables.table_row import TableRow
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.converters.converter import Converter
from holado_python.standard_library.typing import Typing
import logging
from holado_json.ipc.json_converter import JsonConverter
from holado_core.common.tables.table_manager import TableManager
from holado_core.common.exceptions.functional_exception import FunctionalException
import re
from holado_core.common.tools.tools import Tools
from holado_data.data.generator.base import BaseGenerator


logger = logging.getLogger(__name__)



class TableConverter(object):
    
    @classmethod
    def convert_table_with_header_to_dict(cls, table):
        res_list = cls.convert_table_with_header_to_dict_list(table, as_generator=False)
        if len(res_list) == 0:
            return None
        elif len(res_list) == 1:
            return res_list[0]
        else:
            raise TechnicalException(f"Failed to convert table to dict, since table has more than one row.")
    
    @classmethod
    def convert_table_with_header_to_dict_list(cls, table, as_generator=False):
        if as_generator:
            class TableWithHeader2DictGenerator(BaseGenerator):
                def __init__(self, table):
                    super().__init__(name="table with header to dict generator")
                    self.__table = table
                    self.__index_by_name = table.get_column_indexes_by_string_content()
                    self.__table_rows_iter = iter(self.__table.rows)
                
                def __next__(self):
                    row = next(self.__table_rows_iter)
                    return {name: row.get_cell(index).content for name, index in self.__index_by_name.items()}
            
            return TableWithHeader2DictGenerator(table)
        else:
            # index_by_name = table.get_column_indexes_by_string_content()
            #
            # res = []
            # for row in table.rows:
            #     new_dict = {name: row.get_cell(index).content for name, index in index_by_name.items()}
            #     res.append(new_dict)
            #
            # return res
            gen = cls.convert_table_with_header_to_dict_list(table, as_generator=True)
            return [e for e in gen]
    
    @classmethod
    def convert_table_2_list_of_tuples(cls, table, as_generator=False):
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
                    return tuple((cell.content for cell in row.cells))
            
            return Table2TupleGenerator(table)
        else:
            # return [tuple((cell.content for cell in row.cells)) for row in table.rows]
            gen = cls.convert_table_2_list_of_tuples(table, as_generator=True)
            return [e for e in gen]
    
    @classmethod
    def convert_dict_list_to_table_with_header(cls, dict_list):
        """
        Builds a table with header from a list of dictionaries.
        """
        header = set()
        for index, new_dict in enumerate(dict_list):
            if not Converter.is_dict(new_dict):
                raise TechnicalException(f"The list element of index {index} is not a dict (obtained type: {Typing.get_object_class_fullname(new_dict)})")
            header = header.union(new_dict.keys())
        header = sorted(header)

        res = TableWithHeader()
        res.header = TableRow(cells_content=header)
        
        for new_dict in dict_list:
            res.add_row(contents_by_colname=new_dict)
        
        return res
    
    @classmethod
    def convert_name_value_table_2_dict(cls, table):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting Name/Value table to dict (table = {table})")

        res = {}
        if table is not None:
            # Verify table structure
            TableManager.verify_table_is_name_value_table(table)
            
            for row in table.rows:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace("Converting row (%s)", row)
                
                name = row.get_cell(0).content
                value = row.get_cell(1).content
                
                if name in res:
                    raise FunctionalException("Name '{}' appears several times in table".format(name))
                else:
                    res[name] = value
                
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting Name/Value table to dict (table = {table}) => {res}")
        return res

    @classmethod
    def convert_name_value_table_2_json_object(cls, table, converter=None):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting Name/Value table to json object (table = {table})")
        if converter is None:
            converter = JsonConverter()
        
        # Verify table structure
        TableManager.verify_table_is_name_value_table(table)
        
        res = {}
        for row in table.rows:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace("Converting row (%s)", row)
            
            name = row.get_cell(0).content
            value = row.get_cell(1).content
            value = converter.to_json(value)
            
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Adding for name '{name}' json value [{value}] (type: {Typing.get_object_class_fullname(value)})")
            cls._fill_json_dict(res, name, value)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting Name/Value table to json object (table = {table}) => {res}")
        return res
 
    @classmethod
    def extract_table_with_header_from_table(cls, table, row_first_index, row_last_index, col_first_index, col_last_index):
        res = TableWithHeader()
        
        header_content = [c.content for c in table.rows[row_first_index].cells[col_first_index:col_last_index+1]]
        res.header = TableRow(cells_content=header_content)
        
        for i in range(row_first_index+1, row_last_index+1):
            row_content = [c.content for c in table.rows[i].cells[col_first_index:col_last_index+1]]
            res.add_row(cells_content=row_content)
        
        return res
        
 
    @classmethod
    def _fill_json_dict(cls, json_res, name, value):
        if not isinstance(json_res, dict):
            raise TechnicalException(f"Type '{Typing.get_object_class_fullname(json_res)}' is not a dict")
        
        names = name.split(".", maxsplit=1)
        name0 = names[0]
        name1 = names[1] if len(names) > 1 else None
        
        # manage lists
        m = re.match(r"^([^[]+)\[(.*)\]$", name0)
        if m:
            li_name = m.group(1)
            index = int(m.group(2))

            if li_name not in json_res:
                json_res[li_name] = []
            cls._fill_json_list(json_res[li_name], index, name1, value)
            return
        
        if name1 is None:
            cls._fill_json_dict_entry(json_res, name0, value)
        else:
            if name0 not in json_res:
                json_res[name0] = {}
            cls._fill_json_dict(json_res[name0], name1, value)
 
    @classmethod
    def _fill_json_dict_entry(cls, json_res, name, value):
        if name in json_res:
            raise FunctionalException(f"Name '{name}' is already set")
        else:
            json_res[name] = value
 
    @classmethod
    def _fill_json_list(cls, json_res, index, name, value):
        if not isinstance(json_res, list):
            raise TechnicalException(f"Type '{Typing.get_object_class_fullname(json_res)}' is not a list")
        
        # Prepare list with missing elements
        if index + 1 > len(json_res):
            for _ in range(len(json_res), index + 1):
                json_res.append(None)
        
        if name is None:
            if json_res[index] is None:
                json_res[index] = value
            else:        
                raise FunctionalException("List has already an element at index {}".format(index))
        else:
            if json_res[index] is None:
                json_res[index] = {}
            cls._fill_json_dict(json_res[index], name, value)
            
        
    