
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
import logging
from holado_test.behave.behave_function import BehaveFunction
from typing import Dict, Union
from holado_core.common.tools.tools import Tools
from holado_core.common.actors.actions import Action
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.typing import Typing
from holado.common.handlers.undefined import not_applicable

logger = logging.getLogger(__name__)


class ActionInfo(object):
    def __init__(self, uid:str, action:str, params:Dict[str, Union[str,int]], static_params:Dict[str, Union[str,int]], index:int):
        self.uid = uid
        self.action = action
        self.params = params
        self.static_params = static_params
        self.index = index
        
    def __str__(self)->str:
        return f"{Typing.get_object_class_fullname(self)}({self.__dict__})"

class BehaveActionInfo(ActionInfo):
    def __init__(self, uid:str, action:str, params:Dict[str, Union[str,int]], static_params:Dict[str, Union[str,int]], index:int, behave_args:str):
        super().__init__(uid, action, params, static_params, index)
        self.behave_args = behave_args


class FeaturesBehaveAction(Action):
    '''Behave action running features.
    The features to execute are defined by parameter behave_args.
    
    It is possible to pass arguments to the features, by writing the scenarios with expected variables.
    At execution, given parameter 'variable_values' must define expected variable values. 
    '''
    
    def __init__(self, behave_args, variable_manager):
        # Method execute is overriden and doesn't use a method reference, thus parameter func_execute is None
        super().__init__("behave", None)
        self.__behave_function = BehaveFunction(behave_args)
        self.__variable_manager = variable_manager
    
    def execute(self, variable_values=None):
        """Execute features with given variable values.
        """
        if variable_values is not None and not isinstance(variable_values, dict):
            raise TechnicalException(f"Parameter 'variable_values' must be a dict")
        
        if variable_values:
            for key, value in variable_values.items():
                self.__variable_manager.register_variable(key, value)
        
        try:
            return self.__behave_function.run()
        except Exception as exc:
            raise TechnicalException(f"Execution of features with behave failed: {exc}") from exc
    
    
class BehaveActionRunner():
    '''
    Behave action runner.
    Return True if succeeded
    '''
    
    def __init__(self, action_info, variable_manager):
        self.__action = FeaturesBehaveAction(action_info.behave_args, variable_manager)
        self.__action_info = action_info
    
    def __compute_variable_values(self):
        res = {}
        self.__add_variable_values(res, self.__action_info.static_params)
        self.__add_variable_values(res, self.__action_info.params)
        return res
    
    def __add_variable_values(self, res, params):
        if params:
            if isinstance(params, dict):
                for key, value in params.items():
                    self.__add_variable_value(res, key, value)
            elif isinstance(params, list):
                for key, value in params:
                    self.__add_variable_value(res, key, value)
            else:
                raise TechnicalException(f"Unexpected params type '{type(params)}'")
    
    def __add_variable_value(self, res, var_name, value):
        if var_name == 'STATUS':
            return
        if value is not_applicable:
            res[var_name] = 'N/A'
        else:
            res[var_name] = value
    
    def run(self):
        logger.info(f"Processing action '{self.__action_info.action}' of index {self.__action_info.index}: {self.__action_info.params}")
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Running behave with arguments '{self.__action_info.behave_args}' on action of index {self.__action_info.index}: {self.__action_info.params}")
        
        variable_values = self.__compute_variable_values()
        
        logger.info(f"Launching behave with arguments: {self.__action_info.behave_args}")
        if Tools.do_log(logger, logging.DEBUG):
            if variable_values:
                logger.debug(f"   and with variables:\n{Tools.represent_object(variable_values, 8)}")
        res = self.__action.execute(variable_values)
        logger.info(f"behave finished with result: {res}")
        
        if res:
            logger.print(f"Success of action '{self.__action_info.action}' on action of index {self.__action_info.index}: {self.__action_info.params}")
        else:
            logger.error(f"Action '{self.__action_info.action}' failed on action of index {self.__action_info.index}: {self.__action_info.params}")
                
        return res
    
    
