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
from holado_core.common.inspectors.inspector import Inspector
from holado_core.common.finders.tools.enums import FindType
from holado_core.common.finders.then_finder import ThenFinder
import abc
from holado_core.common.inspectors.tools.inspect_context import InspectContext
from holado_core.common.inspectors.tools.inspect_parameters import InspectParameters

logger = logging.getLogger(__name__)



class ElementInspector(Inspector):
    """ Base class for inspector on elements.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        super().__init__(module_name)
    
    def get_finder_element_in(self, finder_container, finder_element, inspect_context:InspectContext=None, inspect_parameters:InspectParameters=None):
        """
        Find element with given finder, in given container
        @param finder_container Finder for container
        @param finder_element Finder for element to find
        @param inspect_context Inspect context
        @param inspect_parameters Inspect parameters
        @return Finder
        """
        if finder_container is None or finder_element is None:
            return self._build_result_finder(finder_element, inspect_context, inspect_parameters)

        res = ThenFinder(f"{finder_element.element_description} in {finder_container.element_description}")

        # Find container
        res.set_next_finder(finder_container)

        # Then find element in container
        res.set_next_finder(FindType.In, True, finder_element)

        return self._build_result_finder(res, inspect_context, inspect_parameters)
    
    
    
    