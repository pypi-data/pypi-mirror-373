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

import logging
import abc
from holado_core.common.finders.tools.find_context import ContainerFindContext
from holado_core.common.exceptions.element_exception import NoSuchElementException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.drivers.element_internal_api import ElementInternalAPI
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class TreeInternalAPI(ElementInternalAPI):
    """ Base class for elements tree internal API.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def find_children(self, criteria, container, find_context, find_parameters):
        """
        Find the children elements verifying given criteria.
        @param container Container in which search
        @param criteria Criteria to verify
        @param find_context Find context
        @param find_parameters Find parameters
        @return Children elements
        """
        if container is None:
            if isinstance(find_context, ContainerFindContext) and find_context.container is not None:
                container = find_context.container
            else:
                raise TechnicalException("Find context has no container")
            
        children = self.find_children_elements(container, find_context, find_parameters)
        return self.validate_elements(criteria, children, find_context, find_parameters)
    
    def find_children_elements(self, container, find_context, find_parameters):
        """
        Find the children elements of given element.
        @param container An element
        @param find_context Find context
        @param find_parameters Find parameters
        @return Children elements
        """
        raise NotImplementedError

    def find_element_in_tree(self, criteria, container, find_context, find_parameters):
        """
        Find, in container tree, the element verifying given criteria.
        @param container Container in which search
        @param criteria Criteria to verify
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found element
        """
        sub_find_parameters = find_parameters.with_analyze_time_spent(False)
        candidates = self.find_elements_in_tree(criteria, container, find_context, sub_find_parameters)
        return self._get_element_from_list(candidates, 1, find_context, sub_find_parameters)
    
    def find_elements_in_tree(self, criteria, container, find_context, find_parameters):
        """
        Find, in container tree, all elements verifying given criteria.
        When an element verifies given criteria, its sub tree is not explored.
        
        @param container Container in which search
        @param criteria Criteria to verify
        @param find_context Find context
        @param find_parameters Find parameters
        @return List of elements
        """
        if container is None:
            if isinstance(find_context, ContainerFindContext) and find_context.container is not None:
                container = find_context.container
            else:
                raise TechnicalException("Find context has no container")
            
        res = []
        sub_find_parameters = find_parameters.get_next_level().with_valid_container(True)
        criteria_context = find_context.get_criteria_context()
        criteria_parameters = find_parameters.get_criteria_parameters()
        
        # Verify this element
        is_validated = False
        if find_parameters.add_valid_container:
            is_validated = criteria.validate(container, criteria_context, criteria_parameters)
            if is_validated:
                res.append(container)
        
        # Verify in its children
        if not is_validated:
            children = self.find_children(None, container, find_context, sub_find_parameters.with_nb_max_elements(None))
            for child in children:
                if find_parameters.nb_max_elements is not None:
                    # Search only remaining max elements to find
                    res.extend( self.find_elements_in_tree(criteria, child, find_context, sub_find_parameters.with_nb_max_elements(find_parameters.nb_max_elements - len(res))) )
                       
                    # Stop if max number of elements is reached
                    if len(res) >= find_parameters.nb_max_elements:
                        break
                else:
                    res.extend( self.find_elements_in_tree(criteria, child, find_context, sub_find_parameters) )
            
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"find_elements_in_tree: criteria={criteria} ; container={container} ; max nb={find_parameters.nb_max_elements} ; visibility={find_parameters.visibility}     ->  {len(res)} elements")
        return res
    
    def find_parent(self, criteria, element, find_context, find_parameters):
        """
        Find the parent element for given element, verifying given criteria.
        @param element An element
        @param criteria Criteria
        @param find_context Find context
        @param find_parameters Find parameters
        @return The parent element
        """
        if element is None:
            if isinstance(find_context, ContainerFindContext) and find_context.container is not None:
                element = find_context.container
            else:
                raise TechnicalException("Find context has no container")
            
        parent_element = element
        found = False
        sub_find_parameters = find_parameters.get_next_level()
        criteria_context = find_context.get_criteria_context()
        criteria_parameters = sub_find_parameters.get_criteria_parameters()
        
        while not found:
            # Find parent
            parent_element = self.find_parent_element(parent_element, find_context, sub_find_parameters)
            
            # Break if reached top of hierarchy
            if parent_element is None:
                break

            # Verify criteria
            if criteria is not None:
                found = criteria.validate(parent_element, criteria_context, criteria_parameters)
            else:
                found = True
            
        if not found:
            if find_parameters.raise_no_such_element:
                raise NoSuchElementException(f"Unable to find parent with criteria: {criteria}")
            else:
                parent_element = None
           
        return parent_element
    
    def find_parent_element(self, element, find_context, find_parameters):
        """
        Find the parent element for given element.
        @param element An element
        @param find_context Find context
        @param find_parameters Find parameters
        @return The parent element
        """
        raise NotImplementedError
    
    
    
    