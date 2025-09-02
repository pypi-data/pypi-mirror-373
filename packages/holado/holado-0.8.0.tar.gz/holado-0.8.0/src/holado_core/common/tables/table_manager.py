
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
from holado_core.common.tables.table_with_header import TableWithHeader
from builtins import object
from holado_core.common.tables.table import Table
from holado_value.common.tables.value_table_with_header import ValueTableWithHeader
from holado_core.common.tools.tools import Tools, reversed_range
from holado_python.standard_library.typing import Typing
import copy
from holado_value.common.tools.value_types import ValueTypes
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_value.common.tables.comparators.table_2_value_table_row_comparator import Table2ValueTable_RowComparator
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tables.comparators.table_comparator_manager import TableComparatorManager
from holado_core.common.tables.comparators.table_row_comparator import TableRowComparator
from holado_core.common.tables.comparators.table_comparator import TableComparator
from holado_core.common.tables.comparators.string_table_comparator import StringTableComparator
from holado_core.common.tables.table_row import TableRow
from holado_core.common.tables.comparators.string_table_row_comparator import StringTableRowComparator

logger = logging.getLogger(__name__)


class TableManager(object):
    
    @classmethod
    def is_table_with_header(cls, table):
        return isinstance(table, TableWithHeader)
    
    #TODO: move in TableConverter
    @classmethod
    def convert_object_attributes_2_name_value_table(cls, obj):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Converting object to name/value table")

        res = TableWithHeader()
        
        # Set header
        res.header.add_cells_from_contents(["Name", "Value"])
        
        # Get attributes
        attributes = Typing.get_object_attributes(obj)
        
        # Set body
        for attr in attributes:
            res.add_row(cells_content=attr)
            
        return res
    
    #TODO: move in TableConverter
    @classmethod
    def convert_list_2_column_table(cls, el_list):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Converting list to column table")

        res = Table()
        
        # Set body
        for el in el_list:
            res.add_row(cells_content=[el])
            
        return res
 
    #TODO: move in TableConverter
    @classmethod
    def convert_object_list_2_table_with_attributes_as_column(cls, list_obj):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Converting object list to table with object attributes as column...")
        res = TableWithHeader()

        for obj in list_obj:
            if not res.header:
                if isinstance(obj, dict):
                    header_names = list(obj.keys())
                else:
                    header_names = Typing.get_object_attribute_names(obj)
                res.header.add_cells_from_contents(cells_content=header_names)
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Result table - set header {res.header.represent(0)}")
            
            if isinstance(obj, dict):
                values_by_name = obj
            else:
                values_by_name = Typing.get_object_attribute_names(obj)
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Result table - add row with {values_by_name}")
            res.add_row(contents_by_colname=values_by_name)

        return res
 
    #TODO: move in TableConverter
    @classmethod
    def convert_object_list_2_column_table(cls, list_obj):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Converting object list to column table...")
        res = Table()

        for obj in list_obj:
#            logger.debug(f"+++++ add row with object: {obj}")
            res.add_row(cells_content=[obj])

        return res
        
    
    #TODO: move in TableConverter
    @classmethod
    def convert_dict_2_name_value_table(cls, obj):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Converting dictionary to name/value table...")
        res = TableWithHeader()
        
        res.header.add_cells_from_contents(["Name", "Value"])
        
        sorted_dict = dict(sorted(obj.items()))
        for entry in sorted_dict.items():
            res.add_row(cells_content=entry)
            
        return res
    
    #TODO: move in TableConverter
    @classmethod
    def convert_dict_2_table_with_keys_as_column(cls, obj):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Converting dictionary to table with keyx as column name...")
        res = TableWithHeader()
        
        res.add_row()
        sorted_dict = dict(sorted(obj.items()))
        for key, value in sorted_dict.items():
            res.add_column(name=key, cells_content=[value])
            
        return res
    
    @classmethod
    def compare_tables(cls, table_1, table_2, compare_params_table, reorder_columns_table_1=True, reorder_columns_table_2=True, raise_exception=True):
        compared_tables, columns_compare_methods, compared_columns, expected_table_columns = cls._extract_compared_data(table_1, table_2, compare_params_table, reorder_columns_table_1, reorder_columns_table_2)
        
        # Verify source table headers
        res = cls._verify_expected_table_columns(table_1, table_2, expected_table_columns, raise_exception=raise_exception)
        if not res:
            return res
        
        # Verify compared table headers
        res = cls._verify_compared_table_columns(compared_tables, compared_columns, raise_exception=raise_exception)
        if not res:
            return res
        
        # Compare table contents
        if columns_compare_methods is not None:
            cells_comparators = [TableComparatorManager.convert_compare_method_2_TableCellComparator(cm.value) if cm.value_type != ValueTypes.NotApplicable else None for cm in columns_compare_methods]
            row_comparator = TableRowComparator(cells_comparators=cells_comparators)
            comparator = TableComparator(row_comparator=row_comparator)
        else:
            comparator = StringTableComparator()
        try:
            res = comparator.equals(compared_tables[0], compared_tables[1], is_obtained_vs_expected=True, raise_exception=raise_exception)
        except FunctionalException as exc:
            raise FunctionalException(f"Tables are different (obtained = table 1 ; expected = table 2):\n{Tools.indent_string(4, exc.message)}") from exc
        
        return res
    
    @classmethod
    def _extract_compared_data(cls, table_1, table_2, compare_params_table, reorder_columns_table_1, reorder_columns_table_2):
        if not isinstance(compare_params_table, ValueTableWithHeader):
            raise TechnicalException(f"Compare parameters table is expected to be a ValueTableWithHeader (obtained type: {Typing.get_object_class_fullname(compare_params_table)})")
        
        res_t1 = copy.copy(table_1)
        res_t2 = copy.copy(table_2)
        colnames_t1 = compare_params_table.get_column(name="Column Names 1")
        colnames_t2 = compare_params_table.get_column(name="Column Names 2")
        has_compare_method = compare_params_table.has_column(name="Compare method", raise_exception=False)
        columns_compare_methods = compare_params_table.get_column(name="Compare method") if has_compare_method else None
        
        # Extract compared data
        compare_colnames_t1 = copy.copy(colnames_t1)
        compare_colnames_t2 = copy.copy(colnames_t2)
        exp_colnames_t1 = copy.copy(colnames_t1)
        exp_colnames_t2 = copy.copy(colnames_t2)
        for ind in reversed_range(len(colnames_t1)):
            if colnames_t1[ind].value_type == ValueTypes.NotApplicable or colnames_t2[ind].value_type == ValueTypes.NotApplicable:
                del compare_colnames_t1[ind]
                del compare_colnames_t2[ind]
                if has_compare_method:
                    del columns_compare_methods[ind]
            if colnames_t1[ind].value_type == ValueTypes.NotApplicable:
                cn_t2 = colnames_t2[ind].string_content
                res_t2.remove_column(name=cn_t2)
                del exp_colnames_t1[ind]
            if colnames_t2[ind].value_type == ValueTypes.NotApplicable:
                cn_t1 = colnames_t1[ind].string_content
                res_t1.remove_column(name=cn_t1)
                del exp_colnames_t2[ind]
        
        # Reorder tables
        if reorder_columns_table_1:
            table_1.order_columns(names=exp_colnames_t1.cells_value)
            res_t1.order_columns(names=compare_colnames_t1.cells_value)
        if reorder_columns_table_2:
            table_2.order_columns(names=exp_colnames_t2.cells_value)
            res_t2.order_columns(names=compare_colnames_t2.cells_value)
        
        return (res_t1, res_t2), columns_compare_methods, (compare_colnames_t1, compare_colnames_t2), (exp_colnames_t1, exp_colnames_t2)
    
    @classmethod
    def _verify_expected_table_columns(cls, table_1, table_2, expected_table_columns, raise_exception=True):
        comp = Table2ValueTable_RowComparator()
        try:
            comp.equals(table_1.header, expected_table_columns[0])
        except VerifyException as exc:
            if raise_exception:
                msg_list = ["Column Names 1 is not matching table 1 columns (columns order is mandatory):",
                            "    Table 1 columns: " + table_1.header.represent(0),
                            "    Column Names 1:  " + expected_table_columns[0].represent(0) ]
                raise FunctionalException("\n".join(msg_list) + f"\n{'-'*20}\n{exc}") from exc
            else:
                return False
        
        try:
            sorted_table_2_header = copy.copy(table_2.header)
            sorted_table_2_header.sort()
            sorted_exp_colnames_t2 = copy.copy(expected_table_columns[1])
            sorted_exp_colnames_t2.sort()
            comp.equals(sorted_table_2_header, sorted_exp_colnames_t2)
        except VerifyException as exc:
            if raise_exception:
                msg_list = ["Column Names 2 is not matching table 2 columns (columns order is not mandatory):",
                            "    Table 2 columns: " + table_2.header.represent(0),
                            "    Column Names 2:  " + expected_table_columns[1].represent(0) ]
                raise FunctionalException("\n".join(msg_list) + f"\n{'-'*20}\n{exc}") from exc
            else:
                return False
        
        return True
    
    @classmethod
    def _verify_compared_table_columns(cls, compared_tables, compared_columns, raise_exception=True):
        if compared_tables[0].nb_columns != len(compared_columns[0]):
            if raise_exception:
                msg_list = ["Compared columns are not matching table 1 columns:",
                            "    Table 1 columns:  " + compared_tables[0].header.represent(0),
                            "    compared columns: " + compared_columns[0].represent(0) ]
                raise FunctionalException("\n".join(msg_list))
            else:
                return False
        if compared_tables[1].nb_columns != len(compared_columns[1]):
            if raise_exception:
                msg_list = ["Compared columns are not matching table 2 columns:",
                            "    Table 2 columns:  " + compared_tables[1].header.represent(0),
                            "    compared columns: " + compared_columns[1].represent(0) ]
                raise FunctionalException("\n".join(msg_list))
            else:
                return False
        
        for ind in range(len(compared_columns[0])):
            index_t1 = compared_tables[0].get_column_index(name=compared_columns[0][ind].string_content)
            index_t2 = compared_tables[1].get_column_index(name=compared_columns[1][ind].string_content)
            if index_t1 != index_t2:
                if raise_exception:
                    msg_list = ["Compared columns have not same indexes in respective tables:",
                                "    Table header 1: " + compared_tables[0].header.represent(0),
                                "    Table header 2: " + compared_tables[1].header.represent(0) ]
                    raise FunctionalException("\n".join(msg_list))
                else:
                    return False
        
        return True
    
    @classmethod
    def verify_table_is_with_header(cls, table, raise_exception=True):
        # Compare headers
        if not cls.is_table_with_header(table):
            if raise_exception:
                raise TechnicalException(f"Table is expected with header (obtained type: {type(table)})")
            else:
                return False
        return True
    
    @classmethod
    def verify_table_is_value_table(cls, table, raise_exception=True):
        # Compare headers
        res = cls.verify_table_is_with_header(table, raise_exception=raise_exception)
        if not res:
            return False
        
        # Build expected header
        expected = TableRow(cells_content=["Value"])
        
        # Verify header content
        comparator = StringTableRowComparator()
        return comparator.equals(expected, table.header, raise_exception=raise_exception)
        
    @classmethod
    def verify_table_is_name_value_table(cls, table, raise_exception=True):
        # Compare headers
        res = cls.verify_table_is_with_header(table, raise_exception=raise_exception)
        if not res:
            return False
        
        # Build expected header
        expected = TableRow(cells_content=["Name", "Value"])
        
        # Verify header content
        comparator = StringTableRowComparator()
        return comparator.equals(expected, table.header, raise_exception=raise_exception)
        
    @classmethod
    def verify_table_is_x_name_value_table(cls, table, x_name, raise_exception=True):
        # Compare headers
        res = cls.verify_table_is_with_header(table, raise_exception=raise_exception)
        if not res:
            return False
        
        # Build expected header
        expected = TableRow(cells_content=[x_name, "Name", "Value"])
        
        # Verify header content
        comparator = StringTableRowComparator()
        return comparator.equals(expected, table.header, raise_exception=raise_exception)
        
    @classmethod
    def verify_table_is_x_table(cls, table, *x_names, raise_exception=True):
        # Compare headers
        res = cls.verify_table_is_with_header(table, raise_exception=raise_exception)
        if not res:
            return False
        
        # Build expected header
        expected = TableRow(cells_content=x_names)
        
        # Verify header content
        comparator = StringTableRowComparator()
        return comparator.equals(expected, table.header, raise_exception=raise_exception)
    
    @classmethod
    def represent_table(cls, table, indent=0):
        res_list = []
        
        if cls.is_table_with_header(table):
            res_list.append("| " + " | ".join(table.header.cells_content) + " |")
        
        for row in table.rows:
            res_list.append("| " + " | ".join(row.cells_content) + " |")
            
        return Tools.indent_string(indent, "\n".join(res_list))
    
    @classmethod
    def set_object_attributes_according_name_value_table(cls, obj, table):
        # Verify table structure
        cls.verify_table_is_name_value_table(table)
        
        for row in table.rows:
            setattr(obj, row.get_cell(0).content, row.get_cell(1).content)
