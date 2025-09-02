
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
from holado.common.handlers.undefined import default_value
from holado_db.tools.db.clients.base.db_audit import TriggerAuditManager

logger = logging.getLogger(__name__)


class PostgreSQLTriggerAuditManager(TriggerAuditManager):
    """Manage audit of tables by triggers.
    WARNING: This case is not tested yet
    """
    def __init__(self, name, db_client):
        super().__init__(name, db_client)
    
    def _get_audit_table_sql_create(self, audit_table_name=default_value):
        audit_table_name = self._get_audit_table_name(audit_table_name)
        return f"""CREATE TABLE {audit_table_name} (
                id SERIAL PRIMARY KEY,
                table_name TEXT,
                record_id INTEGER,
                operation_type TEXT,
                changed_at TIMESTAMP DEFAULT now(),
                changed_by TEXT,
                previous_values JSONB,
                new_values JSONB
            )"""
    
    def _get_drop_trigger_sql_of_audit_table_operation(self, table_name, operation_type, audit_table_name):
        audit_table_name = self._get_audit_table_name(audit_table_name)
        trigger_name = self.get_trigger_name(table_name, operation_type)
        return f"DROP TRIGGER IF EXISTS {trigger_name} on {table_name}"
    
    def _get_create_trigger_sql_to_audit_table_operation(self, table_name, operation_type, audit_table_name):
        audit_table_name = self._get_audit_table_name(audit_table_name)
        trigger_name = self.get_trigger_name(table_name, operation_type)
        trigger_insert_sql = self.__get_trigger_insert_sql(table_name, operation_type, audit_table_name)
        return f"""CREATE TRIGGER {trigger_name} AFTER {operation_type.upper()} ON {table_name}
                BEGIN
                    {trigger_insert_sql}
                END;
                """
    
    def __get_trigger_insert_sql(self, table_name, operation_type, audit_table_name):
        rowid_txt = "NEW.id" if operation_type in ['insert', 'update'] else "OLD.id"
        op_type = operation_type[0]
        prev_vals_txt = "to_jsonb(OLD)" if operation_type in ['update', 'delete'] else "NULL"
        new_vals_txt = "to_jsonb(NEW)" if operation_type in ['insert', 'update'] else "NULL"
        
        audit_info = [f"'{table_name}'",
                      rowid_txt,
                      f"'{op_type}'",
                      "current_user",
                      prev_vals_txt,
                      new_vals_txt,
                     ]
        audit_info = ','.join(audit_info)
        
        return f"""INSERT INTO {audit_table_name} (table_name, record_id, operation_type, changed_by, previous_values, new_values) 
                   VALUES ({audit_info});"""



