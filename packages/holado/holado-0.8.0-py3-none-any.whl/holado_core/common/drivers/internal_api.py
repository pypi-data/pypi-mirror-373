#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
import abc

logger = logging.getLogger(__name__)



class InternalAPI(object):
    """ Base class for internal API.
    
    An internal API is an interface to internal tool that is usually an external dependency.
    The goal is to abstract all internal tools with a common API.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, driver):
        self.__driver = driver
    
    @property
    def driver(self):
        return self.__driver
    
    @property
    def internal_driver(self):
        return self.__driver.internal_driver
    
    
    