# -*- coding: utf-8 -*-

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

import os.path
import sys
import logging


# Add testing solution sources paths
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

# Add HolAdo source paths (needed when using a clone of HolAdo project)
from initialize_holado import insert_holado_source_paths
insert_holado_source_paths()


# Configure HolAdo
import holado
# Initialize HolAdo:
#    - log_level is set to INFO for initialization phase, it will be overwrite by level in logging config file
#    - log_on_console is True for initialization phase, it will be set to False when root log file will be defined
#    - logging config file
from test_holado.test_holado_session_context import TestHoladoSessionContext
holado.initialize(TSessionContext=TestHoladoSessionContext, logging_config_file_path=os.path.join(here, 'logging.conf'), log_level=logging.INFO, log_on_console=True)



# Import generic environment methods
from holado_test.behave.behave_environment import *  # @UnusedWildImport

# Define project specific environment methods

