
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
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.typing import Typing
from holado_core.common.exceptions.functional_exception import FunctionalException

logger = logging.getLogger(__name__)


def create_name_value_table_from_json(json_value, recursive=False, uncollapse_list=False):
    from holado_json.ipc.json_converter import JsonConverter
    
    res = TableWithHeader()
    res.header.add_cells_from_contents(["Name", "Value"])
    
    converter = JsonConverter()
    json_value = converter.to_json(json_value)
    
    name_values = convert_json_value_2_name_values(json_value, recursive=recursive, uncollapse_list=uncollapse_list)
    for name, value in name_values:
        res.add_row(cells_content=(name, value))
    
    return res
    
def create_table_with_header_from_json(json_value, recursive=False, uncollapse_list=False):
    from holado_json.ipc.json_converter import JsonConverter
    
    res = TableWithHeader()
    
    converter = JsonConverter()
    json_value = converter.to_json(json_value)
    
    if isinstance(json_value, list):
        json_list = json_value
    else:
        json_list = [json_value]
    
    for json_val in json_list:
        json_val = converter.to_json(json_val)
        
        name_values = convert_json_value_2_name_values(json_val, recursive=recursive, uncollapse_list=uncollapse_list)
        
        # Add new columns if needed
        for name, value in name_values:
            if not res.has_column(name, raise_exception=False):
                res.add_column(name=name, cells_content = [None]*res.nb_rows)
        
        # Fill table
        values_by_name = {name: value for name, value in name_values}
        res.add_row(contents_by_colname = values_by_name)
        
    # Order columns
    if res.nb_columns > 0:
        res.order_columns(names = sorted(res.get_column_names()))
        
    return res
    
def convert_json_value_2_name_values(json_value, recursive=False, uncollapse_list=False, as_dict=False, sorted_=False):
    """Convert json object as a list of (name, value).
    If as_dict is True, the result is a dict of {name:value}
    """
    res = []
    __fill_name_values_with_json_value(res, None, json_value, recursive=recursive, uncollapse_list=uncollapse_list)
    
    if sorted_:
        res = sorted(res)
    if as_dict:
        res = {e[0]:e[1] for e in res}
    return res
    
def __fill_name_values_with_json_value(res, name_prefix, json_value, recursive=False, uncollapse_list=False):
    if isinstance(json_value, dict):
        __fill_name_values_with_json_dict(res, name_prefix, json_value, recursive=recursive, uncollapse_list=uncollapse_list)
    elif isinstance(json_value, list):
        __fill_name_values_with_json_list(res, name_prefix, json_value, recursive=recursive, uncollapse_list=uncollapse_list)
    else:
        res.append((name_prefix, json_value))
    
def __fill_name_values_with_json_dict(res, name_prefix, json_value, recursive=False, uncollapse_list=False):
    if not isinstance(json_value, dict):
        raise TechnicalException(f"json value is expected to be a dict (obtained: {Typing.get_object_class_fullname(json_value)}")
    
    sorted_dict = dict(sorted(json_value.items()))
    for name, value in sorted_dict.items():
        new_prefix = f"{name_prefix}.{name}" if name_prefix is not None and len(name_prefix) > 0 else name
        if recursive:
            __fill_name_values_with_json_value(res, new_prefix, value, recursive=recursive, uncollapse_list=uncollapse_list)
        else:
            res.append((new_prefix, value))
    
def __fill_name_values_with_json_list(res, name_prefix, json_value, recursive=False, uncollapse_list=False):
    if not isinstance(json_value, list):
        raise TechnicalException(f"json value is expected to be a list (obtained: {Typing.get_object_class_fullname(json_value)}")
    
    if not uncollapse_list:
        res.append((name_prefix, json_value))
        return
        
    if len(json_value) == 0:
        res.append((name_prefix+"[]", None))
        return
        
    for index, value in enumerate(json_value):
        new_prefix = f"{name_prefix}[{index}]" if name_prefix is not None else f"[{index}]"
        __fill_name_values_with_json_value(res, new_prefix, value, recursive=recursive, uncollapse_list=uncollapse_list)


def set_object_attributes_with_json_dict(obj, json_value):
    if not isinstance(json_value, dict):
        raise TechnicalException(f"json value is expected to be a dict (obtained: {Typing.get_object_class_fullname(json_value)}")
    
    for attr_name, attr_value_json in json_value.items():
        if hasattr(obj, attr_name):
            if isinstance(attr_value_json, dict) and not isinstance(getattr(obj, attr_name), dict):
                set_object_attributes_with_json_dict(getattr(obj, attr_name), attr_value_json)
            else:
                setattr(obj, attr_name, attr_value_json)
        else:
            raise FunctionalException(f"Object doesn't have attribute '{attr_name}' (object type: {Typing.get_object_class_fullname(obj)})")


def update_json_object_with_missing_attributes(json_obj, json_ref, recursive=False):
    if not isinstance(json_obj, dict):
        raise TechnicalException(f"json object is expected to be a dict (obtained: {Typing.get_object_class_fullname(json_obj)}")
    if not isinstance(json_ref, dict):
        raise TechnicalException(f"json reference is expected to be a dict (obtained: {Typing.get_object_class_fullname(json_ref)}")

    for key, value in json_ref.items():
        if key not in json_obj:
            json_obj[key] = value
        elif recursive and isinstance(json_obj[key], dict) and isinstance(value, dict):
            update_json_object_with_missing_attributes(json_obj[key], value, recursive=recursive)
    
