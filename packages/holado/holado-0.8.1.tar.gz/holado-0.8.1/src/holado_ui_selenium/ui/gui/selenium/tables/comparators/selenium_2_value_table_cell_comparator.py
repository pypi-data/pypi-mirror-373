
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
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.exceptions.functional_exception import FunctionalException
import logging
from holado_value.common.tables.comparators.table_2_value_table_cell_comparator import Table2ValueTable_CellComparator
from holado_ui_selenium.ui.gui.selenium.inspectors.selenium_inspector import SeleniumInspector
from holado_core.common.finders.tools.find_parameters import FindParameters

logger = logging.getLogger(__name__)


class Selenium2Value_TableCellComparator(Table2ValueTable_CellComparator):
    def __init__(self, inspector:SeleniumInspector=None):
        super().__init__()
        self.__inspector = inspector

    def _equals_symbol(self, cell_1, cell_symbol, is_obtained_vs_expected = True, raise_exception = True):
        res = True
        
        # Get cell selenium element
        cell_1_element = cell_1.content
        
        symbol_value = cell_symbol.value
        if symbol_value is None:
            if cell_1_element is not None:
                if raise_exception:
                    raise VerifyException("Cell value is not None (cell: [{}])".format(cell_1))
                else:
                    res = False
        else:
            # Find symbol element
            element = self.__inspector.get_finder_symbol(symbol_value).find_in(cell_1_element, FindParameters.default(raise_exception))
            
            res = (element is not None)
            if not res and raise_exception:
                raise FunctionalException(f"Unable to find symbol '{symbol_value}'.")
        
        return res
    
    
    
