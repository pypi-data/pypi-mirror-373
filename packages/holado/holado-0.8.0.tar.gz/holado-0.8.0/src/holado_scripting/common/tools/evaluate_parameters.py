#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import copy
from holado.common.handlers.undefined import undefined_value


class EvaluateParameters(object):
    """ Evaluate parameters
    """
    
    __instance_nothing = None
    __instance_default = None
    __instance_default_without_raise = None
    
    def __init__(self, do_interpret=True, do_eval_variable=True, do_eval=True, \
                 raise_on_interpret_error=True, raise_on_variable_eval_error=True, raise_on_eval_error=True,
                 do_interpret_recursively=False, do_eval_variable_recursively=False,
                 result_type=undefined_value):
        """
        Constructor
        @param  
        """
        self.do_interpret = do_interpret
        self.do_interpret_recursively = do_interpret_recursively
        self.do_eval_variable = do_eval_variable
        self.do_eval_variable_recursively = do_eval_variable_recursively
        self.do_eval = do_eval
        self.raise_on_interpret_error = raise_on_interpret_error
        self.raise_on_variable_eval_error = raise_on_variable_eval_error
        self.raise_on_eval_error = raise_on_eval_error
        self.result_type = result_type
        self.result_is_str = result_type is str
    
    def __str__(self)->str:
        return f"{{interpret:({self.do_interpret},recursive:{self.do_interpret_recursively},raise:{self.raise_on_interpret_error}) ; eval variable:({self.do_eval_variable},recursive:{self.do_eval_variable_recursively},raise:{self.raise_on_variable_eval_error}) ; eval:({self.do_eval},raise:{self.raise_on_eval_error}) ; result type:{self.result_type}}}"
    
    def with_interpret(self, do_interpret):
        """
        Note: if wanted do_interpret is the same, self instance is returned, else a new one is returned
        @param do_interpret Wanted do_interpret
        @return Same parameters but with given do_interpret
        """
        if do_interpret == self.do_interpret:
            return self
        else:
            res = copy.deepcopy(self)
            res.do_interpret = do_interpret
            return res
        
    def with_interpret_recursively(self, do_interpret_recursively):
        """
        Note: if wanted do_interpret_recursively is the same, self instance is returned, else a new one is returned
        @param do_interpret Wanted do_interpret_recursively
        @return Same parameters but with given do_interpret_recursively
        """
        if do_interpret_recursively == self.do_interpret_recursively:
            return self
        else:
            res = copy.deepcopy(self)
            res.do_interpret_recursively = do_interpret_recursively
            return res
        
    def with_eval_variable(self, do_eval_variable):
        """
        Note: if wanted do_eval_variable is the same, self instance is returned, else a new one is returned
        @param do_eval_variable Wanted do_eval_variable
        @return Same parameters but with given do_eval_variable
        """
        if do_eval_variable == self.do_eval_variable:
            return self
        else:
            res = copy.deepcopy(self)
            res.do_eval_variable = do_eval_variable
            return res
        
    def with_eval_variable_recursively(self, do_eval_variable_recursively):
        """
        Note: if wanted do_eval_variable_recursively is the same, self instance is returned, else a new one is returned
        @param do_eval_variable_recursively Wanted do_eval_variable_recursively
        @return Same parameters but with given do_eval_variable_recursively
        """
        if do_eval_variable_recursively == self.do_eval_variable_recursively:
            return self
        else:
            res = copy.deepcopy(self)
            res.do_eval_variable_recursively = do_eval_variable_recursively
            return res
        
    def with_eval(self, do_eval):
        """
        Note: if wanted do_eval is the same, self instance is returned, else a new one is returned
        @param do_eval Wanted do_eval
        @return Same parameters but with given do_eval
        """
        if do_eval == self.do_eval:
            return self
        else:
            res = copy.deepcopy(self)
            res.do_eval = do_eval
            return res
        
    def with_raise(self, raise_exception=True):
        """
        Note: if raise booleans are same, self instance is returned, else a new one is returned
        @param raise_exception Whether raise exceptions or not
        @return Same parameters but with raise
        """
        return self.with_raise_on_interpret_error(raise_exception) \
            .with_raise_on_variable_eval_error(raise_exception) \
            .with_raise_on_eval_error(raise_exception)
        
    def with_raise_on_interpret_error(self, raise_on_interpret_error=True):
        """
        Note: if raise_on_interpret_error booleans are same, self instance is returned, else a new one is returned
        @param raise_on_interpret_error Whether raise exceptions or not on interpret error
        @return Same parameters but with raise_on_interpret_error
        """
        if self.raise_on_interpret_error == raise_on_interpret_error:
            return self
        else:
            res = copy.deepcopy(self)
            res.raise_on_interpret_error = raise_on_interpret_error
            return res
        
    def with_raise_on_variable_eval_error(self, raise_on_variable_eval_error=True):
        """
        Note: if raise_on_variable_eval_error booleans are same, self instance is returned, else a new one is returned
        @param raise_on_variable_eval_error Whether raise exceptions or not on variable_eval error
        @return Same parameters but with raise_on_variable_eval_error
        """
        if self.raise_on_variable_eval_error == raise_on_variable_eval_error:
            return self
        else:
            res = copy.deepcopy(self)
            res.raise_on_variable_eval_error = raise_on_variable_eval_error
            return res
        
    def with_raise_on_eval_error(self, raise_on_eval_error=True):
        """
        Note: if raise_on_eval_error booleans are same, self instance is returned, else a new one is returned
        @param raise_on_eval_error Whether raise exceptions or not on eval error
        @return Same parameters but with raise_on_eval_error
        """
        if self.raise_on_eval_error == raise_on_eval_error:
            return self
        else:
            res = copy.deepcopy(self)
            res.raise_on_eval_error = raise_on_eval_error
            return res
        
    def without_raise(self):
        """
        Note: if raise booleans are already False, self instance is returned, else a new one is returned
        @return Same parameters but without raise
        """
        return self.with_raise(False)
        
    def with_result_type(self, result_type=undefined_value):
        """
        Note: if result_type types are same, self instance is returned, else a new one is returned
        @param result_type Evaluation result type
        @return Same parameters but with result_type
        """
        if self.result_type == result_type:
            return self
        else:
            res = copy.deepcopy(self)
            res.result_type = result_type
            res.result_is_str = result_type is str
            return res
    
    @staticmethod
    def default(raise_exception=True):
        """
        @param raise_exception Whether raise exceptions or not
        @return Default evaluate parameters with given raiseability
        """
        if raise_exception:
            return EvaluateParameters.default_with_raise()
        else:
            return EvaluateParameters.default_without_raise()
    
    @staticmethod
    def default_with_raise():
        """
        @return Default evaluate parameters with raises
        """
        if EvaluateParameters.__instance_default is None:
            EvaluateParameters.__instance_default = EvaluateParameters(True, True, True, True, True, True, undefined_value)
        return EvaluateParameters.__instance_default
    
    @staticmethod
    def default_without_raise():
        """
        @return Default evaluate parameters without any raise
        """
        if EvaluateParameters.__instance_default_without_raise is None:
            EvaluateParameters.__instance_default_without_raise = EvaluateParameters(True, True, True, False, False, False, undefined_value)
        return EvaluateParameters.__instance_default_without_raise
    
    @staticmethod
    def default_without_eval(raise_exception=True):
        """
        @param raise_exception Whether raise exceptions or not
        @return Default evaluate parameters with given raiseability and without eval
        """
        return EvaluateParameters.default(raise_exception).with_eval(False)
    
    @staticmethod
    def nothing():
        """
        @return Default evaluate parameters without any raise
        """
        if EvaluateParameters.__instance_nothing is None:
            EvaluateParameters.__instance_nothing = EvaluateParameters(False, False, False, False, False, False, undefined_value)
        return EvaluateParameters.__instance_nothing


