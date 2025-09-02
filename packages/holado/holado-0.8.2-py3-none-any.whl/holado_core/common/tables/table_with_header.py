
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

from builtins import super
from holado_core.common.tables.table_row import TableRow
from holado_core.common.tables.table import Table
from holado_core.common.exceptions.functional_exception import FunctionalException
import copy
from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado_core.common.tables.comparators.table_cell_comparator import TableCellComparator
from holado_core.common.tables.comparators.table_row_comparator import TableRowComparator
from holado_core.common.tools.tools import Tools
from holado_core.common.tables.comparators.table_with_header_comparator import TableWithHeaderComparator

logger = logging.getLogger(__name__)


class TableWithHeader(Table):
    
    def __init__(self):
        super().__init__()
        
        self.__header = TableRow()
        
    @property
    def header(self):
        return self.__header
    
    @header.setter
    def header(self, header):
        self.__header = header

    @Table.nb_columns.getter  # @UndefinedVariable
    def nb_columns(self):
        return len(self.header)
    
    def __copy__(self):
        res = super().__copy__()
        
        # Copy header
        res.header = copy.copy(self.header)
        
        return res
    
    def set_header(self, row=None, cells=None, cells_content=None):
        if row is not None:
            self.header = row
        else:
            self.header = TableRow(cells=cells, cells_content=cells_content)
    
    def add_row(self, row=None, cells=None, cells_content=None, contents_by_colname: dict =None, **kwargs):
        # Manage super call
        if contents_by_colname is None:
            return super().add_row(row=row, cells=cells, cells_content=cells_content, **kwargs)
        
        # Verify column names
        for colname in contents_by_colname:
            if not self.has_column(colname, raise_exception=False):
                raise FunctionalException(f"In parameter 'values_by_colname', the column name '{colname}' is not in table header")
        
        # Add row
        row_contents = [contents_by_colname[cn] if cn in contents_by_colname else None for cn in self.get_column_names()]
        return self.add_row(cells_content=row_contents, **kwargs)
        
    def extend(self, table, copy_method=None, **kwargs):
        # Verify table headers are identical
        comparator = TableWithHeaderComparator()
        comparator.equals_headers(table, self)
        
        super().extend(table, copy_method, **kwargs)
        
    def represent(self, indent = 0, limit_rows = -1, value_prefix = None, value_postfix = None):
        res_list = []
        
        res_list.append(self.header.represent(indent, value_prefix=value_prefix, value_postfix=value_postfix))
        res_list.append("\n")
        
        res_list.extend( super().represent(indent, limit_rows=limit_rows) )
        
        return "".join(res_list)
    
    def get_column(self, index=None, name=None, **kwargs):
        if name is not None:
            index = self.get_column_index(name)
        return super().get_column(index, **kwargs)
    
    def get_column_names(self):
        return [cell.string_content for cell in self.header]
    
    def get_column_indexes_by_string_content(self):
        return {cell.string_content : index for index, cell in enumerate(self.header)}
    
    def get_column_index(self, name):
        indexes = self.get_column_indexes_by_string_content()
        if name in indexes:
            return indexes[name]
        else:
            raise FunctionalException(f"Table has no column named '{name}' (existing column names: {self.header.represent()})")
    
    def has_column(self, name, raise_exception=True):
        try:
            self.get_column_index(name)
        except FunctionalException as exc:
            if raise_exception:
                raise exc
            else:
                return False
        else:
            return True

    def add_column(self, col=None, cells=None, cells_content=None, name=None, **kwargs):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"add_column({col=}, {cells=}, {cells_content=}, {name=})")
        self.header.add_cell(content=name, **kwargs)
        super().add_column(col=col, cells=cells, cells_content=cells_content, **kwargs)

    def remove_column(self, index=None, name=None, **kwargs):
        if name is not None:
            index = self.get_column_index(name)
        self.header.remove_cell(index, **kwargs)
        return super().remove_column(index, **kwargs)
    
    def switch_columns(self, index_1=None, index_2=None, name_1=None, name_2=None, **kwargs):
        if name_1 is not None:
            index_1 = self.get_column_index(name_1)
        if name_2 is not None:
            index_2 = self.get_column_index(name_2)
        if index_1 == index_2:
            raise TechnicalException(f"The two indexes are equal (index = {index_1})")
    
        self.header.switch_cells(index_1, index_2, **kwargs)
        super().switch_columns(index_1, index_2, **kwargs)
    
    def sort(self, indexes=None, names=None, reverse=False, **kwargs):
        """Sort table rows according to indexes or column names order."""
        if names:
            indexes = tuple(self.get_column_index(name) for name in names)
        super().sort(indexes=indexes, reverse=reverse, **kwargs)
    
    def is_sorted(self, indexes=None, names=None, reverse=False, **kwargs):  # @UnusedVariable
        """Check if table rows are sorted according to indexes or column names order."""
        if names:
            indexes = tuple(self.get_column_index(name) for name in names)
        return super().is_sorted(indexes=indexes, reverse=reverse, **kwargs)

    def order_columns(self, indexes=None, names=None, **kwargs):
        if names:
            indexes = tuple(self.get_column_index(name) for name in names)
        super().order_columns(indexes=indexes, **kwargs)
        
    def remove_rows_verifying(self, expected_table, table_comparator, keep_rows=False, **kwargs):
        """
        Remove rows verifying expected values.
        Parameter 'expected_table' has to refer all possible columns. 

        Remove rows that are equals compared to at least one line of expected_table.
        If keep_rows is True, keep the rows rather than remove them. 
        """

        # Verifying header are matching
        table_comparator.equals_headers(self, expected_table, raise_exception=True)

        # Remove rows
        super().remove_rows_verifying(expected_table, table_comparator, keep_rows=keep_rows, **kwargs)

    def remove_rows_only_verifying(self, expected_table, table_comparator, keep_rows=False, **kwargs):  # @UnusedVariable
        """
        Remove rows verifying expected values.
        Parameter 'expected_table' can contain only some columns. 

        Remove rows that are equals compared to at least one line of expected_table.
        If keep_rows is True, keep the rows rather than remove them. 
        """
        col_indexes = [self.get_column_index(hcell.string_content) for hcell in expected_table.header]
        n = 0
        while n < self.nb_rows:
            comp_row = copy.copy(self.get_row(n, **kwargs))
            # logger.info(f"+++++++++++++ line {n} - comp_row: {comp_row.represent(0)}")
            comp_row.order_cells(indexes=col_indexes)
            # logger.info(f"+++++++++++++ line {n} - comp_row: {comp_row.represent(0)}")
            comp_row.keep_cells(indexes=range(len(col_indexes)))
            # logger.info(f"+++++++++++++ line {n} - comp_row: {comp_row.represent(0)}")
            
            found = False
            for i in range(expected_table.nb_rows):
                found = table_comparator.row_comparator.equals(comp_row, expected_table.get_row(i), raise_exception=False);
                if found:
                    break
            
            # logger.info(f"+++++++++++++ line {n}: {found}")
            if found ^ keep_rows:
                self.remove_row(n);
            else:
                n += 1
                
    def remove_rows_duplicated(self, row_comparator=None, column_names=None, **kwargs):
        """
        Remove rows that are duplicates of previous rows.
        If row_comparator is None, column_names is used to create a row comparator that compares only given columns.
        """
        if row_comparator is None and column_names is None:
            raise TechnicalException("If parameter 'row_comparator' is not defined, at least column_names must be defined")
        
        if row_comparator is None and column_names is not None:
            cells_comparators = [TableCellComparator() if cn in column_names else None for cn in self.get_column_names()]
            row_comparator = TableRowComparator(cells_comparators=cells_comparators)
            
        super().remove_rows_duplicated(row_comparator=row_comparator, **kwargs)
    
    def extract_col(self, col_name, **kwargs):
        """
        Builds a new TableWithHeader from column col_name
        """
        if self.has_column(col_name, raise_exception=True):
            returnTable = TableWithHeader()
            returnTable.header = TableRow(cells_content=[col_name])
            
            col = self.get_column(name=col_name, **kwargs)
            for content in col.cells_content:
                returnTable.add_row(cells_content=content, **kwargs)
                
            return returnTable
    
    def rename_column(self, old_name, new_name, **kwargs):
        index=self.get_column_index(old_name)
        
        self.__header.get_cell(index).content = new_name
    
    
    
    