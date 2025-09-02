
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
import logging
from holado_value.common.tools.value import Value

logger = logging.getLogger(__name__)


class ValueTableCell(TableCell):
    
    def __init__(self, cell_content, cell_value=None, do_eval_once=True):
        """
        @summary: Constructor
        @param cell_content: Cell content
        @param cell_value: Cell value
        @param do_eval_once: If cell value must be evaluated only at first value evaluation (ie at first call of value property) (default: True)
        """
        super().__init__(cell_content)
        
        self.__value = Value(original_value=cell_content, value=cell_value, do_eval_once=do_eval_once)
        self.content = self.__value.original_value
        
    def __eq__(self, other):
        self._verify_valid_compared_object(other)
        if isinstance(other, ValueTableCell):
            return (self.value == other.value)
        else:
            return (self.value == other.content)
    
    def __lt__(self, other):
        self._verify_valid_compared_object(other)
        if isinstance(other, ValueTableCell):
            return (self.value < other.value)
        else:
            return (self.value < other.content)

    @TableCell.string_content.getter  # @UndefinedVariable
    def string_content(self):
        return self.__value.string_value
    
    @property
    def content_type(self):
        return self.__value.original_value_type
    
    @property
    def value_type(self):
        return self.__value.value_type
    
    @property
    def value(self):
        return self.__value.value
    
    @value.setter
    def value(self, value):
        self.__value = Value(original_value=None, value=value, do_eval_once=self.__value.do_eval_once)
        self.content = self.__value.original_value
    
    def get_value(self, raise_if_undefined=False):
        return self.__value.get_value(raise_if_undefined=raise_if_undefined)
    
    def represent(self, indent = 0, do_evaluation = False):
        return self.__value.represent(indent, do_evaluation)
        
