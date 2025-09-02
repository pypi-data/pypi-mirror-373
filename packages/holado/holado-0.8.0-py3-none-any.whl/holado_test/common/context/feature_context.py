
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
from datetime import datetime
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_scripting.common.tools.variable_manager import VariableManager
from holado.common.context.session_context import SessionContext

class FeatureContext(Context):
    def __init__(self, feature):
        super().__init__("Feature")
        
        self.__feature = feature
        
        self.__start_date = datetime.now()
        self.__end_date = None
        self.__scenarios = []
    
    def __str__(self):
        return f"{{FeatureContext({id(self)}):{self.feature.name}}}"
     
    @property
    def feature(self):
        return self.__feature
    
    @property
    def start_datetime(self):
        return self.__start_date
    
    @property
    def end_datetime(self):
        return self.__end_date
    
    @property
    def duration(self):
        if self.__end_date is not None:
            return (self.__end_date - self.__start_date).total_seconds()
        else:
            return None
    
    @property
    def has_scenario(self):
        return len(self.__scenarios) > 0
    
    @property
    def current_scenario(self):
        if not self.has_scenario:
            raise TechnicalException("Feature has no scenario")
        return self.__scenarios[-1]
    
    def add_scenario(self, scenario_context):
        self.__scenarios.append(scenario_context)
    
    def end(self):
        self.__end_date = datetime.now()
        
    def has_variable_manager(self):
        return self.has_object("variable_manager")
        
    def get_variable_manager(self) -> VariableManager:
        if not self.has_variable_manager():
            manager = VariableManager(SessionContext.instance().multitask_manager.get_thread_context().get_variable_manager())
            self.set_object("variable_manager", manager)
            manager.initialize(SessionContext.instance().dynamic_text_manager, SessionContext.instance().unique_value_manager)
        return self.get_object("variable_manager")
    
        
