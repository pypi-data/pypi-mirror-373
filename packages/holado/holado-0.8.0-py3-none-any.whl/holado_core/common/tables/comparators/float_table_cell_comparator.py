
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
from holado_core.common.tables.comparators.internal_table_cell_comparator import InternalTableCellComparator


class FloatTableCellComparator(InternalTableCellComparator):
    def __init__(self, diff_precision=None, relative_precision=1e-15):
        """
        Define the comparing method and its associated precision.
        :see: holado_python.common.tools.comparators.float_comparator for more details on possible precisions.
        :param diff_precision: If defined, a difference comparison is done with this precision
        :param relative_precision: If defined, a relative comparison is done with this precision
        """
        from holado_python.common.tools.comparators.float_comparator import FloatComparator
        super().__init__(FloatComparator(diff_precision=diff_precision, relative_precision=relative_precision))
    
    
