
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
import abc
from enum import Enum


logger = logging.getLogger(__name__)


class DBCompareOperator(str, Enum):
    Different = ("!=", "Equal")
    Equal = ("==", "Different")
    Inferior = ("<", "SuperiorOrEqual")
    InferiorOrEqual = ("<=", "Superior")
    Superior = (">", "InferiorOrEqual")
    SuperiorOrEqual = (">=", "Inferior")
    In = ("in", "NotIn")
    NotIn = ("not in", "In")
    
    def __new__(cls, value, not_name):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__not_name = not_name
        return obj
    
    @property
    def not_(self):
        return DBCompareOperator[self.__not_name]
    


class QueryBuilder():
    """
    Generic Query builder.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, db_client=None):
        self.__name = name
        self.__db_client = db_client
    
    @property
    def name(self):
        return self.__name
    
    @property
    def db_client(self):
        return self.__db_client
    
    @db_client.setter
    def db_client(self, client):
        self.__db_client = client
    
    def select(self, table_name, where_data: dict=None, where_compare_data: list=None, sql_return="*"):
        """
        Simple query & values builder of a select by filtering on given where data.
        @param where_data: dictionary of (field_name, value) for simple where clauses.
        @param where_compare_data: list of tuples (field_name, operator, value) for where clauses comparing fields with values.
        """
        raise NotImplementedError

    def insert(self, table_name, data: dict):
        """
        Simple query & values builder of an insert of given data.
        @param data: data to insert as dictionary of (field_name, value).
        """
        raise NotImplementedError
    
    def update(self, table_name, data: dict, where_data: dict=None, where_compare_data: list=None):
        """
        Simple query & values builder of an update of given data.
        @param data: data to update as dictionary of (field_name, value).
        @param where_data: dictionary of (field_name, value) for simple where clauses.
        @param where_compare_data: list of tuples (field_name, operator, value) for where clauses comparing fields with values.
        """
        raise NotImplementedError
    
    def delete(self, table_name, where_data: dict=None, where_compare_data: list=None):
        """
        Simple query & values builder of a delete by filtering on given where data.
        @param where_data: dictionary of (field_name, value) for simple where clauses.
        @param where_compare_data: list of tuples (field_name, operator, value) for where clauses comparing fields with values.
        """
        raise NotImplementedError
    
    def where(self, query, values, where_data: dict):
        """
        Add where clauses to current couple (query, values), and return a new couple (query, values).
        """
        raise NotImplementedError
    
    def where_compare(self, query, values, *, field_name=None, operator:DBCompareOperator=None, value=None, list_of_field_operator_value=None):
        """
        Add where clause with field value comparison to current couple (query, values), and return a new couple (query, values).
        To add multiple clauses in a single call, define list_of_field_operator_value as a list of tuples (field_name, operator, value).
        """
        if list_of_field_operator_value is not None:
            res_query, res_values = query, values
            for f_name, op, val in list_of_field_operator_value:
                res_query, res_values = self.where_compare(res_query, res_values, field_name=f_name, operator=op, value=val)
            return res_query, res_values
        else:
            raise NotImplementedError
        
    def where_in(self, query, values, field_name, field_values, not_in=False):
        """
        Add where in clause to current couple (query, values), and return a new couple (query, values).
        """
        raise NotImplementedError
        
    def where_is_null(self, query, values, field_name, is_not_null=False):
        """
        Add where is null clause to current couple (query, values), and return a new couple (query, values).
        """
        raise NotImplementedError
    
    def where_json_value(self, query, values, field_name, key, value, as_text_value=False):
        """
        Add where clause on a json field key value to current couple (query, values), and return a new couple (query, values).
        """
        raise NotImplementedError
        
    
    def to_sql(self, query):
        raise NotImplementedError
        