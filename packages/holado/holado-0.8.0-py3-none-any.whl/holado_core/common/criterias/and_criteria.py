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

from holado_core.common.criterias.tools.criteria_context import CriteriaContext
from holado_core.common.criterias.tools.criteria_parameters import CriteriaParameters
import logging

logger = logging.getLogger(__name__)



class AndCriteria(object):
    """ Criteria that makes a logical or between added criterias.
    """
    
    def __init__(self):
        self.__criterias = []
    
    @property
    def criterias(self):
        return self.__criterias
    
    def add_criteria(self, criteria):
        """
        Add a criteria in and validation.
        @param criteria Criteria
        """
        self.__criterias.append(criteria)
        
    def validate_element(self, element, criteria_context: CriteriaContext, criteria_parameters: CriteriaParameters):
        return super().validate_element(element, criteria_context, criteria_parameters) \
            and self.__validate_criterias(element, criteria_context, criteria_parameters)

    def __validate_criterias(self, element, criteria_context, criteria_parameters):
        res = True
        sub_parameters = criteria_parameters.get_next_level()
        
        for criteria in self.criterias:
            if not criteria.validate(element, criteria_context, sub_parameters):
                res = False
                break
        
        return res

    def __str__(self):
        res_criterias = []
        for index, criteria in self.criterias:
            res_criterias.append(f"{index}:{{{criteria}}}")
        return super().__str__() + "&{" + "&".join(res_criterias) + "}"
    
    
    