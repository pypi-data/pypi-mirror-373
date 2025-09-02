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



def dependencies():
    return None

def register():
    from holado.common.context.session_context import SessionContext
    from holado_python.common.tools.comparators.datetime_comparator import DatetimeComparator
    from holado_python.common.tools.datetime import DateTime
    
    from holado_protobuf.ipc.protobuf.protobuf_messages import ProtobufMessages
    if ProtobufMessages.is_available():
        SessionContext.instance().services.register_service_type("protobuf_messages", ProtobufMessages,
                            lambda m: m.initialize() )
    
        from holado_protobuf.ipc.protobuf.protobuf_converter import ProtobufConverter
        SessionContext.instance().services.register_service_type("protobuf_converter", ProtobufConverter,
                            lambda m: m.initialize(SessionContext.instance().protobuf_messages) )
    
        from holado_protobuf.ipc.protobuf.protobuf_modifier import ProtobufModifier
        SessionContext.instance().services.register_service_type("protobuf_modifier", ProtobufModifier,
                            lambda m: m.initialize(SessionContext.instance().protobuf_messages) )
        
        
        # Register json conversion
        
        from holado_json.ipc.json_types import JsonTypes
        
        def to_json_from_message(msg):
            converter = SessionContext.instance().protobuf_converter
            return converter.convert_protobuf_object_to_json_object(msg)
        
        JsonTypes.register_resource_for_type_in_class('protobuf.message', None, ProtobufMessages.is_object_message, 
                                (None, to_json_from_message, None), index=0)
        
        
        # Register datetime conversion
        
        from holado_protobuf.ipc.protobuf.types.google.protobuf import Timestamp
        DatetimeComparator.register_resource_for_type_in_class('protobuf.Timestamp', None, 
                                                               lambda o: isinstance(o, Timestamp.protobuf_class()), 
                                                               lambda o: DateTime.seconds_nanos_to_datetime(o.seconds, o.nanos),
                                                               index=0)

        
        
        
