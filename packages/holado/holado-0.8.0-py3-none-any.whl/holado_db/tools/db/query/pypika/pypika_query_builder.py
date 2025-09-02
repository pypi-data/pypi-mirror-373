
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_db.tools.db.query.base.query_builder import QueryBuilder, DBCompareOperator
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing


logger = logging.getLogger(__name__)

try:
    import pypika.functions
    from pypika.queries import Table, Query
    from pypika.terms import Parameter, Function
    with_pypika = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"PyPika is not available for QueryBuilder. Initialization failed on error: {exc}")
    with_pypika = False



class PypikaQueryBuilder(QueryBuilder):
    """
    Query builder for PyPika library.
    """
    @classmethod
    def is_available(cls):
        return with_pypika
    
    def __init__(self, name, db_client=None):
        super().__init__(name, db_client)
    
    def select(self, table_name, where_data: dict=None, where_compare_data: list=None, sql_return="*"):
        """
        Simple query & values builder of a select by filtering on given where data.
        @param where_data: dictionary of (field_name, value) for simple where clauses.
        @param where_compare_data: list of tuples (field_name, operator, value) for where clauses comparing fields with values.
        """
        table = Table(table_name)
        res = Query.from_(table)
        values = ()
        
        if sql_return == "count(*)":
            res = res.select(pypika.functions.Count("*"))
        elif isinstance(sql_return, list):
            res = res.select(*sql_return)
        else:
            res = res.select(sql_return)
        
        if where_data:
            res, values = self.where(res, values, where_data)
        if where_compare_data:
            res, values = self.where_compare(res, values, list_of_field_operator_value=where_compare_data)
        
        return res, values
    
    def insert(self, table_name, data: dict):
        """
        Simple query & values builder of an insert of given data.
        @param data: data to insert as dictionary of (field_name, value).
        """
        col_names = tuple(sorted(data.keys()))
        values = tuple((data[c] for c in col_names))
        sql_placeholder = self.db_client._get_sql_placeholder()
        
        values_placeholder = [Parameter(sql_placeholder)] * len(col_names)
        res = Query.into(table_name).columns(*col_names).insert(*values_placeholder)
        
        return res, values
    
    def update(self, table_name, data: dict, where_data: dict=None, where_compare_data: list=None):
        """
        Simple query & values builder of an update of given data.
        @param data: data to update as dictionary of (field_name, value).
        @param where_data: dictionary of (field_name, value) for simple where clauses.
        @param where_compare_data: list of tuples (field_name, operator, value) for where clauses comparing fields with values.
        """
        col_names = tuple(sorted(data.keys()))
        sql_placeholder = self.db_client._get_sql_placeholder()
        
        table = Table(table_name)
        res = Query.update(table)
        values = []
        for c in col_names:
            val = data[c]
            if isinstance(val, Function):
                res = res.set(c, val)
            else:
                res = res.set(c, Parameter(sql_placeholder))
                values.append(val)
            
        if where_data:
            res, values = self.where(res, values, where_data)
        if where_compare_data:
            res, values = self.where_compare(res, values, list_of_field_operator_value=where_compare_data)
        
        return res, values
    
    def delete(self, table_name, where_data: dict=None, where_compare_data: list=None):
        """
        Simple query & values builder of a delete by filtering on given where data.
        @param where_data: dictionary of (field_name, value) for simple where clauses.
        @param where_compare_data: list of tuples (field_name, operator, value) for where clauses comparing fields with values.
        """
        table = Table(table_name)
        res = Query.from_(table).delete()
        values = ()
        
        if where_data:
            res, values = self.where(res, values, where_data)
        if where_compare_data:
            res, values = self.where_compare(res, values, list_of_field_operator_value=where_compare_data)
            
        return res, values
    
    def where(self, query, values, where_data: dict):
        col_names = tuple(sorted(where_data.keys()))
        sql_placeholder = self.db_client._get_sql_placeholder()
        
        res = query
        table = self.__get_table(query)
        where_values = []
        for c in col_names:
            val = where_data[c]
            if val is None:
                res, where_values = self.where_is_null(res, where_values, c)
            else:
                res = res.where(getattr(table, c) == Parameter(sql_placeholder))
                where_values.append(where_data[c])
        
        if values is not None:
            values = (*values, *where_values)
        else:
            values = where_values
        return res, values
    
    def where_compare(self, query, values, *, field_name=None, operator:DBCompareOperator=None, value=None, list_of_field_operator_value=None):
        if list_of_field_operator_value is not None:
            return super().where_compare(query, values, list_of_field_operator_value=list_of_field_operator_value)
        
        # Manage operators calling other methods
        if operator == DBCompareOperator.In:
            return self.where_in(query, values, field_name, value, not_in=False)
        elif operator == DBCompareOperator.NotIn:
            return self.where_in(query, values, field_name, value, not_in=True)
        
        # Manage other operators
        table = self.__get_table(query)
        sql_placeholder = self.db_client._get_sql_placeholder()
        
        if operator == DBCompareOperator.Different:
            res = query.where(getattr(table, field_name) != Parameter(sql_placeholder))
        elif operator == DBCompareOperator.Equal:
            res = query.where(getattr(table, field_name) == Parameter(sql_placeholder))
        elif operator == DBCompareOperator.Inferior:
            res = query.where(getattr(table, field_name) < Parameter(sql_placeholder))
        elif operator == DBCompareOperator.InferiorOrEqual:
            res = query.where(getattr(table, field_name) <= Parameter(sql_placeholder))
        elif operator == DBCompareOperator.Superior:
            res = query.where(getattr(table, field_name) > Parameter(sql_placeholder))
        elif operator == DBCompareOperator.SuperiorOrEqual:
            res = query.where(getattr(table, field_name) >= Parameter(sql_placeholder))
        else:
            raise TechnicalException(f"Unmanaged compare operator {operator}")
            
        if values is not None:
            values = (*values, value)
        else:
            values = (value)
        return res, values
    
    def where_in(self, query, values, field_name, field_values, not_in=False):
        table = self.__get_table(query)
        if not_in:
            res = query.where(getattr(table, field_name).notin(field_values))
        else:
            res = query.where(getattr(table, field_name).isin(field_values))
        return res, values
    
    def where_is_null(self, query, values, field_name, is_not_null=False):
        table = self.__get_table(query)
        if is_not_null:
            res = query.where(getattr(table, field_name).notnull())
        else:
            res = query.where(getattr(table, field_name).isnull())
        return res, values
        
    def where_json_value(self, query, values, field_name, key, value, as_text_value=False):
        table = self.__get_table(query)
        sql_placeholder = self.db_client._get_sql_placeholder()
        
        if as_text_value:
            res = query.where(getattr(table, field_name).get_text_value(key) == Parameter(sql_placeholder))
        else:
            res = query.where(getattr(table, field_name).get_json_value(key) == Parameter(sql_placeholder))
        
        if values is not None:
            values = (*values, value)
        else:
            values = (value)
        return res, values
    
    def to_sql(self, query):
        if query.__module__.startswith('pypika'):
            return query.get_sql()
        else:
            raise TechnicalException(f"Unmanaged query of type {Typing.get_object_class_fullname(query)}")
    
    # def is_query_type(self, query, query_type):
    #     query_type = query_type.lower()
    #
    #     if query_type == 'insert':
    #         return query._insert_table is not None
    #     elif query_type == 'select':
    #         return len(query._selects) > 0
    #     elif query_type == 'update':
    #         return query._update_table is not None
    #     elif query_type == 'delete':
    #         return query._delete_from
    #     else:
    #         raise TechnicalException(f"Unmanaged query type '{query_type}' (managed query types: 'insert', 'select', 'update', 'delete')")
        
    def __get_table(self, query):
        if query._from is not None and len(query._from) > 0:
            return query._from[0]
        elif query._insert_table is not None:
            return query._insert_table
        elif query._update_table is not None:
            return query._update_table
        else:
            raise TechnicalException(f"Failed to extract table from query [{query}]: {Tools.represent_object(query)}")