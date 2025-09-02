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
from holado_ui_selenium.ui.gui.selenium.inspectors.selenium_inspector import SeleniumInspector
from holado_ui.ui.inspectors.tools.ui_inspect_context import UIInspectContext
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters
from holado_ui_selenium.ui.gui.selenium.criterias.selenium_criteria import SeleniumCriteria
from holado_ui_selenium.ui.gui.selenium.finders.by_selenium_finder import BySeleniumFinder

logger = logging.getLogger(__name__)



class AngularSeleniumInspector(SeleniumInspector):
    """ Selenium inspector with Angular support.
    """
    
    def __init__(self):
        super().__init__("angular")
    
    @SeleniumInspector.default_inspect_builder.getter  # @UndefinedVariable
    def default_inspect_builder(self):
        res = super().default_inspect_builder
    
        res.default_parameters.add_finder_types([
            "mat-select"
            ])
        
        return res
    
    def get_finder_select(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        if inspect_context is None:
            inspect_context = self.inspect_builder.context()
        
        return self.get_finder_by_tag("mat-select", inspect_context.with_finder_type("mat-select"), inspect_parameters)
    
    def get_finder_select_option(self, value, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param value Option value
        @param iContext Inspect context
        @param iParameters Inspect parameters
        @return Finder for the select option with given value
        """
        criteria = SeleniumCriteria(self)
        criteria.tag_name = "mat-option"
        criteria.set_attribute("role", "option")
        criteria.content_text = value
        
        res = BySeleniumFinder(criteria, f"select option '{value}'")
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    
    
    
    