
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
import logging
from typing import Generator, overload
from holado_core.common.exceptions.functional_exception import FunctionalException

logger = logging.getLogger(__name__)


class BaseGenerator(Generator):
    '''
    Base class for generators.
    It extends the possibilities of python generators with batch generation.
    Note: current implementation returns a batch as a list, so be careful on batch size.
    '''
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name=None, batch_size=None):
        super().__init__()
        self.__name = name if name is not None else "generator"
        self.__batch_size = batch_size
        self.__is_in_next_batch = False
        
    @property
    def name(self):
        return self.__name
    
    @property
    def batch_size(self):
        return self.__batch_size
    
    @batch_size.setter
    def batch_size(self, size):
        self.__batch_size = size
    
    @property
    def _is_in_next_batch(self):
        return self.__is_in_next_batch
    
    @overload
    # @abstractmethod
    def send(self, value):
        return Generator.send(self, value)
    
    @overload
    # @abstractmethod
    def throw(self, typ, val=None, tb=None):
        return Generator.throw(self, typ, val=val, tb=tb)
    
    def next_batch(self, size=None, raise_if_incomplete=False, raise_if_empty=True):
        """ Return a batch as a liste of defined size.
        If size parameter is not defined, batch size is supposed to be defined at generator instantiation or with property batch_size.
        If raise_if_incomplete is True, and last batch can not be of batch size, a StopIteration is thrown.
        """
        if size is None:
            if self.batch_size is None:
                raise FunctionalException(f"Undefined batch size. It can be defined at generator instantiation, with property batch_size.")
            size = self.batch_size
        
        self.__is_in_next_batch = True
        try:
            res = []
            for _ in range(size):
                try:
                    element = next(self)
                except StopIteration as exc:
                    if raise_if_empty and len(res) == 0 or raise_if_incomplete:
                        raise exc
                    else:
                        break
                else:
                    # if element is not None:
                        res.append(element)
        finally:
            self.__is_in_next_batch = False
        
        return res



