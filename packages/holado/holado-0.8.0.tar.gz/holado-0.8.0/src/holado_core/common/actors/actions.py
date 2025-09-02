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

logger = logging.getLogger(__name__)



class BaseAction(object):
    """ Base class for actions.
    An action class defines how to process an action, and then it can be processed with different argument values.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, func_execute):
        self.__name = name
        self.__func_execute = func_execute
        
    @property
    def name(self):
        return self.__name
    
    @property
    def function_execute(self):
        return self.__func_execute
    
    @function_execute.setter
    def function_execute(self, func):
        self.__func_execute = func
    
    def execute(self, *args, **kwargs):
        """ Execute action
        @return Result or None
        """
        raise NotImplementedError
        
    
class Action(BaseAction):
    """ Action without input.
    """
    def __init__(self, name, func_execute):
        super().__init__(name, func_execute)
        
    def execute(self, *args, **kwargs):
        """ Execute action
        @return Result or None
        """
        return self.function_execute(*args, **kwargs)
    
    
class FindAction(BaseAction):
    """ Action launching Finder.find method with given find type.
    """
    def __init__(self, name, find_builder, func_execute=None, finder=None, find_type=None):
        super().__init__(f"find '{finder.element_description}'" if name is None and finder is not None else name, func_execute)
        self.__find_builder = find_builder
        
        if finder is not None:
            def f(*args, **kwargs):
                return finder.find(find_type, *args, **kwargs)
            self.function_execute = f
        
    def execute(self, container=None, candidates=None, find_context=None, find_parameters=None):
        container, candidates, find_context, find_parameters = self.__find_builder.update_find_inputs(container, candidates, find_context, find_parameters)
        return self.function_execute(container, candidates, find_context, find_parameters)
    
class FindAllAction(BaseAction):
    """ Action launching Finder.find_all method with given find type.
    """
    def __init__(self, name, find_builder, func_execute=None, finder=None, find_type=None):
        super().__init__(f"find all '{finder.element_description}'" if name is None and finder is not None else name, func_execute)
        self.__find_builder = find_builder
        
        if finder is not None:
            def f(*args, **kwargs):
                return finder.find_all(find_type, *args, **kwargs)
            self.function_execute = f
        
    def execute(self, container=None, candidates=None, find_context=None, find_parameters=None):
        container, candidates, find_context, find_parameters = self.__find_builder.update_find_inputs(container, candidates, find_context, find_parameters)
        return self.function_execute(container, candidates, find_context, find_parameters)
    
    
    
    
    