
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
import os
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
import sys
import importlib
import re
from holado_core.common.tools.tools import Tools
from holado_core.common.tools.converters.converter import Converter
from holado_value.common.tables.value_table_manager import ValueTableManager
from holado_value.common.tools.value_types import ValueTypes
import inspect
from typing import NamedTuple
from holado_core.common.exceptions.holado_exception import HAException
from holado_python.standard_library.typing import Typing
from holado.common.handlers.undefined import undefined_argument, undefined_value

logger = logging.getLogger(__name__)

try:
    import google.protobuf.message
    import google.protobuf.descriptor
    from google.protobuf.descriptor import FieldDescriptor
    # import google.protobuf.pyext
    from google.protobuf.internal import api_implementation
    from holado_protobuf.ipc.protobuf.protobuf_converter import SortOrder
    
    # logger.info(f"Protobuf internal API implementation is of type '{api_implementation.Type()}'")
    if api_implementation.Type() == 'cpp':
        # from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType
        from google.protobuf.pyext._message import ScalarMapContainer as ScalarMap  # @UnresolvedImport @UnusedImport
        from google.protobuf.pyext._message import MessageMapContainer as MessageMap  # @UnresolvedImport @UnusedImport
        # from google.protobuf.pyext._message import RepeatedScalarContainer as RepeatedScalarFieldContainer
        # from google.protobuf.pyext._message import RepeatedCompositeContainer as RepeatedCompositeFieldContainer
    else:
        # from google.protobuf.internal.python_message import GeneratedProtocolMessageType
        from google.protobuf.internal.containers import ScalarMap  # @UnusedImport @Reimport
        from google.protobuf.internal.containers import MessageMap  # @UnusedImport @Reimport
        from google.protobuf.internal.containers import RepeatedScalarFieldContainer, RepeatedCompositeFieldContainer  # @UnusedImport
    
    with_protobuf = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"ProtobufMessages is not available. Initialization failed on error: {exc}")
    with_protobuf = False




class ProtobufMessages(object):
    
    @classmethod
    def is_available(cls):
        return with_protobuf

    if with_protobuf:
        
        @classmethod
        def is_descriptor_enum(cls, obj):
            return isinstance(obj, google.protobuf.descriptor.EnumDescriptor)
    
        @classmethod
        def is_descriptor_message(cls, obj):
            return isinstance(obj, google.protobuf.descriptor.Descriptor)
    
        @classmethod
        def is_object_message(cls, obj):
            return isinstance(obj, google.protobuf.message.Message)
    
        @classmethod
        def is_object_enum(cls, obj):
            class_name = type(obj).__name__.lower()
            return "enum" in class_name
    
        @classmethod
        def is_object_repeated(cls, obj):
            class_name = type(obj).__name__.lower()
            return "repeated" in class_name
    
        @classmethod
        def is_object_map(cls, obj):
            class_name = type(obj).__name__.lower()
            return "map" in class_name and hasattr(obj, 'items') and callable(obj.items)
            # return isinstance(obj, ScalarMap) or isinstance(obj, MessageMap)
            
        def is_message_field_set(self, obj, field_name):
            return self.__is_message_field_set(obj, field_name)
        
        def __init__(self): 
            self.__message_types_by_fullname = {}
            self.__enum_types_by_fullname = {}
            self.__enum_data_by_fullname = {}
            self.__regex_attribute_fullname = re.compile(r'^(.*?)(?:\[(.+)\])?$')
            
            self.__registered_types = []
        
        def initialize(self):
            self._register_types()
            
        def import_all_compiled_proto(self, compiled_proto_path, package_name=None, raise_if_not_exist=True):
            """Register a folder path containing compiled proto files. Usually it corresponds to the parameter '--python_out' passed to proto compiler."""
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[ProtobufMessages] Importing all compiled proto in '{compiled_proto_path}'...")
            
            if package_name is None:
                package_name = ""
            
            if os.path.exists(compiled_proto_path):
                if os.path.isfile(compiled_proto_path):
                    proto_path = os.path.dirname(compiled_proto_path)
                    sys.path.append(proto_path)
                    self.__import_compiled_proto(compiled_proto_path, package_name)
                elif os.path.isdir(compiled_proto_path):
                    sys.path.append(compiled_proto_path)
                    self.__import_all_compiled_proto(compiled_proto_path, package_name)
                else:
                    raise TechnicalException(f"Unmanaged path '{compiled_proto_path}'")
            else:
                msg = f"Path '{compiled_proto_path}' doesn't exist"
                if raise_if_not_exist:
                    raise TechnicalException(msg)
                else:
                    logger.warning(msg)
        
        def __import_all_compiled_proto(self, compiled_proto_path, package_name):
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"[ProtobufMessages] Importing all compiled proto in '{compiled_proto_path}' (package: '{package_name}')...")
            if os.path.isdir(compiled_proto_path):
                lp = os.listdir(compiled_proto_path)
                for cp in lp:
                    if not cp.startswith((".", "_")):
                        cur_proto_path = os.path.join(compiled_proto_path, cp)
                        
                        if os.path.isfile(cur_proto_path):
                            self.__import_compiled_proto(cur_proto_path, package_name)
                        elif os.path.isdir(cur_proto_path):
                            cur_package_name = f"{package_name}.{cp}" if package_name is not None and len(package_name) > 0 else cp
                            self.__import_all_compiled_proto(cur_proto_path, cur_package_name)
                        else:
                            raise TechnicalException(f"Unmanaged path '{cur_proto_path}'")
            else:
                raise TechnicalException(f"Unmanaged path '{compiled_proto_path}'")
        
        def __import_compiled_proto(self, compiled_proto_file_path, package_name):
            if not os.path.isfile(compiled_proto_file_path):
                raise TechnicalException(f"Compiled proto path '{compiled_proto_file_path}' is not a file")
            if not compiled_proto_file_path.endswith("_pb2.py"):
                return
    
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
    
                logger.trace(f"[ProtobufMessages] Importing compiled proto file '{compiled_proto_file_path}' (package: '{package_name}')...")
            
            filename = os.path.splitext(os.path.basename(compiled_proto_file_path))[0]
            module_name = f"{package_name}.{filename}" if package_name is not None and len(package_name) > 0 else filename
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"[ProtobufMessages] Importing module '{module_name}'")
            module = importlib.import_module(module_name)
            
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            
                logger.trace(f"[ProtobufMessages] DESCRIPTOR of module '{module_name}': {self.__represent_descriptor(module.DESCRIPTOR)}")
            module_package = module.DESCRIPTOR.package if hasattr(module.DESCRIPTOR, 'package') else package_name
            self.__import_compiled_proto_object(module, module_package)
    
        def __import_compiled_proto_object(self, module_or_object, module_or_object_fullname):
            # Import message types
            if hasattr(module_or_object.DESCRIPTOR, 'message_types_by_name'):
                for mt_name in module_or_object.DESCRIPTOR.message_types_by_name:
                    self.__import_compiled_proto_message(module_or_object, module_or_object_fullname, mt_name)
                
            # Import enum types
            if hasattr(module_or_object.DESCRIPTOR, 'enum_types_by_name'):
                for et_name in module_or_object.DESCRIPTOR.enum_types_by_name:
                    self.__import_compiled_proto_enum(module_or_object, module_or_object_fullname, et_name)
                
            # Import nested types
            if hasattr(module_or_object.DESCRIPTOR, 'nested_types_by_name'):
                for nt_name in module_or_object.DESCRIPTOR.nested_types_by_name:
                    nt = module_or_object.DESCRIPTOR.nested_types_by_name[nt_name]
                    if self.is_descriptor_message(nt):
                        self.__import_compiled_proto_message(module_or_object, module_or_object_fullname, nt_name)
                    elif self.is_descriptor_enum(nt):
                        self.__import_compiled_proto_enum(module_or_object, module_or_object_fullname, nt_name)
                    else:
                        raise TechnicalException(f"Unmanaged nested type '{nt_name}' having descriptor: {self.__represent_descriptor(nt)}")
    
        def __import_compiled_proto_message(self, module_or_object, module_or_object_fullname, message_type_name):
            if hasattr(module_or_object, message_type_name):
                mt = getattr(module_or_object, message_type_name)
                mt_fullname = f"{module_or_object_fullname}.{message_type_name}" if module_or_object_fullname is not None and len(module_or_object_fullname) > 0 else message_type_name
                self.__message_types_by_fullname[mt_fullname] = mt
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"[ProtobufMessages] New managed message type '{mt_fullname}' (type: '{mt.__qualname__}')")
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[ProtobufMessages] Message type '{mt_fullname}': {Tools.represent_object(mt)}")
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[ProtobufMessages] DESCRIPTOR of message type '{mt_fullname}': {self.__represent_descriptor(mt.DESCRIPTOR)}")
                
                # Import nested types
                self.__import_compiled_proto_object(mt, mt_fullname)
            else:
                raise TechnicalException(f"Not found message type '{message_type_name}' in '{module_or_object_fullname}': {Tools.represent_object(module_or_object)}")
    
        def __import_compiled_proto_enum(self, module_or_object, module_or_object_fullname, enum_type_name):
            if hasattr(module_or_object, enum_type_name):
                et = getattr(module_or_object, enum_type_name)
                et_fullname = f"{module_or_object_fullname}.{enum_type_name}" if module_or_object_fullname is not None and len(module_or_object_fullname) > 0 else enum_type_name
                self.__enum_types_by_fullname[et_fullname] = et
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"[ProtobufMessages] New managed enum type '{et_fullname}' (type: '{Typing.get_object_class_fullname(et)}')")
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[ProtobufMessages] Enum type '{et_fullname}': {Tools.represent_object(et)}")
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[ProtobufMessages] DESCRIPTOR of enum type '{et_fullname}': {self.__represent_descriptor(et.DESCRIPTOR)}")
            else:
                raise TechnicalException(f"Not found enum type '{enum_type_name}' in '{module_or_object_fullname}': {Tools.represent_object(module_or_object)}")
    
        def has_object_type(self, type_fullname):
            """Return if type fullname is known."""
            return self.has_message_type(type_fullname) or self.has_enum_type(type_fullname)
    
        def has_message_type(self, message_type_fullname):
            """Return if message type fullname is known."""
            return message_type_fullname in self.__message_types_by_fullname
    
        def has_enum_type(self, enum_type_fullname):
            """Return if enum type fullname is known."""
            return enum_type_fullname in self.__enum_types_by_fullname
    
        def get_object_type(self, type_fullname):
            """Return type object for given type fullname."""
            if self.has_message_type(type_fullname):
                return self.get_message_type(type_fullname)
            else:
                raise FunctionalException(f"Unknown type fullname '{type_fullname}'")
    
        def get_message_type(self, message_type_fullname):
            """Return type object for given message type fullname."""
            if self.has_message_type(message_type_fullname):
                return self.__message_types_by_fullname[message_type_fullname]
            else:
                raise FunctionalException(f"Unknown message type fullname '{message_type_fullname}'")
    
        def get_enum_type(self, enum_type_fullname):
            """Return type object for given message type fullname."""
            if self.has_enum_type(enum_type_fullname):
                return self.__enum_types_by_fullname[enum_type_fullname]
            else:
                raise FunctionalException(f"Unknown enum type fullname '{enum_type_fullname}' (known enums: {list(self.__enum_types_by_fullname.keys())})")
            
        def get_enum_name(self, enum_value, enum_type_fullname):
            enum_type = self.get_enum_type(enum_type_fullname)
            return self.__get_enum_name(enum_value, enum_type=enum_type)
    
        def get_enum_value(self, fullname=None, enum_type_fullname=None, enum_name=None):
            if fullname is not None:
                enum_type_fullname, enum_name = fullname.rsplit('.', 1)
            enum_type = self.get_enum_type(enum_type_fullname)
            return self.__get_enum_value(enum_name, enum_type=enum_type)
    
        def new_object(self, type_fullname):
            """Return a new object of given type fullname."""
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Creating new object of type '{type_fullname}'...")
            if self.has_object_type(type_fullname):
                if self.has_message_type(type_fullname):
                    mt = self.get_message_type(type_fullname)
                    res = mt()
                else:
                    raise TechnicalException(f"Unmanaged object creation for type fullname '{type_fullname}' (all managed types are logged at start with level DEBUG)")
            else:
                raise TechnicalException(f"Unknown type fullname '{type_fullname}' (all known types are logged at start with level DEBUG)")
            
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"New object of type '{type_fullname}' => {res}")
            return res
    
        def new_message(self, message_type_fullname, fields_table=None, fields_dict=None, serialized_string=None):
            """Return a new message of given message type fullname.
            The content of the message can be filled from serialized string, or from field values in a Name/Value table.
            """
            res = self.new_object(message_type_fullname)
            
            if serialized_string is not None:
                res.ParseFromString(serialized_string)
            elif fields_table is not None:
                if ValueTableManager.verify_table_is_name_value_table(fields_table, raise_exception=False):
                    self.__set_object_fields_with_name_value_table(res, fields_table)
                else:
                    raise TechnicalException(f"When defining parameter fields_table, it must be a Name/Value table: [{Typing.get_object_class_fullname(fields_table)}]\n{fields_table.represent(4)}")
            elif fields_dict is not None:
                self.__set_object_fields_with_dict(res, fields_dict)
            
            if Tools.do_log(logger, logging.DEBUG):
                # logger.debug(f"New message of type '{message_type_fullname}' => {res}")
                logger.debug(f"New message of type '{message_type_fullname}' => {Tools.represent_object(res)}")
            return res
            
        def get_object_field_names(self, obj, recursive=False, uncollapse_repeated=False, add_repeated_index=False, with_unset=True, sort_order=SortOrder.Definition):
            res = self.__get_object_field_names(obj, recursive=recursive, uncollapse_repeated=uncollapse_repeated, add_repeated_index=add_repeated_index, with_unset=with_unset, is_message_field=False, sort_order=sort_order)
            # logger.trace(f"Object of type '{self.get_object_type_fullname(obj)}' has field names: {res}")
            return res
            
        def get_message_field_names(self, obj, recursive=False, uncollapse_repeated=False, add_repeated_index=False, with_unset=True):
            res = self.__get_message_field_names(obj, recursive=recursive, uncollapse_repeated=uncollapse_repeated, add_repeated_index=add_repeated_index, with_unset=with_unset)
            # logger.trace(f"Message of type '{self.get_object_type_fullname(obj)}' has field names: {res}")
            return res
            
        def get_object_field_values(self, obj, attribute_expression):
            """
            Return a list of values for attribute names matching given expression.
            Attribute name expression can contain "." for sub-fields, and "[]" to access all elements of the repeated field.
            The list contains only one value unless a repeated field is included in attribute expression with suffix '[]'.
            """ 
            attr_names = attribute_expression.split('.')
            res_list = [(obj, "")]
            for attr_name in attr_names:
                old_list = res_list
                if attr_name.endswith("[]"):
                    if len(old_list) > 1:
                        raise TechnicalException("Uncollapse two different repeated fields in the same message is not managed.")
                    cur_res = old_list[0][0]
                    cur_fullname = old_list[0][1]
                    real_attr_name = attr_name[:-2]
                    
                    cur_attr_fullname = cur_fullname + '.' + real_attr_name if len(cur_fullname) > 0 else real_attr_name
                    if not hasattr(cur_res, real_attr_name):
                        raise TechnicalException(f"Attribute '{cur_attr_fullname}' doesn't exist in object [{cur_res}]")
                    
                    res_list = []
                    for index, attr_obj in enumerate(getattr(cur_res, real_attr_name)):
                        new_attr_fullname = f"{cur_attr_fullname}[{index}]"
                        res_list.append((attr_obj, new_attr_fullname))
                else:
                    res_list = []
                    for obj, obj_attr_fullname in old_list:
                        new_attr_fullname = f"{obj_attr_fullname}.{attr_name}"
                        if self.__has_object_field(obj, field_name=attr_name):
                            attr_obj = self.__get_object_field(obj, field_name=attr_name)
                            res_list.append((attr_obj, new_attr_fullname))
                        else:
                            raise TechnicalException(f"Attribute '{new_attr_fullname}' doesn't exist in object [{obj}]")
                        
            return [obj for obj, _ in res_list]
                
        def has_object_field(self, obj, attribute_expression, create_field=False):
            leaf_obj, _, attr_last_name = self.__get_leaf_object_and_attribute_names(obj, attribute_expression, create_field=create_field)
            return self.__has_object_field(leaf_obj, field_fullname=attr_last_name)
            
        def get_object_field_value(self, obj, attribute_expression, create_field=False):
            """
            Return the value for attribute name matching given expression.
            Attribute name expression can contain "." for sub-fields.
            """ 
            attr_names = attribute_expression.split('.')
            res = obj
            attr_fullname = ""
            for attr_name in attr_names:
                if self.__has_object_field(res, field_fullname=attr_name):
                    res = self.__get_object_field(res, field_fullname=attr_name, create_field=create_field)
                    attr_fullname = attr_fullname + '.' + attr_name if len(attr_fullname) > 0 else attr_name
                else:
                    attr_name, _ = self.__split_attribute_fullname(attr_name)
                    if len(attr_fullname) > 0:
                        attr_fullname = attr_fullname + '.' + attr_name
                        raise FunctionalException(f"Field '{attr_fullname}' doesn't exist in message type '{self.get_object_type_fullname(obj)}' (in sub-message type '{self.get_object_type_fullname(res)}', existing fields: {self.__get_object_descriptor_field_names(res, False)})")
                    else:
                        raise FunctionalException(f"Field '{attr_name}' doesn't exist in message type '{self.get_object_type_fullname(obj)}' (existing fields: {self.__get_object_descriptor_field_names(obj, False)})")
                
            return res
                
        def set_object_field_value(self, obj, attribute_expression, value):
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Setting protobuf object ({id(obj)}) field '{attribute_expression}' with value [{value}] (type: {Typing.get_object_class_fullname(value)})")
            leaf_obj, leaf_attribute_expression, attr_last_name = self.__get_leaf_object_and_attribute_names(obj, attribute_expression, create_field=True)
                
            # Set value
            if self.__has_object_field(leaf_obj, field_fullname=attr_last_name):
                self.__set_object_field(leaf_obj, field_fullname=attr_last_name, value=value, create_field=True)
            else:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"Field '{attr_last_name}' doesn't exist in type '{self.get_object_type_fullname(leaf_obj)}'")
                attr_name, _ = self.__split_attribute_fullname(attr_last_name)
                if leaf_attribute_expression is not None:
                    attr_fullname = leaf_attribute_expression + '.' + attr_name
                    raise FunctionalException(f"Field '{attr_fullname}' doesn't exist in object type '{self.get_object_type_fullname(obj)}' (in sub-message type '{self.get_object_type_fullname(leaf_obj)}', existing fields: {self.__get_object_descriptor_field_names(leaf_obj, False)})")
                else:
                    raise FunctionalException(f"Field '{attr_name}' doesn't exist in object type '{self.get_object_type_fullname(obj)}' (existing fields: {self.__get_object_descriptor_field_names(obj, False)})")
                
        def __get_leaf_object_and_attribute_names(self, obj, attribute_expression, create_field=False):
            try:
                leaf_attribute_expression, attr_last_name = attribute_expression.rsplit('.', 1)
            except ValueError:
                leaf_obj = obj
                leaf_attribute_expression = None
                attr_last_name = attribute_expression
            else:
                # Get "leaf" object (in object tree) containing the leaf attribute to set
                leaf_obj = self.get_object_field_value(obj, leaf_attribute_expression, create_field=create_field)
            return leaf_obj, leaf_attribute_expression, attr_last_name
    
        def __get_object_field_names(self, obj, recursive=False, uncollapse_repeated=False, add_repeated_index=True, with_unset=True, prefix="", is_message_field=False, sort_order=SortOrder.Definition):
            res = []
            if uncollapse_repeated and ProtobufMessages.is_object_repeated(obj):
                if add_repeated_index:
                    for index, value in enumerate(obj):
                        new_prefix = f"{prefix}[{index}]"
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            logger.trace(f"Adding field names of repeated with prefix '{new_prefix}' (type: {Typing.get_object_class_fullname(value)})")
                        res.extend(self.__get_object_field_names(value, recursive=recursive, uncollapse_repeated=uncollapse_repeated, add_repeated_index=add_repeated_index, with_unset=with_unset, prefix=new_prefix, is_message_field=is_message_field, sort_order=sort_order))
                else:
                    new_prefix = f"{prefix}[]"
                    value = obj[0]
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"Adding field names of repeated with prefix '{new_prefix}' (type: {Typing.get_object_class_fullname(value)})")
                    res.extend(self.__get_object_field_names(value, recursive=recursive, uncollapse_repeated=uncollapse_repeated, add_repeated_index=add_repeated_index, with_unset=with_unset, prefix=new_prefix, is_message_field=is_message_field, sort_order=sort_order))
            elif (recursive or not is_message_field) and ProtobufMessages.is_object_map(obj):
                sorted_dict = dict(sorted(obj.items()))
                for key, value in sorted_dict.items():
                    key_prefix = f"{prefix}[{key}]" if len(prefix) > 0 else key
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"Adding field names of object of prefix '{key_prefix}' (type: {Typing.get_object_class_fullname(value)})")
                    res.extend(self.__get_object_field_names(value, recursive=recursive, uncollapse_repeated=uncollapse_repeated, add_repeated_index=add_repeated_index, with_unset=with_unset, prefix=key_prefix, is_message_field=is_message_field))
            elif (recursive or not is_message_field) and ProtobufMessages.is_object_message(obj):
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"Adding field names of message of prefix '{prefix}' (type: {Typing.get_object_class_fullname(obj)})")
                res.extend(self.__get_message_field_names(obj, recursive=recursive, uncollapse_repeated=uncollapse_repeated, add_repeated_index=add_repeated_index, with_unset=with_unset, prefix=prefix, sort_order=sort_order))
            elif len(prefix) > 0:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"Adding field name '{prefix}' (value type: {Typing.get_object_class_fullname(obj)})")
                res.append(prefix)
            else:
                # logger.trace(f"Adding field name '{attr_name}' (value type: {Typing.get_object_class_fullname(attr_val)})")
                raise TechnicalException(f"Object has no field and prefix is empty (object: {obj} ; type: {Typing.get_object_class_fullname(obj)})")
            return res
    
        def __get_message_field_names(self, obj, recursive=False, uncollapse_repeated=False, add_repeated_index=True, with_unset=True, prefix="", sort_order=SortOrder.Definition):
            res = []
            attribute_names = self.__get_object_descriptor_field_names(obj, sort_order=sort_order)
            for attr_name in attribute_names:
                attr_val = getattr(obj, attr_name)
                new_prefix = f"{prefix + '.' if len(prefix) > 0 else ''}{attr_name}"
                
                # Skip field not set
                if not with_unset:
                    set_status = self.__is_message_field_set(obj, attr_name)
                    if set_status == False:
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            logger.trace(f"Hide unset field '{attr_name}' in object type '{self.get_object_type_fullname(obj)}' (field type: {Typing.get_object_class_fullname(attr_val)})")
                        continue
                
                # Skip optional fields that are not set
                if self.__is_message_field_optional(obj, attr_name):
                    set_status = self.__is_message_field_set(obj, attr_name)
                    if set_status == False:
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            logger.trace(f"Hide unset optional field '{attr_name}' in object type '{self.get_object_type_fullname(obj)}' (field type: {Typing.get_object_class_fullname(attr_val)})")
                        continue
                
                # Skip oneof field that is not set
                if self.__is_message_field_oneof_field(obj, attr_name):
                    set_status = self.__is_message_field_set(obj, attr_name)
                    if set_status == False:
                        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                            logger.trace(f"Hide unset oneof field '{attr_name}' in object type '{self.get_object_type_fullname(obj)}' (field type: {Typing.get_object_class_fullname(attr_val)})")
                        continue
                
                res.extend(self.__get_object_field_names(attr_val, recursive=recursive, uncollapse_repeated=uncollapse_repeated, add_repeated_index=add_repeated_index, with_unset=with_unset, prefix=new_prefix, is_message_field=True, sort_order=sort_order))
            return res
        
        def __is_message_field_oneof_field(self, obj, field_name):
            field_descr = self.__get_object_field_descriptor(obj, field_name)
            res = (field_descr.label == FieldDescriptor.LABEL_OPTIONAL 
                   and field_descr.containing_oneof is not None
                   and field_descr.has_presence)
            return res
        
        def __is_message_field_optional(self, obj, field_name):
            field_descr = self.__get_object_field_descriptor(obj, field_name)
            res = (field_descr.label == FieldDescriptor.LABEL_OPTIONAL 
                   and field_descr.containing_oneof is not None and len(field_descr.containing_oneof.fields) == 1
                   and field_descr.has_presence)
            return res
        
        def __is_message_field_repeated(self, obj, field_name):
            field_descr = self.__get_object_field_descriptor(obj, field_name)
            return (field_descr.label == FieldDescriptor.LABEL_REPEATED)
        
        def __is_message_field_required(self, obj, field_name):
            field_descr = self.__get_object_field_descriptor(obj, field_name)
            return (field_descr.label == FieldDescriptor.LABEL_REQUIRED)
        
        def __is_message_field_set(self, obj, field_name):
            """
            If field can distinguish between unpopulated and default values, return if field is set, else return None.
            """
            try:
                return obj.HasField(field_name)
            except ValueError:
                # logger.trace(f"Field '{field_name}' is not optional. Got error: {exc}")
                return None
            
        def __get_object_descriptor_field_names(self, obj, raise_exception=True, sort_order=SortOrder.Definition):
            #TODO EKL: manage oneof fields => return only the name of the oneof field that is defined 
            if hasattr(obj, 'DESCRIPTOR'):
                descriptor = getattr(obj, 'DESCRIPTOR')
                # TODO: When it will be possible with python generated code, remove from result the deprecated fields
                # logger.info(f"+++++++++++++ descriptor: {self.__represent_descriptor(descriptor)}")
                res = [f.name for f in descriptor.fields if not hasattr(f, "isDeprecated")]
                if sort_order == SortOrder.Alphabetic:
                    res.sort()
                return res
            else:
                # return Typing.get_object_attribute_names(obj)
                if raise_exception:
                    raise TechnicalException(f"Not found attribute 'DESCRIPTOR' in object of type '{self.get_object_type_fullname(obj)}' [{obj}]")
                else:
                    return []
                
        def __get_object_field_descriptor(self, obj, field_name):
            if hasattr(obj, 'DESCRIPTOR'):
                descriptor = getattr(obj, 'DESCRIPTOR')
                if field_name in descriptor.fields_by_name:
                    return descriptor.fields_by_name[field_name]
                else:
                    raise FunctionalException(f"Field '{field_name}' doesn't exist in type '{self.get_object_type_fullname(obj)}'")
            else:
                raise TechnicalException(f"Not found attribute 'DESCRIPTOR' in object of type '{self.get_object_type_fullname(obj)}' [{obj}]")
                
        def __has_object_field(self, obj, field_name=None, field_fullname=None):
            param_in_brackets = None
            if field_name is None:
                field_name, param_in_brackets = self.__split_attribute_fullname(field_fullname)
                
            if len(field_name) == 0:
                # Manage field_fullname in format "[XXX]"
                if param_in_brackets is not None:
                    if self.is_object_repeated(obj):
                        if Converter.is_integer(param_in_brackets):
                            li_index = int(param_in_brackets)
                            res = li_index < len(obj)
                        else:
                            raise FunctionalException(f"For repeated objects, the parameter in brackets must be an integer (field fullname: '{field_fullname}')")
                    elif self.is_object_map(obj):
                        res = param_in_brackets in obj
                        # if not res:
                        #     logger.trace(f"++++++ Key '{param_in_brackets}' in not in map {obj}")
                    else:
                        raise TechnicalException(f"Unexpected brackets in field fullname '{field_fullname}' for object of type '{self.get_object_type_fullname(obj)}'")
                else:
                    raise TechnicalException(f"Unexpected field " + f"fullname '{field_fullname}'" if field_fullname is not None else f"name '{field_name}'")
            elif self.is_object_map(obj):
                res = field_name in obj
            else:
                res = field_name in self.__get_object_descriptor_field_names(obj, False)
                
            if not res:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"Field '{field_name}' doesn't exist in type '{self.get_object_type_fullname(obj)}' (existing fields: {self.__get_object_descriptor_field_names(obj, False)})")
            return res
        
        def __get_object_field_type_fullname(self, obj, field_name):
            if not self.__has_object_field(obj, field_name):
                raise FunctionalException()
            
            field_descr = self.__get_object_field_descriptor(obj, field_name)
            if field_descr.message_type:
                return self.get_object_type_fullname(descriptor=field_descr.message_type)
            elif field_descr.enum_type:
                return self.get_object_type_fullname(descriptor=field_descr.enum_type)
            else:
                return field_descr.type
        
        def __get_object_field(self, obj, field_name=None, field_fullname=None, create_field=False):
            param_in_brackets = None
            if field_name is None:
                field_name, param_in_brackets = self.__split_attribute_fullname(field_fullname)
            
            if len(field_name) == 0:
                # Manage field_fullname in format "[XXX]"
                if param_in_brackets is not None:
                    if self.is_object_repeated(obj):
                        if Converter.is_integer(param_in_brackets):
                            li_index = int(param_in_brackets)
                            res = self.__get_object_repeated_by_index(obj, li_index, add_index=create_field)
                        else:
                            raise FunctionalException(f"For repeated objects, the parameter in brackets must be an integer (field fullname: '{field_fullname}')")
                    elif self.is_object_map(obj):
                        res = obj[param_in_brackets]
                    else:
                        raise TechnicalException(f"Unexpected brackets in field fullname '{field_fullname}' for object of type '{self.get_object_type_fullname(obj)}'")
                else:
                    raise TechnicalException(f"Unexpected field " + f"fullname '{field_fullname}'" if field_fullname is not None else f"name '{field_name}'")
            
            elif self.is_object_map(obj):
                res = obj[field_name]
                
            elif hasattr(obj, field_name):
                if param_in_brackets is not None:
                    if Converter.is_integer(param_in_brackets):
                        li_index = int(param_in_brackets)
                        res = self.__get_object_repeated_field_by_index(obj, field_name, li_index, add_index=create_field)
                    else:
                        res = getattr(obj, field_name)[param_in_brackets]
                else:
                    res = getattr(obj, field_name)
                
                # Manage enum
                res = self.__get_enum_name_if_field_is_enum(res, obj=obj, field_name=field_name)
                
            elif self.__has_object_field(obj, field_name=field_name):
                if create_field:
                    field_type_fullname = self.__get_object_field_type_fullname(obj, field_name)
                    if isinstance(field_type_fullname, int):
                        raise TechnicalException("Unexpected case: the native types are expected to exist in object")
                    res = self.new_object(field_type_fullname)
                    setattr(obj, field_name, res)
                else:
                    raise FunctionalException(f"Field '{field_name}' exists in type '{self.get_object_type_fullname(obj)}' but not in instance [{obj}]")
            else:
                raise FunctionalException(f"Field '{field_name}' doesn't exist in type '{self.get_object_type_fullname(obj)}'")
    
            return res
        
        def __get_object_repeated_by_index(self, obj, index, add_index=False):
            if not ProtobufMessages.is_object_repeated(obj):
                raise FunctionalException(f"Object of type '{self.get_object_type_fullname(obj)}' is not a repeated")
            
            # Add repeated element if it doesn't exist
            if len(obj) < index + 1:
                if add_index:
                    for _ in range(index + 1 - len(obj)):
                        res = obj.add()
                else:
                    raise FunctionalException(f"Index {index} exceeds repeated length {len(obj)}")
            else:
                res = obj[index]
                
            return res
        
        def __get_object_repeated_field_by_index(self, obj, field_name, index, add_index=False):
            field_obj = getattr(obj, field_name)
            if not ProtobufMessages.is_object_repeated(field_obj):
                raise FunctionalException(f"Field '{field_name}' is not a repeated in type '{self.get_object_type_fullname(obj)}'")
            if len(field_obj) < index + 1 and not add_index:
                raise FunctionalException(f"Index {index} exceeds repeated length {len(field_obj)} (field '{field_name}' in object of type '{self.get_object_type_fullname(obj)}' [{obj}])")
            
            return self.__get_object_repeated_by_index(field_obj, index, add_index)
        
        def get_object_type_fullname(self, obj=None, obj_class=None, descriptor=None):
            # None type
            if obj is None and obj_class is None and descriptor is None:
                return None.__class__.__name__
    
            # Object -> object class
            if obj is not None:
                return self.get_object_type_fullname(obj_class=type(obj))
    
            # Object class -> object class descriptor
            if hasattr(obj_class, 'DESCRIPTOR'):
                return self.get_object_type_fullname(descriptor=obj_class.DESCRIPTOR)
            
            # Extract information from descriptor
            if descriptor:
                if hasattr(descriptor, 'full_name'):
                    return descriptor.full_name
                elif descriptor.containing_type is not None:
                    containing_fullname = self.get_object_type_fullname(obj_class=descriptor.containing_type)
                    return containing_fullname + '.' + descriptor.name
                else:
                    raise TechnicalException(f"Failed to extract type fullname from descriptor: {self.__represent_descriptor(descriptor)}")
                
            # Extract information from classzhDM
            if obj_class.__module__.endswith('_pb2'):
                package_name = os.path.splitext(obj_class.__module__)[0]
                return package_name + '.' + obj_class.__name__
            else:
                return obj_class.__module__ + '.' + obj_class.__name__
    
        def __set_object_fields_with_name_value_table(self, obj, table):
            # Verify table structure
            ValueTableManager.verify_table_is_name_value_table(table)
            
            for row in table.rows:
                if row.get_cell(1).value_type not in [ValueTypes.NotApplicable]:
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"Setting protobuf object field with row ({row})")
                    
                    name = row.get_cell(0).value
                    value = row.get_cell(1).value
                    
                    self.set_object_field_value(obj, name, value)
                    
        def __set_object_fields_with_dict(self, obj, values_dict):
            for name, value in values_dict.items():
                self.set_object_field_value(obj, name, value)
        
        def __check_field_value_to_set_is_valid(self, value):
            if value is undefined_argument or value is undefined_value:
                raise ValueError(f"Special objects undefined_* are not valid field values")
            
        def __set_object_field(self, obj, field_name=None, field_fullname=None, value=None, create_field=False):
            in_brackets_str = None
            if field_name is None:
                field_name, in_brackets_str = self.__split_attribute_fullname(field_fullname)
            if not self.__has_object_field(obj, field_name):
                raise TechnicalException(f"Field '{field_name}' doesn't exist in type '{self.get_object_type_fullname(obj)}'")
            self.__check_field_value_to_set_is_valid(value)
            
            try:
                if hasattr(obj, field_name):
                    if in_brackets_str is not None:
                        from holado_test.scenario.step_tools import StepTools
                        in_brackets_obj = StepTools.evaluate_scenario_parameter(in_brackets_str)
                        if isinstance(in_brackets_obj, int):
                            li_index = in_brackets_obj
                            self.__set_object_repeated_field_by_index(obj, field_name, li_index, value, add_index=create_field)
                        else:
                            field_obj = getattr(obj, field_name)
                            field_obj[in_brackets_obj] = value
                    elif self.is_object_map(getattr(obj, field_name)):
                        field_obj = getattr(obj, field_name)
                        for key in value:
                            field_obj[key] = value[key]
                    elif self.is_object_repeated(getattr(obj, field_name)):
                        self.__set_object_repeated_field(obj, field_name, value, add_index=True)
                    else:
                        field_type_fullname = self.__get_object_field_type_fullname(obj, field_name)
                        if isinstance(field_type_fullname, int):
                            self.__set_object_field_attr(obj, field_name, value)
                        else:
                            field_descr = self.__get_object_field_descriptor(obj, field_name)
                            # logger.trace(f"+++++ Setting field '{field_name}' of descriptor: {self.__represent_descriptor(field_descr)}")
                            if field_descr.enum_type is not None:
                                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                                    logger.trace(f"Setting enum field '{field_name}' (type: {field_type_fullname}) with value [{value}] (type: {Typing.get_object_class_fullname(value)})")
                                enum_value = self.__get_enum_value(value, enum_type_descriptor=field_descr.enum_type)
                                self.__set_object_field_attr(obj, field_name, enum_value)
                            else:
                                field_obj = getattr(obj, field_name)
                                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                                    logger.trace(f"Setting field '{field_name}' (type: {field_type_fullname}) with value [{value}] (type: {Typing.get_object_class_fullname(value)})")
                                try:
                                    self.__set_object_value(field_obj, value)
                                except HAException as exc:
                                    raise TechnicalException(f"Unmanaged set of value [{value}] (type: {Typing.get_object_class_fullname(value)}) in field of type '{field_type_fullname}' (field '{field_name}' in object of type '{self.get_object_type_fullname(obj)}' [{obj}])\n  -> {exc.message}") from exc
                                except Exception as exc:
                                    raise TechnicalException(f"Unmanaged set of value [{value}] (type: {Typing.get_object_class_fullname(value)}) in field of type '{field_type_fullname}' (field '{field_name}' in object of type '{self.get_object_type_fullname(obj)}' [{obj}])\n  -> {str(exc)}") from exc
                elif self.__has_object_field(obj, field_name=field_name):
                    if create_field:
                        field_type_fullname = self.__get_object_field_type_fullname(obj, field_name)
                        if isinstance(field_type_fullname, int):
                            self.__set_object_field_attr(obj, field_name, value)
                        else:
                            res = self.new_object(field_type_fullname)
                            try:
                                self.__set_object_value(res, value)
                            except Exception as exc:
                                raise TechnicalException(f"Unmanaged set of value [{value}] (type: {Typing.get_object_class_fullname(value)}) in field of type '{field_type_fullname}' (field '{field_name}' in object of type '{self.get_object_type_fullname(obj)}' [{obj}])\n  -> {exc.message}") from exc
                            setattr(obj, field_name, res)
                    else:
                        raise FunctionalException(f"Field '{field_name}' exists in type '{self.get_object_type_fullname(obj)}' but not in instance [{obj}]")
                else:
                    raise FunctionalException(f"Field '{field_name}' doesn't exist in type '{self.get_object_type_fullname(obj)}'")
            except (FunctionalException, TechnicalException):
                raise
            except Exception as exc:
                if hasattr(obj, field_name):
                    field_obj = getattr(obj, field_name)
                    raise TechnicalException(f"Failed to set field '{field_name}' (type: '{Typing.get_object_class_fullname(field_obj)}') with value [{value}] (type '{Typing.get_object_class_fullname(value)}')") from exc
                else:
                    raise TechnicalException(f"Failed to set field '{field_name}' (type: Unknown) with value [{value}] (type '{Typing.get_object_class_fullname(value)}')") from exc
                    
        def __set_object_field_attr(self, obj, field_name, value):
            if value is None:
                obj.ClearField(field_name)
            else:
                setattr(obj, field_name, value)
    
        def __get_enum_name_if_field_is_enum(self, value, field_descriptor=None, obj=None, field_name=None):
            if field_descriptor is None:
                field_descriptor = self.__get_object_field_descriptor(obj, field_name)
            if field_descriptor.enum_type is not None:
                enum_name = self.__get_enum_name(value, enum_type_descriptor=field_descriptor.enum_type)
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"Getting enum field '{field_descriptor.name}' (type: {field_descriptor.enum_type} ; full_name: {field_descriptor.full_name}): value [{value}] -> name [{enum_name}]")
                return enum_name
            else:
                return value
    
        def __get_enum_name(self, name_or_value, enum_type=None, enum_type_descriptor=None):
            if enum_type is None and enum_type_descriptor is None:
                raise TechnicalException(f"Parameter 'enum_type' or 'enum_type_descriptor' must be defined")
            if enum_type is not None:
                enum_type_descriptor = enum_type.DESCRIPTOR
                
            if isinstance(name_or_value, str):
                return name_or_value
            elif isinstance(name_or_value, int):
                if name_or_value in enum_type_descriptor.values_by_number:
                    return self.__get_enum_name_for_value(enum_type_descriptor, name_or_value)
                else:
                    raise FunctionalException(f"Enum type '{enum_type_descriptor.full_name}' has no value '{name_or_value}' (possible values: {[k for k in enum_type_descriptor.values_by_number]})")
            elif self.is_object_repeated(name_or_value):
                return [self.__get_enum_name(v, enum_type_descriptor=enum_type_descriptor) for v in name_or_value]
            else:
                raise TechnicalException(f"Unexpected value type '{Typing.get_object_class_fullname(name_or_value)}'")
        
        def __get_enum_name_for_value(self, enum_type_descriptor, value):
            enum_type_fullname = self.get_object_type_fullname(descriptor=enum_type_descriptor)
            if not enum_type_fullname in self.__enum_data_by_fullname:
                self.__load_enum_data(enum_type_fullname, enum_type_descriptor)
            return self.__enum_data_by_fullname[enum_type_fullname].values_by_number[value].name
            
        def __get_enum_value(self, name_or_value, enum_type=None, enum_type_descriptor=None):
            if enum_type is None and enum_type_descriptor is None:
                raise TechnicalException(f"Parameter 'enum_type' or 'enum_type_descriptor' must be defined")
            if enum_type is not None:
                enum_type_descriptor = enum_type.DESCRIPTOR
                
            if isinstance(name_or_value, str):
                if name_or_value in enum_type_descriptor.values_by_name:
                    return enum_type_descriptor.values_by_name[name_or_value].number
                else:
                    raise FunctionalException(f"Enum type '{enum_type_descriptor.full_name}' has no name '{name_or_value}' (possible names: {[k for k in enum_type_descriptor.values_by_name]})")
            else:
                return name_or_value
        
        def __load_enum_data(self, enum_type_fullname, enum_type_descriptor):
            if enum_type_fullname in self.__enum_data_by_fullname:
                raise TechnicalException(f"Data of enum type '{enum_type_fullname}' was already loaded")
            data = NamedTuple('EnumData', values_by_number=dict)
            data.values_by_number = {}
            for value in enum_type_descriptor.values:
                if value.number not in data.values_by_number or value.index > data.values_by_number[value.number].index:
                    data.values_by_number[value.number] = value
            self.__enum_data_by_fullname[enum_type_fullname] = data
        
        def __set_object_value(self, field_obj, value, raise_exception=True):
            res = False
            for hpt in self.__registered_types:
                if hpt.is_instance_of(field_obj):
                    res = hpt.set_object_value(field_obj, value, raise_exception=raise_exception)
                    if res:
                        break
                    
            if not res and raise_exception:
                field_classes = inspect.getmro(type(field_obj))
                registered_types_str = ', '.join([f"{t} ({t.protobuf_class()})" for t in self.__registered_types])
                raise TechnicalException(f"Failed to manage type of field {Typing.get_object_class_fullname(field_obj)} (classes: {field_classes}) with registered types (and internal types): {registered_types_str}")
            return res
        
        def __set_object_repeated_field(self, obj, field_name, values, add_index=False):
            if not isinstance(values, list):
                raise FunctionalException(f"For repeated field '{field_name}', parameter 'values' is not a list (type: {Typing.get_object_class_fullname(values)})")
            
            for index, value in enumerate(values):
                self.__set_object_repeated_field_by_index(obj, field_name, index, value, add_index)
        
        def __set_object_repeated_field_by_index(self, obj, field_name, index, value, add_index=False):
            repeated_field_obj = getattr(obj, field_name)
            if not ProtobufMessages.is_object_repeated(repeated_field_obj):
                raise FunctionalException(f"Field '{field_name}' is not a repeated in type '{self.get_object_type_fullname(obj)}'")
            self.__check_field_value_to_set_is_valid(value)
            
            field_descr = self.__get_object_field_descriptor(obj, field_name)
            if field_descr.message_type is not None:
                # Get field object at given index
                if len(repeated_field_obj) < index + 1:
                    if add_index:
                        for _ in range(index + 1 - len(repeated_field_obj)):
                            obj_at_index = repeated_field_obj.add()
                    else:
                        raise FunctionalException(f"Index {index} exceeds repeated length {len(repeated_field_obj)} (field '{field_name}' in type '{self.get_object_type_fullname(obj)}')")
                else:
                    obj_at_index = repeated_field_obj[index]
                    
                # Set field object value
                try:
                    self.__set_object_value(obj_at_index, value)
                except Exception as exc:
                    raise TechnicalException(f"Unmanaged set of value [{value}] (type: {Typing.get_object_class_fullname(value)}) in repeated field of type '{self.get_object_type_fullname(obj_at_index)}' (at index {index} of field '{field_name}' in object of type '{self.get_object_type_fullname(obj)}' [{obj}])\n  -> {exc.message}") from exc
            else:
                if field_descr.enum_type is not None:
                    value_to_set = self.__get_enum_value(value, enum_type_descriptor=field_descr.enum_type)
                else:
                    value_to_set = value
                    
                if len(repeated_field_obj) < index:
                    if add_index:
                        for _ in range(index - len(repeated_field_obj)):
                            repeated_field_obj.append(type(value)())
                    else:
                        raise FunctionalException(f"Index {index} exceeds repeated length {len(repeated_field_obj)} (field '{field_name}' in object [{obj}])")
                    
                if len(repeated_field_obj) == index:
                    if add_index:
                        try:
                            repeated_field_obj.append(value_to_set)
                        except Exception as exc:
                            raise TechnicalException(f"Failed to add value [{value_to_set}] in repeated field at index {index} (field '{field_name}' in type '{self.get_object_type_fullname(obj)}')") from exc
                    else:
                        raise FunctionalException(f"Index {index} exceeds repeated length {len(repeated_field_obj)} (field '{field_name}' in type '{self.get_object_type_fullname(obj)}')")
                else:
                    try:
                        repeated_field_obj[index] = value_to_set
                    except Exception as exc:
                        raise TechnicalException(f"Failed to set value [{value_to_set}] in repeated field at index {index} (field '{field_name}' in type '{self.get_object_type_fullname(obj)}')") from exc
                
        def __split_attribute_fullname(self, attr_fullname):
            m = self.__regex_attribute_fullname.match(attr_fullname)
            res = [m.group(1), m.group(2)]
            # logger.trace(f"++++++++++ __split_attribute_fullname('{attr_fullname}') => {res}")
            return res
    
        def __represent_descriptor(self, descr, indent=0):
            res_str = [str(type(descr))]
            for name, value in Typing.get_object_attributes(descr):
                if "_by_" in name:
                    res_str.append(f"    {name}:")
                    for el in value:
                        res_str.append(f"        {el}: {self.__represent_descriptor(value[el], 8) if 'Descriptor' in str(type(value[el])) else value[el]}")
                else:
                    # if name == "containing_type":
                        res_str.append(f"    {name}: {value}")
                    # else:
                    #     res_str.append(f"    {name}: {self.__represent_descriptor(value, 4) if 'Descriptor' in str(type(value)) else value}")
            return Tools.indent_string(indent, "\n".join(res_str))
            
        def _register_types(self):
            # Duration must be registered before Message
            from holado_protobuf.ipc.protobuf.types.google.protobuf import Duration as hpt_Duration
            self.register_type(hpt_Duration)
    
            # Timestamp must be registered before Message
            from holado_protobuf.ipc.protobuf.types.google.protobuf import Timestamp as hpt_Timestamp
            self.register_type(hpt_Timestamp)
    
            from holado_protobuf.ipc.protobuf.types.google.protobuf import Message as hpt_Message
            self.register_type(hpt_Message)
    
        def register_type(self, protobuf_type, index=None):
            """
            Register a holado protobuf type (subclass of holado_protobuf.ipc.protobuf.abstracts.type.Type)
            """
            if protobuf_type in self.__registered_types:
                raise TechnicalException(f"Protobuf type '{protobuf_type.__class__.__name__}' is already registered")
            
            if index is not None:
                self.__registered_types.insert(index, protobuf_type)
            else:
                self.__registered_types.append(protobuf_type)


