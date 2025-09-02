
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
import copy
from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing
from holado_python.common.iterables import is_sorted

logger = logging.getLogger(__name__)


class Table(object):
    def __init__(self):
        super().__init__()
        
        self.__content = None
        self.__parent = None
        
        self.__rows = []
        
    def __iter__(self):
        return self.__rows.__iter__()

    def __next__(self):
        return self.__rows.__next__()
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.__rows[key]
        else:
            raise TechnicalException(f"Unmanaged key: {key} (type: {Typing.get_object_class_fullname(key)})")
    
    def __copy__(self):
        cls = self.__class__
        res = cls()
        
        # Copy rows
        for row in self.rows:
            res.add_row(row=copy.copy(row))
        
        return res

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result
    
    def __repr__(self)->str:
        if self.nb_rows < 10 or self.nb_rows * self.nb_columns < 100:
            return f"<{self.__class__.__name__}>({self.nb_rows}x{self.nb_columns})\n{self.represent()}"
        else:
            return f"<{self.__class__.__name__}>({self.nb_rows}x{self.nb_columns})\n{self.represent(limit_rows=10)}[...]"
    
    @property
    def content(self):
        """ Content of whole table, relevant for some table types. """
        return self.__content
    
    @content.setter
    def content(self, content):
        """ Set content of whole table, relevant for some table types. """
        self.__content = content
    
    @property
    def parent(self):
        """ Parent, relevant for some table types. It's usually the origin of its creation. """
        return self.__parent
    
    @parent.setter
    def parent(self, parent):
        """ Set parent. """
        self.__parent = parent
    
    @property
    def rows(self):
        return self.__rows
    
    @property
    def nb_columns(self):
        if self.nb_rows > 0:
            return len(self.rows[0])
        else:
            return 0
    
    @property
    def nb_rows(self):
        return len(self.__rows)
            
    def add_row(self, row=None, cells=None, cells_content=None, **kwargs):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"add_row({row=}, {cells=}, {cells_content=})")
        if row is not None:
            self.__rows.append(row)
            return row
        else:
            return self.add_row(row=self._new_row(cells=cells, cells_content=cells_content, **kwargs), **kwargs)
        
    def extend(self, table, copy_method=None, **kwargs):  # @UnusedVariable
        for row in table.rows:
            if copy_method is not None:
                new_row = copy_method(row)
            else:
                new_row = row
            self.add_row(row=new_row, **kwargs)
        
    def _new_row(self, cells=None, cells_content=None, **kwargs):  # @UnusedVariable
        return TableRow(cells=cells, cells_content=cells_content)
        
    def get_row(self, index, **kwargs) -> TableRow :  # @UnusedVariable
        return self.rows[index]
    
    def get_column(self, index, **kwargs):
        res = self._new_row(**kwargs)
        for row in self.rows:
            res.add_cell(cell=row[index], **kwargs)
        return res

    def add_column(self, col=None, cells=None, cells_content=None, **kwargs):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"add_column({col=}, {cells=}, {cells_content=})")
        if col is not None:
            self.add_column(cells=col.cells, **kwargs)
        elif cells is not None:
            if len(cells) != self.nb_rows:
                raise TechnicalException(f"Length of cells is {len(cells)} whereas table has {self.nb_rows} rows")
            for i, cell in enumerate(cells):
                self.get_row(i).add_cell(cell=cell, **kwargs)
        elif cells_content is not None:
            if len(cells_content) != self.nb_rows:
                raise TechnicalException(f"Length of cells is {len(cells_content)} whereas table has {self.nb_rows} rows")
            for i, cell_content in enumerate(cells_content):
                self.get_row(i).add_cell(content=cell_content, **kwargs)
        else:
            for row in self.rows:
                row.add_cell(content=None, **kwargs)
        
    def remove_column(self, index=None, **kwargs):
        if index is None:
            raise TechnicalException("index must be specified")
        
        for row in self.rows:
            row.remove_cell(index, **kwargs)
        
    def remove_row(self, index=None, **kwargs):  # @UnusedVariable
        if index is None:
            raise TechnicalException("index must be specified")
        elif index >= self.nb_rows:
            raise FunctionalException(f"index is out of range ({index} >= {self.nb_rows})")
        
        return self.rows.pop(index)
    
    def represent(self, indent = 0, limit_rows=-1):
        res_list = []
        has_limited = False
        for row in self.rows:
            if limit_rows >=0 and len(res_list) >= limit_rows:
                has_limited = True
                break
            
            if row is not None:
                res_row = row.represent(indent)
            else:
                res_row = "{ROW_IS_NONE}"
            res_row += "\n"
            res_list.append(res_row)
            
        res = "".join(res_list)
        if has_limited:
            res += Tools.indent_string(indent, "[...]\n")
        return res
    
    def switch_columns(self, index_1, index_2, **kwargs):
        if index_1 == index_2:
            raise TechnicalException(f"The two indexes are equal (index = {index_1})")
    
        for row in self.rows:
            row.switch_cells(index_1, index_2, **kwargs)
            
    def sort(self, indexes, reverse=False, **kwargs):  # @UnusedVariable
        """Sort table rows according to indexes order."""
        if not indexes:
            raise TechnicalException("At least one index must be defined")
        self.__rows.sort(key=lambda x: tuple(x[i] for i in indexes), reverse=reverse)
    
    def is_sorted(self, indexes, reverse=False, **kwargs):  # @UnusedVariable
        """Check if table rows are sorted according to indexes order."""
        if not indexes:
            raise TechnicalException("At least one index must be defined")
        return is_sorted(self.__rows, key=lambda x: tuple(x[i] for i in indexes), reverse=reverse)

    def order_columns(self, indexes=None, **kwargs):
        orig_col_indexes = list(range(self.nb_columns))
        for col_index, orig_col_ind in enumerate(indexes):
            cur_col_ind = orig_col_indexes.index(orig_col_ind)
            if cur_col_ind != col_index:
                self.switch_columns(index_1=col_index, index_2=cur_col_ind, **kwargs)
                orig_col_indexes[col_index], orig_col_indexes[cur_col_ind] = orig_col_indexes[cur_col_ind], orig_col_indexes[col_index]
        
    def remove_rows_verifying(self, expected_table, table_comparator, keep_rows=False, **kwargs):
        """
        Remove rows that are equals compared to at least one line of expected_table.
        If keep_rows is True, keep the rows rather than remove them. 
        """
        n = 0
        while n < self.nb_rows:
            row = self.get_row(n, **kwargs)
            
            found = False
            for i in range(expected_table.nb_rows):
                found = table_comparator.row_comparator.equals(row, expected_table.get_row(i), raise_exception=False);
                if found:
                    break
            
            if found ^ keep_rows:
                self.remove_row(n)
            else:
                n += 1
            
    def remove_rows_duplicated(self, row_comparator, **kwargs):
        """
        Remove rows that are duplicates of previous rows, using given row_comparator.
        """
        n = 1
        while n < self.nb_rows:
            row = self.get_row(n)
            
            found = False
            for i in range(n):
                found = row_comparator.equals(row, self.get_row(i), raise_exception=False);
                if found:
                    break
            
            if found:
                self.remove_row(n, **kwargs)
            else:
                n += 1
            
    def is_empty(self, **kwargs):  # @UnusedVariable
        return self.nb_rows == 0


