# -*- coding: utf-8 -*-

import logging
from holado_test.behave.behave import execute_steps

logger = logging.getLogger(__name__)


class TSConfigManager:

    def __init__(self):
        self.__func_path_manager = None
        
    def initialize(self, func_path_manager):
        self.__func_path_manager = func_path_manager
    
    @property
    def __path_manager(self):
        return self.__func_path_manager()
    
    def configure_system_with_default_settings(self):
        # Remove possible side effects of previous execution 
        execute_steps(u"""
            # Given ensure XXX
            """)
    




