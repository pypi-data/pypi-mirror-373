
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
import abc

logger = logging.getLogger(__name__)


class GetOrCreateObject(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        self.__name = name
        
    @property
    def name(self):
        return self.__name
    
    def has(self, name):
        return self._goc_has_object(name)
    
    def get(self, name):
        if self.has(name):
            return self._goc_get_object(name)
        else:
            return None
    
    def create(self, name, *args, **kwargs):
        res = self._goc_new_object(name, *args, **kwargs)
        self._goc_set_object(name, res)
        return res
    
    def get_or_create(self, name, *args, **kwargs):
        if self.has(name):
            return self.get(name)
        else:
            return self.create(name, *args, **kwargs)

    def _goc_has_object(self, name):
        raise NotImplementedError()

    def _goc_get_object(self, name):
        raise NotImplementedError()

    def _goc_new_object(self, name, *args, **kwargs):
        raise NotImplementedError()

    def _goc_set_object(self, name, obj):
        raise NotImplementedError()


class GetOrCreateVariable(GetOrCreateObject):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name):
        super().__init__(name)
        self.__func_variable_manager = None
        
    def initialize(self, func_variable_manager):
        self.__func_variable_manager = func_variable_manager
        
    @property
    def __variable_manager(self):
        return self.__func_variable_manager()
        
    def _goc_has_object(self, name):
        return self.__variable_manager.exists_variable(name)
        
    def _goc_get_object(self, name):
        return self.__variable_manager.get_variable_value(name)

    def _goc_set_object(self, name, obj):
        self.__variable_manager.register_variable(name, obj)
        

class GetOrCreateVariableObject(GetOrCreateVariable):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name):
        super().__init__(name)
        
    def initialize(self, func_variable_manager):
        super().initialize(func_variable_manager)
        
    def get(self, name):
        varname = self._goc_get_varname(name)
        return varname, super().get(name)
    
    def create(self, name, *args, **kwargs):
        varname = self._goc_get_varname(name)
        return varname, super().create(name, *args, **kwargs)
    
    def _goc_has_object(self, name):
        varname = self._goc_get_varname(name)
        return super()._goc_has_object(varname)
        
    def _goc_get_object(self, name):
        varname = self._goc_get_varname(name)
        return super()._goc_get_object(varname)

    def _goc_set_object(self, name, obj):
        varname = self._goc_get_varname(name)
        super()._goc_set_object(varname, obj)
        
    def _goc_get_varname(self, name):
        return f"GOC_{self.name.upper()}_{str(name).replace(' ','').upper()}"
        
        
        
