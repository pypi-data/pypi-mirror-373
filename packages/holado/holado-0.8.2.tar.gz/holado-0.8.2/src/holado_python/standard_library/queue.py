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

import logging
import queue
import typing

logger = logging.getLogger(__name__)


class IterableQueue(queue.Queue, typing.Iterable):
    
    class Sentinel(object):
        def __eq__(self, __o: object) -> bool:
            return isinstance(__o, IterableQueue.Sentinel)
        
    __sentinel = Sentinel()
    
    
    def __init__(self, maxsize=0, block_on_get=True, block_on_get_timeout=None, block_on_put=True, block_on_put_timeout=None):
        super().__init__(maxsize if maxsize else 0)
        self.__block_on_get = block_on_get if block_on_get is not None else True
        self.__block_on_get_timeout = block_on_get_timeout
        self.__block_on_put = block_on_put if block_on_put is not None else True
        self.__block_on_put_timeout = block_on_put_timeout

    def __iter__(self):
        return iter(self.get, self.__sentinel)

    def __len__(self):
        return self.qsize()

    def close(self):
        self.put(self.__sentinel)
            
    def get(self):
        res = super().get(block=self.__block_on_get, timeout=self.__block_on_get_timeout)
        
        # Put again the sentinel in case of multiple readers
        if self.is_sentinel(res):
            self.put(res)
            
        return res
    
    def put(self, item):
        return super().put(item, block=self.__block_on_put, timeout=self.__block_on_put_timeout)
    
    def is_sentinel(self, item):
        return item == self.__sentinel
    

class IterableLifoQueue(IterableQueue):
    '''Copyt of implementation of queue.LifoQueue but inheriting of IterableQueue.'''

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.pop()
    
    
    
