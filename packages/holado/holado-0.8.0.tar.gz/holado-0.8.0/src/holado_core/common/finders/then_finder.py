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
from holado_core.common.tools.tools import Tools
from holado.holado_config import Config
from holado_core.common.exceptions.element_exception import NoSuchElementException
from holado_core.common.finders.element_finder import ElementFinder
from holado_core.common.finders.tools.find_parameters import FindParameters
from holado_core.common.finders.tools.find_context import ContainerFindContext

logger = logging.getLogger(__name__)


class ThenFinder(ElementFinder):
    """ Finder that search successively in a list of self.__finders.
    Search is done from first added to last added finder, using output of previous finder as input of next finder.
    """
    
    def __init__(self, description=None):
        super().__init__(description)
        self.__self.__finders = []
    
    def set_next_finder(self, finder, find_type=None, update_root_container=None):
        """
        Append given finder in then succession.
        @param finder A finder.
        @param find_type Find method type.
        """
        if find_type is not None:
            finder.find_type = find_type
        if update_root_container is not None:
            finder.find_updater.set_update_root(update_root_container)
            
        # Only first finder can unspecify the find type
        if len(self.__self.__finders) > 0:
            finder.verify_find_type_is_defined("Except first finder, all others must specify find type.")
            
        self.__self.__finders.append(finder)
    
    def _find_all_container(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        res = None
        stop = False
        sub_parameters = find_parameters.get_next_level()
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"{self._get_indent_string_level(find_parameters)}[ThenFinder({self.element_description})._find_all_container] -> begin in [{find_context.get_input_description()}]")
        
        # Prepare analyze time spent
        if find_parameters.analyze_time_spent:
            start = Tools.timer_s()
        
        finder = self.__self.__finders[0]
        try:
            # Process first finder
            res = finder._find_all_container(find_context, sub_parameters)
        except NoSuchElementException as exc:
            if (1 < len(self.__self.__finders) and find_parameters.raise_intermediate_no_such_element
                    or 1 == len(self.__self.__finders) and find_parameters.raise_no_such_element):
                Tools.raise_same_exception_type(exc, f"[ThenFinder({self.element_description})[0]: {finder.element_description}] {exc.message}")
            else:
                stop = True
        except Exception as exc:
            Tools.raise_same_exception_type(exc, f"[ThenFinder({self.element_description})[0]: {finder.element_description}] {exc.message}")
        
        # Process next self.__finders
        if not stop and len(self.__self.__finders) > 1:
            res = self.__process_next_finder(res, 1, finder, find_context, find_parameters)
        
        # Analyze time spent
        if find_parameters.analyze_time_spent:
            duration = Tools.timer_s() - start
            if duration > Config.threshold_warn_time_spent_s:
                logger.warning(f"ThenFinder[{self.element_description}]._find_all_container end (took: {duration} s)     -> {len(res)} elements")
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            if len(res) == 0:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"{self._get_indent_string_level(find_parameters)}[ThenFinder({self.element_description})._find_all_container] -> return 0 candidate")
            else:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"{self._get_indent_string_level(find_parameters)}[ThenFinder({self.element_description})._find_all_container] -> return {len(res)} candidates:\n{self._represent_candidates_output(res, 4)}")
        
        if len(res) == 0 and find_parameters.raise_no_such_element:
            raise NoSuchElementException(f"[ThenFinder({self.element_description})._find_all_container] Unable to find any element")
        return res
    
    def __process_next_finder(self, candidates, finder_index, previous_finder, find_context, find_parameters):
        res = []
        cur_container = None
        candidates_for_next_finder = None
        sub_find_parameters = find_parameters.get_next_level()
        
        # Manage intermediate result
        if len(candidates) == 0:
            if find_parameters.raise_intermediate_no_such_element:
                raise NoSuchElementException(f"[ThenFinder({self.element_description})[{finder_index-1}]] Unable to find intermediate {previous_finder.element_description}")
            # Else process next finders in case of finder managing no result
        
        # Get finder to use
        finder = self.__finders.get(finder_index)
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            prefix_message = f"{self._get_indent_string_level(find_parameters)}[ThenFinder({self.element_description}).__process_next_finder[{finder_index}]: {finder.element_description}]"
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{prefix_message} -> begin with {len(candidates)} candidates:\n{self._represent_candidates_output(res, 4)}")
        
        # Process finder on each candidate
        for i, cur_container in enumerate(candidates):
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{prefix_message}     -> candidate {i}: {self._represent_candidate_output(cur_container)}")
            
            # Process finder
            try:
                candidates_for_next_finder = finder.find_all(container=cur_container, find_context=find_context, find_parameters=sub_find_parameters)
            except NoSuchElementException:
                # Nothing, continue with another candidate
                continue
            except Exception as exc:
                Tools.raise_same_exception_type(exc, f"[ThenFinder({self.element_description})[{finder_index}]: {finder.element_description} - on candidate {i+1}/{len(candidates)}] {exc.message}")
                
            # Process next finder if existing
            if finder_index + 1 < len(self.__finders):
                try:
                    self._add_candidates(res, self.__process_next_finder(candidates_for_next_finder, finder_index + 1, finder, find_context, find_parameters))
                except NoSuchElementException:
                    # Nothing, continue with another candidate
                    continue
                
            else:
                self._add_candidates(res, candidates_for_next_finder)
                if Tools.do_log(logger, logging.TRACE) and len(candidates_for_next_finder) > 0:  # @UndefinedVariable
                    logger.trace(f"{prefix_message}     -> candidate {i} => {len(candidates_for_next_finder)} elements found")
            
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            if len(res) == 0:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"{prefix_message} -> return 0 candidate")
            else:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"{prefix_message} -> return {len(res)} candidates:\n{self._represent_candidates_output(res, 4)}")

        return res
    
    
    
    
    