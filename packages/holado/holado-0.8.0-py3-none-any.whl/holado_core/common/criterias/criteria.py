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
from holado_core.common.tools.tools import Tools
from holado_core.common.criterias.tools.criteria_context import CriteriaContext,\
    ContainerCriteriaContext
from holado_core.common.criterias.tools.criteria_parameters import CriteriaParameters
from holado.holado_config import Config
import logging
import abc

logger = logging.getLogger(__name__)



class Criteria(object):
    """ Base class of a family used to validate elements.
    """
    __metaclass__ = abc.ABCMeta
    
    def validate(self, element, criteria_context: CriteriaContext, criteria_parameters: CriteriaParameters):
        """ Verify if element verifies expected criteria.
        If element is None and criteria_context is a ContainerCriteriaContext, criteria_context.container is used as element
        @param element Element to validate
        @param criteria_context Criteria context
        @param criteria_parameters Criteria parameters
        @return True if given element verifies expected criteria
        """
        if element is None:
            if isinstance(criteria_context, ContainerCriteriaContext) and criteria_context.container is not None:
                return self.validate(criteria_context.container, criteria_context, criteria_parameters)
            else:
                raise TechnicalException("Find context has no container")
            
        # Prepare analyze time spent
        if criteria_parameters.analyze_time_spent:
            start = Tools.timer_s()
        
        res = self.validate_element(element, criteria_context, criteria_parameters)
        
        # Analyze time spent
        if criteria_parameters.analyze_time_spent:
            duration = Tools.timer_s() - start
            if duration > Config.threshold_warn_time_spent_s:
                logger.warning(f"{self._get_indent_string_level(criteria_parameters)}[{self}].validate({element}) -> {res} (took {duration} s)")
        
        return res

    def validate_element(self, element, criteria_context: CriteriaContext, criteria_parameters: CriteriaParameters):
        return True

    def __str__(self):
        return self.__class__.__name__

    def reset(self):
        """ Reset the criteria."""
        pass
    
    def _get_indent_string_level(self, criteria_parameters: CriteriaParameters=None, level=None):
        if level is not None:
            return Tools.get_indent_string(level * 4)
        elif criteria_parameters is not None:
            return self._get_indent_string_level(level=criteria_parameters.find_level)
        else:
            raise TechnicalException("level or criteria_parameters must be defined")
    
    
    