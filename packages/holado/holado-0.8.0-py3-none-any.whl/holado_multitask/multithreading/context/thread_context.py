
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

from builtins import super
from holado.common.context.context import Context
import logging
from holado_scripting.common.tools.variable_manager import VariableManager
from holado.common.context.session_context import SessionContext

logger = logging.getLogger(__name__)


class ThreadContext(Context):
    def __init__(self, name, unique_name):
        super().__init__(f"Thread[{name};{unique_name}]")
        
        self.__thread_uid = None
        self.__thread_name = name
        self.__thread_unique_name = unique_name
    
    def __str__(self):
        return f"{{ThreadContext({id(self)}):{self.__thread_uid}:{self.__thread_name}:{self.__thread_unique_name}}}"

    @property
    def thread_name(self):
        return self.__thread_name
    
    @property
    def thread_unique_name(self):
        return self.__thread_unique_name
    
    @property
    def thread_uid(self):
        return self.__thread_uid
    
    @thread_uid.setter
    def thread_uid(self, uid):
        self.__thread_uid = uid
    
    
    def has_variable_manager(self):
        return self.has_object("variable_manager")
        
    def get_variable_manager(self) -> VariableManager:
        if not self.has_variable_manager():
            parent_thread_context = SessionContext.instance().multitask_manager.get_parent_thread_context(uid=self.thread_uid)
            if parent_thread_context is not None:
                var_man = parent_thread_context.get_variable_manager()
            else:
                var_man = SessionContext.instance().variable_manager
                
            manager = VariableManager(var_man)
            self.set_object("variable_manager", manager)
            manager.initialize(SessionContext.instance().dynamic_text_manager, SessionContext.instance().unique_value_manager)
        return self.get_object("variable_manager")
    
    
    ### Manage feature context
    
    def has_feature_context(self):
        return self.has_object("feature_context")
    
    def get_feature_context(self):
        return self.get_object("feature_context")
    
    def set_feature_context(self, feature_context):
        return self.set_object("feature_context", feature_context)
    
    def delete_feature_context(self):
        self.get_feature_context().delete_object()
        self.remove_object("feature_context")
    
    
    