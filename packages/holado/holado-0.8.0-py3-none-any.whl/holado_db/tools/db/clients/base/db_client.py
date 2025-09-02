
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
from builtins import NotImplementedError
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.tables.table_row import TableRow
import abc
from holado_core.common.tools.tools import Tools
from holado_core.common.tables.table import Table
from holado_db.tools.db.query.base.query_builder import QueryBuilder
from holado_data.data.generator.base import BaseGenerator
from holado_python.standard_library.typing import Typing
from holado.common.handlers.object import Object

logger = logging.getLogger(__name__)


class DBClient(Object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, connect_kwargs, with_cursor=True, auto_commit=True):
        super().__init__(name)
        
        self.__connect_kwargs = connect_kwargs
        self.__with_cursor = with_cursor
        self.__auto_commit = auto_commit
        
        self.__connection = None
        self.__query_builder = None
        self.__audit_manager = None
        self.__column_names_by_table = {}
    
    @property
    def query_builder(self) -> QueryBuilder:
        return self.__query_builder
    
    @query_builder.setter
    def query_builder(self, builder):
        self.__query_builder = builder
    
    @property
    def is_connected(self):
        return self.__connection is not None
    
    @property
    def connection(self):
        return self.__connection
    
    @property
    def cursor(self):
        if not self.__with_cursor:
            raise TechnicalException(f"DB client '{self.__name}' doesn't manage cursor")
        return self.__cursor
    
    @property
    def audit_manager(self):
        if self.__audit_manager is None:
            self.__audit_manager = self._new_audit_manager()
        return self.__audit_manager
    
    def _new_audit_manager(self):
        """Create a new audit manager.
        By default, use a audit manager with a single table of audit for whole DB and with triggers on audited tables.
        Override this method in order to define which audit manager to use.
        """
        raise NotImplementedError()
    
    def connect(self):
        try:
            self.__connection = self._connect(**self.__connect_kwargs)
        except Exception as exc:
            Tools.raise_same_exception_type(exc, f"[{self.name}] Failed to connect with parameters {self.__connect_kwargs}")
        if self.__with_cursor:
            self.__cursor = self.__connection.cursor()
    
    def _connect(self, **kwargs):
        raise NotImplementedError()
    
    def _verify_is_connected(self):
        if not self.is_connected:
            raise FunctionalException(f"DB Client '{self.name}' is not connected")
    
    # Manage queries
    
    def insert(self, table_name, data: dict, do_commit=None):
        """
        Insert given data.
        Parameter 'data' has to be a dictionary with keys equal to table column names.
        """
        query, values = self.query_builder.insert(table_name, data)
        return self.execute_query(query, *values, do_commit=do_commit)
    
    def update(self, table_name, data: dict, where_data: dict=None, where_compare_data: list=None, do_commit=None):
        """
        Update given data.
        Parameters 'data' and 'where_data' have to be dictionaries with keys equal to table column names.
        """
        query, values = self.query_builder.update(table_name, data, where_data=where_data, where_compare_data=where_compare_data)
        return self.execute_query(query, *values, do_commit=do_commit)
    
    def select(self, table_name, where_data: dict=None, where_compare_data: list=None, sql_return="*", **kwargs):
        """
        Select by filtering on given where data.
        @param where_data: dictionary of (field_name, value) for simple where clauses.
        @param where_compare_data: list of tuples (field_name, operator, value) for where clauses comparing fields with values.
        """
        query, values = self.query_builder.select(table_name, where_data=where_data, where_compare_data=where_compare_data, sql_return=sql_return)
        return self.execute_query(query, *values, do_commit=False, **kwargs)
    
    def delete(self, table_name, where_data: dict=None, where_compare_data: list=None, do_commit=None):
        """
        Delete by filtering on given where data.
        Parameter 'where_data' has to be a dictionary with keys equal to table column names.
        """
        query, values = self.query_builder.delete(table_name, where_data=where_data, where_compare_data=where_compare_data)
        return self.execute_query(query, *values, do_commit=do_commit)
    
    def count(self, table_name, where_data: dict=None, where_compare_data: list=None):
        result = self.select(table_name, where_data=where_data, where_compare_data=where_compare_data, sql_return="count(*)")
        return result[0][0].content
        
    def execute_query(self, query, *args, **kwargs):
        sql = self.query_builder.to_sql(query)
        
        # Force do_commit to False for select queries
        do_commit = kwargs.pop('do_commit', None)
        
        return self.execute(sql, *args, do_commit=do_commit, **kwargs)
        
    def execute(self, sql, *args, **kwargs):
        # Manage specific parameters
        if self.is_query_type(sql, 'select'):
            do_commit = False
        else:
            do_commit = kwargs.pop('do_commit', None)
            if do_commit is None:
                do_commit = self.__auto_commit
        result_as_dict_list = kwargs.pop('result_as_dict_list', False)
        as_generator = kwargs.pop('as_generator', False)
        if as_generator and do_commit:
            raise TechnicalException(f"'do_commit=True' and 'as_generator=True' are incompatible")
        if as_generator and not result_as_dict_list:
            raise TechnicalException(f"'as_generator=True' is possible only with 'result_as_dict_list=True'")
            
        self._verify_is_connected()
        
        # Execute
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Executing SQL [{Tools.truncate_text(sql, 1000)}] (args: {Tools.truncate_text(args, 1000)} ; kwargs: {Tools.truncate_text(kwargs, 1000)})...")
        try:
            if args:
                self.cursor.execute(sql, args)
            elif kwargs:
                self.cursor.execute(sql, kwargs)
            else:
                self.cursor.execute(sql)
        except self._get_base_exception_type() as exc:
            self.rollback()
            raise TechnicalException(f"[{self.name}] Error while executing SQL [{sql}] (args: {args} ; kwargs: {kwargs})") from exc
        
        # Get result
        if self.cursor.description:
            field_names = [field[0] for field in self.cursor.description]
            
            if result_as_dict_list:
                class Cursor2DictGenerator(BaseGenerator):
                    def __init__(self, field_names, cursor):
                        super().__init__(name="DB cursor to dict generator")
                        self.__field_names = field_names
                        self.__cursor = cursor
                        self.__cursor_iter = iter(self.__cursor)
                    
                    def __next__(self):
                        row_values = next(self.__cursor_iter)
                        return dict(zip(self.__field_names, row_values))
                
                gen = Cursor2DictGenerator(field_names, self.cursor)
                if as_generator:
                    res = gen
                else:
                    res = [e for e in gen]
            else:
                res = TableWithHeader()
                res.header = TableRow(cells_content=field_names)
                
                row_values = self.cursor.fetchone()
                while row_values:
                    res.add_row(cells_content=row_values)
                    row_values = self.cursor.fetchone()
        elif self.cursor.rowcount > 0:
            res = self.cursor.rowcount
        else:
            res = None
        
        self.__log_sql_result(res, message=f"Executed SQL [{Tools.truncate_text(sql, 1000)}] (args: {Tools.truncate_text(args, 1000)} ; kwargs: {Tools.truncate_text(kwargs, 1000)})")
        
        # Manage commit
        if do_commit:
            try:
                self.commit()
            except self._get_base_exception_type() as exc:
                self.rollback()
                raise TechnicalException(f"[{self.name}] Error while commit after SQL [{sql}] (args: {args} ; kwargs: {kwargs})") from exc
            
        return res
    
    def is_query_type(self, sql_or_query, query_type):
        from sql_metadata.keywords_lists import QueryType
        import sql_metadata
        import pypika.queries
        
        if isinstance(sql_or_query, pypika.queries.QueryBuilder):
            sql = self.query_builder.to_sql(sql_or_query)
        else:
            sql = sql_or_query
        if not isinstance(sql, str):
            raise TechnicalException(f"Unexpected type '{Typing.get_object_class_fullname(sql)}' for parameter sql_or_query")
        sql = sql.lower()
        
        # Parsing query with sql_metadata can be costly, thus begin by fast and simple methods
        query_type_str = query_type.lower() if isinstance(query_type, str) else query_type.name.lower()
        for qt in ['select', 'insert', 'update', 'delete']:
            if sql.startswith(qt):
                return qt == query_type_str
        
        # Parse more complex queries
        if isinstance(query_type, str):
            query_type = QueryType[query_type.upper()]
        if not isinstance(query_type, QueryType):
            raise TechnicalException(f"Unmanage query_type of type '{Typing.get_object_class_fullname(query_type)}'")
        
        try:
            p = sql_metadata.Parser(sql)
            res = p.query_type == query_type
        except ValueError as exc:
            if "Not supported query type" in str(exc):
                res = False
            else:
                raise TechnicalException(f"Failed to define query type") from exc
        except Exception as exc:
            raise TechnicalException(f"Failed to define query type") from exc
        
        return res
    
    def set_or_update_json_key_value(self, table_name, field_name, json_key, json_value, where_data: dict=None, where_compare_data: list=None):
        """
        Set or update a json field with key=value.
        """
        raise NotImplementedError()
        
    def _get_sql_placeholder(self):
        """
        Return the character/string to use as placeholder in SQL requests.
        """
        raise NotImplementedError()

    def _get_base_exception_type(self):
        raise NotImplementedError()
    
    def __log_sql_result(self, sql_result, message="SQL result", limit_rows=10):
        if Tools.do_log(logger, logging.DEBUG):
            res_str = self.__represent_sql_result(sql_result, limit_rows=limit_rows)
            if '\n' in res_str:
                logger.debug(f"[{self.name}] {message}:\n{Tools.indent_string(4, res_str)}")
            else:
                logger.debug(f"[{self.name}] {message} => {res_str}")
    
    def __represent_sql_result(self, sql_result, limit_rows = 10):
        if isinstance(sql_result, Table):
            return sql_result.represent(limit_rows=limit_rows)
        elif isinstance(sql_result, list) and limit_rows > 0 and len(sql_result) > limit_rows:
            return str(sql_result[:limit_rows])[:-1] + f", ...({len(sql_result)-limit_rows})]"
        else:
            return str(sql_result)
    
    
    # Manage transactions
    
    def commit(self):
        self.connection.commit()
        
    def rollback(self):
        self.connection.rollback()
    
    
    # Manage tables
    
    def exist_table(self, table_name):
        raise NotImplementedError()
    
    def create_table(self, table_name, create_sql, raise_if_exist=False, do_commit=True, do_audit=False):
        if not self.exist_table(table_name):
            self.execute(create_sql, do_commit=do_commit)
            if not self.exist_table(table_name):
                raise TechnicalException(f"Failed to create table '{table_name}' with SQL request [{create_sql}]")
            
            # Audit table
            if do_audit:
                self.audit_manager.audit_table(table_name)
        elif raise_if_exist:
            raise FunctionalException(f"Table '{table_name}' already exists")
    
    def drop_table(self, table_name, raise_if_not_exist=False, do_commit=True):
        if self.exist_table(table_name):
            sql = f"drop table {table_name};"
            self.execute(sql, do_commit=do_commit)
            if self.exist_table(table_name):
                raise TechnicalException(f"Failed to drop table '{table_name}' with SQL request [{sql}]")
        elif raise_if_not_exist:
            raise FunctionalException(f"Table '{table_name}' doesn't exist")
    
    def get_table_column_names(self, table_name):
        if table_name not in self.__column_names_by_table:
            self.__column_names_by_table[table_name] = self._get_table_column_names(table_name)
        return self.__column_names_by_table[table_name]
    
    def _get_table_column_names(self, table_name):
        sql = f"select * from {table_name} limit 1"
        try:
            self.cursor.execute(sql)
        except self._get_base_exception_type() as exc:
            self.rollback()
            raise TechnicalException(f"[{self.name}] Error while executing SQL [{sql}]") from exc
        
        if self.cursor.description:
            res = [field[0] for field in self.cursor.description]
        else:
            raise TechnicalException(f"Failed to get column names of table {table_name}")
        
        return res
        
