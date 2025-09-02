
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
from behave.runner import Runner
from behave.parser import parse_feature
from holado.holado_config import Config


logger = logging.getLogger(__name__)



class IndependantRunner(Runner):
    """
    Independant Behave runner.
    
    WARNING: with current implementation, many files must exist in current working directory:
        - a folder "features" with at least one .feature file, even empty
        - a folder "steps" with a x_steps.py file importing all step files
        - a file "environment.py" containing "from XXX.behave_environment import *"
    """
    
    def __init__(self, config, step_paths=None):
        super().__init__(config)
        logger.info(f"Using behave runner IndependantRunner({step_paths=})")
        self.__step_paths = step_paths
        
    def load_step_definitions(self, extra_step_paths=None):
        # TODO: replace default implementation by loading steps in self.step_paths
        super().load_step_definitions(extra_step_paths)
        
        # logger.warning(f"++++ Loading step definitions ({self.__step_paths=})")
        # super().load_step_definitions(extra_step_paths=self.__step_paths)
        # logger.warning(f"++++ Loaded steps: {the_step_registry.steps}")
        
    def setup_paths(self):
        # TODO: replace default implementation by setting runtime defined paths passed in constructor
        super().setup_paths()
        
        # logger.warning(f"++++ setup_paths: {self.__step_paths=}")
        # self.path_manager.add(self.__step_paths)
        
    def run_model(self, features=None):
        # Use a custom feature that waits 7 days
        feature_text = \
            """
            Feature: Fake
                Scenario: Fake
                    When wait {runner_session_timeout} seconds
            """.format(runner_session_timeout=Config.session_timeout_seconds)
        feature = parse_feature(feature_text)
        
        return super().run_model([feature])


