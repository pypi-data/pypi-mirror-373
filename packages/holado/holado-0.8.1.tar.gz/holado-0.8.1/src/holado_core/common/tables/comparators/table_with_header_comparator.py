
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
import logging
from holado_core.common.tables.comparators.string_table_row_comparator import StringTableRowComparator
from holado_core.common.exceptions.exceptions import Exceptions
from holado_core.common.tools.tools import Tools
from holado_core.common.tables.comparators.table_comparator import TableComparator

logger = logging.getLogger(__name__)


class TableWithHeaderComparator(TableComparator):
    def __init__(self, header_comparator=None, row_comparator=None, cell_comparator=None):
        super().__init__(row_comparator=row_comparator, cell_comparator=cell_comparator)
        
        self.__header_comparator = header_comparator if header_comparator is not None else StringTableRowComparator()

    @property
    def header_comparator(self):
        return self.__header_comparator
        
    def equals(self, table_1, table_2, is_obtained_vs_expected = True, raise_exception = True):
        return (self.equals_headers(table_1, table_2, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception)
                and super().equals(table_1, table_2, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception))
    
    def contains_rows(self, table_1, table_2, check_row_order = True, is_obtained_vs_expected = True, raise_exception = True):
        return (self.equals_headers(table_1, table_2, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception)
                and super().contains_rows(table_1, table_2, check_row_order=check_row_order, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception))

    def doesnt_contain_rows(self, table_1, table_2, is_obtained_vs_expected = True, raise_exception = True):
        return (self.equals_headers(table_1, table_2, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception)
                and super().doesnt_contain_rows(table_1, table_2, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception))

    def equals_headers(self, table_1, table_2, is_obtained_vs_expected = True, raise_exception = True):
        try:
            return self.__header_comparator.equals(table_1.header, table_2.header, is_obtained_vs_expected=is_obtained_vs_expected, raise_exception=raise_exception);
        except FunctionalException as exc:
            msg = f"Table headers are not the same:\n -> {Exceptions.exception_message(exc)}"
            if raise_exception:
                raise VerifyException(msg) from exc
            else:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(msg)
                return False
        except Exception as exc:
            msg = "Error while comparing tables headers:\n{}\n  table {} header: {}\n  table {} header: {}".format(
                    Tools.indent_string(4, Exceptions.exception_message(exc)), 
                    self._get_name_1(is_obtained_vs_expected), self._represent_row(table_1.header, 0), 
                    self._get_name_2(is_obtained_vs_expected), self._represent_row(table_2.header, 0))
            raise TechnicalException(msg) from exc
    
