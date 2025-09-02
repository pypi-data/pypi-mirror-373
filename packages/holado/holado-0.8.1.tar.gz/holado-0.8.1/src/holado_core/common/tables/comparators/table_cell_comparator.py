
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
from holado_core.common.tools.comparators.comparator import Comparator
import abc
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_value.common.tables.value_table_cell import ValueTableCell
from holado_python.standard_library.typing import Typing


class TableCellComparator(Comparator):
    __metaclass__ = abc.ABCMeta    

    def __init__(self):
        super().__init__("table cell")
    
    def _convert_input(self, obj, name):
        if isinstance(obj, ValueTableCell):
            res = obj.value
        elif isinstance(obj, TableCell):
            res = obj.content
        else:
            raise TechnicalException(f"Unexpected input of type {Typing.get_object_class_fullname(obj)} (expected: TableCell or any sub-type)")
        return res
        
    
