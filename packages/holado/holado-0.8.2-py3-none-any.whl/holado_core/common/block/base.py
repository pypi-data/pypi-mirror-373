
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

from builtins import super
import abc
from datetime import datetime
import logging
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class BaseBlock(object):
    '''
    Base class for blocks
    '''
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, ID=None):
        super().__init__()
        self.__id = ID if ID is not None else name
        self.__name = name
        
        self.__start_dt = None
        self.__end_dt = None

    @property
    def ID(self):
        return self.__id
    
    @ID.setter
    def ID(self, id_):
        self.__id = id_

    @property
    def name(self):
        return self.__name

    @property
    def start_datetime(self):
        return self.__start_dt

    @property
    def end_datetime(self):
        return self.__end_dt

    @property
    def duration(self):
        if self.__start_dt is not None and self.__end_dt is not None:
            return self.__end_dt - self.__start_dt
        else:
            return None
    
    @abc.abstractmethod
    def process(self):
        raise NotImplementedError

    def _process_start(self):
        self.__start_dt = datetime.now()

    def _process_end(self):
        self.__end_dt = datetime.now()
    


class BaseScope(BaseBlock):
    '''
    Base class for scope blocks
    '''
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, ID=None):
        super().__init__(name, ID=ID)
        self.__content = []
    
    def process(self, *args, **kwargs):
        """
        Process the scope.
        Returns last scope step result
        """
        res = None
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Processing scope [{self.name}]: begin")
        
        self._process_start()
        try:
            res = self._process_blocks(*args, **kwargs)
        finally:
            self._process_end()
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Processing scope [{self.name}]: end")

        return res
    
    def _process_blocks(self, *args, **kwargs):
        """
        Process inner blocks of the scope.
        Returns last scope step result
        """
        res = None
        for block in self.__content:
            res = block.process(*args, **kwargs)
        return res
    
    def add_block(self, block):
        self.__content.append(block)
        
    def add_method_call(self, func, *args, **kwargs):
        from holado_core.common.block.block_method import BlockMethod
        self.add_block( BlockMethod(func, *args, **kwargs) )
        
    
