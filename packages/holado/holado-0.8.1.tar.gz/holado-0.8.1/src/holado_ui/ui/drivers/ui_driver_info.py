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
from holado_core.common.drivers.tree_driver import TreeDriver

logger = logging.getLogger(__name__)



class UIDriverInfo(object):
    """ Information on a generic UI driver
    """
    
    def __init__(self, driver_uid, driver, is_hidden):
        self.__driver_uid = driver_uid
        self.__driver = driver
        self.__is_hidden = is_hidden
    
    @property
    def uid(self):
        return self.__driver_uid
    
    @property
    def driver(self):
        return self.__driver
    
    @property
    def is_hidden(self):
        return self.__is_hidden
    
    
    
    
    