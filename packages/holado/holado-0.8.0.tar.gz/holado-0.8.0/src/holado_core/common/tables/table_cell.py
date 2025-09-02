
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

from holado_core.common.tools.tools import Tools
import copy
from functools import total_ordering
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.typing import Typing


@total_ordering
class TableCell(object):
    EMPTY_SYMBOL = u"None"
    # LEFT_MERGED_SYMBOL = u"LeftMerged";
    # TOP_MERGED_SYMBOL = u"TopMerged";
    
    """
    @summary: Table cell
    """
    def __init__(self, cell_content = None):
        self.__parent = None
        
        if cell_content is not None and isinstance(cell_content, str) and cell_content == TableCell.EMPTY_SYMBOL:
            self.__content = None
        else:
            self.__content = cell_content
    
    @property
    def parent(self):
        """ Parent, relevant for some table types. It's usually the origin of its creation. """
        return self.__parent
    
    @parent.setter
    def parent(self, parent):
        """ Set parent. """
        self.__parent = parent

    @property
    def content(self):
        return self.__content
    
    @content.setter
    def content(self, cell_content):
        self.__content = cell_content
    
    @property
    def string_content(self):
        if self.__content is not None:
            return str(self.__content)
        else:
            return None
    
    def _verify_valid_compared_object(self, other, raise_exception=True):
        res = isinstance(other, TableCell)
        if not res and raise_exception:
            return TechnicalException(f"Unmanaged comparison between types '{self.__class__.__name__}' and '{other.__class__.__name__}'")
        
    def __eq__(self, other):
        self._verify_valid_compared_object(other)
        return (self.content == other.content)
    
    def __lt__(self, other):
        self._verify_valid_compared_object(other)
        return (self.content < other.content)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __eq__(self, other):
        if not isinstance(other, TableCell):
            return NotImplemented(f"Not implemented to compare a {Typing.get_object_class_fullname(self)} to a {Typing.get_object_class_fullname(other)}")
        return (self.content == other.content)
    
    def __lt__(self, other):
        if not isinstance(other, TableCell):
            return NotImplemented(f"Not implemented to compare a {Typing.get_object_class_fullname(self)} to a {Typing.get_object_class_fullname(other)}")
        return (self.content < other.content)
    
    def __repr__(self)->str:
        return f"<{self.__class__.__name__}>[{self.represent()}]"
        
    def is_empty(self, **kwargs):  # @UnusedVariable
        return (self.__content is None)
        
    def represent(self, indent = 0, cell_value_prefix = "'", cell_value_postfix = "'"):
        res_list = []
        
        res_list.append(Tools.get_indent_string(indent))
        
        if self.is_empty():
            res_list.append(TableCell.EMPTY_SYMBOL)
        elif isinstance(self.__content, str):
            if cell_value_prefix is not None:
                res_list.append(cell_value_prefix)
            res_list.append(self.string_content)
            if cell_value_postfix is not None:
                res_list.append(cell_value_postfix)
        else:
            res_list.append(self.string_content)
        
        return "".join(res_list)
        
    def compare_to(self, cell):
        raise NotImplementedError()
    
