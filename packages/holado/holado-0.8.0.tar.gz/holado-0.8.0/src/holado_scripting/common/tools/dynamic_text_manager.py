
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
from holado.holado_config import Config
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class DynamicTextManager(object):
    """
    @summary: Dynamic text manager.
    For every text it manages, it modifies the texts by adding a dynamic suffix.
    The suffix is computed from the timestamp of the moment when the text is registered to be dynamic.
    
    The scope of the text can be specified, so that the same text can have a different suffix by scope.
    Usual usage is to use the thread id as scope, so that the same text has a different suffix by thread.
    The default scope is None.
    """
    
    def __init__(self, name):
        self.__name = name
        self.__texts = {}
        self.__unique_value_manager = None

    def initialize(self, unique_value_manager):
        self.__unique_value_manager = unique_value_manager
        
    def __set_text(self, scope, key, value):
        if scope not in self.__texts:
            self.__texts[scope] = {}
        self.__texts[scope][key] = value
        
    def has(self, text, scope=None):
        return self.__has_text(text, scope=scope)
    
    def get(self, text, is_dynamic=True, scope=None):
        if is_dynamic:
            return self.__get_text(text, scope=scope)
        else:
            return text
        
    def __get_text(self, text, scope=None):
        if not self.__has_text(text, scope=scope):
            self.__new_text(text, scope=scope)
        return self.__texts[scope][text]
        
    def __has_text(self, text, scope=None):
        return scope in self.__texts and text in self.__texts[scope]
    
    def __new_text(self, text, scope=None):
        # Compute text with unique suffix
        suffix = self.__unique_value_manager.new_string(padding_length=Config.unique_string_padding_length)
        res = text + suffix

        # Store dynamic text
        self.__set_text(scope, text, res)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.__name}] New dynamic text in scope {scope}: [{text}] -> [{res}]")

