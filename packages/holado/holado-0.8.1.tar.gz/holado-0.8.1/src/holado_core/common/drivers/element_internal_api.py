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
from holado_core.common.drivers.internal_api import InternalAPI
from holado_core.common.finders.tools.find_context import ContainerFindContext,\
    ListContainersFindContext
from holado_core.common.exceptions.element_exception import TooManyElementsException,\
    NoSuchElementException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class ElementInternalAPI(InternalAPI):
    """ Base class for element internal API.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def find_element(self, criteria, find_context, find_parameters):
        """
        Find element with given criteria
        @param criteria Criteria
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found element
        """
        if isinstance(find_context, ContainerFindContext) and find_context.container is not None:
            return self.find_element_by_container(criteria, find_context.container, find_context, find_parameters)
        elif isinstance(find_context, ListContainersFindContext) and find_context.nb_containers > 0:
            return self.find_element_by_candidates(criteria, find_context.containers, find_context, find_parameters)
        else:
            raise TechnicalException("Find context has no container")
    
    
    def find_element_by_container(self, criteria, container, find_context, find_parameters):
        """
        Find element with given criteria and container
        
        A default implementation use find_elements_by_container.
        It is usually recommended to override it with a dedicated implementation.
        @param criteria Criteria
        @param container Container
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found element
        """
        # Manage no candidates
        if container is None:
            if find_parameters.raise_no_such_element:
                raise NoSuchElementException("No container")
            else:
                return None
        
        found_elements = self.find_elements_by_container(criteria, container, find_context, find_parameters)
        return self._get_element_from_list(found_elements, 1, criteria, find_context, find_parameters)
    
    def find_element_by_candidates(self, criteria, candidates, find_context, find_parameters):
        """
        Find element in given candidates with given criteria
        
        This default implementation use find_elements_by_candidates.
        It is usually recommended to override it with a dedicated implementation.
        @param candidates List of candidates
        @param criteria Criteria
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found element
        """
        # Manage no candidates
        if len(candidates) == 0:
            if find_parameters.raise_no_such_element:
                raise NoSuchElementException("No candidates")
            else:
                return None
        
        found_elements = self.find_elements_by_candidates(criteria, candidates, find_context, find_parameters)
        return self._get_element_from_list(found_elements, len(candidates), criteria, find_context, find_parameters)
    
    def find_elements(self, criteria, find_context, find_parameters):
        """
        Find elements in context container with given criteria
        @param criteria Criteria
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found elements
        """
        if isinstance(find_context, ContainerFindContext) and find_context.container is not None:
            return self.find_elements_by_container(criteria, find_context.container, find_context, find_parameters)
        elif isinstance(find_context, ListContainersFindContext) and find_context.nb_containers > 0:
            return self.find_elements_by_candidates(criteria, find_context.containers, find_context, find_parameters)
        else:
            raise TechnicalException("Find context has no container")
    
    def find_elements_by_container(self, criteria, container, find_context, find_parameters):
        """
        Find elements in given container with given criteria
        @param criteria Criteria
        @param container Container
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found elements
        """
        raise NotImplementedError

    def find_elements_by_candidates(self, criteria, candidates, find_context, find_parameters):
        """
        Find elements in given candidates with given criteria
        
        This default implementation use find_elements_by_container.
        It is usually recommended to override it with a dedicated implementation.
        @param candidates List of candidates
        @param criteria Criteria
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found elements
        """
        if criteria is None:
            return candidates
        else:
            res = []
            if find_parameters.add_valid_container:
                res = self.validate_elements(criteria, candidates, find_context, find_parameters)
                
            # Continue if max number of elements is not reached
            if find_parameters.nb_max_elements is None or len(res) < find_parameters.nb_max_elements:
                sub_find_parameters = find_parameters.with_valid_container(False)
                for el in candidates:
                    found_elements = self.find_elements_by_container(criteria, el, find_context, sub_find_parameters)
                    res.extend(found_elements)
                    
                    # Stop if max number of elements is reached
                    if find_parameters.nb_max_elements is not None and len(res) >= find_parameters.nb_max_elements:
                        break
            
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"find_elements_by_candidates: criteria={criteria} ; nb candidates={len(candidates)} ; max nb={find_parameters.nb_max_elements} ; visibility={find_parameters.visibility}   ->  {len(res)} elements")
            return res

    def validate_elements(self, criteria, elements, find_context, find_parameters):
        """
        @param criteria Criteria
        @param elements List of elements to validate
        @param find_context Find context
        @param find_parameters Find parameters
        @return List of elements validating given criteria
        """
        if criteria is None:
            return elements
        else:
            res = []
            criteria_context = find_context.get_criteria_context()
            criteria_parameters = find_parameters.get_criteria_parameters()

            # Search elements
            for el in elements:
                if criteria.validate(el, criteria_context, criteria_parameters):
                    res.add(el)
                       
                    # Stop if max number of elements is reached
                    if criteria_parameters.nb_max_elements is not None and len(res) >= criteria_parameters.nb_max_elements:
                        break
            
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Validate {len(elements)} elements: criteria={criteria} ; nbMax={criteria_parameters.nb_max_elements} ; visibility={criteria_parameters.visibility}   ->  {len(res)} elements")
            return res
    
    def _get_element_from_list(self, found_elements, nb_candidates, criteria, find_context, find_parameters):
        """
        Get element from found elements that should contain only one element.
        @param found_elements List of elements previously found
        @param criteria Criteria
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found element
        """
        # Analyze search result
        if len(found_elements) == 1:
            return found_elements[0]
        elif len(found_elements) > 1:
            msg_list = ["More than one"]
            if find_parameters.nb_max_elements is not None:
                msg_list.append(f" (at least {len(found_elements)})")
            else:
                msg_list.append(f" ({len(found_elements)})")
            msg_list.append(f" element was found")
            if nb_candidates > 1:
                msg_list.append(f" (in {nb_candidates} candidates)")
            if criteria is not None:
                msg_list.append(f" with criteria={criteria}")
            msg_list.append(":\n")
            msg_list.append(self.represent_elements(found_elements, 4))
            raise TooManyElementsException("".join(msg_list))
        elif find_parameters.raise_no_such_element:
            msg_list = ["Unable to find element"]
            if nb_candidates > 1:
                msg_list.append(f" (in {nb_candidates} candidates)")
            if criteria is not None:
                msg_list.append(f" with criteria={criteria}")
            raise NoSuchElementException("".join(msg_list))
    
    def represent_elements(self, elements, indent):
        """
        @param elements Elements
        @param indent Indent
        @return String representing elements
        """
        res_list = []

        for i, el in enumerate(elements):
            res_list.append(f"{i} : {self.get_element_description(el)}")
        
        return Tools.indent_string(indent, "\n".join(res_list))
    
    def get_element_description(self, element):
        """
        @param element Element
        @return Element description
        """
        raise NotImplementedError
    
    
    
    