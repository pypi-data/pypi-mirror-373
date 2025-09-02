# -*- coding: utf-8 -*-

import os
import sys
import logging



# Add testing solution project source path
here = os.path.abspath(os.path.dirname(__file__))
source_path = os.path.normpath(os.path.join(here, 'src'))
sys.path.insert(0, source_path)

# Add HolAdo source paths (needed when using a clone of HolAdo project)
from initialize_holado import insert_holado_source_paths
insert_holado_source_paths()


# Configure HolAdo
import holado
from context.session_context import TSSessionContext
# holado.initialize(TSessionContext=TSSessionContext, 
holado.initialize(TSessionContext=None, 
                  logging_config_file_path=os.path.join(here, 'logging.conf'), log_level=logging.INFO,
                  garbage_collector_periodicity=None)


# Import generic environment methods
from behave_environment import *

# Define project specific environment methods
# TestConfig.profile_memory_in_features = True
# TestConfig.profile_memory_in_scenarios = True



