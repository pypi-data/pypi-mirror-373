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
from holado_ui_selenium.ui.gui.selenium.inspectors.selenium_inspector import SeleniumInspector
from holado_ui.ui.inspectors.tools.ui_inspect_context import UIInspectContext
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters
from holado_ui_selenium.ui.gui.selenium.criterias.selenium_criteria import SeleniumCriteria
from holado_core.common.criterias.or_criteria import OrCriteria
from holado_core.common.finders.else_finder import ElseFinder
import re
from holado_core.common.finders.then_finder import ThenFinder
from holado_core.common.finders.tools.enums import FindType
from holado_ui_selenium.ui.gui.selenium.criterias.selenium_criteria_and_verifier import SeleniumCriteriaAndVerifier
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado.common.context.session_context import SessionContext
from holado_ui_selenium.ui.gui.selenium.finders.by_selenium_finder import BySeleniumFinder
from holado_core.common.criterias.and_criteria import AndCriteria
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class HtmlSeleniumInspector(SeleniumInspector):
    """ Selenium inspector with Angular support.
    """
    
    def __init__(self):
        super().__init__("html")
    
    @SeleniumInspector.default_inspect_builder.getter  # @UndefinedVariable
    def default_inspect_builder(self):
        res = super().default_inspect_builder
    
        res.default_parameters.add_finder_types([
            "label", "label as div", "label as span",
            "select",
            "text-node", "text-content"
            ])
        
        return res
    
    def _get_criteria_editable_element(self):
        res = OrCriteria()
        
        criteria = SeleniumCriteria(self)
        criteria.tag_name = "input"
        criteria.set_attribute_pattern("type", "text|password")
        res.add_criteria(criteria)
        
        # Criteria for select
        criteria = SeleniumCriteria(self)
        criteria.tag_name = "select"
        res.add_criteria(criteria)
        
        # Criteria for textarea
        criteria = SeleniumCriteria(self)
        criteria.tag_name = "textarea"
        res.add_criteria(criteria)

        return res
    
    def _get_criteria_text_element(self):
        res = OrCriteria()
        
        # Editable form
        res.add_criteria( self._get_criteria_editable_element() )
        
        # Element containing text
        criteria = SeleniumCriteria(self)
        criteria.tag_name_pattern = "div|td|span|p"
#        criteria.content_text_pattern = "[^\\s]+";    # With contentText, a text element containing another text element won't be validated
        criteria.inner_text_pattern = "[^\\s]+"
        res.add_criteria(criteria)
        
        return res
    
    def get_finder_label(self, label, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        if inspect_context is None:
            inspect_context = self.inspect_builder.context()
        
        return self._build_result_finder_from_list([
                # Add search by label
                self.get_finder_by_tag_and_inner_text("label", label, inspect_context.without_ui_context().with_finder_type("label"), inspect_parameters),
                # Add search by div
                self.get_finder_by_tag_and_inner_text("div", label, inspect_context.without_ui_context().with_finder_type("label as div"), inspect_parameters),
                # Add search by span
                self.get_finder_by_tag_and_inner_text("span", label, inspect_context.without_ui_context().with_finder_type("label as span"), inspect_parameters)
            ], inspect_context, inspect_parameters)
        return self.get_finder_by_tag("select", inspect_context.with_finder_type("select"), inspect_parameters)
    
    def get_finder_select(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        if inspect_context is None:
            inspect_context = self.inspect_builder.context()
        
        return self.get_finder_by_tag("select", inspect_context.with_finder_type("select"), inspect_parameters)
    
    def get_finder_input_text(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for input text
        """
        criteria = SeleniumCriteria(self)
        criteria.tag_name = "input"
        criteria.set_attribute("type", "text")
        
        res = BySeleniumFinder(criteria=criteria, description="text input")
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_table(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        return self.get_finder_by_tag("table", "table", inspect_context, inspect_parameters)

    def get_finder_table_row(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder for table rows (including header row if existing)
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        criteria = SeleniumCriteria(self)
        criteria.tag_name = "tr"
        
        res = BySeleniumFinder(criteria=criteria, description="table row")
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_table_cell(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder for table cells
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        criteria = SeleniumCriteria(self)
        criteria.tag_name_pattern = "^th|td$"
        
        res = BySeleniumFinder(criteria=criteria, description="table cell")
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_text(self, text, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        if inspect_context is None:
            inspect_context = self.inspect_builder.context()
        
        res = ElseFinder(f"text '{text}'")
        
        res.set_next_finder(self.get_finder_by_node_text(text, inspect_context.without_ui_context().with_finder_type("text-node"), inspect_parameters))
        res.set_next_finder(self.get_finder_by_content_text(text, inspect_context.without_ui_context().with_finder_type("text-content"), inspect_parameters))
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_text_containing(self, text, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"WARNING: the use of a finder for text containing '{text}' can be very slow, it should be limited to small zones")
        criteria = SeleniumCriteria(self)
        criteria.set_content_text_pattern(re.escape(text), False)
        
        res = BySeleniumFinder(criteria=criteria, description=f"text containing '{text}'")
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_text_element(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        return self._get_finder_text_element(None, inspect_context, inspect_parameters)
    
    def _get_finder_text_element(self, additional_criteria, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        criteria_text = self._get_criteria_text_element()
        if additional_criteria is None:
            res = BySeleniumFinder(criteria=criteria_text, description="text element")
        else:
            criteria = AndCriteria()
            criteria.add_criteria(criteria_text)
            criteria.add_criteria(additional_criteria)
            res = BySeleniumFinder(criteria=criteria, description=f"text element verifying [{additional_criteria}]")
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_symbol(self, expected_symbol, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        # Build pattern for Title symbol
        pattern_title = r"^Title\('(.*)'\)$"
        
        matcher = re.match(pattern_title, expected_symbol)
        if matcher:
            interpreter = SessionContext.instance().text_interpreter
            verifier = SessionContext.instance().text_verifier
            
            # Get and interpret title
            title = matcher.group(1)
            title = interpreter.interpret(title)
            
            # Create appropriate finder whereas title contain a verify section or not
            if interpreter.contains_interpret(title):
                # Criteria to find an element with a title
                criteria = SeleniumCriteria(self)
                criteria.set_attribute_pattern("title", ".+")
                
                # Criteria to then check title
                criteria_check = SeleniumCriteriaAndVerifier(criteria, verifier)
                criteria_check.set_attribute("title", title)
                
                # Return finder
                return BySeleniumFinder(criteria=criteria_check, description=f"titled as '{title}'")
            else:
                criteria = SeleniumCriteria(self)
                criteria.set_attribute("title", title)
                return BySeleniumFinder(criteria=criteria, description=f"titled with '{title}'")
        else:
            raise TechnicalException(f"Unmanaged symbol '{expected_symbol}'")
    
    def get_finder_zone(self, zone_name, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        res = ThenFinder(f"zone '{zone_name}'")
        
        # Find label
        res.set_next_finder( self.get_finder_text(zone_name, inspect_context.without_ui_context(), inspect_parameters) )
        
        # Find div in parents
        criteria = SeleniumCriteria(self)
        criteria.tag_name = "div"
        res.set_next_finder(FindType.InParents, BySeleniumFinder(criteria=criteria, description="div parent") )
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    
    
    
    