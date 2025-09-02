
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

logger = logging.getLogger(__name__)


class HALogger(logging.Logger):
    default_message_size_limit = None
    
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
    
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, msg_size_limit=None):
        # def find_handlers(logger_):
        #     index = 0
        #     while len(logger_.handlers) == 0:
        #         if logger_.parent is not None:
        #             logger_ = logger_.parent
        #             index += 1
        #         else:
        #             break
        #     return index, logger_.handlers
        # print(f"-------------- {id(self)} | {self.name} | {level}/{self.getEffectiveLevel()} | {msg} | {find_handlers(self)=} | {self.filters=}")
        try:
            from holado_core.common.tools.tools import Tools
        except ImportError as exc:
            if "Python is likely shutting down" in str(exc):
                return
            else:
                raise exc
        
        if msg_size_limit is None:
            msg_size_limit = HALogger.default_message_size_limit
        msg_to_log = Tools.truncate_text(msg, msg_size_limit)
            
        logging.Logger._log(self, level, msg_to_log, args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)
    
    # def setLevel(self, level)->None:
    #     logger.print(f"Change logger {self} level to {level}")
    #     logging.Logger.setLevel(self, level)
    
class HARootLogger(HALogger):
    """
    Implementation is a copy of logging.RootLogger
    """
    def __init__(self, level):
        """
        Initialize the logger with the name "root".
        """
        super().__init__("root", level)

    def __reduce__(self):
        return logging.getLogger, ()




    