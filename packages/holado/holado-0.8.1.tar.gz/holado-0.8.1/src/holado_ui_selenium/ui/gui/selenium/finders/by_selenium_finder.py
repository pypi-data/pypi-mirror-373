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
from holado_ui_selenium.ui.gui.selenium.finders.selenium_finder import SeleniumFinder
from holado_core.common.finders.tools.find_context import ContainerFindContext
from holado_core.common.finders.tools.find_parameters import FindParameters
from holado_core.common.criterias.criteria import Criteria
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools
from holado.holado_config import Config
from holado_ui_selenium.ui.gui.selenium.handlers.selenium_by import SeleniumBy
from selenium.webdriver.common.by import By
from holado_core.common.exceptions.element_exception import NoSuchElementException

logger = logging.getLogger(__name__)


class BySeleniumFinder(SeleniumFinder):
    """ Finder by selenium.
    """
    
    def __init__(self, css:str=None, xpath:str=None, criteria:Criteria=None, description=None):
        super().__init__(description)
        self.__css = css
        self.__xpath = xpath
        self.__criteria = criteria
        
        if css is None and xpath is None and criteria is None:
            raise TechnicalException("At least one of css, xpath and criteria must be defined.")
        if css is not None and xpath is not None:
            raise TechnicalException("css and xpath cannot be defined together, but criteria can be defined in addition to css or xpath.")
    
    @property
    def css(self):
        return self.__css
    
    @property
    def xpath(self):
        return self.__xpath
    
    @property
    def criteria(self):
        return self.__criteria
    
    def _find_all_container(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        res = None
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            prefix_logs = f"{self._get_indent_string_level(find_parameters)}[BySeleniumFinder({self.element_description})._find_all_container]"
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{prefix_logs} -> begin in [{find_context.get_input_description()}]")
        
        # Prepare analyze time spent
        if find_parameters.analyze_time_spent:
            start = Tools.timer_s()
        
        # Find elements
        if self.css is not None:
            res = self.internal_api.find_elements_by(SeleniumBy(By.CSS_SELECTOR, self.css), self.criteria, find_context, find_parameters)
        elif self.xpath is not None:
            res = self.internal_api.find_elements_by(SeleniumBy(By.XPATH, self.xpath), self.criteria, find_context, find_parameters)
        else:
            criteria_context = find_context.get_criteria_context()
            criteria_parameters = find_parameters.get_criteria_parameters()
            
            # Look if container verify criteria
            if self.criteria.validate(None, criteria_context, criteria_parameters):
                res = [find_context.container]
            
            # Search in container
            if res is None:
                res = self.internal_api.find_elements(self.criteria, find_context, find_parameters)
        
        # Analyze time spent
        if find_parameters.analyze_time_spent:
            duration = Tools.timer_s() - start
            if duration > Config.threshold_warn_time_spent_s:
                logger.warning(f"{prefix_logs} -> end (took: {duration} s)     -> {len(res)} elements")
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"{prefix_logs} -> return {len(res)} candidates:\n{self._represent_candidates_output(res, 4)}")
        
        return self._build_result_list(res, find_context, find_parameters)
    
    def _find_all_in_parents(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        if self.css is not None:
            raise TechnicalException("css is not managed in this case.")
        elif self.xpath is not None:
            raise TechnicalException("xpath is not managed in this case.")
        else:
            res = []
            
            try:
                parent = self.internal_api.find_parent(self.criteria, None, find_context, find_parameters)
            except NoSuchElementException:
                parent = None
                
            if parent is not None:
                res.add(parent)
            
            return self._build_result_list(res, find_context, find_parameters)
    
    def is_valid_element(self, element, find_context, find_parameters):
        if self.css is not None:
            raise TechnicalException("css is not managed in this case.")
        elif self.xpath is not None:
            raise TechnicalException("xpath is not managed in this case.")
        elif self.criteria is not None:
            criteria_context = find_context.get_criteria_context()
            criteria_parameters = find_parameters.get_criteria_parameters()
            return self.criteria.validate(element, criteria_context, criteria_parameters)
        else:
            return super().is_valid_element(element, find_context, find_parameters)
    
    def __str__(self):
        res_list = [super().__str__()]
        
        # Values
        if self.css is not None:
            res_list.append(f"&css='{self.css}'")
        if self.xpath is not None:
            res_list.append(f"&xpath='{self.xpath}'")
        if self.criteria is not None:
            res_list.append(f"&criteria={{{self.criteria}}}")
        
        return "".join(res_list)
    
    
    
    
    
    