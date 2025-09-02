
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
import json
from holado_core.common.resource.persisted_data_manager import PersistedDataManager
from holado_python.standard_library.typing import Typing
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools
from holado.common.handlers.undefined import undefined_value, undefined_argument
from holado_python.common.tools.datetime import DateTime
from holado_db.tools.db.query.base.query_builder import DBCompareOperator
from holado.common.handlers.enums import AutoNumber

logger = logging.getLogger(__name__)


class MethodCallStatus(AutoNumber):
    Ready = ()
    Completed = ()
    Failed = ()
    Expired = ()
    

class PersistedMethodToCallManager(PersistedDataManager):
    def __init__(self, scope_name, delete_on_success=True, delete_on_fail=False, delete_on_success_after_fail=False, expiration_try_counter=10, data_name="method", table_name="method_to_call", db_name="default"):
        super().__init__(data_name=data_name, table_name=table_name, 
                         table_sql_create=self._get_default_table_sql_create(table_name), 
                         db_name=db_name)
        self.__scope_name = scope_name
        self.__delete_on_success = delete_on_success
        self.__delete_on_fail = delete_on_fail
        self.__delete_on_success_after_fail = delete_on_fail
        self.__expiration_try_counter = expiration_try_counter
    
    def initialize(self, resource_manager, expression_evaluator):
        super().initialize(resource_manager)
        self.__expression_evaluator = expression_evaluator
    
    def _get_default_table_sql_create(self, table_name):
        return f"""CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                scope_name text NOT NULL,
                function_qualname text NOT NULL,
                self_getter TEXT,
                args TEXT,
                kwargs TEXT,
                use text NOT NULL,
                use_index integer NOT NULL,
                created_at TEXT,
                changed_at TEXT,
                status TEXT,
                try_counter INTEGER,
                error TEXT,
                do_delete_on_success INTEGER,
                do_delete_on_fail INTEGER,
                do_delete_on_success_after_fail INTEGER
            )"""
    
    def add_function_to_call(self, function_qualname, args_list=None, kwargs_dict=None, use="default", use_index=0, add_if_exists=False, delete_on_success=undefined_argument, delete_on_fail=undefined_argument, delete_on_success_after_fail=undefined_argument):
        """Add a function to call.
        @param function_qualname: Qualified name of function
        @param args_list: List of function args (default: None)
        @param kwargs_dict: Dict of function kwargs (default: None)
        @param use: Define persistent usage. It usually corresponds to a specific scope.
        @param use_index: use index, useable to order the functions to call. By default all are 0. If set to None, it is automatically set to max(use_index)+1.
        @param delete_on_success: If True, delete function after its success
        @param delete_on_fail: If True, delete function after its fail
        @param delete_on_success_after_fail: If True, delete function after its success even if it has previously failed
        """
        self.add_method_to_call(function_qualname, None, args_list, kwargs_dict, use, use_index, add_if_exists, delete_on_success, delete_on_fail, delete_on_success_after_fail)
    
    def add_method_to_call(self, function_qualname, self_getter_eval_str, args_list=None, kwargs_dict=None, use="default", use_index=0, add_if_exists=False, delete_on_success=undefined_argument, delete_on_fail=undefined_argument, delete_on_success_after_fail=undefined_argument):
        """Add a method to call.
        @param function_qualname: Qualified name of function
        @param self_getter_eval_str: String to eval in order to get the self instance to use when calling method 
        @param args_list: List of function args (default: None)
        @param kwargs_dict: Dict of function kwargs (default: None)
        @param use: Define persistent usage. It usually corresponds to a specific scope.
        @param use_index: Use index, useable to order the functions to call. By default all are 0. If set to None, it is automatically set to max(use_index)+1.
        @param add_if_exists: Add if method already exists (default: False)
        @param delete_on_success: If True, delete method after its success
        @param delete_on_fail: If True, delete method after its fail
        @param delete_on_success_after_fail: If True, delete method after its success even if it has previously failed
        """
        # Define persisted data that can define if method is already persisted
        data = {
            'scope_name': self.__scope_name,
            'function_qualname': function_qualname,
            'self_getter': self_getter_eval_str,
            'use': use,
            }
        if args_list is not None:
            data['args'] = json.dumps(args_list)
        if kwargs_dict is not None:
            data['kwargs'] = json.dumps(kwargs_dict)
        
        # Return if data is already persisted and add_if_exists==True
        filter_compare_data = [('status', DBCompareOperator.In, [MethodCallStatus.Ready.name, MethodCallStatus.Failed.name])]
        if not add_if_exists and self.has_persisted_data(filter_data=data, filter_compare_data=filter_compare_data):
            return
        
        # Persist data
        if use_index is None:
            use_index = self.__get_use_next_index(use)
        now_str = DateTime.datetime_2_str(DateTime.utcnow())
        data.update({
            'use_index': use_index,
            'created_at': now_str,
            'changed_at': now_str,
            'status': MethodCallStatus.Ready.name,
            'try_counter': 0,
            'do_delete_on_success': self.__get_db_on_delete_after_when_add_method(delete_on_success, self.__delete_on_success),
            'do_delete_on_fail': self.__get_db_on_delete_after_when_add_method(delete_on_fail, self.__delete_on_fail),
            'do_delete_on_success_after_fail': self.__get_db_on_delete_after_when_add_method(delete_on_success_after_fail, self.__delete_on_success_after_fail)
            })
        
        self.add_persisted_data(data)
    
    def get_number_of_functions_and_method_to_call(self, use=undefined_argument):
        methods_data = self.__get_functions_and_methods_to_call(use=use)
        return len(methods_data)
    
    def __get_db_on_delete_after_when_add_method(self, method_delete, default_delete):
        if method_delete is not undefined_argument:
            if method_delete is undefined_value:
                return -1
            else:
                return method_delete
        else:
            if default_delete is undefined_value:
                return -1
            else:
                return default_delete
        
    def __get_do_delete_after_call(self, db_delete, default_delete):
        if db_delete != -1:
            return db_delete
        else:
            if default_delete is undefined_value:
                return False
            else:
                return default_delete
        
    def __get_use_next_index(self, use):
        datas = self.get_persisted_datas({'scope_name':self.__scope_name, 'use':use})
        if datas:
            return max(map(lambda x:x['use_index'], datas)) + 1
        else:
            return 0
    
    def __get_functions_and_methods_to_call(self, use=undefined_argument, use_index=None):
        filter_data = {'scope_name':self.__scope_name}
        if use is not undefined_argument:
            filter_data['use'] = use
            if use_index is not None:
                filter_data['use_index'] = use_index
        filter_compare_data = [('status', DBCompareOperator.In, [MethodCallStatus.Ready.name, MethodCallStatus.Failed.name])]
        return self.get_persisted_datas(filter_data, filter_compare_data=filter_compare_data)
    
    def call_functions_and_methods(self, use="default", use_index=None):
        """Call methods of given use
        @param use: Define persistent usage. It usually corresponds to a specific scope.
        @param use_index: If defined, call only functions and methods of given index.
        @param delete_after_call: Define if function or method is deleted after call from persisted data.
        """
        # Get functions and methods to call
        methods_data = self.__get_functions_and_methods_to_call(use=use)
        
        # Call methods
        if methods_data:
            for meth_index, meth_data in enumerate(methods_data):
                status, do_delete, error = None, None, ''
                try:
                    self._call_function_or_method(meth_data)
                except Exception as exc:
                    error = Tools.represent_exception(exc, indent=8)
                    msg_list = [f"Error while calling following method (use: '{use}' ; use index: {use_index} ; method index: {meth_index}):"]
                    msg_list.append(Tools.represent_object(meth_data, 8))
                    msg_list.append("    Error:")
                    msg_list.append(error)
                    msg_list.append("  => Continue to process persisted methods")
                    msg_list.append("     WARNING: this method is removed from persisted methods to avoid recursive and blocking errors")
                    logger.error("\n".join(msg_list))
                    status = MethodCallStatus.Failed
                    do_delete = self.__get_do_delete_after_call(meth_data['do_delete_on_fail'], self.__delete_on_fail)
                else:
                    status = MethodCallStatus.Completed
                    if meth_data['try_counter'] == 0:
                        do_delete = self.__get_do_delete_after_call(meth_data['do_delete_on_success'], self.__delete_on_success)
                    else:
                        do_delete = self.__get_do_delete_after_call(meth_data['do_delete_on_success_after_fail'], self.__delete_on_success_after_fail)
                
                self.__update_persisted_data_after_call(do_delete, meth_data, status, error)
                
    def __update_persisted_data_after_call(self, do_delete, meth_data, status, error):
        if do_delete:
            self.__delete_function_or_method(meth_data)
        else:
            self.__update_function_or_method_status(meth_data, status, error)
    
    def __delete_function_or_method(self, function_or_method_data):
        filter_data = {'id':function_or_method_data['id']}
        self.delete_persisted_data(filter_data)
    
    def __update_function_or_method_status(self, function_or_method_data, status, error):
        filter_data = {'id':function_or_method_data['id']}
        try_counter = function_or_method_data['try_counter'] + 1
        if try_counter >= self.__expiration_try_counter and status == MethodCallStatus.Failed:
            status = MethodCallStatus.Expired
        
        data = {
            'status': status.name,
            'try_counter': try_counter,
            'error': error,
            'changed_at': DateTime.datetime_2_str(DateTime.utcnow()),
            }
        self.update_persisted_data(data, filter_data=filter_data)
    
    def _call_function_or_method(self, function_or_method_data):
        _, func = self.__expression_evaluator.evaluate_python_expression(function_or_method_data['function_qualname'])
        if not Typing.is_function(func):
            raise TechnicalException(f"Failed to evaluate python expression '{function_or_method_data['function_qualname']}' as a function (obtained: {func} [type: {Typing.get_object_class_fullname(func)}] ; function data: {function_or_method_data})")
        
        func_self = None
        if function_or_method_data['self_getter'] is not None:
            _, func_self = self.__expression_evaluator.evaluate_python_expression(function_or_method_data['self_getter'])
        
        if function_or_method_data['args'] is not None:
            args = json.loads(function_or_method_data['args'])
        else:
            args = []
        if function_or_method_data['kwargs'] is not None:
            kwargs = json.loads(function_or_method_data['kwargs'])
        else:
            kwargs = {}
        
        if func_self is not None:
            func(func_self, *args, **kwargs)
        else:
            func(*args, **kwargs)
        
    
