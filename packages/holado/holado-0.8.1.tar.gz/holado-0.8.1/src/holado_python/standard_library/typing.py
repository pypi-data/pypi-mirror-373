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
from typing import NamedTuple, get_origin
from typing import types  # @UnresolvedImport
from holado_core.common.handlers.enums import AccessType
import inspect
from holado_core.common.exceptions.technical_exception import TechnicalException


logger = logging.getLogger(__name__)


class Typing(object):
    
    @classmethod
    def is_NamedTuple(cls, obj=None, class_=None):
        # if obj is not None:
        #     class_ = type(obj)
        # return hasattr(class_, '__orig_bases__') and class_.__orig_bases__[0] == NamedTuple
        if obj is not None:
            return (hasattr(obj, "__base__") and obj.__base__ == tuple or not hasattr(obj, "__dict__")) \
                and hasattr(obj, '_fields') and len(obj._fields) > 0 and any(map(lambda x:isinstance(x, str), obj._fields))
        else:
            return hasattr(class_, '__orig_bases__') and class_.__orig_bases__[0] == NamedTuple
    
    @classmethod
    def is_Generic(cls, generic_name, obj=None, class_=None):
        if obj is not None:
            class_ = type(obj)
        return hasattr(class_, '_name') and class_._name == generic_name
    
    @classmethod
    def is_List(cls, obj=None, class_=None):
        return cls.is_Generic('List', obj, class_)
    
    @classmethod
    def is_Dict(cls, obj=None, class_=None):
        return cls.is_Generic('Dict', obj, class_)
    
    @classmethod
    def is_typing_type(cls, class_):
        return get_origin(class_) is not None
    
    @classmethod
    def get_origin_type(cls, class_):
        if class_ is not None and cls.is_typing_type(class_):
            orig_type = get_origin(class_)
            if type(orig_type) == type:
                return orig_type
            else:
                return None
        else:
            return class_
    
    @classmethod
    def is_function(cls, target):
        return isinstance(target, types.FunctionType)
    
    @classmethod
    def is_method(cls, target):
        return isinstance(target, types.MethodType)
    
    @classmethod
    def get_method_function(cls, target):
        return target.__func__
    
    @classmethod
    def get_method_object_instance(cls, target):
        return target.__self__
    
    @classmethod
    def get_function_qualname(cls, target):
        return target.__qualname__
    
    @classmethod
    def get_function_fullname(cls, target):
        func_qualname = cls.get_function_qualname(target)
        if hasattr(target, "__module__"):
            return target.__module__ + "." + func_qualname
        else:
            return func_qualname
    
    
    @classmethod
    def get_class_name(cls, class_):
        return class_.__name__
    
    @classmethod
    def get_class_fullname(cls, class_):
        if class_ is None:
            return None
        
        class_name = cls.get_class_name(class_)
        if hasattr(class_, "__module__"):
            return class_.__module__ + "." + class_name
        else:
            return class_name
    
    @classmethod
    def get_object_class(cls, obj):
        if hasattr(obj, "__class__"):
            return obj.__class__
        else:
            return type(obj)
    
    @classmethod
    def get_object_class_name(cls, obj):
        return cls.get_object_class(obj).__name__
    
    @classmethod
    def get_object_class_fullname(cls, obj):
        obj_class_name = cls.get_object_class_name(obj)
        if hasattr(obj, "__module__"):
            return obj.__module__ + "." + obj_class_name
        else:
            return obj_class_name
    
    @classmethod
    def get_object_attributes(cls, obj, access_type=AccessType.Public):
        if hasattr(obj, "__module__") and getattr(obj, "__module__") == 'zeep.objects' and hasattr(obj, "__values__"):
            # Manage zeep objects separately
            d = getattr(obj, "__values__")
            return [(key, d[key]) for key in sorted(d)]
        elif Typing.is_NamedTuple(obj):
            return [(k, getattr(obj, k)) for k in obj._fields]
        else:
            try:
                try:
                    if not hasattr(obj, '__bases__'):
                        obj.__bases__ = ()
                except KeyError:
                    obj.__bases__ = ()
                except AttributeError:
                    pass
            
                if access_type == AccessType.Public:
                    return [(name, member) for name, member in inspect.getmembers(obj, lambda a: not inspect.isroutine(a)) if not name.startswith('_')]
                elif access_type == AccessType.Protected:
                    return [(name, member) for name, member in inspect.getmembers(obj, lambda a: not inspect.isroutine(a)) if not name.startswith('__')]
                elif access_type == AccessType.Private:
                    return [(name, member) for name, member in inspect.getmembers(obj, lambda a: not inspect.isroutine(a))]
                else:
                    raise TechnicalException(f"Unmanaged access type '{access_type}'")
            except ModuleNotFoundError:
                return []
    
    @classmethod
    def get_object_attribute_names(cls, obj):
        if hasattr(obj, "__module__") and getattr(obj, "__module__") == 'zeep.objects' and hasattr(obj, "__values__"):
            # Manage zeep objects separately
            d = getattr(obj, "__values__")
            return [key for key in sorted(d)]
        else:
            return [name for name, _ in inspect.getmembers(obj, lambda a: not inspect.isroutine(a)) if not name.startswith('_')]
    
    @classmethod
    def get_object_attribute_values_by_name(cls, obj):
        if hasattr(obj, "__module__") and getattr(obj, "__module__") == 'zeep.objects' and hasattr(obj, "__values__"):
            # Manage zeep objects separately
            return getattr(obj, "__values__")
        else:
            return {name: member for name, member in inspect.getmembers(obj, lambda a: not inspect.isroutine(a)) if not name.startswith('_')}
    
    @classmethod
    def get_class_for_type_name(cls, type_name):
        type_name_splitted = type_name.split('.')
        if len(type_name_splitted) > 1:
            module = __import__(type_name_splitted[0])
            for name in type_name_splitted[1:-1]:
                module = getattr(module, name)
            res = getattr(module, type_name_splitted[-1])
        else:
            res = globals()[type_name]
            
        return res

    
    

