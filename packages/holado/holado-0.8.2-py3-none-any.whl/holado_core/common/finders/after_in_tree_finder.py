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
import logging
from holado_core.common.finders.tools.find_context import ContainerFindContext
from holado_core.common.finders.tools.find_parameters import FindParameters
from holado_core.common.finders.tools.enums import FindType
from holado_core.common.finders.tree_finder import TreeFinder
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class AfterInTreeFinder(TreeFinder):
    """ Finder that searches through tree an element after given one.
    It goes through parents, and for each parent, look in children after the child coming from if element is found.
    The element is searched using given finder from each possible child.
    """
    
    def __init__(self, finder_element, description=None):
        super().__init__(description)
        self.find_type = FindType.Custom
        
        self.__finder_element = finder_element
    
    def _find_all_container(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"FinderHtmlAfterInTree[{self.element_description}]._find_all_container begin  It should be replaced by another find method for performance reasons")

        res = []
        sub_find_parameters = find_parameters.get_next_level(False)
        
        current_context = find_context
        while len(res) == 0:
            # Find parent
            parent = self._find_parent(current_context, sub_find_parameters)
            if parent is None:
                # Root parent is reached, stop searching
                break
            
            # Get children
            children = self._find_children(current_context, sub_find_parameters, parent)
            
            # Get index in children
            index_in_children = children.index(current_context.container)
            if index_in_children < 0:
                raise TechnicalException("Unable to find element in children of parent")
            
            # Search through each possible child
            for index in range(index_in_children + 1, len(children)):
                child = children[index]
                
                # Check child
                try:
                    if self.__finder_element.is_valid_input(child, current_context, sub_find_parameters):
                        self._add_candidate(res, child)
                        continue
                except NotImplementedError:
                    # check this child is not relevant, continue code
                    pass
                
                # Check in child
                res_child = self.__finder_element.find_all_in(child, find_context=current_context, find_parameters=sub_find_parameters)
                if len(res_child) > 0:
                    self._add_candidates(res, res_child)
                    continue
            
            # Prepare next loop
            current_context = current_context.withContainer(parent)
        
        return res
    
    
    
    
    
    