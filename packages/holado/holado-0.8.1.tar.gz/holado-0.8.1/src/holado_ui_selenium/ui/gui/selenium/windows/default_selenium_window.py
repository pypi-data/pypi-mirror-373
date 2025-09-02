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
from holado_ui_selenium.ui.gui.selenium.windows.selenium_window import SeleniumWindow
from holado_ui_selenium.ui.gui.selenium.inspectors.default_selenium_inspector import DefaultSeleniumInspector
from holado_ui_selenium.ui.gui.selenium.actors.default_selenium_actor import DefaultSeleniumActor

logger = logging.getLogger(__name__)



class DefaultSeleniumWindow(SeleniumWindow):
    """ Default Selenium window.
    """
    
    def __init__(self):
        super().__init__()
    
    def _initialize_inspect_builder(self):
        # # Get default (usually all modules and finder types)
        # res = self.inspector.inspect_builder
        #
        # # OR remove modules and add wanted with their default inspect builders
        # res = self.inspector.inspect_builder
        # res.remove_all_modules()
        # res.add_module("angular")
        # res.add_module("html")
        #
        # # OR remove a module and finder types from default inspect builders
        # res = self.inspector.inspect_builder
        # res.remove_module("angular")
        # res.get_inspect_builder_for_module("html").default_parameters.remove_finder_types([
        #         "text-node"
        #         ])
        #
        # # OR remove all finder types and add only wanted ones
        # res = self.inspector.inspect_builder
        # res.get_inspect_builder_for_module("html").default_parameters.remove_all_finder_types()
        # res.get_inspect_builder_for_module("html").default_parameters.add_finder_types([
        #         "text-node"
        #         ])
        
        # OR None to use default initialized in inspector
        res = None
        
        return res
        
    
    def _initialize_inspector(self):
        res = DefaultSeleniumInspector()
        res.initialize(self)
        return res

    def _initialize_actor(self):
        res = DefaultSeleniumActor()
        res.initialize(self)
        return res
    
    
    
    