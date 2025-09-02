
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
from holado_json.ipc.json_types import JsonTypes
from holado_core.common.handlers.features.resource_by_type import FeatureObjectAndClassResourceByType
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)

class JsonConverter(FeatureObjectAndClassResourceByType):
    
    def __init__(self):
        super().__init__()
        self.import_registered_resources_in_class(class_=JsonTypes)
    
    @classmethod
    def _get_class_resource_description(cls, plural=False):
        if plural:
            return 'class json types'
        else:
            return 'class json type'
    
    def _get_resource_description(self, plural=False):
        if plural:
            return 'json types'
        else:
            return 'json type'
    
    def to_json(self, obj):
        resource = self.get_resource_for_type(obj=obj)
        if resource[1] is not None:
            return resource[1](obj)
        else:
            raise TechnicalException(f"Resource 'to_json' is not defined for object of type {Typing.get_object_class_fullname(obj)}")
    
    def from_json_to(self, obj_json, class_, _parents=None):
        if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
            logger.trace(f"[{Typing.get_object_class_fullname(self)}] from_json_to({obj_json}, {Typing.get_class_fullname(class_)})")
        # Find resource associated to class_, else find the resource associated to json object
        resource = None
        if class_ is not None:
            resource = self.get_resource_for_type(class_=class_, raise_if_not_found=False)
        if resource is None:
            resource = self.get_resource_for_type(obj=obj_json)
        
        # If defined, use complex json conversion method, else use simple method
        if resource[2] is not None:
            return resource[2](obj_json, class_, _parents=_parents, converter=self)
        elif resource[0] is not None:
            return resource[0](obj_json)
        else:
            raise TechnicalException(f"Resource 'from_json_to' is not defined for type {class_}")
        
    
    
    
    
