
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
from holado.common.handlers.object import Object
import abc
from holado.common.handlers.undefined import default_value, any_value

logger = logging.getLogger(__name__)


class DBAuditManager(Object):
    """Base class for audit managers.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, db_client):
        super().__init__(name)
        
        self.__db_client = db_client
    
    @property
    def _db_client(self):
        return self.__db_client
    
    def audit_table(self, table_name, operation_types=any_value, **kwargs):
        raise NotImplementedError()

    def _get_audit_table_name(self, audit_table_name=default_value):
        if audit_table_name is default_value:
            return "_audit"
        else:
            return audit_table_name

    def _get_audit_table_sql_create(self, audit_table_name=default_value):
        raise NotImplementedError()
    
    def ensure_audit_table_exists(self, audit_table_name=default_value):
        audit_table_name = self._get_audit_table_name(audit_table_name)
        create_sql = self._get_audit_table_sql_create(audit_table_name=audit_table_name)
        self._db_client.create_table(audit_table_name, create_sql, raise_if_exist=False, do_commit=True, do_audit=False)
    


class TriggerAuditManager(DBAuditManager):
    def __init__(self, name, db_client):
        super().__init__(name, db_client)
    
    def audit_table(self, table_name, operation_types=any_value, audit_table_name=default_value, **kwargs):
        self.ensure_audit_table_exists(audit_table_name)
        
        if operation_types is any_value:
            operation_types = ['insert', 'update', 'delete']
        else:
            operation_types = [ot.lower() for ot in operation_types]
        
        for op_type in operation_types:
            self.drop_trigger_of_audit_table_operation(table_name, op_type, audit_table_name, **kwargs)
            self.create_trigger_to_audit_table_operation(table_name, op_type, audit_table_name, **kwargs)
    
    def get_trigger_name(self, table_name, operation_type):
        return f"audit_{table_name}_on_{operation_type}"
    
    def drop_trigger_of_audit_table_operation(self, table_name, operation_type, audit_table_name, **kwargs):
        drop_sql = self._get_drop_trigger_sql_of_audit_table_operation(table_name, operation_type, audit_table_name)
        
        do_commit = kwargs.pop('do_commit', True)
        self._db_client.execute(drop_sql, do_commit=do_commit, **kwargs)
    
    def _get_drop_trigger_sql_of_audit_table_operation(self, table_name, operation_type):
        raise NotImplementedError()
    
    def create_trigger_to_audit_table_operation(self, table_name, operation_type, audit_table_name, **kwargs):
        create_sql = self._get_create_trigger_sql_to_audit_table_operation(table_name, operation_type, audit_table_name)
        
        do_commit = kwargs.pop('do_commit', True)
        self._db_client.execute(create_sql, do_commit=do_commit, **kwargs)
    
    def _get_create_trigger_sql_to_audit_table_operation(self, table_name, operation_type):
        raise NotImplementedError()




