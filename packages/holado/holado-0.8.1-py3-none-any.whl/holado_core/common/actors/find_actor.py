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

import logging
import abc
from holado_core.common.finders.tools.find_builder import FindBuilder
from holado_core.common.actors.actions import FindAllAction, FindAction, Action
from holado_core.common.actors.actor import Actor

logger = logging.getLogger(__name__)



class FindActor(Actor):
    """ Base class for find actor.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        super().__init__(module_name)
        self.__find_builder = None
        
    def initialize(self):
        """
        Initialize actor
        """
        self.__find_builder = self.default_find_builder
    
    @property
    def default_find_builder(self):
        """
        @return New default find builder for this inspector
        """
        return FindBuilder()
    
    @property
    def find_builder(self):
        """
        @return Find builder defined for this inspector
        """
        return self.__find_builder
    
    def act_find(self, finder, find_type, redo=True):
        """
        @param finder Finder
        @param find_type Find type
        @return Action that find element with finder
        """
        res = FindAction(None, self.find_builder, finder=finder, find_type=find_type)
        return self._act_with_redo(res) if redo else res
    
    def act_find_all(self, finder, find_type, redo=True):
        """
        @param finder Finder
        @param find_type Find type
        @return Action that find all elements with finder
        """
        res = FindAllAction(None, self.find_builder, finder=finder, find_type=find_type)
        return self._act_with_redo(res) if redo else res
    
    def act_number_of_occurrences(self, finder=None, find_type=None):
        """
        @return Number of occurrences
        """
        if finder is None:
            def func(elements):
                return len(elements)
            return Action("number of occurences", func)
        else:
            return self.act_then(
                self.act_find_all(finder, find_type),
                self.act_number_of_occurrences() )
    
    def _act_with_redo(self, action):
        """
        Manage redo for given action
        @param action Action
        @return New action managing redo
        """
        if isinstance(action, FindAction) or isinstance(action, FindAllAction):
            def func(container, candidates, find_context, find_parameters):
                if find_parameters.redo:
                    new_parameters = find_parameters.with_redo(False)
                    redo = self._get_redo(action, container, candidates, find_context, new_parameters)
                    redo.ignore_all(find_parameters.redo_ignored_exceptions)
                    return redo.execute()
                else:
                    return action.execute(container, candidates, find_context, find_parameters)
                
            return type(action)(f"{action.name} with redo", self.find_builder, func)
        else:
            return super()._act_with_redo(action)
    
    
    
    
    