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
from holado_core.common.finders.tools.enums import FindType
from holado_core.common.finders.tools.find_context import FindContext
from holado_core.common.finders.tools.find_parameters import FindParameters
from holado_core.common.exceptions.element_exception import NoSuchElementException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class ParentSeleniumFinder(SeleniumFinder):
    """ Finder for the parent.
    """
    
    def __init__(self, description=None):
        super().__init__(description if description else "parent")
        self.find_type = FindType.Custom
    
    def _find_all(self, find_context:FindContext, find_parameters:FindParameters):
        res = []
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            prefix_logs = f"{self._get_indent_string_level(find_parameters)}[ParentSeleniumFinder({self.element_description})._find_all]"
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{prefix_logs} -> begin in [{find_context.get_input_description()}]")
        
        try:
            parent = self.internal_api.find_parent(find_context, find_parameters)
        except NoSuchElementException:
            parent = None
        if parent is not None:
            res.add(parent)
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"{prefix_logs} -> return {len(res)} candidates:\n{self._represent_candidates_output(res, 4)}")
        
        return self._build_result_list(res, find_context, find_parameters)
    
    
    
    
    