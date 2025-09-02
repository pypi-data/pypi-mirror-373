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
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class FeatureClassResourceByName(object):
    __registered_resources_by_class_and_name = {}
    __ordered_resource_names_by_class = {}
    
    @classmethod
    def _get_class_resource_description(cls, plural=False):
        if plural:
            return 'class resources'
        else:
            return 'class resource'
    
    @classmethod
    def _clear_class_registered_resources(cls):
        cls_name = Typing.get_class_fullname(cls)
        if cls_name in cls.__registered_resources_by_class_and_name:
            cls.__registered_resources_by_class_and_name[cls_name].clear()
            cls.__ordered_resource_names_by_class[cls_name].clear()
    
    @classmethod
    def _get_class_registered_resources(cls):
        cls_name = Typing.get_class_fullname(cls)
        if cls_name in cls.__registered_resources_by_class_and_name:
            return dict(cls.__registered_resources_by_class_and_name[cls_name])
        else:
            return {}
    
    @classmethod
    def register_resource_in_class(cls, name, resource, index=-1):
        cls_name = Typing.get_class_fullname(cls)
        if cls_name not in cls.__registered_resources_by_class_and_name:
            cls.__registered_resources_by_class_and_name[cls_name] = {}
            cls.__ordered_resource_names_by_class[cls_name] = []
            
        cls.__registered_resources_by_class_and_name[cls_name][name] = resource
        
        while name in cls.__ordered_resource_names_by_class[cls_name]:
            cls.__ordered_resource_names_by_class[cls_name].remove(name)
        if index < 0:
            cls.__ordered_resource_names_by_class[cls_name].append(name)
        else:
            cls.__ordered_resource_names_by_class[cls_name].insert(index, name)
        if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
            logger.trace(f"[{Typing.get_class_fullname(cls)}] Registered class resources: {cls.__ordered_resource_names_by_class[cls_name]}")
    
    @classmethod
    def import_registered_resources_in_class(cls, class_=None, obj=None, index=-1):
        if class_ is not None and issubclass(class_, FeatureClassResourceByName):
            resources_to_import_by_name = class_._get_class_registered_resources()
            ordered_resource_names_to_import = class_.get_class_resource_names()
        elif obj is not None and isinstance(obj, FeatureClassResourceByName):
            resources_to_import_by_name = obj._get_class_registered_resources()
            ordered_resource_names_to_import = obj.get_class_resource_names()
        elif obj is not None and isinstance(obj, FeatureObjectResourceByName):
            resources_to_import_by_name = obj._registered_resources
            ordered_resource_names_to_import = obj.get_resource_names()
        else:
            raise TechnicalException(f"Unmanaged import registered {cls._get_class_resource_description(True)} from (class_={class_} ; type(obj)={Typing.get_object_class_fullname(obj)})")
        
        for name in ordered_resource_names_to_import:
            cls.register_resource_in_class(name, resources_to_import_by_name[name], index=index)
        
    @classmethod
    def get_class_resource(cls, name, raise_if_not_found=True):
        registered_resources = cls._get_class_registered_resources()
        if name in registered_resources:
            return registered_resources[name]
        
        if raise_if_not_found:
            raise ElementNotFoundException(f"Not found {cls._get_class_resource_description()} of name '{name}' in registered {cls._get_class_resource_description(True)} {list(registered_resources.keys())}")
        else:
            return None
        
    @classmethod
    def get_class_resource_names(cls):
        cls_name = Typing.get_class_fullname(cls)
        if cls_name in cls.__ordered_resource_names_by_class:
            return list(cls.__ordered_resource_names_by_class[cls_name])
        else:
            return []


class FeatureObjectResourceByName(object):
    def __init__(self):
        self.__registered_resources_by_name = {}
        self.__ordered_resource_names = []
    
    @property
    def _registered_resources(self):
        return dict(self.__registered_resources_by_name)
    
    def _get_resource_description(self, plural=False):
        if plural:
            return 'resources'
        else:
            return 'resource'
    
    def _clear_registered_resources(self):
        self.__registered_resources_by_name.clear()
        self.__ordered_resource_names.clear()
    
    def register_resource(self, name, resource, index=-1):
        self.__registered_resources_by_name[name] = resource
        
        while name in self.__ordered_resource_names:
            self.__ordered_resource_names.remove(name)
        if index < 0:
            self.__ordered_resource_names.append(name)
        else:
            self.__ordered_resource_names.insert(index, name)
        if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
            logger.trace(f"[{Typing.get_object_class_fullname(self)}] Registered resources: {self.__ordered_resource_names}")
    
    def import_registered_resources(self, class_=None, obj=None, index=-1):
        if class_ is not None and issubclass(class_, FeatureClassResourceByName):
            resources_to_import_by_name = class_._get_class_registered_resources()
            ordered_resource_names_to_import = class_.get_class_resource_names()
        elif obj is not None and isinstance(obj, FeatureClassResourceByName):
            resources_to_import_by_name = obj._get_class_registered_resources()
            ordered_resource_names_to_import = obj.get_class_resource_names()
        elif obj is not None and isinstance(obj, FeatureObjectResourceByName):
            resources_to_import_by_name = obj._registered_resources
            ordered_resource_names_to_import = obj.get_resource_names()
        else:
            raise TechnicalException(f"Unmanaged import registered {self._get_resource_description(True)} from (class_={class_} ; type(obj)={Typing.get_object_class_fullname(obj)})")
        
        for name in ordered_resource_names_to_import:
            self.register_resource(name, resources_to_import_by_name[name], index=index)
    
    def get_resource(self, name, raise_if_not_found=True):
        if name in self.__registered_resources_by_name:
            return self.__registered_resources_by_name[name]
        
        if raise_if_not_found:
            raise ElementNotFoundException(f"Not found {self._get_resource_description()} of name '{name}' in registered {self._get_resource_description(True)} {list(self.__registered_resources_by_name.keys())}")
        else:
            return None
    
    def get_resource_names(self):
        return list(self.__ordered_resource_names)


class FeatureObjectOverClassResourceByName(FeatureObjectResourceByName):
    def __init__(self):
        super().__init__()

    def get_resource(self, name, raise_if_not_found=True):
        res = super().get_resource(name, raise_if_not_found=False)
        if not res:
            res = self.get_class_resource(name, raise_if_not_found=False)
        
        if not res and raise_if_not_found:
            raise ElementNotFoundException(f"Not found {self._get_resource_description()} of name '{name}' in registered {self._get_resource_description(True)} {list(self._registered_resources.keys())} and registered {self._get_class_resource_description(True)} {list(self._get_class_registered_resources().keys())}")
        return res
    
    def get_resource_names(self):
        res = super().get_resource_names()
        class_resource_names = self.get_class_resource_names()
        for name in class_resource_names:
            res.append(name)
        return res


class FeatureObjectAndClassResourceByName(FeatureObjectOverClassResourceByName, FeatureClassResourceByName):
    def __init__(self):
        FeatureObjectOverClassResourceByName.__init__(self)


