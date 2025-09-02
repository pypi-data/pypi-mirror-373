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

from holado_core.common.exceptions.element_exception import ElementNotFoundException
from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado.common.handlers.undefined import undefined_argument
from holado_core.common.handlers.features.resource_by_name import FeatureClassResourceByName,\
    FeatureObjectResourceByName
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class FeatureClassResourceByType(FeatureClassResourceByName):
    @classmethod
    def _get_class_resource_description(cls, plural=False):
        if plural:
            return 'class resources by type'
        else:
            return 'class resource by type'
    
    @classmethod
    def register_resource_for_type_in_class(cls, name, is_class_func, is_obj_func, resource, index=-1):
        super().register_resource_in_class(name, (is_class_func, is_obj_func, resource), index=index)
    
    @classmethod
    def import_registered_resources_in_class(cls, class_=None, obj=None):
        if (class_ is not None and issubclass(class_, FeatureClassResourceByType)
            or obj is not None 
                and (isinstance(obj, FeatureClassResourceByType) or isinstance(obj, FeatureObjectResourceByType) ) ):
            super(FeatureClassResourceByType, cls).import_registered_resources_in_class(class_=class_, obj=obj)
        else:
            raise TechnicalException(f"Unmanaged import registered {cls._get_class_resource_description(True)} from (class_={class_} ; type(obj)={Typing.get_object_class_fullname(obj)})")
    
    @classmethod
    def get_class_resource_for_type(cls, class_=None, obj=undefined_argument, raise_if_not_found=True):
        # Replace a 'typing' class description by a real class
        #TODO: manage Union class_ by looping on union types
        real_class = Typing.get_origin_type(class_)
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[{Typing.get_class_fullname(cls)}] Finding class resource in {cls.get_class_resource_names()} for type '{Typing.get_class_fullname(class_)}'" + (f" and object of type '{Typing.get_object_class_fullname(obj)}'" if obj is not undefined_argument else ""))
        res = None
        for resource_name in cls.get_class_resource_names():
            is_class_func, is_obj_func, resource = cls.get_class_resource(resource_name)
            try:
                # Note: start by using is_obj_func and/or obj as it can be more accurate
                if is_obj_func is not None and obj is not undefined_argument:
                    if is_obj_func(obj):
                        res = resource
                elif is_class_func is not None:
                    if obj is not undefined_argument:
                        if is_class_func(type(obj)):
                            res = resource
                    elif real_class is not None:
                        if is_class_func(real_class):
                            res = resource
            except Exception:
                real_class_descr = '' if real_class == class_ else f' ; real class={real_class}'
                # raise TechnicalException(f"Error while getting {cls._get_class_resource_description()} named '{resource_name}' and associated to (class={class_}{real_class_descr} ; type(obj)={Typing.get_object_class_fullname(obj)}) in registered {cls._get_class_resource_description(True)} {list(cls._get_class_registered_resources())}") from exc
                if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"Error while getting {cls._get_class_resource_description()} named '{resource_name}' and associated to (class={class_}{real_class_descr} ; type(obj)={Typing.get_object_class_fullname(obj)}) in registered {cls._get_class_resource_description(True)} {list(cls._get_class_registered_resources())}")
                    
            if res is not None:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[{Typing.get_class_fullname(cls)}] Found class resource '{resource_name}' for type '{Typing.get_class_fullname(class_)}'" + (f" and object of type '{Typing.get_object_class_fullname(obj)}'" if obj is not undefined_argument else ""))
                return res
            else:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[{Typing.get_class_fullname(cls)}] Class resource '{resource_name}' doesn't match for type '{Typing.get_class_fullname(class_)}'" + (f" and object of type '{Typing.get_object_class_fullname(obj)}'" if obj is not undefined_argument else ""))
       
        if raise_if_not_found:
            raise ElementNotFoundException(f"Not found {cls._get_class_resource_description()} associated to (class={class_} ; type(obj)={Typing.get_object_class_fullname(obj)}) in registered {cls._get_class_resource_description(True)} {list(cls._get_class_registered_resources())}")
        else:
            return None


class FeatureObjectResourceByType(FeatureObjectResourceByName):
    def __init__(self):
        super().__init__()
        
    def _get_resource_description(self, plural=False):
        if plural:
            return 'resources by type'
        else:
            return 'resource by type'
        
    def register_resource_for_type(self, name, is_class_func, is_obj_func, resource, index=-1):
        self.register_resource(name, (is_class_func, is_obj_func, resource))
        
    def import_registered_resources(self, class_=None, obj=None):
        if (class_ is not None and issubclass(class_, FeatureClassResourceByType)
            or obj is not None 
                and (isinstance(obj, FeatureClassResourceByType) or isinstance(obj, FeatureObjectResourceByType) ) ):
            super().import_registered_resources(class_=class_, obj=obj)
        else:
            raise TechnicalException(f"Unmanaged import registered {self._get_resource_description(True)} from (class_={class_} ; type(obj)={Typing.get_object_class_fullname(obj)})")
        
    def get_resource_for_type(self, class_=None, obj=undefined_argument, raise_if_not_found=True):
        # Replace a 'typing' class description by a real class
        #TODO: manage Union class_ by looping on union types
        real_class = Typing.get_origin_type(class_)
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[{Typing.get_object_class_fullname(self)}] Finding resource in {self.get_resource_names()} matching for type '{Typing.get_class_fullname(class_)}'" + (f" and object of type '{Typing.get_object_class_fullname(obj)}'" if obj is not undefined_argument else ""))
        res = None
        for resource_name in self.get_resource_names():
            is_class_func, is_obj_func, resource = self.get_resource(resource_name)
            try:
                # Note: start by using is_obj_func and/or obj as it can be more accurate
                if is_obj_func is not None and obj is not undefined_argument:
                    if is_obj_func(obj):
                        res = resource
                    else:
                        # Current resource is not matchine
                        pass
                elif is_class_func is not None:
                    if obj is not undefined_argument:
                        if is_class_func(type(obj)):
                            res = resource
                        else:
                            # Current resource is not matchine
                            pass
                    elif real_class is not None:
                        if is_class_func(real_class):
                            res = resource
                    else:
                        raise TechnicalException(f"Unexpected case")
                else:
                    raise TechnicalException(f"Unexpected case")
            except Exception as exc:
                raise TechnicalException(f"Error while getting {self._get_resource_description()} named '{resource_name}' and associated to (class={class_} ; type(obj)={Typing.get_object_class_fullname(obj)}) in registered {self._get_resource_description(True)} {list(self._registered_resources.keys())}") from exc
            
            if res is not None:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[{Typing.get_object_class_fullname(self)}] Found resource '{resource_name}' for type '{Typing.get_class_fullname(class_)}'" + (f" and object of type '{Typing.get_object_class_fullname(obj)}'" if obj is not undefined_argument else ""))
                return res
            else:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[{Typing.get_object_class_fullname(self)}] Resource '{resource_name}' doesn't match for type '{Typing.get_class_fullname(class_)}'" + (f" and object of type '{Typing.get_object_class_fullname(obj)}'" if obj is not undefined_argument else ""))
        
        if raise_if_not_found:
            raise ElementNotFoundException(f"Not found {self._get_resource_description()} associated to (class={class_} ; type(obj)={Typing.get_object_class_fullname(obj)}) in registered {self._get_resource_description(True)} {list(self._registered_resources.keys())}")
        else:
            return None

class FeatureObjectOverClassResourceByType(FeatureObjectResourceByType):
    def __init__(self):
        super().__init__()

    def get_resource_for_type(self, class_=None, obj=undefined_argument, raise_if_not_found=True):
        res = super().get_resource_for_type(class_, obj, raise_if_not_found=False)
        if not res:
            res = self.get_class_resource_for_type(class_, obj, raise_if_not_found=False)
        
        if not res and raise_if_not_found:
            raise ElementNotFoundException(f"Not found {self._get_resource_description()} associated to (class={class_} ; type(obj)={Typing.get_object_class_fullname(obj)}) in registered {self._get_resource_description(True)} {list(self._registered_resources.keys())} and registered {self._get_class_resource_description(True)} {list(self._get_class_registered_resources().keys())}")
        return res

class FeatureObjectAndClassResourceByType(FeatureObjectOverClassResourceByType, FeatureClassResourceByType):
    def __init__(self):
        FeatureObjectOverClassResourceByType.__init__(self)


