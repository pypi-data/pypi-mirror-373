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
from holado_multitask.multithreading.reflection.sys import get_current_function_name
from holado_ui.ui.gui.inspectors.gui_inspector import GUIInspector
import abc
from holado_ui.ui.inspectors.tools.ui_inspect_context import UIInspectContext
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters
from holado_ui_selenium.ui.gui.selenium.criterias.selenium_criteria import SeleniumCriteria
from holado_core.common.criterias.and_criteria import AndCriteria
from holado_ui_selenium.ui.gui.selenium.finders.parent_selenium_finder import ParentSeleniumFinder
from holado_ui_selenium.ui.gui.selenium.finders.children_selenium_finder import ChildrenSeleniumFinder
import re
from holado_ui_selenium.ui.gui.selenium.finders.by_selenium_finder import BySeleniumFinder

logger = logging.getLogger(__name__)



class SeleniumInspector(GUIInspector):
    """ Base class for Selenium inspector.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        super().__init__(module_name)
    
    def get_finder_parent(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        return ParentSeleniumFinder()
    
    def get_finder_children(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        return ChildrenSeleniumFinder()
    
    def get_finder_select(self, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for select elements
        """
        return self._get_finder_from_modules(get_current_function_name(), [], [], inspect_context, inspect_parameters)
    
    def get_finder_by_content_text(self, text, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param text Text
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for element with given text as content
        """
        criteria = SeleniumCriteria(self)
        criteria.content_text = text
        res = BySeleniumFinder(criteria=criteria, description=f"text with content '{text}'")
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_by_node_text(self, text, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param text Text
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for node with given text
        """
        # Path to the node, containing a text node, equals to the text after trimming
        xpath = ".//text()[normalize-space(.) = concat('{}', '')]/..".format(text.replace("'", "', \"'\", '"))
        
        # Add verification, because if only xpath is used hidden texts (ex: not selected select options) are also found
        criteria = SeleniumCriteria(self)
        criteria.content_text = text
        
        res = BySeleniumFinder(xpath=xpath, criteria=criteria, description=f"text '{text}'")
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_by_class_name(self, class_name, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder by class name.
        @param class_name Class name.
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder.
        """
        criteria = SeleniumCriteria(self)
        criteria.class_name = class_name
        res = BySeleniumFinder(criteria=criteria, description=f"element with class '{class_name}'")
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_by_id(self, id_, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param id Id
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return finder for an element with given id
        """
        criteria = SeleniumCriteria(self)
        criteria.id = id_
        res = BySeleniumFinder(criteria=criteria, description=f"element with id '{id_}'")
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_by_tag(self, tag_name, element_description=None, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder for an element with given tag name
        @param tag_name Tag name
        @param element_description Element description
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        if element_description is None:
            element_description = tag_name
        
        criteria = SeleniumCriteria(self)
        criteria.tag_name = tag_name
        res = BySeleniumFinder(criteria=criteria, description=element_description)
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_by_tag_and_attribute(self, tag_name, attr_name, attr_value, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder by given attribute.
        @param tag_name Tag name
        @param attr_name Attribute name.
        @param attr_value Attribute value.
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder.
        """
        xpath = f"//{tag_name}[@{attr_name}='{attr_value}']"
        return self.get_finder_by_xpath(xpath, f"{tag_name} with attribute '{attr_name}' = '{attr_value}'", inspect_context, inspect_parameters)
    
    def get_finder_by_tag_and_inner_text(self, tag_name, inner_text, element_description=None, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        @param tag_name Tag name
        @param inner_text Inner text
        @param element_description Element description
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder for an element with given tag and inner text
        """
        if element_description is None:
            element_description = f"{tag_name} '{inner_text}'"
        
        criteria = SeleniumCriteria(self)
        criteria.tag_name = tag_name
        criteria.inner_text = inner_text
        
        res = BySeleniumFinder(criteria=criteria, description=element_description)
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    def get_finder_by_attribute(self, attr_name, attr_value, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder by given attribute.
        @param attr_name Attribute name.
        @param attr_value Attribute value.
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder.
        """
        xpath = f"//*[@{attr_name}='{attr_value}']"
        return self.get_finder_by_xpath(xpath, f"element with attribute '{attr_name}' = '{attr_value}'", inspect_context, inspect_parameters)
    

    def get_finder_by_xpath(self, xpath, element_description, inspect_context:UIInspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Finder by given XPath.
        @param xpath XPath
        @param element_description Element description
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder.
        """
        res = BySeleniumFinder(xpath=xpath, description=element_description)
        
        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    
    
    