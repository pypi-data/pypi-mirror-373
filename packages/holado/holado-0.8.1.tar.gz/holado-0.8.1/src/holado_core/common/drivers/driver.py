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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado.common.handlers.object import DeleteableObject
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.finders.tools.find_builder import FindBuilder
from holado.common.handlers.enums import ObjectStates

logger = logging.getLogger(__name__)



class Driver(DeleteableObject):
    """ Base class for drivers.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name=None):
        super().__init__(name or "Driver")
        
        self.__internal_driver = None
        self.__internal_api = None
        
        # Tools
        self.__text_verifier = None
        self.__find_builder = None      # Builder used to create default find context and parameters
    
    @property
    def _has_internal_driver(self):
        """
        @return If internal driver is defined
        """
        return self.__internal_driver is not None
    
    @property
    def internal_driver(self):
        """
        @return Internal driver
        """
        if not self._has_internal_driver():
            raise TechnicalException("Internal driver is not defined.")
        return self.__internal_driver
    
    @internal_driver.setter
    def internal_driver(self, internal_driver):
        self.__internal_driver = internal_driver
    
    @property
    def internal_api(self):
        """
        @return Internal API
        """
        if self.__internal_api is None:
            raise TechnicalException("Internal API is not defined.")
        return self.__internal_api
    
    @property
    def text_verifier(self):
        """
        @return Text verifier to use
        """
        if self.__text_verifier is None:
            raise TechnicalException("Text verifier is not defined")
        return self.__text_verifier
    
    @text_verifier.setter
    def text_verifier(self, text_verifier):
        """
        @param text_verifier Text verifier to use
        """
        self.__text_verifier = text_verifier
    
    @property
    def find_builder(self):
        """
        @return Find builder (if not set a default one is instantiated)
        """
        if self.__find_builder is None:
            self.__find_builder = FindBuilder()
        return self.__find_builder
    
    @find_builder.setter
    def find_builder(self, find_builder):
        """
        @param find_builder Find builder to use rather than default
        """
        self.__find_builder = find_builder
    
    def initialize(self):
        """
        Initialize driver
        """
        self.__internal_api = self._initialize_internal_api()
    
    def _initialize_internal_api(self):
        """
        Method used internally at driver initialization, in order to instantiate the appropriate internal API type.
        @return a new internal API instance
        """
        raise NotImplementedError

    def is_open(self):
        """
        @return True if driver is open
        """
        return self._has_internal_driver()
    
    def _verify_is_open(self):
        if not self.is_open():
            raise FunctionalException("Driver is not opened")
    
    def open(self):
        """
        Open driver
        """
        self.object_state = ObjectStates.Opening
        self._close_driver()
        self.object_state = ObjectStates.Open

    def _open_driver(self):
        """
        Implement open process
        """
        raise NotImplementedError
    
    def close(self):
        """
        Close driver
        """
        self.object_state = ObjectStates.Closing
        self._close_driver()
        self.object_state = ObjectStates.Closed
    
    def _close_driver(self):
        """
        Implement close process
        """
        raise NotImplementedError
    
    
    