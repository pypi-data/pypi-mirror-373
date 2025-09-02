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


from holado_test.scenario.step_tools import StepTools
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_protobuf.ipc.protobuf.protobuf_messages import ProtobufMessages
import logging
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.common.tools.datetime import DateTime
from holado_python.standard_library.typing import Typing
from holado_protobuf.ipc.protobuf.protobuf_converter import SortOrder

logger = logging.getLogger(__name__)


if ProtobufMessages.is_available():
    
    # TODO: check if needed
    import google.protobuf.pyext
    
    def __get_protobuf_converter():
        return SessionContext.instance().protobuf_converter
    
    def __get_protobuf_messages():
        return SessionContext.instance().protobuf_messages
    
    def __get_protobuf_modifier():
        return SessionContext.instance().protobuf_modifier
    
    def __get_scenario_context():
        return SessionContext.instance().get_scenario_context()
    
    def __get_text_interpreter():
        return __get_scenario_context().get_text_interpreter()
    
    def __get_variable_manager():
        return __get_scenario_context().get_variable_manager()
    
    def __get_session_context():
        return SessionContext.instance()
    
    @Step(r"(?P<var_name>{Variable}) = convert Protobuf object (?P<obj_var_name>{Variable}) to datetime")
    def step_impl(context, var_name, obj_var_name):  # @DuplicatedSignature
        from google.protobuf import timestamp_pb2
        
        var_name = StepTools.evaluate_variable_name(var_name)
        obj = StepTools.evaluate_variable_value(obj_var_name)
        
        if not isinstance(obj, timestamp_pb2.Timestamp):  # @UndefinedVariable
            raise TechnicalException(f"Object must be of type google.protobuf.Timestamp (obtained type: {Typing.get_object_class_fullname(obj)})")
        
        res = DateTime.seconds_nanos_to_datetime(obj.seconds, obj.nanos)
        
        __get_variable_manager().register_variable(var_name, res)

    @Step(r"(?P<var_name>{Variable}) = convert list (?P<list_var_name>{Variable}) to list of Protobuf field (?P<attribute_name>{Str})")
    def step_impl(context, var_name, list_var_name, attribute_name):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        attr_name = StepTools.evaluate_scenario_parameter(attribute_name)
        list_obj = StepTools.evaluate_variable_value(list_var_name)
        
        res = []
        for index, obj in enumerate(list_obj):
            if hasattr(obj, attr_name):
                attr_val = getattr(obj, attr_name)
                if ProtobufMessages.is_object_repeated(attr_val):
                    attr_val = [v for v in attr_val]
                # logger.debug(f"Result list - add field value [{attr_val}] (type: {Typing.get_object_class_fullname(attr_val)} ; dir: {dir(attr_val)})")
                res.append(attr_val)
            else:
                raise FunctionalException(f"In list, object of index {index} hasn't attribute '{attr_name}'")
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Given(r"(?P<var_name>{Variable}) = convert list (?P<list_var_name>{Variable}) to merged list of Protobuf repeated field (?P<attribute_name>{Str})")
    def step_impl(context, var_name, list_var_name, attribute_name):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        attr_name = StepTools.evaluate_scenario_parameter(attribute_name)
        list_obj = StepTools.evaluate_variable_value(list_var_name)
        
        res = []
        for index, obj in enumerate(list_obj):
            if hasattr(obj, attr_name):
                attr_val = getattr(obj, attr_name)
                if not ProtobufMessages.is_object_repeated(attr_val):
                    raise FunctionalException(f"In list, object of index {index} has field '{attr_name}' but it isn't repeated")
                
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"In list, object of index {index} has field '{attr_name}' repeated {len(attr_val)} times")
                for val in attr_val:
                    # logger.debug(f"Result list - add field value [{val}] (type: {Typing.get_object_class_fullname(val)} ; dir: {dir(val)})")
                    res.append(val)
            else:
                raise FunctionalException(f"In list, object of index {index} hasn't attribute '{attr_name}'")
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Step(r"(?P<var_name>{Variable}) = convert list (?P<list_var_name>{Variable}) to list of (?P<proto_type_str>{Str}) Protobuf objects")
    def step_impl(context, var_name, list_var_name, proto_type_str):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        list_obj = StepTools.evaluate_variable_value(list_var_name)
        proto_type_str = StepTools.evaluate_scenario_parameter(proto_type_str)
        
        res = []
        for index, obj in enumerate(list_obj):
            new_obj = __get_protobuf_messages().new_object(proto_type_str)
            field_names = __get_protobuf_messages().get_object_field_names(obj, recursive=True, uncollapse_repeated=True, add_repeated_index=True, with_unset=False)
            for fn in field_names:
                try:
                    value = __get_protobuf_messages().get_object_field_value(obj, fn)
                    __get_protobuf_messages().set_object_field_value(new_obj, fn, value)
                except Exception as exc:
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"For object of index {index}, failed to set field '{fn}': {str(exc)}")
            res.append(new_obj)
        
        __get_variable_manager().register_variable(var_name, res)
    
    
    @Given(r'(?P<var_name>{Variable}) = convert list (?P<list_obj_str>{Variable}) to table with Protobuf fields as columns')
    def step_impl(context, var_name, list_obj_str):
        var_name = StepTools.evaluate_variable_name(var_name)
        list_obj = StepTools.evaluate_variable_value(list_obj_str)
        
        res = __get_protobuf_converter().create_table_with_protobuf_fields_as_columns(list_obj, recursive=False)
    
        __get_variable_manager().register_variable(var_name, res)
    
    @Given(r'(?P<var_name>{Variable}) = convert list (?P<list_obj_str>{Variable}) to table with Protobuf fields as columns recursively')
    def step_impl(context, var_name, list_obj_str):
        var_name = StepTools.evaluate_variable_name(var_name)
        list_obj = StepTools.evaluate_variable_value(list_obj_str)
        
        res = __get_protobuf_converter().create_table_with_protobuf_fields_as_columns(list_obj, recursive=True)
    
        __get_variable_manager().register_variable(var_name, res)
    
    @Given(r'(?P<var_name>{Variable}) = convert list (?P<list_obj_str>{Variable}) to table with Protobuf fields as columns recursively and repeated fields uncollapsed')
    def step_impl(context, var_name, list_obj_str):
        var_name = StepTools.evaluate_variable_name(var_name)
        list_obj = StepTools.evaluate_variable_value(list_obj_str)
        
        res = __get_protobuf_converter().create_table_with_protobuf_fields_as_columns(list_obj, recursive=True, uncollapse_repeated=True)
    
        __get_variable_manager().register_variable(var_name, res)
    
     
    @Step(r"(?P<var_name>{Variable}) = new Protobuf object of type (?P<proto_type_str>{Str})")
    def step_impl(context, var_name, proto_type_str):
        var_name = StepTools.evaluate_variable_name(var_name)
        proto_type_str = StepTools.evaluate_scenario_parameter(proto_type_str)
        table = BehaveStepTools.get_step_table(context)
        
        res = __get_protobuf_messages().new_message(proto_type_str, fields_table=table)
            
        __get_variable_manager().register_variable(var_name, res)  

    @Step(r"(?P<var_name>{Variable}) = serialize Protobuf object (?P<proto_str>{Variable})")
    def step_impl(context, var_name, proto_str):
        var_name = StepTools.evaluate_variable_name(var_name)
        obj = StepTools.evaluate_variable_value(proto_str)
        res = obj.SerializeToString()
        __get_variable_manager().register_variable(var_name, res) 
       
    @Step(r"(?P<var_name>{Variable}) = serialize list (?P<obj_list>{Variable}) of Protobuf objects")
    def step_impl(context, var_name, obj_list):
        var_name = StepTools.evaluate_variable_name(var_name)
        obj_list = StepTools.evaluate_variable_value(obj_list)
        
        res = []
        for obj in obj_list:
            obj = obj.SerializeToString()
            res.append(obj)
        
        __get_variable_manager().register_variable(var_name, res)
       
    @Step(r"(?P<var_name>{Variable}) = unserialize string (?P<ser_str>{Str}) as (?P<proto_type_str>{Str}) Protobuf object")
    def step_impl(context, var_name, ser_str, proto_type_str):
        var_name = StepTools.evaluate_variable_name(var_name)
        ser_str = StepTools.evaluate_scenario_parameter(ser_str)
        proto_type_str = StepTools.evaluate_scenario_parameter(proto_type_str)
    
        obj = __get_protobuf_messages().new_message(proto_type_str, serialized_string=ser_str)

        __get_variable_manager().register_variable(var_name, obj)
       
    @Step(r"(?P<var_name>{Variable}) = unserialize string list (?P<ser_list>{Variable}) as (?P<proto_type_str>{Str}) Protobuf objects")
    def step_impl(context, var_name, ser_list, proto_type_str):
        var_name = StepTools.evaluate_variable_name(var_name)
        ser_list = StepTools.evaluate_variable_value(ser_list)
        proto_type_str = StepTools.evaluate_scenario_parameter(proto_type_str)
        
        res = []
        for ser_str in ser_list:
            obj = __get_protobuf_messages().new_message(proto_type_str, serialized_string=ser_str)
            res.append(obj)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Given(r"(?P<var_name>{Variable}) = convert Protobuf object (?P<obj_var_name>{Variable}) to json object")
    def step_impl(context, var_name, obj_var_name):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        obj = StepTools.evaluate_variable_value(obj_var_name)
        res = __get_protobuf_converter().convert_protobuf_object_to_json_object(obj)
        __get_variable_manager().register_variable(var_name, res)
    
    @Given(r"(?P<var_name>{Variable}) = convert list (?P<obj_list_var_name>{Variable}) of Protobuf objects to json objects")
    def step_impl(context, var_name, obj_list_var_name):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        obj_list = StepTools.evaluate_variable_value(obj_list_var_name)
        
        res = []
        for obj in obj_list:
            res_obj = __get_protobuf_converter().convert_protobuf_object_to_json_object(obj)
            res.append(res_obj)
            
        __get_variable_manager().register_variable(var_name, res)
    
    @Given(r"(?P<var_name>{Variable}) = convert Protobuf object (?P<obj_var_name>{Variable}) to name/value table(?: with(?:(?P<with_names_str> names)?(?: and)?(?P<with_repeated_str> repeated)? uncollapsed)?(?: and)?(?P<with_unset_str> unset fields)?)?(?: \((?P<sort_alphabetically>sort alphabetically)?\))?")
    def step_impl(context, var_name, obj_var_name, with_names_str, with_repeated_str, with_unset_str, sort_alphabetically):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        obj = StepTools.evaluate_variable_value(obj_var_name)
        recursive = with_names_str is not None
        uncollapse_repeated = with_repeated_str is not None
        with_unset = with_unset_str is not None
        sort_order = SortOrder.Alphabetic if sort_alphabetically is not None else None
        
        res = __get_protobuf_converter().convert_protobuf_object_to_name_value_table(obj, recursive=recursive, uncollapse_repeated=uncollapse_repeated, with_unset=with_unset, sort_order=sort_order)
        
        __get_variable_manager().register_variable(var_name, res)
    
    @Given(r"(?P<var_name>{Variable}) = value of Protobuf enum (?P<enum_fullname>{Str})")
    def step_impl(context, var_name, enum_fullname):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        enum_fullname = StepTools.evaluate_scenario_parameter(enum_fullname)
        res = __get_protobuf_messages().get_enum_value(fullname=enum_fullname)
        __get_variable_manager().register_variable(var_name, res)

    @Given(r"(?P<var_name>{Variable}) = name of value (?P<enum_value>{Str}) of Protobuf enum type (?P<enum_type_fullname>{Str})")
    def step_impl(context, var_name, enum_value, enum_type_fullname):  # @DuplicatedSignature
        var_name = StepTools.evaluate_variable_name(var_name)
        enum_value = StepTools.evaluate_scenario_parameter(enum_value)
        enum_type_fullname = StepTools.evaluate_scenario_parameter(enum_type_fullname)
        res = __get_protobuf_messages().get_enum_name(enum_value=enum_value, enum_type_fullname=enum_type_fullname)
        __get_variable_manager().register_variable(var_name, res)

    @Given(r"import Protobuf enum type (?P<enum_type_fullname>{Str})")
    def step_impl(context, enum_type_fullname):  # @DuplicatedSignature
        enum_type_fullname = StepTools.evaluate_scenario_parameter(enum_type_fullname)
        res = __get_protobuf_messages().get_enum_type(enum_type_fullname=enum_type_fullname)
        __get_variable_manager().register_variable(res.DESCRIPTOR.name, res)
        
        # Register each enum name fullname
        # Note: accept_expression=False is needed, otherwise, when importing a second enum with same package name, 
        #       previous line "enum_type_fullname = StepTools.evaluate_scenario_parameter(enum_type_fullname)" will fail
        for name, value in res.DESCRIPTOR.values_by_name.items():
            __get_variable_manager().register_variable(f"{res.DESCRIPTOR.full_name}.{name}", value.number, accept_expression=False)

    @Given(r"import values of Protobuf enum type (?P<enum_type_fullname>{Str})(?: with prefix (?P<prefix>{Str}))?")
    def step_impl(context, enum_type_fullname, prefix):  # @DuplicatedSignature
        enum_type_fullname = StepTools.evaluate_scenario_parameter(enum_type_fullname)
        prefix = StepTools.evaluate_scenario_parameter(prefix)
        et = __get_protobuf_messages().get_enum_type(enum_type_fullname=enum_type_fullname)
        for name, value in et.DESCRIPTOR.values_by_name.items():
            if prefix:
                __get_variable_manager().register_variable(prefix+name, value.number, accept_expression=False)
            else:
                __get_variable_manager().register_variable(name, value.number)
       
    @Step(r"(?P<var_name>{Variable}) = list (?P<obj_list>{Variable}) of Protobuf objects with timestamps shifted by (?P<shift_seconds>{Int}) seconds")
    def step_impl(context, var_name, obj_list, shift_seconds):
        var_name = StepTools.evaluate_variable_name(var_name)
        obj_list = StepTools.evaluate_variable_value(obj_list)
        shift_seconds = StepTools.evaluate_scenario_parameter(shift_seconds)
        
        res = __get_protobuf_modifier().shift_all_timestamps(obj_list, shift_seconds)
        
        __get_variable_manager().register_variable(var_name, res)



