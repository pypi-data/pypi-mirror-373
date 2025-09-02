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

from timeit import default_timer as timer
from holado_core.common.finders.finder import Finder
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.element_exception import NoSuchElementException
from holado.holado_config import Config
import logging
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class OrFinder(Finder):
    """ Finder that search using multiple finder.
    All referenced finders are executed, and all results are merged.
    """
    
    def __init__(self, description=None):
        super().__init__(description)
        self.__finders = []
    
    @property
    def finders(self):
        return self.__finders
    
    def add_finder(self, finder):
        """
        Append given finder in or succession.
        @param finder A finder
        """
        self.__finders.append(finder)

    def add_finders(self, other_finder):
        """
        @param other_finder Other OrFinder to merge with
        """
        for finder in other_finder.finders:
            self.add_finder(finder)

    def _find_all(self, find_context, find_parameters):
        context = self.update_context(find_context)
        parameters = self.update_parameters(find_parameters)
        
        res = []
        exc_previous = None
        sub_find_parameters = parameters.get_next_level()
        
        # Prepare analyze time spent
        if parameters.analyze_time_spent:
            start = Tools.timer_s()

        for index, finder in enumerate(self.__finders):
            try:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"{self._get_indent_string_level(parameters)}[OrFinder({self.element_description})[{index}]:{finder.element_description}] begin")
                beg = Tools.timer_s()
                
                try:
                    self._add_candidates(res, finder.find_all(context, sub_find_parameters))
                except NoSuchElementException as exc:
                    if exc_previous is None:
                        exc_previous = exc
                
                end = Tools.timer_s()
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"{self._get_indent_string_level(parameters)}[OrFinder({self.element_description})[{index}]:{finder.element_description}] end ({end-beg} s)")
            except TechnicalException as exc:
                raise TechnicalException(f"[OrFinder({self.element_description})[{index}]:{finder.element_description}] {exc.message}") from exc
        
        # Analyze time spent
        if parameters.analyze_time_spent:
            duration = Tools.timer_s() - start
            if duration > Config.threshold_warn_time_spent_s:
                logger.warning(f"OrFinder[{self.element_description}].findAll end (took {duration} s)     ->  {len(res)} elements")

        if len(res) == 0 and exc_previous is not None:
            Tools.raise_same_exception_type(exc_previous, f"Unable to find {self.element_description} in {find_context.get_find_type_container_description_prefix()}{find_context.get_input_complete_description_and_details()}")
        return res
    
    def is_valid_input(self, container, find_context, find_parameters):
        return self._is_valid_input_in(self.__finders, container, find_context, find_parameters)
    
    def is_valid_output(self, element, find_context, find_parameters):
        return self._is_valid_output_in(self.__finders, element, find_context, find_parameters)
    
    
    