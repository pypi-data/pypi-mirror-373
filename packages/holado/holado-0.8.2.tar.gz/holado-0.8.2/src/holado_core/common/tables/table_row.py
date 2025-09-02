
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
from holado_core.common.tables.table_cell import TableCell
from holado_core.common.tools.tools import Tools
import copy
from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class TableRow(list):
    def __init__(self, cells=None, cells_content=None, **kwargs):
        super().__init__()
        
        self.__content = None
        self.__parent = None
        
        if cells is not None:
            self.cells.extend(cells)
        elif cells_content is not None:
            self.add_cells_from_contents(cells_content, **kwargs)
        
    @property
    def content(self):
        """ Content of whole table row, relevant for some table types. """
        return self.__content
    
    @content.setter
    def content(self, content):
        """ Set content of whole table row, relevant for some table types. """
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
    def cells(self): 
        return self
    
    @property
    def cells_content(self): 
        return tuple(c.content for c in self.cells)
    
    @property
    def nb_cells(self): 
        return len(self.cells)
    
    def __copy__(self):
        cls = self.__class__
        res = cls()
        
        # Copy cells
        for cell in self.cells:
            res.add_cell(cell=copy.copy(cell))
            
        return res

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result
    
    def __repr__(self)->str:
        if self.nb_cells < 100:
            return f"<{self.__class__.__name__}>({self.nb_cells})[{self.represent()}]"
        else:
            return f"<{self.__class__.__name__}>({self.nb_cells})"

    def add_cell(self, cell=None, content=None, **kwargs):
        """Add a cell
        @param cell: Cell instance
        @param content: Cell content
        @param kwargs: Additional arguments needed by sub-classes.
        """
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"add_cell({cell=}, {content=} [{Typing.get_object_class_fullname(content)}])")
        if cell is not None:
            self.cells.append(cell)
        else:
            self.add_cell(cell=self._new_cell(content, **kwargs), **kwargs)
    
    def add_cells_from_contents(self, cells_content, **kwargs):
        """Add cells from their contents
        @param cells_content: Cells content
        @param kwargs: Additional arguments needed by sub-classes.
        """
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"add_cells_from_contents({cells_content=})")
        for cell_content in cells_content:
            self.add_cell(content=cell_content, **kwargs)
    
    def get_cell(self, index, **kwargs) -> TableCell :  # @UnusedVariable
        return self.cells[index]
    
    def _new_cell(self, content, **kwargs):  # @UnusedVariable
        return TableCell(cell_content=content)
    
    def remove_cell(self, index, **kwargs):  # @UnusedVariable
        return self.cells.pop(index)
    
    def keep_cells(self, indexes, **kwargs):
        for i in reversed(range(self.nb_cells)):
            if i not in indexes:
                self.remove_cell(i, **kwargs)
    
    def represent(self, indent = 0, value_prefix = None, value_postfix = None, marge_left = " ", marge_right = " "):
        res_list = []
        
        res_list.append(Tools.get_indent_string(indent))
        res_list.append("|")
        for cell in self.cells:
            if marge_left is not None:
                res_list.append(marge_left)
            
            if cell is not None:
                if value_prefix is not None or value_postfix is not None:
                    res_list.append(cell.represent(0, value_prefix, value_postfix))
                else:
                    res_list.append(cell.represent(0))
            else:
                res_list.append("{CELL_IS_NONE}")
            
            if marge_right is not None:
                res_list.append(marge_right)
            
            res_list.append("|")
        
        return "".join(res_list)

    def order_cells(self, indexes=None, **kwargs):
        orig_indexes = list(range(self.nb_cells))
        for cell_index, orig_cell_ind in enumerate(indexes):
            cur_cell_ind = orig_indexes.index(orig_cell_ind)
            if cur_cell_ind != cell_index:
                self.switch_cells(index_1=cell_index, index_2=cur_cell_ind, **kwargs)
                orig_indexes[cell_index], orig_indexes[cur_cell_ind] = orig_indexes[cur_cell_ind], orig_indexes[cell_index]
        
    def switch_cells(self, index_1, index_2, **kwargs):
        if index_1 == index_2:
            raise TechnicalException(f"The two indexes are equal (index = {index_1})")
    
        self.cells[index_1], self.cells[index_2] = self.cells[index_2], self.cells[index_1]

