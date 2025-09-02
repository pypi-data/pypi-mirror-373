
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
from holado_core.common.exceptions.technical_exception import TechnicalException
import abc
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class Type(object):
    """
    Manage actions related to a specific protobuf type
    """
    __metaclass__ = abc.ABCMeta

    @classmethod
    def protobuf_class(cls):
        raise NotImplementedError('Method not implemented!')
    
    @classmethod
    def is_instance_of(cls, obj, raise_exception=False):
        res = isinstance(obj, cls.protobuf_class())
        if not res and raise_exception:
            raise TechnicalException(f"Object has to be of protobuf type {cls.protobuf_class()} (obtained type: {Typing.get_object_class_fullname(obj)}")
        return res
        
    @classmethod
    def set_object_value(cls, obj, value, raise_exception=False):
        cls.is_instance_of(obj, raise_exception=True)
        return cls._set_object_value(obj, value, raise_exception=raise_exception)


    