
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



from builtins import range
from builtins import super
from holado_core.common.tools.comparators.comparator import Comparator
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
import logging
from holado_core.common.exceptions.exceptions import Exceptions

logger = logging.getLogger(__name__)


class TableRowComparator(Comparator):
    def __init__(self, cell_comparator=None, cells_comparators=None):
        """
        Define the method used to compare cells.
        Implementation tests first if cells_comparators is defined, else it uses cell_comparator 
        """
        super().__init__("table row")
        
        self.__cell_comparator = cell_comparator
        self.__cells_comparators = cells_comparators
        if self.__cell_comparator is None and self.__cells_comparators is None:
            raise TechnicalException("No cell comparator is defined")
        
    def equals(self, row_1, row_2, is_obtained_vs_expected = True, raise_exception = True):
        try:
            res = True
            
            # Verify number of cells
            if row_1.nb_cells != row_2.nb_cells:
                if raise_exception:
                    raise VerifyException("Rows have not same number of cells (row {name1}: {nb1} cells ; row {name2}: {nb2} cells):\n  row {name1}:\n{repr1}\n  row {name2}:\n{repr2})".format(
                                                   name1=self._get_name_1(is_obtained_vs_expected), nb1=row_1.nb_cells, repr1=row_1.represent(0), 
                                                   name2=self._get_name_2(is_obtained_vs_expected), nb2=row_2.nb_cells, repr2=row_2.represent(0)))
                else:
                    return False
            if self.__cells_comparators is not None and row_1.nb_cells > len(self.__cells_comparators):
                raise TechnicalException("Rows have more cells than defined in list of cells comparators")
                
                
            # Compare cells content
            for i in range(row_1.nb_cells):
                # Define cell comparator to use
                if self.__cells_comparators is not None:
                    cell_comp = self.__cells_comparators[i]
                else:
                    cell_comp = self.__cell_comparator
                
                # Manage case where the cell comparator is None, meaning the cells mustn't be compared
                if cell_comp is None:
                    continue
                
                # Compare cells
                try:
                    res = cell_comp.equals(row_1.get_cell(i),
                                           row_2.get_cell(i),
                                           is_obtained_vs_expected = is_obtained_vs_expected,
                                           raise_exception = raise_exception)
                except FunctionalException as exc:
                    msg = "Difference exists in row at cells of index {}:\n{}\n  row {}: {}\n  row {}: {}\n  cell comparator: {}".format(
                            i, Tools.indent_string(4, Exceptions.exception_message(exc)), 
                            self._get_name_1(is_obtained_vs_expected), self.__represent_row(row_1), 
                            self._get_name_2(is_obtained_vs_expected), self.__represent_row(row_2),
                            cell_comp)
                    raise VerifyException(msg) from exc
                except Exception as exc:
                    msg = "Error while comparing cells of index {}:\n{}\n  row {}: {}\n  row {}: {}\n  cell comparator: {}".format(
                            i, Tools.indent_string(4, Exceptions.exception_message(exc)), 
                            self._get_name_1(is_obtained_vs_expected), self.__represent_row(row_1), 
                            self._get_name_2(is_obtained_vs_expected), self.__represent_row(row_2),
                            cell_comp)
                    raise TechnicalException(msg) from exc
                
                if not res:
                    if raise_exception:
                        raise TechnicalException("This case should have already raised an exception")
                    else:
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug("Difference exists in row at cells of index {}:\n  row {}:\n{}\n  row {}:\n{}".format(
                                         i, self._get_name_1(is_obtained_vs_expected), self.__represent_row(row_1, 4), self._get_name_2(is_obtained_vs_expected), self.__represent_row(row_2, 4)))
                        break
                    
            return res
        except (FunctionalException, TechnicalException) as exc:
            raise exc
        except Exception as exc:
            msg = "Error while comparing rows:\n{}\n  row {}: {}\n  row {}: {}".format(
                    Tools.indent_string(4, Exceptions.exception_message(exc)), 
                    self._get_name_1(is_obtained_vs_expected), self.__represent_row(row_1), 
                    self._get_name_2(is_obtained_vs_expected), self.__represent_row(row_2))
            raise TechnicalException(msg) from exc
    
    def __represent_row(self, row, indent=0):
        try:
            return row.represent(indent)
        except Exception as exc:
            return f"[ERROR while representing row: {Exceptions.exception_message(exc)}]"
        

