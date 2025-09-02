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



def configure(use_holado_logger=True, logging_config_file_path=None, log_level=None, log_on_console=False, log_in_file=True):
    from holado_logging.common.logging.log_config import LogConfig
    LogConfig.configure(use_holado_logger=use_holado_logger, config_file_path=logging_config_file_path, log_level=log_level, log_on_console=log_on_console, log_in_file=log_in_file)
    
def dependencies():
    return None

def initialize_and_register():
    from holado.common.context.session_context import SessionContext
    from holado_logging.common.logging.log_manager import LogManager
    
    log_manager = LogManager()
    log_manager.configure()
    log_manager.initialize()
    
    SessionContext.instance().services.register_service_instance("log_manager", log_manager, SessionContext.instance(), 
                                                                 raise_if_service_exist=False, raise_if_object_exist=False)

