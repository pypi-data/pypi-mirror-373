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
import re
from holado_core.common.tools.tools import Tools
from holado.holado_config import Config
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions import technical_exception
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class SeleniumCriteria(GUICriteria):
    """ Criteria for Selenium elements.
    """
    
    def __init__(self, selenium_inspector, check_editable:CheckEditableModes=CheckEditableModes.NoCheck):
        super().__init__(check_editable)
        
        from holado_ui_selenium.ui.gui.selenium.inspectors.selenium_inspector import SeleniumInspector
        if selenium_inspector is None:
            raise technical_exception(f"Parameter 'selenium_inspector' must be defined")
        if not isinstance(selenium_inspector, SeleniumInspector):
            raise technical_exception(f"Parameter 'selenium_inspector' is of type {Typing.get_object_class_fullname(selenium_inspector)}' that is not a SeleniumInspector")
        self.__inspector = selenium_inspector
        
        self.__attribute_value_by_attribute_name = {}
        self.__pattern_by_attribute_name = {}
        self.__content_text = None
        self.__pattern_content_text = None
        self.__pattern_inner_html = None
        self.__inner_text = None
        self.__pattern_inner_text = None
        self.__tag_name = None
        self.__pattern_tag_name = None
    
    def set_attribute(self, attr_name, attr_value):
        """
        @param attr_name Attribute name
        @param attr_value Attribute value
        """
        if attr_value is not None and len(attr_value) > 0:
            self.__attribute_value_by_attribute_name[attr_name] = attr_value
        elif attr_name in self.__attribute_value_by_attribute_name:
            del self.__attribute_value_by_attribute_name[attr_name]
    
    def get_attribute(self, attr_name):
        """
        @param attr_name Attribute name
        @return Attribute value
        """
        return self.__attribute_value_by_attribute_name.get(attr_name)
    
    def set_attribute_pattern(self, attr_name, attr_value, case_insensitive=False):
        """
        @param attr_name Attribute name
        @param attr_value Attribute value pattern
        @param case_insensitive If True set case insensitive flag
        """
        if attr_value is not None and len(attr_value) > 0:
            if case_insensitive:
                pattern = re.compile(attr_value, re.IGNORECASE)
            else:
                pattern = re.compile(attr_value)
            self.__pattern_by_attribute_name[attr_name] = pattern
        elif attr_name in self.__pattern_by_attribute_name:
            del self.__pattern_by_attribute_name[attr_name]
    
    @property
    def class_name(self):
        """
        @return Class name
        """
        return self.get_attribute("class")
    
    @class_name.setter
    def class_name(self, class_name):
        """
        @param class_name Class name
        """
        self.set_attribute("class", class_name)
    
    @property
    def class_name_pattern(self):
        """
        @return Class name
        """
        pattern = self.get_attribute_pattern("class")
        if pattern is not None:
            return pattern.pattern
        else:
            return None
    
    @class_name_pattern.setter
    def class_name_pattern(self, class_name):
        """
        @param class_name Class name
        """
        self.set_class_name_pattern(class_name)
    
    def set_class_name_pattern(self, class_name, case_insensitive=False):
        """
        @param class_name Class name
        """
        self.set_attribute_pattern("class", class_name, case_insensitive)
    
    @property
    def content_text(self):
        """
        @return Content text
        """
        return self.__content_text
    
    @content_text.setter
    def content_text(self, content_text):
        """
        @param content_text Content text
        """
        if content_text is not None and len(content_text) > 0:
            self.__content_text = content_text.decode('string_escape')
        else:
            self.__content_text = None
    
    @property
    def content_text_pattern(self):
        """
        @return Content text pattern
        """
        pattern = self.__pattern_content_text
        if pattern is not None:
            return pattern.pattern
        else:
            return None
    
    @content_text_pattern.setter
    def content_text_pattern(self, content_text):
        """
        @param content_text Content text pattern
        """
        self.set_content_text_pattern(content_text)
    
    def set_content_text_pattern(self, content_text, unescape=True):
        """
        @param content_text Content text pattern
        @param unescape If True unescape the content text pattern
        """
        if content_text is not None and len(content_text) > 0:
            if unescape:
                self.__pattern_content_text = re.compile(content_text.decode('string_escape'))
            else:
                self.__pattern_content_text = re.compile(content_text)
        else:
            self.__pattern_content_text = None
    
    @property
    def id(self):
        """
        @return Id
        """
        return self.get_attribute("id")
    
    @id.setter
    def id(self, id_):
        """
        @param id Id
        """
        self.set_attribute("id", id_)
    
    @property
    def id_pattern(self):
        """
        @return Id pattern
        """
        pattern = self.get_attribute_pattern("id")
        if pattern is not None:
            return pattern.pattern
        else:
            return None
    
    @id_pattern.setter
    def id_pattern(self, id_):
        """
        @param id Id pattern
        """
        self.set_attribute_pattern("id", id_)
    
    @property
    def inner_html_pattern(self):
        """
        @return Inner HTML pattern
        """
        pattern = self.__pattern_inner_html
        if pattern is not None:
            return pattern.pattern
        else:
            return None
    
    @inner_html_pattern.setter
    def inner_html_pattern(self, inner_html):
        """
        @param inner_html Inner HTML pattern
        """
        self.set_inner_html_pattern(inner_html)
    
    def set_inner_html_pattern(self, inner_html, unescape=True):
        """
        @param inner_html Inner HTML pattern
        @param unescape If True unescape the inner HTML pattern
        """
        if inner_html is not None and len(inner_html) > 0:
            if unescape:
                self.__pattern_inner_html = re.compile(inner_html.decode('string_escape'))
            else:
                self.__pattern_inner_html = re.compile(inner_html)
        else:
            self.__pattern_inner_html = None
    
    @property
    def inner_text(self):
        """
        @return Inner text
        """
        return self.__inner_text
    
    @inner_text.setter
    def inner_text(self, inner_text):
        """
        @param inner_text Inner text
        """
        if inner_text is not None and len(inner_text) > 0:
            self.__inner_text = inner_text.decode('string_escape')
        else:
            self.__inner_text = None
    
    @property
    def inner_text_pattern(self):
        """
        @return Inner text pattern
        """
        pattern = self.__pattern_inner_text
        if pattern is not None:
            return pattern.pattern
        else:
            return None
    
    @inner_text_pattern.setter
    def inner_text_pattern(self, inner_text):
        """
        @param inner_text Inner text pattern
        """
        self.set_inner_text_pattern(inner_text)
    
    def set_inner_text_pattern(self, inner_text, unescape=True):
        """
        @param inner_text Inner text pattern
        @param unescape If True unescape the content text pattern
        """
        if inner_text is not None and len(inner_text) > 0:
            if unescape:
                self.__pattern_inner_text = re.compile(inner_text.decode('string_escape'))
            else:
                self.__pattern_inner_text = re.compile(inner_text)
        else:
            self.__pattern_inner_text = None
    
    @property
    def name(self):
        """
        @return Name
        """
        return self.get_attribute("name")
    
    @name.setter
    def name(self, name):
        """
        @param name Name
        """
        self.set_attribute("name", name)
    
    @property
    def name_pattern(self):
        """
        @return Name pattern
        """
        pattern = self.get_attribute_pattern("name")
        if pattern is not None:
            return pattern.pattern
        else:
            return None
    
    @name_pattern.setter
    def name_pattern(self, name):
        """
        @param name Name pattern
        """
        self.set_attribute_pattern("name", name)
    
    @property
    def tag_name(self):
        """
        @return Tag name
        """
        return self.__tag_name
    
    @tag_name.setter
    def tag_name(self, tag_name):
        """
        @param tag_name Tag name
        """
        if tag_name is not None and len(tag_name) > 0:
            self.__tag_name = tag_name.decode('string_escape')
        else:
            self.__tag_name = None
    
    @property
    def tag_name_pattern(self):
        """
        @return Tag name pattern
        """
        pattern = self.__pattern_tag_name
        if pattern is not None:
            return pattern.pattern
        else:
            return None
    
    @tag_name_pattern.setter
    def tag_name_pattern(self, tag_name):
        """
        @param tag_name Tag name pattern
        """
        self.set_tag_name_pattern(tag_name)
    
    def set_tag_name_pattern(self, tag_name, unescape=True):
        """
        @param tag_name Tag name pattern
        @param unescape If True unescape the content text pattern
        """
        if tag_name is not None and len(tag_name) > 0:
            if unescape:
                self.__pattern_tag_name = re.compile(tag_name.decode('string_escape'))
            else:
                self.__pattern_tag_name = re.compile(tag_name)
        else:
            self.__pattern_tag_name = None
    
    def validate(self, element, criteria_context: CriteriaContext, criteria_parameters: CriteriaParameters):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"{self._get_ident_string_level(criteria_parameters)}[{self} ; [{self._internal_api.get_element_description(element)}]] validate : begin")
        
        # Prepare analyze time spent
        if criteria_parameters.analyze_time_spent:
            start = Tools.timer_s()
        
        # Validate self element
        res = self.validate_element(element, criteria_context, criteria_parameters)

        # Verify element children
        if res and (self.__content_text is not None or self.__pattern_content_text is not None):
            # Verify that no child also verify the same criteria
            res = self.__no_child_validates(element, criteria_context, criteria_parameters)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"{self._get_indent_string_level(criteria_parameters)}[{self} ; [{self._internal_api.get_element_description(element)}]] validate : end -> {res}")
        
        # Analyze time spent
        if criteria_parameters.analyze_time_spent:
            duration = Tools.timer_s() - start
            if duration > Config.threshold_warn_time_spent_s:
                logger.warning(f"{self._get_indent_string_level(criteria_parameters)}[{self} ; [{self._internal_api.get_element_description(element)}]] validate -> {res} (took {duration} s)")
        
        return res
    
    
    def __no_child_validates(self, element, criteria_context, criteria_parameters):
        res = True

        for child in self._internal_api.find_children(None, element, criteria_context, criteria_parameters):
            if self.validate_element(child, criteria_context, criteria_parameters):
                res = False
                break
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"{self._get_indent_string_level(criteria_parameters)}    [{self} ; [{self._internal_api.get_element_description(element)}]] no child validates : end -> {res}")
        return res
    
    def validate_element(self, element, criteria_context, criteria_parameters):
        if not element.is_web_element():
            return False

        element_text = None
        web_element = self._get_web_element(element)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.trace(f"{self._get_indent_string_level(criteria_parameters)}    [{self} ; [{self._internal_api.get_element_description(element)}]] validate element : begin")

        res = super().validate_element(element, criteria_context, criteria_parameters)

        # Values
        if res and self.__tag_name is not None:
            res = (self.__tag_name == web_element.tag_name)
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate tag_name -> {res}")
        
        if res and len(self.__attribute_value_by_attribute_name) > 0:
            for attr_name, attr_value in self.__attribute_value_by_attribute_name.items():
                value = web_element.get_attribute(attr_name)
                if value is not None:
                    if attr_name in ["class", "style"]:
                        res = (attr_value in value)
                    else:
                        res = (attr_value == value)
                else:
                    res = False
                if not res:
                    break
            
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate attribute value -> {res}")
        
        # Patterns
        if res and self.__pattern_inner_html is not None:
            value = self._internal_api.get_inner_html(element)
            res = (self.__pattern_inner_html.search(value) is not None)
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate pattern on inner html (obtained: '{value}' ; expected: '{self.__pattern_inner_html.pattern}') -> {res}")
        
        if res and self.__pattern_tag_name is not None:
            value = web_element.tag_name
            res = (self.__pattern_tag_name.search(value) is not None)
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate pattern on tag name (obtained: '{value}' ; expected: '{self.__pattern_tag_name.pattern}') -> {res}")
        
        if res and len(self.__pattern_by_attribute_name) > 0:
            for attr_name, attr_pattern in self.__pattern_by_attribute_name.items():
                value = web_element.get_attribute(attr_name)
                if value is not None:
                    res = (attr_pattern.search(value) is not None)
                else:
                    res = False
                
                if not res:
                    break
            
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate pattern on attributes -> {res}")
        
        # Values using get_element_text (put at end for performance)
        if res and self.__content_text is not None:
            if element_text is None:
                element_text = self._internal_api.get_element_text(element, criteria_context, criteria_parameters)
            res = (self.__content_text == element_text)
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate content text (obtained: '{element_text}' ; expected: '{self.__content_text}') -> {res}")
        
        if res and self.__inner_text is not None:
            if element_text is None:
                element_text = self._internal_api.get_element_text(element, criteria_context, criteria_parameters)
            res = (self.__inner_text == element_text)
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate inner text (obtained: '{element_text}' ; expected: '{self.__inner_text}') -> {res}")
        
        # Patterns using get_element_text (put at end for performance)
        if res and self.__pattern_content_text is not None:
            if element_text is None:
                element_text = self._internal_api.get_element_text(element, criteria_context, criteria_parameters)
            res = (self.__pattern_content_text.search(element_text) is not None)
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate pattern on content text (obtained: '{element_text}' ; expected: '{self.__pattern_content_text.pattern}') -> {res}")
        
        if res and self.__pattern_inner_text is not None:
            if element_text is None:
                element_text = self._internal_api.get_element_text(element, criteria_context, criteria_parameters)
            res = (self.__pattern_inner_text.search(element_text) is not None)
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{self._get_indent_string_level(criteria_parameters)}        [{self}] validate pattern on inner text (obtained: '{element_text}' ; expected: '{self.__pattern_inner_text.pattern}') -> {res}")
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.trace(f"{self._get_indent_string_level(criteria_parameters)}    [{self} ; [{self._internal_api.get_element_description(element)}]] validate element : end -> {res}")
        return res
    
    def _is_editable(self, element):
        if element.is_web_element:
            web_element = self._get_web_element(element)
            is_readonly = (web_element.get_attribute("readonly") is not None)
            return not is_readonly and web_element.is_enabled()
        else:
            return False
    
    def __str__(self):
        res_list = [super().__str__()]
        
        # Values
        if self.content_text is not None:
            res_list.append(f"&content_text='{self.content_text}'")
        if self.inner_text is not None:
            res_list.append(f"&inner_text='{self.inner_text}'")
        if self.tag_name is not None:
            res_list.append(f"&tag_name='{self.tag_name}'")
        if not self.__attribute_value_by_attribute_name.empty():
            res_list.append("&attributes={")
            attr_list = []
            for key, value in self.__attribute_value_by_attribute_name.items():
                attr_list.append(f"'{key}':'{value}'")
            res_list.append(", ".join(attr_list))
            res_list.append("}")
        
        # Patterns
        if self.__pattern_content_text is not None:
            res_list.append(f"&content_text_pattern='{self.content_text_pattern}'")
        if self.__pattern_inner_html is not None:
            res_list.append(f"&inner_html_pattern='{self.inner_html_pattern}'")
        if self.__pattern_inner_text is not None:
            res_list.append(f"&inner_text_pattern='{self.inner_text_pattern}'")
        if self.__pattern_tag_name is not None:
            res_list.append(f"&tag_name_pattern='{self.tag_name_pattern}'")
        if not self.__pattern_by_attribute_name.empty():
            res_list.append("&attributes_patterns={")
            attr_list = []
            for key, value in self.__pattern_by_attribute_name.items():
                attr_list.append(f"'{key}':'{value}'")
            res_list.append(", ".join(attr_list))
            res_list.append("}")
        
        return "".join(res_list)
    
    @property
    def _inspector(self):
        return self.__inspector
    
    
    def _internal_api(self):
        return self._inspector.internal_api
    
    def _get_web_element(self, element_holder):
        if element_holder.is_web_element:
            return element_holder.element
        else:
            raise TechnicalException(f"Holded element is of type '{Typing.get_object_class_fullname(element_holder.element)}' rather than WebElement")
    
    