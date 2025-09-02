
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

import logging
from holado_db.tools.db.clients.sqlite.sqlite_client import SQLite3Client
from holado_db.tools.db.clients.postgresql.postgresql_client import PostgreSQLClient
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.handlers.abstracts.get_or_create import GetOrCreateVariableObject
from holado_core.common.tools.tools import Tools
from holado.common.context.session_context import SessionContext


logger = logging.getLogger(__name__)



class DBManager(GetOrCreateVariableObject):
    """
    Manage DB clients, agnostic to managed DB.
    
    It manages an instance by thread for DB types (ex: sqlite3) which clients don't support multithreading.
    Note: Even if sqlite3 can support multithreading (with 'connect' parameter 'check_same_thread=False'),
          current implementation of DBManager keeps sqlite3 default behavior.
    """
    
    def __init__(self, name):
        super().__init__(name if name else "DBManager")
        
        self.__func_query_manager = None
        self.__db_info_by_db_type = {}
    
    def initialize(self, func_variable_manager, func_query_manager):
        super().initialize(func_variable_manager)
        self.__func_query_manager = func_query_manager
        
        if SQLite3Client.is_available():
            self.register_db_client("sqlite3", SQLite3Client, do_support_multithreading=False)
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("SQLite3 package is not installed, this type of DB is not available")
        if PostgreSQLClient.is_available():
            self.register_db_client("postgresql", PostgreSQLClient)
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("PostgreSQL package is not installed, this type of DB is not available")
    
    @property
    def __query_manager(self):
        return self.__func_query_manager()
    
    def register_db_client(self, db_type, new_client_func, do_support_multithreading=True):
        self.__db_info_by_db_type[db_type] = (new_client_func, do_support_multithreading)
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Registered DB type '{db_type}'")
    
    def get_or_create(self, name, *args, **kwargs):
        # Manager DB types that need a client by thread
        db_type = self.__find_db_type(args, kwargs)
        if db_type is not None and not self.__db_info_by_db_type[db_type][1]:
            thread_db_manager = SessionContext.instance().multitask_manager.get_thread_context().db_manager
            if thread_db_manager is not self:
                return thread_db_manager.get_or_create(name, *args, **kwargs)
            else:
                # Prefix name by thread UID, since same variable manager is shared by all thread context DBManagers
                thread_uid = SessionContext.instance().multitask_manager.get_thread_uid()
                real_name = f"{thread_uid}-{name}"
        else:
            real_name = name
        
        return super().get_or_create(real_name, *args, **kwargs)
    
    def __find_db_type(self, args, kwargs):
        if kwargs and 'db_type' in kwargs:
            return kwargs['db_type']
        elif args and len(args) > 0 and args[0] in self.__db_info_by_db_type:
            return args[0]
        else:
            return None
    
    def _goc_new_object(self, name, db_type, connect_kwargs):
        res = self.new_client(name, db_type, connect_kwargs)
        res.connect()
        return res
    
    def new_client(self, name, db_type, connect_kwargs):
        if db_type in self.__db_info_by_db_type:
            try:
                res = self.__db_info_by_db_type[db_type][0](name, connect_kwargs)
            except Exception as exc:
                raise TechnicalException(f"Failed to create client for DB type '{db_type}' with connect parameters: {connect_kwargs}") from exc
        else:
            raise TechnicalException(f"Unmanaged DB type '{db_type}'")
        
        res.query_builder = self.__query_manager.new_default_query_builder(db_type, res)
        return res
        
        
        
        