
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
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
import logging
from holado_core.common.tables.comparators.string_table_row_comparator import StringTableRowComparator
from holado_core.common.exceptions.exceptions import Exceptions
from holado_core.common.tools.tools import Tools
from holado_core.common.tables.comparators.table_row_comparator import TableRowComparator

logger = logging.getLogger(__name__)


class TableComparator(Comparator):
    def __init__(self, row_comparator=None, cell_comparator=None):
        super().__init__("table")
        
        if row_comparator is not None:
            self.__row_comparator = row_comparator
        elif cell_comparator is not None:
            self.__row_comparator = TableRowComparator(cell_comparator)
        else:
            self.__row_comparator = StringTableRowComparator()

    @property
    def row_comparator(self):
        return self.__row_comparator
    
    def equals(self, table_1, table_2, is_obtained_vs_expected = True, raise_exception = True):
        try:
            res = True
            
            # Verify number of rows
            if table_1.nb_rows != table_2.nb_rows:
                if raise_exception:
                    raise VerifyException("Tables have not same number of rows (table {name1}: {nb1} rows ; table {name2}: {nb2} rows):\n  table {name1}:\n{repr1}\n  table {name2}:\n{repr2})".format(
                                                  name1=self._get_name_1(is_obtained_vs_expected), nb1=table_1.nb_rows, repr1=table_1.represent(4),
                                                  name2=self._get_name_2(is_obtained_vs_expected), nb2=table_2.nb_rows, repr2=table_2.represent(4)))
                else:
                    return False
                
            # Compare rows content
            for i in range(table_1.nb_rows):
                try:
                    res = self.__row_comparator.equals(table_1.get_row(i),
                                                       table_2.get_row(i),
                                                       is_obtained_vs_expected=is_obtained_vs_expected,
                                                       raise_exception=raise_exception)
                except FunctionalException as exc:
                    msg = "Difference exists at line of index {}:\n----------------------------------\n -> {}\n----------------------------------\n  table {}:\n{}\n  table {}:\n{}".format(
                            i, Exceptions.exception_message(exc), self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
                    raise VerifyException(msg) from exc
                except Exception as exc:
                    msg = "Error while comparing line of index {}:\n----------------------------------\n -> {}\n----------------------------------\n  table {}:\n{}\n  table {}:\n{}".format(
                            i, Exceptions.exception_message(exc), self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
                    raise TechnicalException(msg) from exc
                
                if not res:
                    if raise_exception:
                        raise TechnicalException("This case should have already raised an exception")
                    else:
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug("Difference exists at line of index {}:\n  table {}:\n{}\n  table {}:\n{}".format(
                                       i, self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4)))
                        break
                    
            return res
        except (FunctionalException, TechnicalException) as exc:
            raise exc
        except Exception as exc:
            msg = "Error while comparing tables:\n{}\n  table {}:\n{}\n  table {}:\n{}".format(
                    Tools.indent_string(4, Exceptions.exception_message(exc)), 
                    self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), 
                    self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
            raise TechnicalException(msg) from exc
    
    def contains_rows(self, table_1, table_2, check_row_order = True, is_obtained_vs_expected = True, raise_exception = True):
        try:
            res = True
            
            # Compare rows content
            start_index = 0
            for i in range(table_2.nb_rows):
                try:
                    res, row_index = self.contains_row(table_1, table_2.get_row(i), start_row_index = start_index,
                                                       is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception)
                    if check_row_order:
                        start_index = row_index + 1
                except FunctionalException as exc:
                    msg = "Table {} doesn't contain row {} of index {}:\n----------------------------------\n -> {}\n----------------------------------\n  table {}:\n{}\n  table {}:\n{}".format(
                            self._get_name_1(is_obtained_vs_expected), self._get_name_2(is_obtained_vs_expected), i, Exceptions.exception_message(exc), self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
                    raise VerifyException(msg) from exc
                except Exception as exc:
                    msg = "Error while checking if table {} contains row {} of index {}:\n----------------------------------\n -> {}\n----------------------------------\n  table {}:\n{}\n  table {}:\n{}".format(
                            self._get_name_1(is_obtained_vs_expected), self._get_name_2(is_obtained_vs_expected), i, Exceptions.exception_message(exc), self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
                    raise TechnicalException(msg) from exc
                
                if not res:
                    break
                    
            return res
        except (FunctionalException, TechnicalException) as exc:
            raise exc
        except Exception as exc:
            msg = "Error while checking if table {} contains rows of table {}:\n{}\n  table {}:\n{}\n  table {}:\n{}".format(
                    self._get_name_1(is_obtained_vs_expected), self._get_name_2(is_obtained_vs_expected), 
                    Tools.indent_string(4, Exceptions.exception_message(exc)), 
                    self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), 
                    self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
            raise TechnicalException(msg) from exc
    
    def doesnt_contain_rows(self, table_1, table_2, is_obtained_vs_expected = True, raise_exception = True):
        try:
            res = True
            
            # Compare rows content
            for i in range(table_2.nb_rows):
                try:
                    row_res, _ = self.contains_row(table_1, table_2.get_row(i),
                                                       is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=False)
                except Exception as exc:
                    msg = "Error while checking if table {} contains row {} of index {}:\n----------------------------------\n -> {}\n----------------------------------\n  table {}:\n{}\n  table {}:\n{}".format(
                            self._get_name_1(is_obtained_vs_expected), self._get_name_2(is_obtained_vs_expected), i, Exceptions.exception_message(exc), self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
                    raise TechnicalException(msg) from exc
                
                if row_res:
                    if raise_exception:
                        msg = "Table {} contains row {} of index {}:\n  table {}:\n{}\n  table {}:\n{}".format(
                                self._get_name_1(is_obtained_vs_expected), self._get_name_2(is_obtained_vs_expected), i, self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
                        raise VerifyException(msg)
                    else:
                        res = False
                        break
                
            return res
        except (FunctionalException, TechnicalException) as exc:
            raise exc
        except Exception as exc:
            msg = "Error while checking if table {} contains rows of table {}:\n{}\n  table {}:\n{}\n  table {}:\n{}".format(
                    self._get_name_1(is_obtained_vs_expected), self._get_name_2(is_obtained_vs_expected), 
                    Tools.indent_string(4, Exceptions.exception_message(exc)), 
                    self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), 
                    self._get_name_2(is_obtained_vs_expected), self._represent_table(table_2, 4))
            raise TechnicalException(msg) from exc
    
    def contains_row(self, table_1, row_2, start_row_index = 0, is_obtained_vs_expected = True, raise_exception = True):
        try:
            res = True
            res_index = -1
            
            # Compare rows content
            for i in range(start_row_index, table_1.nb_rows):
                try:
                    res = self.__row_comparator.equals(table_1.get_row(i),
                                                       row_2,
                                                       is_obtained_vs_expected=is_obtained_vs_expected,
                                                       raise_exception=False)
                except Exception as exc:
                    msg = "Error while comparing line of index {}:\n----------------------------------\n -> {}\n----------------------------------\n  table {}:\n{}\n  table {}:\n{}".format(
                            i, Exceptions.exception_message(exc), self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_row(row_2, 4))
                    raise TechnicalException(msg) from exc
                
                if res:
                    res_index = i
                    break
                
            if not res and raise_exception:
                msg = "Table doesn't contain the row:\n  table {}:\n{}\n  row {}:\n{}".format(
                               self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), self._get_name_2(is_obtained_vs_expected), self._represent_row(row_2, 4))
                raise VerifyException(msg)
                    
            return (res, res_index)
        except (FunctionalException, TechnicalException) as exc:
            raise exc
        except Exception as exc:
            msg = "Error while searching row in table:\n{}\n  table {}:\n{}\n  row {}:\n{}".format(
                    Tools.indent_string(4, Exceptions.exception_message(exc)), 
                    self._get_name_1(is_obtained_vs_expected), self._represent_table(table_1, 4), 
                    self._get_name_2(is_obtained_vs_expected), self._represent_row(row_2, 4))
            raise TechnicalException(msg) from exc
    
    def _represent_table(self, table, indent):
        try:
            return table.represent(indent)
        except Exception as exc:
            return f"[ERROR while representing table: {Exceptions.exception_message(exc)}]"
    
    def _represent_row(self, row, indent):
        try:
            return row.represent(indent)
        except Exception as exc:
            return f"[ERROR while representing table row: {Exceptions.exception_message(exc)}]"
