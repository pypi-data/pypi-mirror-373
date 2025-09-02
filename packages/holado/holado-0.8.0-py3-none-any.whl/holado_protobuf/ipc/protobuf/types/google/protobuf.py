
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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_python.common.tools.datetime import DateTime
import re
from datetime import datetime, timedelta
from holado_protobuf.ipc.protobuf.abstracts.type import Type
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


#TODO: add all types of https://googleapis.dev/python/protobuf/latest/google/protobuf.html
 

class Duration(Type):
    """
    Manage actions with type google.protobuf.Duration
    """
    @classmethod
    def protobuf_class(cls):
        from google.protobuf.duration_pb2 import Duration as gp_Duration  # @UnresolvedImport
        return gp_Duration
    
    @classmethod
    def _set_object_value(cls, obj, value, raise_exception=False):
        if isinstance(value, cls.protobuf_class()):
            obj.CopyFrom(value)
        elif isinstance(value, timedelta):
            obj.FromTimedelta(value)
        elif isinstance(value, int) or isinstance(value, float):
            nanos = round(value * 1e9)
            obj.FromNanoseconds(nanos)
        elif isinstance(value, str):
            if re.match(r"-?\d+(?:.\d+)?s", value): 
                obj.FromJsonString(value)
            else:
                if raise_exception:
                    raise FunctionalException("For Duration objects, the value must be in a string format '-?\\d+(?:.\\d+)?s' (ex: '1s', '1.01s', '1.0000001s', '-3.100s')")
                else:
                    return False
        else:
            if raise_exception:
                raise FunctionalException(f"For Duration objects, the value must be a timedelta, an int or a string (got value type '{Typing.get_object_class_fullname(value)}')")
            else:
                return False
        return True


class Message(Type):
    """
    Manage actions with type google.protobuf.Message
    """
    @classmethod
    def protobuf_class(cls):
        from google.protobuf.message import Message as gp_Message
        return gp_Message
    
    @classmethod
    def _set_object_value(cls, obj, value, raise_exception=False):
        if value is None:
            obj.SetInParent()
        elif isinstance(value, cls.protobuf_class()):
            obj.CopyFrom(value)
        elif isinstance(value, dict):
            from google.protobuf import json_format
            json_format.ParseDict(value, obj)
        else:
            if raise_exception:
                raise FunctionalException(f"For Message objects, the value must be None or a {cls.protobuf_class()} (got value type '{Typing.get_object_class_fullname(value)}')")
            else:
                return False
        return True
        

class Timestamp(Type):
    """
    Manage actions with type google.protobuf.Timestamp
    """
    @classmethod
    def protobuf_class(cls):
        from google.protobuf.timestamp_pb2 import Timestamp as gp_Timestamp  # @UnresolvedImport
        return gp_Timestamp
    
    @classmethod
    def _set_object_value(cls, obj, value, raise_exception=False):
        if isinstance(value, cls.protobuf_class()):
            obj.CopyFrom(value)
        elif isinstance(value, datetime):
            obj.FromDatetime(value)
        elif isinstance(value, str):
            if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:.\d+)?Z", value): 
                obj.FromJsonString(value)
            elif DateTime.is_str_datetime(value):
                dt = DateTime.str_2_datetime(value)
                obj.FromDatetime(dt)
            else:
                if raise_exception:
                    raise FunctionalException("For Timestamp objects, the value must be in a string format like '2022-01-01T01:00:00Z' or '2022-01-01 01:00:00'")
                else:
                    return False
        else:
            if raise_exception:
                raise FunctionalException(f"For Timestamp objects, the value must be a datetime or a string (got value type '{Typing.get_object_class_fullname(value)}')")
            else:
                return False
        return True
        

    

    