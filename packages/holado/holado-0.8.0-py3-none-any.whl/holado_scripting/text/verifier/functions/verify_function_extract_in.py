
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

from holado_scripting.text.base.base_verify_function import BaseVerifyFunction
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException


class VerifyFunctionExtractIn(BaseVerifyFunction):

    def __init__(self, var_manager):
        self.__variable_manager = var_manager
        
    def apply(self, value_to_check, args, raise_exception):
        # Verify arguments
        if not isinstance(args, list):
            raise TechnicalException("Arguments must be a list")
        if len(args) != 1:
            raise FunctionalException("Function 'ExtractIn' requires one argument.")

        var_name = args[0]
        self.__variable_manager.register_variable(var_name, value_to_check)
        return True
    
    
