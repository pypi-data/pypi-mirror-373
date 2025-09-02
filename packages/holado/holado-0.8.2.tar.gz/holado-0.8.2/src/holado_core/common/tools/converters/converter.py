#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_core.common.exceptions.technical_exception import TechnicalException
import io



class Converter(object):
    
    @classmethod
    def is_boolean(cls, value):
        return isinstance(value, bool)\
            or isinstance(value, str) and (value == "False" or value == "True")

    @classmethod
    def to_boolean(cls, value):
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value == "True":
                return True
            elif value == "False":
                return False
            else:
                raise TechnicalException(f"String value '{value}' is not a boolean")
        else:
            from holado_python.standard_library.typing import Typing
            raise TechnicalException(f"Value [{value}] (type: {Typing.get_object_class_fullname(value)}) is not a boolean")

    @classmethod
    def is_dict(cls, obj):
        return isinstance(obj, dict)

    @classmethod
    def to_dict(cls, value):
        if isinstance(value, dict):
            return value
        else:
            return dict(value)

    @classmethod
    def is_list(cls, obj):
        return isinstance(obj, list)

    @classmethod
    def to_list(cls, value):
        if value is None:
            return None
        elif isinstance(value, list):
            return value
        elif cls.is_iterable(value):
            return list(value)
        else:
            from holado_python.standard_library.typing import Typing
            raise TechnicalException(f"Unmanaged convertion to list of object of type {Typing.get_object_class_fullname(value)}")

    @classmethod
    def is_integer(cls, value):
        try:
            int(value)
        except ValueError:
            return False
        else:
            return True

    @classmethod
    def to_integer(cls, value):
        if isinstance(value, int):
            return value
        else:
            return int(value)

    @classmethod
    def is_float(cls, value):
        try:
            float(value)
        except ValueError:
            return False
        else:
            return True

    @classmethod
    def to_float(cls, value):
        if isinstance(value, float):
            return value
        else:
            return float(value)
        
    @classmethod
    def is_primitive(cls, obj):
        from holado_python.standard_library.typing import Typing
        return (not hasattr(obj, '__dict__') or type(obj) == type) and not Typing.is_NamedTuple(obj)
        
    @classmethod
    def is_iterable(cls, obj):
        try:
            _ = (e for e in obj)
        except TypeError:
            return False
        else:
            return True
    
    @classmethod
    def is_file_like(cls, obj):
        return isinstance(obj, io.TextIOBase) or isinstance(obj, io.BufferedIOBase) or isinstance(obj, io.RawIOBase) or isinstance(obj, io.IOBase)



