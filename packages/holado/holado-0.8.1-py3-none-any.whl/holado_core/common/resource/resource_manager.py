
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

import os
import logging
from holado.common.context.session_context import SessionContext
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools
# from holado_report.report.analyze.scenario_duration_manager import ScenarioDurationManager

logger = logging.getLogger(__name__)



class ResourceManager():
    """
    Manage local resources, ie resources stored on disk during and through sessions.
    For example, it can be used to persist data through sessions, so that a session can adapt its behavior according previous sessions.
    """
    def __init__(self, local_resource_path):
        self.__local_resource_path = local_resource_path
        
        self.__func_db_manager = None
        self.__func_path_manager = None
        self.__db_connect_kwargs_by_name = {}
        
    def initialize(self, func_db_manager, func_path_manager):
        self.__func_db_manager = func_db_manager
        self.__func_path_manager = func_path_manager
        
        self.__path_manager.makedirs(self.__local_resource_path, is_directory=True)
        
    @property
    def __db_manager(self):
        return self.__func_db_manager()
    
    @property
    def __path_manager(self):
        return self.__func_path_manager()
        
    @property
    def local_resource_path(self):
        return self.__local_resource_path
    
    def get_path(self, *args):
        return os.path.join(self.__local_resource_path, *args)
    
    def get_persistent_db_client(self, name):
        """
        Return a SQLite3 DB client to the persistent DB of given name
        """
        _, res = self.__db_manager.get_or_create(name, 'sqlite3', self.__get_db_connect_kwargs(name))
        return res
    
    def __get_db_connect_kwargs(self, name):
        if name not in self.__db_connect_kwargs_by_name:
            db_filepath = self.get_path("persistent", "db", f"{name}.sqlite3")
            SessionContext.instance().path_manager.makedirs(db_filepath)
            
            uri = f"file:{db_filepath}?mode=rwc"
            connect_kwargs = {'database': uri,
                              'uri': True}
            self.__db_connect_kwargs_by_name[name] = connect_kwargs
        return self.__db_connect_kwargs_by_name[name]
        
    def persist_pair(self, key, value, db_name="default", table_name="pair", do_commit=True):
        client = self.get_persistent_db_client(db_name)
        client.execute(f"create table if not exists {table_name} (key, value)", do_commit=do_commit)
        
        client.execute(f"insert into {table_name} values (?, ?)", key, value, do_commit=do_commit)
        
    def has_data_table(self, table_name, db_name="default"):
        client = self.get_persistent_db_client(db_name)
        return client.exist_table(table_name)
        
    def create_data_table(self, table_name, create_sql, db_name="default", raise_if_exist=False, do_commit=True, do_audit=False):
        client = self.get_persistent_db_client(db_name)
        client.create_table(table_name, create_sql, raise_if_exist=raise_if_exist, do_commit=do_commit, do_audit=do_audit)
        
    def delete_data_table(self, table_name, db_name="default", raise_if_not_exist=False, do_commit=True):
        client = self.get_persistent_db_client(db_name)
        client.drop_table(table_name, raise_if_not_exist=raise_if_not_exist, do_commit=do_commit)
        
    def check_data_table_schema(self, table_name, create_sql, db_name="default"):
        client = self.get_persistent_db_client(db_name)
        result = client.select("sqlite_schema", where_data={'name':table_name}, sql_return='sql')
        if not result:
            return False
        
        sql = result[0][0].content
        return sql == create_sql
        
    def count_persisted_data(self, table_name, where_data: dict=None, where_compare_data: list=None, db_name="default"):
        client = self.get_persistent_db_client(db_name)
        return client.count(table_name, where_data=where_data, where_compare_data=where_compare_data)
        
    def has_persisted_data(self, table_name, where_data: dict=None, where_compare_data: list=None, db_name="default"):
        count = self.count_persisted_data(table_name, where_data=where_data, where_compare_data=where_compare_data, db_name=db_name)
        return count > 0
        
    def get_persisted_data(self, table_name, where_data: dict=None, where_compare_data: list=None, db_name="default", result_as_dict_list=False, as_generator=False):
        client = self.get_persistent_db_client(db_name)
        result = client.select(table_name, where_data=where_data, where_compare_data=where_compare_data, result_as_dict_list=result_as_dict_list, as_generator=as_generator)
        return result
        
    def add_persisted_data(self, table_name, data: dict, db_name="default", do_commit=True):
        client = self.get_persistent_db_client(db_name)
        client.insert(table_name, data, do_commit=do_commit)
        
    def update_persisted_data(self, table_name, data: dict, where_data: dict=None, where_compare_data: list=None, db_name="default", do_commit=True):
        client = self.get_persistent_db_client(db_name)
        result = client.update(table_name, data=data, where_data=where_data, where_compare_data=where_compare_data, do_commit=do_commit)
        return result
        
    def delete_persisted_data(self, table_name, where_data: dict=None, where_compare_data: list=None, db_name="default", do_commit=True):
        client = self.get_persistent_db_client(db_name)
        client.delete(table_name, where_data=where_data, where_compare_data=where_compare_data, do_commit=do_commit)
        
