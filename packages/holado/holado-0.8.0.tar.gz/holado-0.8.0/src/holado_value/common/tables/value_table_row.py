
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
from holado_value.common.tables.value_table_cell import ValueTableCell
from holado_core.common.tables.table_row import TableRow
import logging
from holado_core.common.tools.tools import Tools
from holado.common.handlers.undefined import undefined_value

logger = logging.getLogger(__name__)


class ValueTableRow(TableRow):
    def __init__(self, cells=None, cells_content=None, cells_value=None, **kwargs):
        super().__init__(cells=cells, cells_content=cells_content, **kwargs)
        if cells_value is not None:
            self.add_cells_from_values(cells_value, **kwargs)
    
    @property
    def cells_value(self): 
        return tuple(c.value for c in self.cells)

    def _new_cell(self, content, value=undefined_value, do_eval_once=True, **kwargs):  # @UnusedVariable
        return ValueTableCell(cell_content=content, cell_value=value, do_eval_once=do_eval_once)
    
    def add_cells_from_values(self, cells_value, do_eval_once=True, **kwargs):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"add_cells_from_values({cells_value=})")
        for cell_value in cells_value:
            self.add_cell(value=cell_value, do_eval_once=do_eval_once, **kwargs)
    
    
