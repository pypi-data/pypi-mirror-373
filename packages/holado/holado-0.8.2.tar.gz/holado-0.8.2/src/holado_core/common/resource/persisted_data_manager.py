
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
from holado_core.common.tools.tools import Tools
import copy
from holado.common.handlers.undefined import undefined_argument

logger = logging.getLogger(__name__)



class PersistedDataManager():
    """
    Manage data persisted in a dedicated table.
    """
    def __init__(self, data_name, table_name, table_sql_create, db_name="default", do_audit=False):
        self.__data_name = data_name
        self.__table_name = table_name
        self.__table_sql_create = table_sql_create
        self.__db_name = db_name
        self.__do_audit = do_audit
        
        self.__resource_manager = None
    
    def initialize(self, resource_manager):
        self.__resource_manager = resource_manager
        
    @property
    def table_name(self):
        return self.__table_name
    
    def ensure_persistent_db_exists(self):
        if self.__resource_manager.has_data_table(self.__table_name, db_name=self.__db_name):
            if self.__resource_manager.check_data_table_schema(self.__table_name, self.__table_sql_create, db_name=self.__db_name):
                # Table already exists with the right schema
                return
            else:
                # Table already exists but with wrong schema => delete table before creating it again
                self.__resource_manager.delete_data_table(self.__table_name, db_name=self.__db_name, raise_if_not_exist=True, do_commit=True)
        
        # Create table
        # Note: method create_data_table raise an exception if it doesn't succeed to create the table
        self.__resource_manager.create_data_table(self.__table_name, self.__table_sql_create, db_name=self.__db_name, raise_if_exist=True, do_commit=True, do_audit=self.__do_audit)
    
    def has_persisted_data(self, filter_data=None, filter_compare_data=None):
        return self.__resource_manager.has_persisted_data(self.__table_name, where_data=filter_data, where_compare_data=filter_compare_data, db_name=self.__db_name)
        
    def get_persisted_datas(self, filter_data=None, filter_compare_data=None, as_generator=False):
        """
        Note: Whereas 'data' is already a plural, a 's' is added in method name to be coherent with other method names
        """
        return self.__resource_manager.get_persisted_data(self.__table_name, where_data=filter_data, where_compare_data=filter_compare_data, db_name=self.__db_name, result_as_dict_list=True, as_generator=as_generator)

    def get_persisted_data(self, filter_data=None, filter_compare_data=None):
        """
        Note: Whereas 'datum' should be the right word in method name since method returns only one datum, method is named with 'data' in its usual singular meaning for most people.
        """
        data = self.get_persisted_datas(filter_data=filter_data, filter_compare_data=filter_compare_data)
        if len(data) > 1:
            raise TechnicalException(f"Too many ({len(data)}) {self.__data_name} found for filter {filter_data}.")
        elif len(data) == 1:
            return data[0]
        else:
            return None
        
    def count_persisted_data(self, filter_data=None, filter_compare_data=None):
        return self.__resource_manager.count_persisted_data(self.__table_name, where_data=filter_data, where_compare_data=filter_compare_data, db_name=self.__db_name)

    def update_persisted_data(self, data, filter_data=None, filter_compare_data=None):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Update persisted {self.__data_name} for {filter_data} and {filter_compare_data}: {data}")
        self.__resource_manager.update_persisted_data(self.__table_name, data, where_data=filter_data, where_compare_data=filter_compare_data, db_name=self.__db_name)

    def add_persisted_data(self, data, persisted_filter_data=None):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Add persisted {self.__data_name} for {persisted_filter_data}: {data}")
        data = copy.copy(data)
        if persisted_filter_data:
            data.update(persisted_filter_data)
        self.__resource_manager.add_persisted_data(self.__table_name, data, db_name=self.__db_name)
        
    def update_or_add_persisted_data(self, persisted_filter_data, data, persisted_data=undefined_argument):
        if persisted_data is undefined_argument:
            has_persisted_data = self.has_persisted_data(persisted_filter_data)
        else:
            has_persisted_data = persisted_data is not None
        
        if has_persisted_data:
            self.update_persisted_data(data, filter_data=persisted_filter_data)
        else:
            self.add_persisted_data(data, persisted_filter_data)
        
    def delete_persisted_data(self, filter_data):
        self.__resource_manager.delete_persisted_data(self.__table_name, where_data=filter_data, db_name=self.__db_name)



