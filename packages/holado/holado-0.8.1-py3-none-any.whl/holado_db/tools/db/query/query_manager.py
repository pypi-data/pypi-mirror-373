
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


logger = logging.getLogger(__name__)



class QueryManager():
    """
    Manage Query builders, agnostic to managed libraries.
    """
    
    def __init__(self, name):
        self.__name = name if name else "QueryManager"
        
        self.__builder_new_func_by_type = {}
        self.__default_builder_type = None
        
    def initialize(self):
        from holado_db.tools.db.query.pypika.pypika_query_builder import PypikaQueryBuilder
        if PypikaQueryBuilder.is_available():
            self.register_query_builder("pypika", PypikaQueryBuilder)
            self.__default_builder_type = "pypika"
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("PyPika package is not installed, this type of Query builder is not available")
        
    @property
    def name(self):
        return self.__name
        
    @property
    def default_builder_type(self):
        return self.__default_builder_type
        
    @default_builder_type.setter
    def default_builder_type(self, builder_type):
        self.__default_builder_type = builder_type
    
    def register_query_builder(self, builder_type, new_builder_func):
        self.__builder_new_func_by_type[builder_type] = new_builder_func
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Registered Query builder type '{builder_type}'")
    
    def new_default_query_builder(self, name, db_client):
        if self.__default_builder_type is None:
            raise TechnicalException(f"Default query builder type is not defined. Registered query builders: {list(self.__builder_new_func_by_type.keys())}")
        return self.new_query_builder(name, self.__default_builder_type, db_client)
    
    def new_query_builder(self, name, builder_type, db_client):
        if builder_type in self.__builder_new_func_by_type:
            try:
                res = self.__builder_new_func_by_type[builder_type](name, db_client)
            except Exception as exc:
                raise TechnicalException(f"Failed to create Query builder for builder type '{builder_type}'") from exc
        else:
            raise TechnicalException(f"Unmanaged Query builder type '{builder_type}'")
        return res
        
        
        
        