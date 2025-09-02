
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
from holado_core.common.tables.table_with_header import TableWithHeader
from google.protobuf import json_format
from holado_core.common.tools.converters.converter import Converter
from holado_core.common.tools.tools import Tools
from holado_protobuf.ipc.protobuf.types.google.protobuf import Duration,\
    Timestamp
from holado.common.handlers.enums import AutoNumber

logger = logging.getLogger(__name__)


class SortOrder(AutoNumber):
    """
    Sort order.
    """
    
    Definition = ()
    Alphabetic = ()
    


class ProtobufConverter(object):
    """
    Manage the conversion of Protobuf types (in given ProtobufMessages) to many types.
    """
    def __init__(self): 
        self.__protobuf_messages = None
    
    def initialize(self, protobuf_messages): 
        self.__protobuf_messages = protobuf_messages
    
    def create_table_with_protobuf_fields_as_columns(self, list_proto_obj, recursive=False, uncollapse_repeated=False, with_unset=True):
        res = TableWithHeader()
    
        if len(list_proto_obj) > 0:
            # Set table header
            self.__fill_table_header_with_protobuf_fields(res, list_proto_obj[0], recursive=recursive, uncollapse_repeated=uncollapse_repeated, with_unset=with_unset)
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Result table - set header {res.header.represent(0)}")
            
            # Add table rows
            self.__fill_table_rows_with_protobuf_fields(res, list_proto_obj, uncollapse_repeated=uncollapse_repeated)
            
        return res
    
    def __fill_table_header_with_protobuf_fields(self, res_table, obj, recursive=False, uncollapse_repeated=False, with_unset=True):
        attribute_names = self.__protobuf_messages.get_message_field_names(obj, recursive=recursive, uncollapse_repeated=uncollapse_repeated, with_unset=with_unset)
        res_table.header.add_cells_from_contents(cells_content=attribute_names)
    
    def __fill_table_rows_with_protobuf_fields(self, res_table, list_obj, uncollapse_repeated=False):
        for obj in list_obj:
            if uncollapse_repeated:
                values_by_name = {cn: self.__protobuf_messages.get_object_field_values(obj, cn) for cn in res_table.get_column_names()}
                
                names_uncollapsed = [cn for cn in values_by_name if len(values_by_name[cn]) > 1]
                
                if len(names_uncollapsed) == 0:
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"Result table - add row with {values_by_name}")
                    values_by_name = {cn: values_by_name[cn][0] for cn in values_by_name}
                    res_table.add_row(contents_by_colname=values_by_name)
                elif len(names_uncollapsed) == 1:
                    name_uncollapsed = names_uncollapsed[0]
                    values_uncollapsed = values_by_name.pop(name_uncollapsed)
                    values_by_name = {cn: values_by_name[cn][0] for cn in values_by_name}
                    for value in values_uncollapsed:
                        vbn = dict(values_by_name)
                        vbn[name_uncollapsed] = value
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"Result table - add row with {vbn}")
                        res_table.add_row(contents_by_colname=vbn)
                else:
                    raise TechnicalException("Uncollapse two different repeated fields in the same message is not managed.")
            else:
                values_by_name = {cn: self.__protobuf_messages.get_object_field_value(obj, cn) for cn in res_table.get_column_names()}
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Result table - add row with {values_by_name}")
                res_table.add_row(contents_by_colname=values_by_name)
    
    def convert_protobuf_object_to_json_object(self, proto_obj):
        if isinstance(proto_obj, Timestamp.protobuf_class()) or isinstance(proto_obj, Duration.protobuf_class()):
            # Note: currently, Python doesn't support nanoseconds in datetime, thus it is replaced by string format managed in Protobuf types when available
            return proto_obj.ToJsonString()
        elif self.__protobuf_messages.is_object_repeated(proto_obj):
            return [self.convert_protobuf_object_to_json_object(fv) for fv in proto_obj]
        elif self.__protobuf_messages.is_object_map(proto_obj):
            return dict(proto_obj)
        elif self.__protobuf_messages.is_object_message(proto_obj):
            # Note: following commented code could be an alternative, but it doesn't convert correctly some protobuf types to json
            #     res_str = json_format.MessageToJson(proto_obj)
            #     return json.loads(res_str)
            
            res = {}
            attr_names = self.__protobuf_messages.get_object_field_names(proto_obj, with_unset=False)
            for attr_name in attr_names:
                # Manage special fields
                if hasattr(proto_obj, attr_name):
                    attr_value = getattr(proto_obj, attr_name)
                    if (isinstance(attr_value, Timestamp.protobuf_class()) or isinstance(attr_value, Duration.protobuf_class())
                        or self.__protobuf_messages.is_object_repeated(attr_value) or self.__protobuf_messages.is_object_map(attr_value)
                        or self.__protobuf_messages.is_object_message(attr_value)
                        ):
                        res[attr_name] = self.convert_protobuf_object_to_json_object(attr_value)
                        continue
                    
                # Default
                attr_value = self.__protobuf_messages.get_object_field_value(proto_obj, attr_name)
                if not Converter.is_primitive(attr_value):
                    attr_value = json_format.MessageToDict(attr_value)
                res[attr_name] = attr_value
            return res
        elif Converter.is_primitive(proto_obj):
            return proto_obj
        else:
            raise TechnicalException(f"Unmanaged protobuf object of type '{type(proto_obj)}'")
    
    def convert_protobuf_object_to_name_value_table(self, proto_obj, recursive=False, uncollapse_repeated=False, with_unset=True, sort_order=SortOrder.Definition):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting Protobuf object {id(proto_obj)} to Name/Value table")
        res = TableWithHeader()
        res.header.add_cells_from_contents(["Name", "Value"])
        
        attr_names = self.__protobuf_messages.get_object_field_names(proto_obj, recursive=recursive, uncollapse_repeated=uncollapse_repeated, add_repeated_index=True, with_unset=with_unset, sort_order=sort_order)
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting Protobuf object {id(proto_obj)} to Name/Value table: field names = {attr_names}")
            
        for attr_name in attr_names:
            attr_val = self.__protobuf_messages.get_object_field_value(proto_obj, attr_name)
            row = res.add_row(cells_content=(attr_name, attr_val))
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Converting Protobuf object {id(proto_obj)} to Name/Value table: added row {row}")
            
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Convert Protobuf object {id(proto_obj)} to Name/Value table =>\n{res.represent(indent=4)}")
        return res


    