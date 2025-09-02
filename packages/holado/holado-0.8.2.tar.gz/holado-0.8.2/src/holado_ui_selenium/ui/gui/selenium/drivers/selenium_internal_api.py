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
from selenium.common.exceptions import StaleElementReferenceException, UnexpectedAlertPresentException, \
    InvalidSelectorException, WebDriverException, SessionNotCreatedException
from selenium.webdriver.common.by import By
from holado_ui.ui.gui.drivers.gui_internal_api import GUIInternalAPI
from holado_ui_selenium.ui.gui.selenium.drivers.selenium_driver import SeleniumDriver
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.element_exception import NoSuchElementException,\
    TooManyElementsException
from holado_core.common.finders.tools.find_context import WithRootContainerFindContext,\
    ContainerFindContext, ListContainersFindContext
from holado_ui_selenium.ui.gui.selenium.handlers.selenium_by import SeleniumBy
import html
from selenium.webdriver.common.action_chains import ActionChains
from holado_core.common.exceptions.functional_exception import FunctionalException
from selenium.webdriver.support.select import Select
from datetime import datetime
import os
from holado_core.common.tools.tools import Tools
import time
from selenium.webdriver.remote.webelement import WebElement
from Screenshot import Screenshot
from holado_core.common.tools.converters.converter import Converter
from holado_core.common.handlers.redo import Redo
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from holado_ui_selenium.ui.gui.selenium.criterias.selenium_criteria import SeleniumCriteria
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class SeleniumInternalAPI(GUIInternalAPI):
    """ Implement all needed internal API methods with Selenium.
    """
    
    @staticmethod
    def selenium_version():
        """
        @return Selenium version
        """
        import selenium
        return selenium.__version__
    
    def __init__(self, driver:SeleniumDriver):
        super().__init__(driver)
        
        # Wait settings
        self.__wait_jquery = True
        self.__wait_angular = True
    
    @property
    def wait_angular(self):
        return self.__wait_angular
    
    @wait_angular.setter
    def wait_angular(self, wait_angular):
        """
        @param wait_angular If wait angular
        """
        self.__wait_angular = wait_angular
    
    @property
    def wait_jquery(self):
        return self.__wait_jquery
    
    @wait_jquery.setter
    def wait_jquery(self, wait_jquery):
        """
        @param wait_jquery If wait jquery
        """
        self.__wait_jquery = wait_jquery
        
    def find_element_by(self, by:SeleniumBy, criteria, find_context, find_parameters):
        """
        Find element with given criteria
        @param by By criteria
        @param criteria Criteria
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found element
        """
        if isinstance(find_context, ContainerFindContext) and find_context.container is not None:
            return self.find_element_by_container_by(by, criteria, find_context.container, find_context, find_parameters)
        elif isinstance(find_context, ListContainersFindContext) and find_context.nb_containers > 0:
            return self.find_element_by_candidates_by(by, criteria, find_context.containers, find_context, find_parameters)
        else:
            raise TechnicalException("Find context has no container")
    
    def find_elements_by(self, by:SeleniumBy, criteria, find_context, find_parameters):
        """
        Find elements in context container with given criteria
        @param by By criteria
        @param criteria Criteria
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found elements
        """
        if isinstance(find_context, ContainerFindContext) and find_context.container is not None:
            return self.find_elements_by_container_by(by, criteria, find_context.container, find_context, find_parameters)
        elif isinstance(find_context, ListContainersFindContext) and find_context.nb_containers > 0:
            return self.find_elements_by_candidates_by(by, criteria, find_context.containers, find_context, find_parameters)
        else:
            raise TechnicalException("Find context has no container")
    
    def find_element_by_container(self, criteria, container, find_context, find_parameters):
        if criteria is None:
            raise TechnicalException("Criteria must be defined")
        
        if isinstance(criteria, SeleniumCriteria):
            if criteria.class_name is not None:
                return self.find_element_by_container_by(SeleniumBy(By.CLASS_NAME, criteria.class_name), criteria, container, find_context, find_parameters)
            elif criteria.id is not None:
                return self.find_element_by_container_by(SeleniumBy(By.ID, criteria.id), criteria, container, find_context, find_parameters)
            elif criteria.name is not None:
                return self.find_element_by_container_by(SeleniumBy(By.NAME, criteria.name), criteria, container, find_context, find_parameters)
            elif criteria.getTagName() is not None:
                return self.find_element_by_container_by(SeleniumBy(By.TAG_NAME, criteria.tag_name), criteria, container, find_context, find_parameters)
            else:
                return self.find_element_in_tree(criteria, container, find_context, find_parameters)
        else:
            return self.find_element_in_tree(criteria, container, find_context, find_parameters)
        
    def find_element_by_container_by(self, by:SeleniumBy, criteria, container, find_context, find_parameters):
        """
        Find element in given container with given criteria
        @param by By criteria
        @param criteria Criteria
        @param container Container
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found element
        """
        res = None
        
        # Find elements
        found_elements = self.find_elements_by_container_by(by, criteria, container, find_context, find_parameters)
        
        # Analyse search result
        if len(found_elements) == 1:
            res = found_elements[0]
        elif len(found_elements) > 1:
            msg_list = ["More than one"]
            if find_parameters.nb_max_elements > 0:
                msg_list.append(f" (at least {len(found_elements)})")
            else:
                msg_list.append(f" ({len(found_elements)})")
            msg_list.append(f" element were found with: by={by}")
            if criteria is not None:
                msg_list.append(f" ; criteria={criteria}")
            msg_list.append(":\n")
            msg_list.append(self.represent_elements(found_elements, 4))
            raise TooManyElementsException("".join(msg_list))
        elif find_parameters.raise_no_such_element:
            if criteria is not None:
                raise NoSuchElementException(f"Unable to find element with: by={{{by}}} ; criteria={{{criteria}}} ; container={{{container.get_complete_description_and_details()}}}")
            else:
                raise NoSuchElementException(f"Unable to find element with: by={{{by}}} ; container={{{container.get_complete_description_and_details()}}}")
        
        return res
    
    def find_elements_by_container(self, criteria, container, find_context, find_parameters):
        if criteria is None:
            raise TechnicalException("Criteria must be defined")
        
        if isinstance(criteria, SeleniumCriteria):
            if criteria.class_name is not None:
                return self.find_elements_by_container_by(SeleniumBy(By.CLASS_NAME, criteria.class_name), criteria, container, find_context, find_parameters)
            elif criteria.id is not None:
                return self.find_elements_by_container_by(SeleniumBy(By.ID, criteria.id), criteria, container, find_context, find_parameters)
            elif criteria.name is not None:
                return self.find_elements_by_container_by(SeleniumBy(By.NAME, criteria.name), criteria, container, find_context, find_parameters)
            elif criteria.getTagName() is not None:
                return self.find_elements_by_container_by(SeleniumBy(By.TAG_NAME, criteria.tag_name), criteria, container, find_context, find_parameters)
            else:
                return self.find_elements_in_tree(criteria, container, find_context, find_parameters)
        else:
            return self.find_elements_in_tree(criteria, container, find_context, find_parameters)
        
    def find_elements_by_container_by(self, by:SeleniumBy, criteria, container, find_context, find_parameters):
        """
        Find elements in given container with given criteria
        @param by By criteria
        @param criteria Criteria
        @param container Container
        @param find_context Find context
        @param find_parameters Find parameters
        @return Found elements
        """
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"find_elements_by_container_by: by={{{by}}} ; criteria={{{criteria}}} ; container={{{container}}} ; nb_max={{{find_parameters.nb_max}}} ; visibility={{{find_parameters.visibility}}}")
        
        res = []
        criteria_parameters = find_parameters.get_criteria_parameters()
        
        # Search elements
        elements = container.get_list_holder_for(
                container.element.find_elements(by.by, by.value), 
                str(by) )
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"find_elements_by_container_by: by={{{by}}} ; criteria={{{criteria}}} ; container={{{container}}} ; nb_max={{{find_parameters.nb_max}}} ; visibility={{{find_parameters.visibility}}}       ->  {len(elements)} candidates found by selenium")
        
        # Filter on visibility
        for el in elements:
            if criteria is None or criteria.validate(el, find_context, criteria_parameters):
                if self.is_visible(el, find_context, find_parameters):
                    res.append(el)
                    
                    # Stop if max number of elements is reached
                    if find_parameters.nb_max_elements is not None and len(res) >= find_parameters.nb_max_elements:
                        break
                else:
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"Element is {'not ' if find_parameters.visibility else ''}visible (element: [{self.get_element_description(el)}])")
                    
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"find_elements_by_container_by: by={{{by}}} ; criteria={{{criteria}}} ; container={{{container}}} ; nb_max={{{find_parameters.nb_max}}} ; visibility={{{find_parameters.visibility}}}       ->  {len(res)} elements")
        return res
    
    def find_parent_element(self, element, find_context, find_parameters):
        # Limit to root element
        root_element = None
        if isinstance(find_context,  WithRootContainerFindContext):
            root_element = find_context.root_container
        if root_element is not None and element.element == root_element.element:
            if find_parameters.raise_no_such_element:
                raise NoSuchElementException("Root element is reached.")
            else:
                return None
        
        # Search parent
        try:
            return self.find_element_by_container_by(SeleniumBy(By.XPATH, ".."), element, find_context, find_parameters)
        except TooManyElementsException as exc:
            raise TechnicalException(str(exc)) from exc
        except NoSuchElementException as exc:
            if find_parameters.raise_no_such_element:
                raise exc
            else:
                return None
        except (InvalidSelectorException | StaleElementReferenceException) as exc:
            if "HTMLDocument" in str(exc):
                # When HTMLDocument is reached, FirefoxDriver throws a StaleElementReferenceException, the other drivers an InvalidSelectorException
                if find_parameters.raise_no_such_element:
                    raise NoSuchElementException("HTMLDocument is reached.")
                else:
                    return None
            else:
                raise exc
    
    def find_children_elements(self, container, find_context, find_parameters):
        return self.find_elements_by_container_by(SeleniumBy(By.XPATH, "./*"), None, container, find_context, find_parameters)
    
    def _get_element_text(self, element, find_context, find_parameters):
        if find_parameters.visibility is not None and find_parameters.visibility:
            return self.__get_element_text_visible(element, find_context, find_parameters)
        else:
            return self.get_text_content(element)
    
    def __get_element_text_visible(self, element, find_context, find_parameters):
        res = None
        sub_find_parameters = find_parameters.with_analyze_time_spent(False)
        sub_find_parameters_1 = sub_find_parameters.with_nb_max_elements(1)
        web_element = self._get_web_element(element)
        
        # Case of input with value attribute
        if web_element.tag_name in ["input", "textarea"]:
            res = web_element.get_attribute("value")
        
        
        # Case of select with selected option attribute
        if res is None and web_element.tag_name == "select":
            options = web_element.find_elements(By.TAG_NAME, "option")
            for option in options:
                if option.is_selected:
                    res = option.text.strip()
                    break
        
        # Else, case with inner inputs or selects
        if (res is None
            and ( len(self.find_elements_by_container_by(SeleniumBy(By.TAG_NAME, "input"), None, element, find_context, sub_find_parameters_1)) > 0
                or len(self.find_elements_by_container_by(SeleniumBy(By.TAG_NAME, "select"), None, element, find_context, sub_find_parameters_1)) > 0
                or len(self.find_elements_by_container_by(SeleniumBy(By.TAG_NAME, "textarea"), None, element, find_context, sub_find_parameters_1)) > 0
                ) ):
            res_list = []
            
            # Add text of each child
            children = self.find_children(None, element, find_context, sub_find_parameters.with_nb_max_elements(None))
            for child in children:
                if self.is_visible(child, find_context, sub_find_parameters):
                    res_list.append(self.__get_element_text_visible(child, find_context, sub_find_parameters))
                else:
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"Element is not visible (element: [{self.get_element_description(child)}])")
            
            res = "".join(res_list)
        
        # Else, return inner text
        if res is None:
            res = web_element.text.strip()
            res = html.unescape(res).strip()
        
        return res
    
    def get_text_content(self, element):
        """
        @param element An element
        @return Element's text content, including hidden text 
        """
        web_element = self._get_web_element(element)
        return web_element.get_attribute("textContent")
    
    def get_inner_html(self, element):
        """
        @param element An element
        @return Inner HTML of given element 
        """
        web_element = self._get_web_element(element)
        return web_element.get_attribute("innerHTML")
    
    def get_outer_html(self, element):
        """
        @param element An element
        @return HTML of given element 
        """
        web_element = self._get_web_element(element)
        return web_element.get_attribute("outerHTML")
    
    def is_displayed(self, element):
        web_element = self._get_web_element(element)
        res = web_element.is_displayed()
        
        # Check style has not "display: none"
        if res:
            value = web_element.get_attribute("style")
            res = ("display: none" not in value)
        
        return res
    
    def is_visible(self, element, find_context, find_parameters):
        res = None
        web_element = self._get_web_element(element)

        if find_parameters.visibility is None:
            return True
        
        # Case of a select option
        if web_element.tag_name == "option":
            try:
                parent = self.find_parent(element, find_context, find_parameters.with_analyze_time_spent(False).without_raise())
            except NoSuchElementException:
                parent = None
            
            if parent is not None:
                parent_element = self._get_web_element(parent)
                if parent_element.tag_name == "select":
                    selected_options = Select(parent_element).all_selected_options
                    res = (find_parameters.visibility == (web_element in selected_options))
        
        # Else
        if res is None:
            res = (find_parameters.visibility == self.is_displayed(element))
        
        return res
    
    def move_mouse_over(self, element):
        web_element = self._get_web_element(element)
        ActionChains(self.internal_driver).move_to_element(web_element).perform()
    
    def make_screenshot(self, destination_path, context_description):
        done = False
        try_counter = 0
        while not done:
            try_counter += 1
            try:
                # Take screenshot
                super().make_screenshot(destination_path, context_description)
                done = True
            except FunctionalException as exc:
                if try_counter < 3:
                    logger.warning(f"Unable to make screenshot ; retry (error: {str(exc)})")
                else:
                    logger.error(f"Unable to make screenshot ; stop retries (error: {str(exc)})")
                    return
            except Exception as exc:
                logger.error(f"Unable to make screenshot (error: {str(exc)})")
                return
    
    def get_screenshot_file(self, screenshot_path, element=None, margin_around_element=0):
        # Implementation is using: https://pypi.org/project/Selenium-Screenshot/
        self.driver._path_manager.makedirs(screenshot_path)
        dir_path, filename = os.path.split(screenshot_path)
        ss = Screenshot.Screenshot()
        
        if element is None:
            # Take screenshot
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace("Getting screenshot file...")
            res = ss.full_screenshot(self.internal_driver, save_path=dir_path , image_name=filename)
        else:
            # Take screenshot
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace("Getting screenshot file of element...")
            res = ss.get_element(self.internal_driver, self._get_web_element(element), save_path=dir_path , image_name=filename)
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace("Got screenshot file '{}'", res.getPath())
        return res
    
    def make_page_source_backup(self, destination_path, context_description):
        """
        Make a backup of current page source.
        @param destination_path Destination path
        @param context_description Context description that will be inserted in file names
        """
        # Create file name
        date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
        file_name = f"{date_str}-{context_description}-page_source.html"
        path = os.path.join(destination_path, file_name)
        
        page_source = None
        try_counter = 0
        while page_source is None:
            try_counter += 1
            try:
                # Take sources
                page_source = self.get_page_source()
            except FunctionalException as exc:
                if try_counter < 3:
                    logger.warning(f"Unable to make browser page source backup ; retry (error: {str(exc)})")
                else:
                    logger.error(f"Unable to make browser page source backup ; stop retries (error: {str(exc)})")
                    return
            except Exception as exc:
                logger.error(f"Unable to make browser page source backup (error: {str(exc)})")
                return
        
        # Create file
        self.driver._path_manager.makedirs(path)
        with open(path, 'wt') as fout:
            fout.write(page_source)
    
    def get_page_source(self):
        """
        Get browser page source.
        @return File containing screenshot
        """
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace("Getting page source...")
        
        return self.internal_driver.page_source
    
    def get_element_description(self, element, with_text=True):
        if element.is_web_element:
            res_list = []
            web_element = self._get_web_element(element)
            id_ = web_element.get_attribute("id")
            if id_ is None or len(id_) == 0:
                id_ = web_element.id
            
            res_list.append(f"id={id_}", )
            res_list.append(f"tag={web_element.tag_name}")
            res_list.append(f"coordinates={self.get_element_coordinates(element)}")
            res_list.append(f"size={self.get_element_size(element)}")
            if with_text:
                res_list.append(f"text=[{Tools.truncate_text(self.get_element_text(element), 1000)}]")
            res_list.append(f"html=[{Tools.truncate_text(self.get_outer_html(element), 1000)}]")
            
            return " ; ".join(res_list)
        else:
            return element.description
    
    def scroll_into_view(self, element, sleep_after_scroll_ms):
        if self.internal_driver is None:
            raise TechnicalException("Driver is None")
            
        self.internal_driver.execute_script("arguments[0].scrollIntoView(True)", self._get_web_element(element))
        time.sleep(sleep_after_scroll_ms/1000)
    
    def scroll_to(self, x, y, sleep_after_scroll_ms):
        if self.internal_driver is None:
            raise TechnicalException("Driver is None")
            
        self.internal_driver.execute_script(f"window.scrollTo({x}, {y})")
        time.sleep(sleep_after_scroll_ms/1000)
    
    def scroll_by(self, x, y, sleep_after_scroll_ms):
        if self.internal_driver is None:
            raise TechnicalException("Driver is None")
            
        self.internal_driver.execute_script(f"window.scrollBy({x}, {y})")
        time.sleep(sleep_after_scroll_ms/1000)
    
    def generate_xpath(self, web_element):
        """
        @param element Element
        @return Generated xpath of element
        """
        return self.__generate_xpath(web_element, "")

    def __generate_xpath(self, child_element:WebElement, current):
        child_tag = child_element.tag_name
        if child_tag == "html":
            return "/html[1]"+current
        
        parent_element = child_element.find_element(By.XPATH, "..")
        children_elements = parent_element.find_elements(By.XPATH, "*")
        count = 0
        for children_element in children_elements:
            children_element_tag = children_element.tag_name
            if child_tag == children_element_tag:
                count += 1
            
            if child_element == children_element:
                return self.__generate_xpath(parent_element, f"/{child_tag}[{count}]{current}")
        
        return None
    
    def refresh_browser(self):
        """
        Refresh browser
        """
        self.internal_driver.refresh()
    
    #TODO move in windows in order to adapt behavior on window type
    def wait_until_window_is_loaded(self, timeout_seconds):
        if not self.is_activated_wait_until_window_is_loaded():
            logger.info("Skipped wait until window is loaded (deactivated)")
            return
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Waiting until window is loaded...")
        
        class WinRedo(Redo):
            def __init__(self, driver):
                super().__init__("window is loaded")
                self.__driver = driver
                
            def _process(self):
                res = False
                
                try:
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        msg_list = ["Waiting until window is loaded: "]

                    # Verify HTML document
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        msg_list.append("HTML document")
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            logger.trace(f"{''.join(msg_list)}...")
                    
                    res = (self.internal_driver.execute_script("return document.readyState") == "complete")
                    if not res and logger.isTraceEnabled():
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            logger.trace(f"{''.join(msg_list)} is KO")
                    
                    # Verify jQuery
                    if res and self.__wait_jquery:
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            msg_list.append(" is OK  jQuery")
                            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                                logger.trace(f"{''.join(msg_list)}...")
                        
                        res = Converter.to_boolean(self.internal_driver.execute_script("return window.jQuery == undefined || jQuery.active === 0"))
                        if not res and logger.isTraceEnabled():
                            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                                logger.trace(f"{''.join(msg_list)} is KO")
                    
                    
                    # Verify angular
                    if res and self.__wait_angular:
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            msg_list.append(" is OK  angular")
                            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                                logger.trace(f"{''.join(msg_list)}...")
                        
                        res = Converter.to_boolean(self.internal_driver.execute_script("return window.angular == undefined || angular.element(document).injector() !== undefined && angular.element(document).injector().get('$http').pendingRequests.length === 0"))
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            logger.trace(f"{''.join(msg_list)} is {'OK' if res else 'KO'}")
                    
                except UnexpectedAlertPresentException as exc:
                    raise exc
                except WebDriverException as exc:
                    if str(exc).startswith("[JavaScript Error: "):
                        # FIXME: find a better workaround for this JavaScript error
                        logger.warning(f"Window is considered loaded when a JavaScript error occurs ; JavaScript error: {str(exc)}")
                        res = True 
                    else:
                        logger.warning(f"Retry because of unexpected exception of type '{Typing.get_object_class_fullname(exc)}' during Javascript call: {str(exc)}")
                        res = False
                
                return res
            
            def _process_interrupt(self, thread):
                # This call is needed, so that the blocking executeScript is stopped.
                # Otherwise, the process method continue until it finishes normally.
                
                # Following step is not working anymore, it directly throws exception UnsupportedOperationException
#                thread.stop(new InterruptedException())
                thread.stop()
            
        redo = WinRedo()
        redo.redo_while(False)
        redo.with_process_timeout(10)
        redo.with_nb_successive_failure_before_error(3)
        if timeout_seconds is not None:
            redo.with_timeout(timeout_seconds)

        try:
            redo.execute()
        except UnexpectedAlertPresentException:
            # Nothing  next sentence should manage this alert
            pass
    
    def add_cookie(self, cookie):
        """
        @param cookie Cookie
        """
        self.internal_driver.add_cookie(cookie)
    
    def disactivate_js_on_before_unload(self):
        self.internal_driver.execute_script("window.onbeforeunload = function(e){}")
    
    def click_on_element_with_selenium(self, element):
        """
        @param element Element
        """
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"clicking with selenium on element [{self.get_element_description(element)}] (source: [{self.get_outer_html(element)}])")
        self._get_web_element(element).click()
    
    def click_on_element_with_javascript(self, element):
        """
        @param element Element
        """
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"clicking with javascript on element [{self.get_element_description(element)}] (source: [{self.get_outer_html(element)}])")
        
        self.internal_driver.execute_script("arguments[0].click()", self._get_web_element(element))
    
    def write_to_element_all_keys(self, element, value):
        """
        @param element Element
        @param value Value
        """
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"writing text '{value}' in element [{self.get_element_description(element)}]")
        
        # Write text
        self.send_keys(element, value)
        self.wait_until_window_is_loaded()
    
    def write_to_element_key_by_key(self, element, value):
        """
        @param element Element
        @param value Value
        """
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"writing (key by key) text '{value}' in element [{self.get_element_description(element)}]")

        # Send each text character
        for c in value:
            self.send_keys(element, c)
            self.wait_until_window_is_loaded()
        
    def send_key_multiple_times_all_keys(self, element, key:Keys, nb_times):
        """
        @param element Element
        @param key Key
        @param nb_times Number times
        """
        keys_list = []
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Sending {nb_times} {key} to element [{self.get_element_description(element)}]")

        # Add as many backspace as existing text length
        for _ in range(nb_times):
            # Call backspace character
            keys_list.append(key)
        
        
        # Send keys
        self.send_keys(element, "".join(keys_list))
        self.wait_until_window_is_loaded()
    
    def send_key_multiple_times_key_by_key(self, element, key:Keys, nb_times):
        """
        @param element Element
        @param key Key
        @param nb_times Number times
        """
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Sending (key by key) {nb_times} {key} to element [{self.get_element_description(element)}]")

        # Send as many backspace as existing text length
        for _ in range(nb_times):
            self.send_keys(element, key)
            self.wait_until_window_is_loaded()
    
    def send_keys(self, element, keys):
        """
        @param element Web element
        @param keys Keys to send (as string or Keys value)
        """
        self._get_web_element(element).send_keys(keys)
    
    def clear_element(self, element):
        self._get_web_element(element).clear()
    
    def focus(self):
        self.internal_driver.execute_script("window.focus()")
    
    def maximize(self):
        self.internal_driver.maximize_window()
        self.wait_until_window_is_loaded()
    
    def get_cookies(self):
        """
        @return Cookies
        """
        return self.internal_driver.get_cookies()
    
    def open_new_window(self):
        self.internal_driver.execute_script("window.open()")
    
    def is_stale(self, element):
        """
        @param element Web element
        @return If element is stale
        """
        return EC.staleness_of(self._get_web_element(element)).apply(self.internal_driver)
    
    def getWindowHandles(self):
        """
        @return List of driver handles
        """
        try:
            return self.internal_driver.window_handles
        except SessionNotCreatedException:
            return []
    
    def get_element_coordinates(self, element):
        raise NotImplementedError
    
    def get_element_location(self, element):
        return self._get_web_element(element).location
    
    def get_element_rectangle(self, element):
        return self._get_web_element(element).rect
    
    def get_element_size(self, element):
        return self._get_web_element(element).size
    
    def _get_web_element(self, element_holder):
        if element_holder.is_web_element:
            return element_holder.element
        else:
            raise TechnicalException(f"Holded element is of type '{Typing.get_object_class_fullname(element_holder.element)}' rather than WebElement")
    
    
    
    
    