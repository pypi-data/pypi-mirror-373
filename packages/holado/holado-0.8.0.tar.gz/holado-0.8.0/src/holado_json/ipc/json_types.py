
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
import json
from holado_core.common.exceptions.technical_exception import TechnicalException
from json.decoder import JSONDecodeError
import base64
from holado_python.standard_library.typing import Typing
from typing import get_args, get_type_hints
from holado_core.common.handlers.features.resource_by_type import FeatureClassResourceByType
from holado.common.handlers.undefined import undefined_value
import inspect

logger = logging.getLogger(__name__)


# Define managed json types

class JsonTypes(FeatureClassResourceByType):
    @classmethod
    def _get_class_resource_description(cls, plural=False):
        if plural:
            return 'json types'
        else:
            return 'json type'
    
    @classmethod
    def _new_parents(cls, parents, class_, **kwargs):
        if parents is None:
            res = []
        else:
            res = list(parents)
        res.append( (class_, kwargs) )
        return res


# Register default json types

JsonTypes.register_resource_for_type_in_class('primitive', lambda c: c in [int, float, bool, type(None)], None, 
                   (lambda x: x, lambda x: x, None))
JsonTypes.register_resource_for_type_in_class('bytes', lambda c: inspect.isclass(c) and issubclass(c, bytes), None, 
                   (base64.b64decode, base64.b64encode, None))


def _to_json_from_str(value):
    try:
        return json.loads(value)
    except JSONDecodeError:
        return value

JsonTypes.register_resource_for_type_in_class('str', lambda c: inspect.isclass(c) and issubclass(c, str), None, 
                   (lambda x: x, _to_json_from_str, None))


def _from_json_to_Dict(obj_json, class_, _parents=None, converter=None):
    if not isinstance(obj_json, dict):
        raise TechnicalException(f"Argument 'obj_json' must be a dict")
    if converter is None:
        from holado_json.ipc.json_converter import JsonConverter
        converter = JsonConverter()
    
    # Define key and value types if they are available, else type of of key and value will be used
    args = get_args(class_)
    if len(args) > 0:
        if len(args) != 2:
            raise TechnicalException(f"Unmanaged convert from json to {Typing.get_class_fullname(class_)}: 2 type arguments are expected (obtained type arguments: {args})")
        key_type, value_type = args
    else:
        # Use object type of each dict key & value
        key_type, value_type = None, None
    
    res = {}
    for k, v in obj_json.items():
        key = converter.from_json_to(k, key_type, _parents=JsonTypes._new_parents(_parents, class_, name=k, index=0))
        value = converter.from_json_to(v, value_type, _parents=JsonTypes._new_parents(_parents, class_, name=k, index=1))
        res[key] = value
    
    return res

def _to_json_from_dict_or_list(value):
    try:
        tmp = json.dumps(value)
        return json.loads(tmp)
    except JSONDecodeError:
        return value
    
JsonTypes.register_resource_for_type_in_class('Dict', lambda c: inspect.isclass(c) and issubclass(c, dict), None, 
                   (None, _to_json_from_dict_or_list, _from_json_to_Dict))


def _from_json_to_List(obj_json, class_, _parents=None, converter=None):
    if not isinstance(obj_json, list):
        raise TechnicalException(f"Argument 'obj_json' must be a list")
    if converter is None:
        from holado_json.ipc.json_converter import JsonConverter
        converter = JsonConverter()
    
    element_type = get_args(class_)[0]
    
    res = []
    for index, el in enumerate(obj_json):
        res_el = converter.from_json_to(el, element_type, _parents=JsonTypes._new_parents(_parents, class_, index=index))
        res.append(res_el)
    
    return res

JsonTypes.register_resource_for_type_in_class('List', lambda c: inspect.isclass(c) and issubclass(c, list), None, 
                        (None, _to_json_from_dict_or_list, _from_json_to_List))


def _from_json_to_NamedTuple(obj_json, class_, _parents=None, converter=None):
    if not isinstance(obj_json, dict):
        raise TechnicalException(f"Argument 'obj_json' must be a dict")
    if converter is None:
        from holado_json.ipc.json_converter import JsonConverter
        converter = JsonConverter()
    
    kwargs = {}
    for name, type_ in get_type_hints(class_).items():
        if name not in obj_json:
            raise TechnicalException(f"No field '{name}' in json object (existing fields: {list(obj_json.keys())})")
        value = converter.from_json_to(obj_json[name], type_, _parents=JsonTypes._new_parents(_parents, class_, name=name))
        kwargs[name] = value
        
    return class_(**kwargs)

JsonTypes.register_resource_for_type_in_class('NamedTuple', lambda c: Typing.is_NamedTuple(class_=c), None, 
                        (None, None, _from_json_to_NamedTuple))


def _from_json_to_object(obj_json, class_, _parents=None, converter=None):
    if not isinstance(obj_json, dict):
        raise TechnicalException(f"Argument 'obj_json' must be a dict")
    if converter is None:
        from holado_json.ipc.json_converter import JsonConverter
        converter = JsonConverter()
    
    res = undefined_value
    
    # Try with constructor having all dict keys as arguments
    try:
        res = class_(**obj_json)
    except TypeError as exc:  # @UnusedVariable
        # logger.print(f"++++++++++ class_(**obj_json): {exc}")
        pass
    
    if res is undefined_value:
        try:
            res = class_()
        except TypeError as exc:  # @UnusedVariable
            # logger.print(f"++++++++++ class_(): {exc}")
            pass
        if res is not undefined_value:
            for k, v in obj_json.items():
                if not isinstance(k, str):
                    raise TechnicalException(f"Failed to set a field in object of type {class_}: a field has name [{k}] that is not a string (from json object: {obj_json})")
                value = converter.from_json_to(v, None, _parents=JsonTypes._new_parents(_parents, class_, name=k, index=1))
                if hasattr(res, k):
                    setattr(res, k, value)
                else:
                    raise TechnicalException(f"Failed to set field '{k}' in object of type {class_}: attribute '{k}' doesn't exists")
    
    if res is undefined_value:
        raise TechnicalException(f"Failed to create {class_} instance from json object {obj_json}")
    return res

JsonTypes.register_resource_for_type_in_class('object', lambda c: inspect.isclass(c) and issubclass(c, object), lambda o: isinstance(o, object) and hasattr(o, '__dict__'), 
                        (None, lambda x: x.__dict__, _from_json_to_object))
    



