
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
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.tools.tools import Tools
from holado_db.tools.db.clients.postgresql.postgresql_audit import PostgreSQLTriggerAuditManager
from holado_db.tools.db.query.pypika.pypika_query_builder import PypikaQueryBuilder
from holado_core.common.exceptions.technical_exception import TechnicalException

logger = logging.getLogger(__name__)

try:
    import psycopg
    with_psycopg = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"PostgreSQLClient is not available. Initialization failed on error: {exc}")
    with_psycopg = False

if PypikaQueryBuilder.is_available():
    from pypika.terms import Function, LiteralValue
    
    # from pypika import Function
    class JsonbSet(Function):
        def __init__(self, name, *args, **kwargs):
            super().__init__('jsonb_set', LiteralValue(name), *args, **kwargs)


class PostgreSQLClient(DBClient):
    @classmethod
    def is_available(cls):
        return with_psycopg

    def __init__(self, name, connect_kwargs):
        super().__init__(name if name else 'PostgreSQL', connect_kwargs)
        
    def _new_audit_manager(self):
        return PostgreSQLTriggerAuditManager("Audit with triggers", self)
        
    def _get_base_exception_type(self):
        return psycopg.Error
    
    def _connect(self, **kwargs):
        return psycopg.connect(**kwargs)
        
    def _get_sql_placeholder(self):
        return "%s"
        
    def exist_table(self, table_name):
        result = self.execute(f"SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = '{table_name}'")
        return result is not None
        
    def set_or_update_json_key_value(self, table_name, field_name, json_key, json_value, where_data: dict=None, where_compare_data: list=None):
        # Help on JSON column: https://www.databasestar.com/postgresql-json/#How_to_Update_JSON_Data_in_PostgreSQL
        result = self.select(table_name, where_data=where_data, where_compare_data=where_compare_data, sql_return=field_name)
        is_set = isinstance(result, TableWithHeader) and result[0][0].content is not None
        if not is_set:
            self.update(table_name, {field_name: f'{{"{json_key}":"{json_value}"}}'}, where_data=where_data, where_compare_data=where_compare_data, do_commit=True)
        else:
            result = self.select(table_name, where_data=where_data, where_compare_data=where_compare_data, sql_return=f"{field_name}")
            is_key_set = False
            if isinstance(result, TableWithHeader) and result[0][0].content is not None:
                is_key_set = json_key in result[0][0].content
            if is_key_set:
                if not PypikaQueryBuilder.is_available():
                    # Note: This case cannot appear currently (04/08/2025), but can appear if another QueryBuilder is managed that is not using pypika
                    raise TechnicalException(f"Missing dependence: pypika")
                self.update(table_name, {field_name: JsonbSet(f'{field_name}', f'{{"{json_key}"}}', f'"{json_value}"')}, where_data=where_data, where_compare_data=where_compare_data, do_commit=True)
            else:
                self.update(table_name, {field_name: f'{field_name} || {{"{json_key}":"{json_value}"}}'}, where_data=where_data, where_compare_data=where_compare_data, do_commit=True)
    
    
