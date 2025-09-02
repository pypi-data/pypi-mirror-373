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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.finders.tools.enums import FindType
from holado_ui.ui.gui.windows.gui_window import GUIWindow
import abc
from holado_ui_selenium.ui.gui.selenium.handlers.selenium_holder import SeleniumHolder,\
    PopupHolder
from holado_ui.ui.handlers.ui_context import UIContext
from selenium.common.exceptions import NoAlertPresentException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_ui_selenium.ui.gui.selenium.handlers.selenium_redo import SeleniumRedo
from holado_value.common.tables.value_table_with_header import ValueTableWithHeader
from holado_ui_selenium.ui.gui.selenium.tables.converters.selenium_table_converter import SeleniumTableConverter
from holado_ui_selenium.ui.gui.selenium.tables.comparators.selenium_2_value_table_comparator import Selenium2Value_TableComparator
from holado_ui_selenium.ui.gui.selenium.tables.comparators.selenium_2_value_table_with_header_comparator import Selenium2Value_TableWithHeaderComparator
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class SeleniumWindow(GUIWindow):
    """ Base class for Selenium windows.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        super().__init__()
    
    def get_window_container(self):
        return SeleniumHolder(None, self.driver, self.driver.internal_driver, "page content")
    
    def click_on_element_by_id(self, ui_context:UIContext, element_id):
        """
        Click on element of given ID value
        @param ui_context UI Context
        @param element_id Element ID
            """
        finder = self.inspector.get_finder_by_id(element_id, self.inspect_builder().context(ui_context), None)
        self.actor.act_find_and_click_on(finder, FindType.In).execute(self.current_container)
    
    def __find_alert(self):
        """
        Checks and register an alert
                """
        res = None
        
        try:
            res = self.driver.internal_driver.swith_to.alert
        except NoAlertPresentException:
            res = None
        
        return res
    
    def check_new_popup_is_opened(self, expected_popup_title=None, raise_exception=True):
        res = True
        
        # Search if an alert is present
        alert = self.__find_alert()
        if alert is not None:
            # Checking popup title
            if expected_popup_title is not None and len(expected_popup_title) > 0:
                raise FunctionalException(f"An alert popup is present while checking popup '{expected_popup_title}'")
            
            # Update container info
            self._enter_popup("{ALERT}", SeleniumHolder(self.driver, alert, self.driver.internal_driver, "{ALERT}"))
        else:
            popup = self.find_popup(expected_popup_title, raise_exception)
            if popup is not None:
                # Update container info
                popup_name = expected_popup_title
                if popup_name is None:
                    popup_name = "{EMPTY}"
                self._enter_popup(popup_name, self._get_popup_container(expected_popup_title, popup))
            else:
                # This case appear when raise_exception is False and popup wasn't found
                res = False
        
        if not res and raise_exception:
            if expected_popup_title is not None:
                raise FunctionalException(f"Unable to find a popup of title '{expected_popup_title}'")
            else:
                raise FunctionalException("Unable to find a popup")
        
        return res
    
    def _get_popup_container(self, popup_title, popup_element):
        # Update container info
        if popup_title is not None and len(popup_title) > 0:
            popup_description = f"popup '{popup_title}'"
        else:
            popup_description = "popup"
        return PopupHolder(self.driver, self._get_web_element(popup_element), self.driver.internal_driver, popup_title, popup_description)
    
    def get_table(self, ui_context:UIContext=None):
        """
        Find a table and return it as a Table instance
        @param ui_context UI Context
        @return a Table instance
        """
        finder = self.inspector.get_finder_table(self.inspect_builder.context(ui_context), None)
        return self.get_table_by_finder(finder, FindType.In, self.current_container)
    
    def get_table_with_header(self, ui_context:UIContext=None):
        """
        Find a table and return it as a Table instance
        @param ui_context UI Context
        @return a Table instance
        """
        finder = self.inspector.get_finder_table(self.inspect_builder.context(ui_context), None)
        return self.get_table_with_header_by_finder(finder, FindType.In, self.current_container)
    
    def get_table_by_finder(self, finder_table, find_type, container):
        """
        Find a table with given finder in given container and return it as a Table instance
        @param finder_table Finder for table
        @param find_type Find type
        @param container Container
        @return Table instance
        """
        # Find table in given zone
        table_element = finder_table.find(find_type, container)
        
        # Convert to table type
        return SeleniumTableConverter.convert_element_to_selenium_table(self.inspector, table_element)
    
    def get_table_with_header_by_finder(self, finder_table, find_type, container):
        """
        Find a table with given finder in given container and return it as a Table instance
        @param finder_table Finder for table
        @param find_type Find type
        @param container Container
        @return Table instance
        """
        # Find table in given zone
        table_element = finder_table.find(find_type, container)
        
        # Convert to table type
        return SeleniumTableConverter.convert_element_to_selenium_table_with_header(self.inspector, table_element)
    
    def check_table_contains(self, ui_context, expected, raise_exception):
        class CheckRedo(SeleniumRedo):
            def __init__(self_redo):  # @NoSelf
                super().__init__("check table contains", self.driver)
            
            def _process(self_redo):  # @NoSelf
                if isinstance(expected, ValueTableWithHeader):
                    obtained = self.get_table_with_header(ui_context)
                    comparator = Selenium2Value_TableWithHeaderComparator(self.inspector)
                else:
                    obtained = self.get_table(ui_context)
                    comparator = Selenium2Value_TableComparator(inspector=self.inspector)
                return comparator.contains_rows(obtained, expected, raise_exception=raise_exception)
            
        redo = CheckRedo()
        return redo.execute()
    
    def check_table_displays(self, ui_context, expected, raise_exception):
        class CheckRedo(SeleniumRedo):
            def __init__(self_redo):  # @NoSelf
                super().__init__("check table displays", self.driver)
            
            def _process(self_redo):  # @NoSelf
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace("Comparing tables...")
                    
                if isinstance(expected, ValueTableWithHeader):
                    obtained = self.get_table_with_header(ui_context)
                    comparator = Selenium2Value_TableWithHeaderComparator(self.inspector)
                else:
                    obtained = self.get_table(ui_context)
                    comparator = Selenium2Value_TableComparator(inspector=self.inspector)
                res = comparator.equals(obtained, expected, raise_exception=raise_exception)
                
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"Compared tables -> {res}")
                return res
            
        redo = CheckRedo()
        return redo.execute()
    
    def _get_web_element(self, element_holder):
        if element_holder.is_web_element:
            return element_holder.element
        else:
            raise TechnicalException(f"Holded element is of type '{Typing.get_object_class_fullname(element_holder.element)}' rather than WebElement")
    
    
    
    