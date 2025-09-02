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

from holado_core.common.exceptions.technical_exception import TechnicalException


class FindBuilder(object):
    """ Find builder
    """
    
    def __init__(self):
        self.__default_context = None
        self.__default_parameters = None
    
    @property
    def default_context(self):
        """
        Get or create default context.
        This method is usually used to build the default context.
        @return Default find context
        """
        if self.__default_context is None:
            from holado_core.common.finders.tools.find_context import FindContext
            self.__default_context = FindContext.default()
        return self.__default_context
    
    def context(self, find_context=None, find_type=None, container=None, containers=None):
        """
        @param find_context Find context to update
        @param find_type Find type
        @param container Container
        @param containers Containers
        @return Updated find context
        """
        if find_context is None:
            find_context = self.default_context
            
        if container is not None:
            from holado_core.common.finders.tools.find_context import ContainerFindContext
            res = ContainerFindContext(find_context=find_context).with_container(container)
        elif containers is not None:
            from holado_core.common.finders.tools.find_context import ListContainersFindContext
            res = ListContainersFindContext(find_context=find_context).with_containers(containers)
        else:
            res = find_context
            
        if find_type is not None:
            res = res.with_find_type(find_type)
        
        return res
    

    @property
    def default_parameters(self):
        """
        Get or create default parameters.
        This method is usually used to build the default parameters.
        @return Default find parameters
        """
        if self.__default_parameters is None:
            from holado_core.common.finders.tools.find_parameters import FindParameters
            self.__default_parameters = FindParameters.default()
        return self.__default_parameters
    
    def parameters(self, find_parameters=None, raise_exception=None):
        """
        @param raise_exception Whether raise exceptions or not
        @return Find parameters
        """
        if find_parameters is None:
            res = self.default_parameters
        else:
            res = find_parameters
            
        if raise_exception is not None:
            res = res.with_raise(raise_exception)
            
        return res
    
    def parameters_with_raise(self):
        """
        @return Default find parameters with raises
        """
        return self.parameters(True)
    
    def parameters_without_raise(self):
        """
        @return Default find parameters without any raise
        """
        return self.parameters(False)
    
    def update_find_inputs(self, container, candidates, find_context, find_parameters):
        if container is None and candidates is None:
            from holado_core.common.finders.tools.find_context import ContainerFindContext, ListContainersFindContext
            if isinstance(find_context, ContainerFindContext) and find_context.container is not None:
                container = find_context.container
            elif isinstance(find_context, ListContainersFindContext) and find_context.containers is not None:
                candidates = find_context.containers
            else:
                raise TechnicalException("No container is defined")
                
        if find_context is None:
            find_context = self.context()
        if find_parameters is None:
            find_parameters = self.parameters()
        
        return container, candidates, find_context, find_parameters

    