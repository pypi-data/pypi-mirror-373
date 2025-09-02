
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
from holado_value.common.tables.value_table_with_header import ValueTableWithHeader
from holado_core.common.tables.table_manager import TableManager
from holado_core.common.tools.tools import Tools
from holado_value.common.tables.value_table import ValueTable
from holado_core.common.exceptions.verify_exception import VerifyException

logger = logging.getLogger(__name__)


class ValueTableManager(TableManager):
    
    @classmethod
    def is_value_table(cls, table):
        return isinstance(table, ValueTable) or isinstance(table, ValueTableWithHeader)
    
    @classmethod
    def verify_is_value_table(cls, table, raise_exception=True):
        res = cls.is_value_table(table)
        
        if not res and raise_exception:
            raise VerifyException(f"Table is not a ValueTable of ValueTableWithHeader (table type: {type(table)})")
        return res
    
    @classmethod
    def set_object_attributes_according_name_value_table(cls, obj, table):
        if not cls.is_value_table(table):
            super().set_object_attributes_according_name_value_table(obj, table)
        
        # Verify table structure
        cls.verify_table_is_name_value_table(table)
        
        for row in table.rows:
            setattr(obj, row.get_cell(0).value, row.get_cell(1).value)
    
