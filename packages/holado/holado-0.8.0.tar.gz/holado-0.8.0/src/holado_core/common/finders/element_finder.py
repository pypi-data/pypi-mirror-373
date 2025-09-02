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

from timeit import default_timer as timer
from holado_core.common.finders.finder import Finder
import logging

logger = logging.getLogger(__name__)


class ElementFinder(Finder):
    """ Generic finder of elements.
    """
    
    def __init__(self, description=None):
        super().__init__(description)
    
    def _build_result_element(self, res, find_context, find_parameters, element_description=None):
        super()._build_result_element(res, find_context, find_parameters)
        
        if element_description is not None and len(element_description) > 0:
            res.description = element_description
        elif self.element_description is not None:
            res.description = self.element_description
            
        return res
    
    def _build_result_list(self, res, find_context, find_parameters, element_description=None):
        for el in res:
            self._build_result_element(el, find_context, find_parameters, element_description)
        return res
    
    def is_valid_input(self, element, find_context, find_parameters):
        return self.is_valid_element(element, find_context, find_parameters)
    
    def is_valid_output(self, element, find_context, find_parameters):
        return self.is_valid_element(element, find_context, find_parameters)
    
    def is_valid_element(self, element, find_context, find_parameters):
        """
        Return if element is valid according this finder.
        @param element Element to validate
        @param find_context Find context
        @param find_parameters Find parameters
        @return True if element is valid according this finder
        """
        raise NotImplementedError(f"Unimplemented is_valid_element since inconsistent for [{self.finder_description}]")
    
    
    
    