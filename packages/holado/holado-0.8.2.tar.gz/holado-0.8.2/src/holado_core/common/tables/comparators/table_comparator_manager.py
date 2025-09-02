
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
from builtins import object
from holado_core.common.tables.comparators.string_table_cell_comparator import StringTableCellComparator
import re
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tables.comparators.integer_table_cell_comparator import IntegerTableCellComparator
from holado_core.common.tables.comparators.float_table_cell_comparator import FloatTableCellComparator
from holado_core.common.tables.comparators.bytes_table_cell_comparator import BytesTableCellComparator
from holado_core.common.tables.comparators.datetime_table_cell_comparator import DatetimeTableCellComparator
from holado_core.common.tables.comparators.boolean_table_cell_comparator import BooleanTableCellComparator
from holado_core.common.tools.converters.converter import Converter
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class TableComparatorManager(object):
    
    @classmethod
    def convert_compare_method_2_TableCellComparator(cls, compare_method):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Converting compare method name to associated TableCellComparator")

        if compare_method == "Boolean":
            return BooleanTableCellComparator()
        elif compare_method == "Bytes":
            return BytesTableCellComparator()
        elif compare_method == "Datetime":
            return DatetimeTableCellComparator()
        elif compare_method.startswith("Float"):
            regex = re.compile(r"Float\((.*)\)")
            r_match = regex.match(compare_method)
            if r_match:
                precision_str = r_match.group(1)
                if Converter.is_float(precision_str):
                    precision = float(precision_str)
                    return FloatTableCellComparator(diff_precision=precision, relative_precision=None)
                else:
                    raise FunctionalException("The parameter of compare method 'Float' is a precision that must be a float")
            else:
                return FloatTableCellComparator()
        elif compare_method == "Integer":
            return IntegerTableCellComparator()
        elif compare_method == "String":
            return StringTableCellComparator()
        
        
