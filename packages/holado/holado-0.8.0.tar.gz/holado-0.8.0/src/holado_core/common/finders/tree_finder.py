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
from holado_core.common.finders.element_finder import ElementFinder
from holado_core.common.finders.tools.find_context import ContainerFindContext
from holado_core.common.finders.tools.find_parameters import FindParameters
from holado_core.common.finders.tools.enums import FindType

logger = logging.getLogger(__name__)


class TreeFinder(ElementFinder):
    """ Generic finder in a tree of elements.
    """
    
    def __init__(self, description=None):
        super().__init__(description)
    
    def find_in_children(self, container=None, candidates=None, find_context=None, find_parameters=None):
        """
        @param container Container from which make search.
        @param candidates Candidate containers.
        @param find_context Find context
        @param find_parameters Find parameters
        @return Element found in children.
        """
        return self.find(FindType.InChildren, container, candidates, find_context, find_parameters)
    
    def find_all_in_children(self, container=None, candidates=None, find_context=None, find_parameters=None):
        """
        @param container Container from which make search.
        @param candidates Candidate containers.
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        return self.find_all(FindType.InChildren, container, candidates, find_context, find_parameters)
    
    def find_in_parents(self, container=None, candidates=None, find_context=None, find_parameters=None):
        """
        @param container Container from which make search.
        @param candidates Candidate containers.
        @param find_context Find context
        @param find_parameters Find parameters
        @return Element found in parents.
        """
        return self.find(FindType.InParents, container, candidates, find_context, find_parameters)
    
    def find_all_in_parents(self, container=None, candidates=None, find_context=None, find_parameters=None):
        """
        @param container Container from which make search.
        @param candidates Candidate containers.
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        return self.find_all(FindType.InParents, container, candidates, find_context, find_parameters)
    
    def _find_all_container(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        if find_context.find_type == FindType.InChildren:
            return self._find_all_in_children(find_context, find_parameters)
        elif find_context.find_type == FindType.InParents:
            return self._find_all_in_parents(find_context, find_parameters)
        else:
            return super()._find_all_container(find_context, find_parameters)
    
    # def _find_in_children(self, find_context:ContainerFindContext, find_parameters:FindParameters):
    #     """
    #     Find element in children of given container. 
    #     @param find_context Find context
    #     @param find_parameters Find parameters
    #     @return Element found.
    #     """
    #     if find_context.find_type == FindType.InChildren:
    #         # Unexpected case, self method should be overridden
    #         raise NotImplementedError(f"[{self.finder_description}] {self}")
    #     else:
    #         return self.find(find_context.with_find_type(FindType.InChildren), find_parameters)
    
    
    def _find_all_in_children(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        """
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found in container children.
        """
        res = []
        candidates = self._find_children(find_context, find_parameters)
        for cand in candidates:
            if self.is_valid_output(cand, find_context, find_parameters):
                res.append(cand)
        return res
    
    def _find_children(self, find_context:ContainerFindContext, find_parameters:FindParameters, container=None):
        return self.get_finder_children(find_context, find_parameters).find_all_in(container=container, find_context=find_context, find_parameters=find_parameters)
    
    def _get_finder_children(self, find_context, find_parameters):
        return self.inspector.get_finder_children(find_context, find_parameters)
    
    
    # def _find_in_parents(self, find_context:ContainerFindContext, find_parameters:FindParameters):
    #     """
    #     Find element in parents of given container. 
    #     @param find_context Find context
    #     @param find_parameters Find parameters
    #     @return Element found.
    #     """
    #     if find_context.find_type == FindType.InParents:
    #         # Unexpected case, self method should be overridden
    #         raise NotImplementedError(f"[{self.finder_description}] {self}")
    #     else:
    #         return self.find(find_context.with_find_type(FindType.InParents), find_parameters)
    
    def _find_all_in_parents(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        """
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found in container parents.
        """
        res = []
        cand = self._find_parent(find_context, find_parameters)
        if self.is_valid_output(cand, find_context, find_parameters):
            res.append(cand)
        return res
    
    def _find_parent(self, find_context:ContainerFindContext, find_parameters:FindParameters, container=None):
        return self.get_finder_parent(find_context, find_parameters).find(container=container, find_context=find_context, find_parameters=find_parameters)
    
    def _get_finder_parent(self, find_context, find_parameters):
        return self.inspector.get_finder_parent(find_context, find_parameters)
    
    
    
    
    
    