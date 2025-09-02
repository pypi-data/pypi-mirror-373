#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_core.common.finders.tools.enums import FindType



class FindUpdater(object):
    """ Find updater
    """
    
    def __init__(self):
        self.__find_type = FindType.Undefined
        self.__context_values = {}
        self.__parameters_values = {}

    @property
    def find_type(self):
        """
        @return Specific find method type. 
        """
        return self.__find_type
    
    @find_type.setter
    def find_type(self, find_type):
        """
        Set a specific find method type.
        If previously set to Custom, the set is skipped, to preserve custom find type of Finder.
        @param find_type Find method type.
        """
        if self.find_type != FindType.Custom:
            self.__find_type = find_type

    def has_context_value(self, name):
        """
        @param name Property name 
        @return If has context property value
        """
        return name in self.__context_values
    
    def get_context_value(self, name):
        """
        @param name Property name 
        @return Context property value
        """
        return self.__context_values[name]
    
    def set_context_value(self, name, value):
        """
        @param name Property name 
        @param value Property value
        """
        self.__context_values[name] = value
    
    def set_update_root(self, update_root):
        """
        Set if root container must be updated with current container.
        @param update_root boolean
        """
        self.set_context_value("update_root_container", update_root)
    
    def has_parameters_value(self, name):
        """
        @param name Property name 
        @return If has parameters property value
        """
        return name in self.__parameters_values
    
    def get_parameters_value(self, name):
        """
        @param name Property name 
        @return Parameters property value
        """
        return self.__parameters_values[name]
    
    def set_parameters_value(self, name, value):
        """
        @param name Property name 
        @param value Property value
        """
        self.__parameters_values[name] = value
    
    
    
    
    