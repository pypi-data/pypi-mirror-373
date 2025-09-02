
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
import copy

logger = logging.getLogger(__name__)


class ProtobufModifier(object):
    """
    Manage the modification of Protobuf objects with optimized algorithms.
    """
    def __init__(self): 
        self.__protobuf_messages = None
        self.__timestamp_field_names_by_type = {}
    
    def initialize(self, protobuf_messages): 
        self.__protobuf_messages = protobuf_messages
    
    def shift_all_timestamps(self, list_proto_obj, shift_seconds, do_copy=True):
        res = []
        
        for obj in list_proto_obj:
            # Define timestamp fields
            obj_type = self.__protobuf_messages.get_object_type_fullname(obj=obj)
            if obj_type in self.__timestamp_field_names_by_type:
                field_names = self.__timestamp_field_names_by_type[obj_type]
            else:
                all_field_names = self.__protobuf_messages.get_object_field_names(obj, recursive=True, uncollapse_repeated=True, add_repeated_index=True, with_unset=False)
                field_names = []
                for fn in all_field_names:
                    if fn.endswith('.nanos') and f"{fn[:-6]}.seconds" in all_field_names:
                        field_name = fn[:-6]
                        value = self.__protobuf_messages.get_object_field_value(obj, field_name)
                        value_type = self.__protobuf_messages.get_object_type_fullname(obj=value)
                        if value_type == "google.protobuf.Timestamp":
                            field_names.append(field_name)
                self.__timestamp_field_names_by_type[obj_type] = field_names
            
            # Update object
            if do_copy:
                res_obj = copy.deepcopy(obj)
            else:
                res_obj = obj
            for fn in field_names:
                ts = self.__protobuf_messages.get_object_field_value(res_obj, fn)
                if ts.seconds != 0:
                    ts.seconds += shift_seconds
            res.append(res_obj)
            
        return res
    


