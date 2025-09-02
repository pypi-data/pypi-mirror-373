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
from holado.common.handlers.object import Object

logger = logging.getLogger(__name__)


class Undefined(Object):
    def __init__(self, name, undefined_value=0):
        super().__init__(name)
        self.__value = undefined_value
    
    def __str__(self)->str:
        if self.name is not None:
            return f"<{self.name}>"
        else:
            return super().__str__()

def is_undefined(obj):
    return isinstance(obj, Undefined)


# Define specific undefined objects

undefined_argument = Undefined("Undefined argument", 0)
undefined_value = Undefined("Undefined value", 1)
not_applicable = Undefined("Not Applicable", 2)
to_be_defined = Undefined("To be defined", 3)               # Usage: initial variable value defining it is to be defined. It is useful when undefined_value can be a possible value.



# Define specific default values
# Note: Real value is defined by methods managing these values as argument.

default_value = Undefined("Default value", 10)
default_context = Undefined("Default context", 11)      # Example of real value: for ThreadsManager it means "current ScenarioContext" if a scenario context exists else "SessionContext".


# Define symbolic values

any_value = Undefined("Any value", 20)
not_defined_value = Undefined("Not defined value", 21)


