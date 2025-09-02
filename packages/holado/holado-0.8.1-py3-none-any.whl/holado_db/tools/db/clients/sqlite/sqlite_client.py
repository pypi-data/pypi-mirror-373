
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2023 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
from holado_db.tools.db.clients.base.db_client import DBClient
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools
from holado_db.tools.db.clients.sqlite.sqlite_audit import SQLite3TriggerAuditManager

logger = logging.getLogger(__name__)

try:
    import sqlite3
    with_sqlite3 = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"SQLite3Client is not available. Initialization failed on error: {exc}")
    with_sqlite3 = False


class SQLite3Client(DBClient):
    @classmethod
    def is_available(cls):
        return with_sqlite3

    def __init__(self, name, connect_kwargs):
        super().__init__(name if name else 'SQLite3', connect_kwargs)
        
    def _new_audit_manager(self):
        return SQLite3TriggerAuditManager("Audit with triggers", self)
    
    def _get_base_exception_type(self):
        return sqlite3.Error
        
    def _connect(self, **kwargs):
        try:
            connect_kwargs = dict(kwargs)
            database = connect_kwargs.pop("database")
            return sqlite3.connect(database, **connect_kwargs)
        except Exception as exc:
            raise FunctionalException(f"Failed to connect with kwargs={kwargs}.\nUsage:\n{Tools.indent_string(4, sqlite3.connect.__doc__)}") from exc  # @UndefinedVariable
        
    def _get_sql_placeholder(self):
        return "?"
        
    def exist_table(self, table_name):
        result = self.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        return result is not None and result.nb_rows > 0
        
        
