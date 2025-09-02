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


class InspectContext(object):
    """ Base inspect context
    In usual use cases, the appropriate sub-class should be instantiated.
    """
    
    __instance_default = None
    
    def __init__(self, find_type=None, inspect_context=None):
        if find_type is not None:
            self.__find_type = find_type
        elif inspect_context is not None:
            self.__find_type = inspect_context.find_type
        else:
            self.__find_type = None
    
    @property
    def find_type(self):
        """
        @return Find type
        """
        return self.__find_type
    
    def with_find_type(self, find_type):
        """
        Note: if wanted find type is the same, self instance is returned, else a new one is returned
        @param find_type Find type
        @return Same context but with given find type
        """
        if find_type == self.find_type:
            return self
        else:
            res = copy.deepcopy(self)
            res.find_type = find_type
            return res
    
    @staticmethod
    def default(find_type=None):
        """
        @return Default inspect context
        """
        if InspectContext.__instance_default is None:
            InspectContext.__instance_default = InspectContext()
        res = InspectContext.__instance_default
        
        if find_type is not None:
            res = res.with_find_type(find_type)
        
        return res
    
    
    
    
    
    