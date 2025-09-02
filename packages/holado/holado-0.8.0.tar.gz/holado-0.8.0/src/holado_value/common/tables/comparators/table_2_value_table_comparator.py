
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
from holado_core.common.tables.comparators.table_comparator import TableComparator
from holado_value.common.tables.comparators.table_2_value_table_row_comparator import Table2ValueTable_RowComparator


class Table2ValueTable_Comparator(TableComparator):
    def __init__(self, row_comparator=None, cell_comparator=None, **kwargs):
        if row_comparator is None:
            row_comparator = Table2ValueTable_RowComparator(cell_comparator=cell_comparator, **kwargs)
        super().__init__(row_comparator=row_comparator, cell_comparator=None)
    
    
