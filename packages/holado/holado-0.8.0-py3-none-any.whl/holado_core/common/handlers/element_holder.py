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

import abc
from holado_core.common.finders.tools.find_info import FindInfo


class ElementHolder(object):
    """ Information on an element.
    """
    __metaclass__ = abc.ABCMeta    
    
    def __init__(self, parent, instance, description=None):
        """
        @param parent Parent
        @param instance Element instance
        @param description Element description
        """
        self.__parent = parent
        self.__instance = instance
        self.__description = description
        self.__find_info = None

    @property
    def parent(self):
        """
        @return Parent
        """
        return self.__parent
    
    @property
    def element(self):
        """
        @return Element instance
        """
        return self.__instance

    @property
    def description(self):
        """
        @return Element description
        """
        return self.__description

    @description.setter
    def description(self, description):
        """
        @param description New description
        """
        self.__description = description

    @property
    def complete_description(self):
        """
        @return Element description with parent descriptions
        """
        if self.parent is not None:
            return f"{self.parent.get_complete_description()} -> {self.description}"
        else:
            return self.description

    @property
    def complete_description_and_details(self):
        """
        @return Element description with parent descriptions and details on element
        """
        return f"{self.complete_description} [{self.element}]"
    
    @property
    def find_info(self):
        """
        @return Find information
        """
        return self.__find_info

    def update_find_info(self, finder, find_context, find_parameters):
        """
        Update find information
        @param finder Finder used to find element
        @param find_context Find context
        @param find_parameters Find parameters
        """
        if self.__find_info is None:
            findInfo = FindInfo()
            findInfo.finder = finder
            findInfo.find_context = find_context
            findInfo.find_parameters = find_parameters
    
    def get_holder_for(self, element_instance, element_description):
        """
        @param element_instance New element instance.
        @param element_description New element description.
        @return Element holder for given element instance
        """
        raise NotImplementedError
    
    def get_list_holder_for(self, element_instances, element_description):
        """
        @param element_instances New element instance list.
        @param element_description New element description.
        @return Element holder for given element instance
        """
        res = []
        for element_instance in element_instances:
            res.append(self.get_holder_for(element_instance, element_description))
        return res
    
    def __eq__(self, obj:object)->bool:
        return self.__instance is obj.element or self.__instance == obj.element
    
    
    
    