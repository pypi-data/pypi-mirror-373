
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

from holado.common.context.session_context import SessionContext
import logging
from holado_core.common.tables.table import Table
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class TesterTools(object):
    
    __logger_is_configured = False
    
    @classmethod
    def __configure_logger(cls):
        if not cls.__logger_is_configured:
            if cls.__get_report_manager().has_report_path:
                file_path = cls.__get_report_manager().get_path("logs", "tester.log")
                SessionContext.instance().log_manager.add_file_handler(file_path, logger)
            __logger_is_configured = True
    
    @classmethod
    def __get_report_manager(cls):
        return SessionContext.instance().report_manager
    
    @classmethod
    def log(cls, msg, unlimited=False):
        cls.__configure_logger()
        
        if unlimited:
            logger.print(msg, msg_size_limit=-1)
        else:
            # logger.info(msg)
            logger.print(msg)
        
    @classmethod
    def represent(cls, obj):
        if isinstance(obj, Table):
            res = obj.represent()
        else:
            # res = str(obj)
            res = Tools.represent_object(obj)
        return res

