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

from holado_core.common.criterias.tools.criteria_context import CriteriaContext
from holado_core.common.criterias.tools.criteria_parameters import CriteriaParameters
import logging
from holado_ui.ui.gui.criterias.enums import CheckEditableModes
from holado_ui.ui.gui.criterias.gui_criteria import GUICriteria
from holado_core.common.tools.tools import Tools
from holado.holado_config import Config
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_scripting.text.verifier.text_verifier import TextVerifier
from holado_ui_selenium.ui.gui.selenium.criterias.selenium_criteria import SeleniumCriteria
from holado_core.common.exceptions.functional_exception import FunctionalException

logger = logging.getLogger(__name__)



class SeleniumCriteriaAndVerifier(GUICriteria):
    """ Apply a SeleniumCriteria, and if validated apply verifications by verifier.
    """
    
    def __init__(self, criteria:SeleniumCriteria, text_verifier:TextVerifier):
        super().__init__(CheckEditableModes.NoCheck)
        
        self.__criteria = criteria
        self.__text_verifier = text_verifier
        
        self.__attribute_value_by_attribute_name = {}
    
    def get_attribute(self, attr_name):
        """
        @param attr_name Attribute name
        @return Attribute value
        """
        return self.__attribute_value_by_attribute_name.get(attr_name)
    
    def set_attribute(self, attr_name, attr_value):
        """
        @param attr_name Attribute name
        @param attr_value Attribute value
        """
        if attr_value is not None and len(attr_value) > 0:
            self.__attribute_value_by_attribute_name[attr_name] = attr_value
        elif attr_name in self.__attribute_value_by_attribute_name:
            del self.__attribute_value_by_attribute_name[attr_name]
    
    
    def validate(self, element, criteria_context: CriteriaContext, criteria_parameters: CriteriaParameters):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"{self._get_ident_string_level(criteria_parameters)}[{self} ; [{self._internal_api.get_element_description(element)}]] validate : begin")
        
        # Prepare analyze time spent
        if criteria_parameters.analyze_time_spent:
            start = Tools.timer_s()
        
        # Validate element
        res = self.criteria.validate(element, criteria_context, criteria_parameters)

        # If validated, verify
        if res:
            try:
                res = self.__check_element(element)
            except FunctionalException as e:
                raise TechnicalException(str(e)) from e
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"{self._get_indent_string_level(criteria_parameters)}[{self} ; [{self._internal_api.get_element_description(element)}]] validate : end -> {res}")
        
        # Analyze time spent
        if criteria_parameters.analyze_time_spent:
            duration = Tools.timer_s() - start
            if duration > Config.threshold_warn_time_spent_s:
                logger.warning(f"{self._get_indent_string_level(criteria_parameters)}[{self} ; [{self._internal_api.get_element_description(element)}]] validate -> {res} (took {duration} s)")
        
        return res
    
    def __check_element(self, element):
        res = True
        for attr_name, attr_value in self.__attribute_value_by_attribute_name.items():
            web_element = element.element
            value = web_element.get_attribute(attr_name)
            if value is not None:
                res = self.__text_verifier.check(attr_value, value)
            else:
                res = False
            if not res:
                break

        return res;
    
    def __str__(self):
        res_list = [super().__str__()]
        
        res_list.append(f"&criteria=[{self.__criteria}]")

        if not self.__attribute_value_by_attribute_name.empty():
            res_list.append("&attributes={")
            attr_list = []
            for key, value in self.__attribute_value_by_attribute_name.items():
                attr_list.append(f"'{key}':'{value}'")
            res_list.append(", ".join(attr_list))
            res_list.append("}")
        
        return "".join(res_list)
    
    
    