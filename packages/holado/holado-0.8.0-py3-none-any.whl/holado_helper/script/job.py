
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
from typing import NamedTuple, List, get_type_hints
from holado_helper.script.action import BehaveActionInfo
from holado_json.ipc.json_converter import JsonConverter
from holado_json.ipc.json_types import JsonTypes
from holado_json.ipc.json_types import _from_json_to_NamedTuple as orig_from_json_to_NamedTuple
from holado_json.ipc.json_types import _from_json_to_object as orig_from_json_to_object
from holado_python.standard_library.typing import Typing
import inspect

logger = logging.getLogger(__name__)

class Job(NamedTuple):
    actions:List[BehaveActionInfo]
    in_parallel:bool
    
    
class JobJsonConverter(JsonConverter):
    def __init__(self, script_inst):
        super().__init__()
        self.__script_inst = script_inst
        self.__job_counter = 0
        self.__action_info_counter = 0
        
        self.__override_registered_types()
        
    def __override_registered_types(self):
        self.register_resource_for_type('NamedTuple', lambda c: Typing.is_NamedTuple(class_=c), lambda o: Typing.is_NamedTuple(obj=o), 
                           (None, None, self._from_json_to_NamedTuple))

        self.register_resource_for_type_in_class('object', lambda c: inspect.isclass(c) and issubclass(c, object), lambda o: isinstance(o, object) and hasattr(o, '__dict__'), 
                                (None, lambda x: x.__dict__, self._from_json_to_object))
    
    def _from_json_to_object(self, obj_json, class_, _parents=None, converter=None):
        if inspect.isclass(class_) and issubclass(class_, BehaveActionInfo):
            self.__action_info_counter += 1
            action = obj_json['action']
            
            params = self.from_json_to(obj_json['params'], dict, _parents=JsonTypes._new_parents(_parents, class_, name='params'))
            action_params = self.__script_inst.build_processing_action_params(action, action_args=obj_json, action_params=params, job_id=self.__job_counter)
            
            static_params = self.__script_inst.action_registry.get_action_static_parameters_values(action)
            
            tags = self.__script_inst.build_action_tags(action, action_args=obj_json)
            behave_args = self.__script_inst._build_behave_args(tags)
            
            index = _parents[-1]['index'] if _parents is not None and 'index' in _parents[-1] else None
            return self.__script_inst.new_action_info(action, behave_args=behave_args, params=action_params, static_params=static_params, index=index)
        else:
            return orig_from_json_to_object(obj_json, class_, _parents=_parents, converter=converter)
    
    def _from_json_to_NamedTuple(self, obj_json, class_, _parents=None, converter=None):
        if inspect.isclass(class_) and issubclass(class_, Job):
            self.__job_counter += 1
            actions = self.from_json_to(obj_json['actions'], get_type_hints(Job)['actions'], _parents=JsonTypes._new_parents(_parents, class_, name='actions'))
            is_parallel = obj_json.get('is_parallel', False)
            return Job(actions, is_parallel)
        else:
            return orig_from_json_to_NamedTuple(obj_json, class_, _parents=_parents, converter=converter)



