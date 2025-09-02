
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

from holado.holado_config import Config
import traceback
import sys
from holado_core.common.handlers.enums import AccessType
import logging
import time
from holado_python.standard_library.typing import Typing
from holado.common.handlers.undefined import default_value

logger = logging.getLogger(__name__)


def reversed_enumerate(l):
    return zip(range(len(l)-1, -1, -1), reversed(l))

def reversed_range(min_, max_=None, step=-1):
    if max_ is None:
        min_, max_ = 0, min_
    return range(max_-1, min_-1, step)


class Tools(object):
    
    @classmethod
    def get_indent_string(cls, indent):
        return " " * indent
    
    @classmethod
    def indent_string(cls, indent, txt, *, do_indent_first_line=True):
        ind_str = Tools.get_indent_string(indent)
        lines = txt.split("\n") if txt else []
        if do_indent_first_line:
            return ind_str + ("\n" + ind_str).join(lines)
        else:
            return ("\n" + ind_str).join(lines)

    @classmethod
    def truncate_text(cls, text, length=Config.message_truncate_length, truncated_suffix=default_value, is_length_with_suffix=False, is_suffix_with_truncated_length=True):
        """Truncate text if needed.
        Default truncate suffix is '[...(xxx)]' if is_suffix_with_truncated_length=True else '[...]'
        Note: length can be None, meaning no truncate to do
        """
        if length is not None and len(text) > length:
            if truncated_suffix is default_value:
                truncated_suffix = f"[...({len(text)-length})]" if is_suffix_with_truncated_length else "[...]"
            if truncated_suffix:
                if is_length_with_suffix:
                    return text[0 : length - len(truncated_suffix)] + truncated_suffix
                else:
                    return text[0 : length] + truncated_suffix
            else:
                return text[0 : length]
        else:
            return text
    
    @classmethod
    def represent_exception(cls, exc, tb=None, indent=0):
        if sys.version_info >= (3,10):
            if tb is not None:
                list_format = traceback.format_exception(exc, value=exc, tb=tb)
            else:
                list_format = traceback.format_exception(exc)
        else:
            list_format = traceback.format_exception(type(exc), exc, exc.__traceback__)
        return Tools.indent_string(indent, "".join(list_format))
    
    @classmethod
    def represent_object(cls, obj, indent=0, *, do_indent_first_line=True, full_details=False, access_type=AccessType.Public, max_level=3):
        return cls.__represent_object(obj, indent, do_indent_first_line, full_details, access_type, max_level, [])
    
    @classmethod
    def __represent_object(cls, obj, indent, do_indent_first_line, full_details, access_type, max_level, _internal):
        from holado_core.common.tools.converters.converter import Converter
        
        if Converter.is_primitive(obj) and not Converter.is_dict(obj) and not Converter.is_list(obj):
            # logger.print(f"+++++ Tools.__represent_object: is primitive")
            res = f"{obj} [{str(type(obj))}]" if full_details else f"{obj}"
        else:
            id_obj = id(obj)
            if id_obj in _internal:
                res = f"[RECURSION] (type: {str(type(obj))} ; id: {id_obj})" if full_details else f"[RECURSION]"
            else:
                _internal.append(id_obj)
                
                if Converter.is_dict(obj):
                    # logger.print(f"+++++ Tools.__represent_object: is dict")
                    res_list = [f"{str(type(obj))}({id_obj})"] if full_details else []
                    # keys = sorted(value.keys())
                    keys = list(obj.keys())
                    for key in keys:
                        # logger.print(f"+++++ Tools.__represent_object:     key: {key}")
                        val_str = cls.__represent_object(obj[key], 0, True, full_details, access_type, max_level-1, _internal)
                        if '\n' in val_str:
                            res_list.append(f"    {key}:")
                            res_list.append(Tools.indent_string(4, val_str))
                        else:
                            res_list.append(f"    {key}: {val_str}")
                    res = "\n".join(res_list)
                elif Converter.is_list(obj):
                    # logger.print(f"+++++ Tools.__represent_object: is list")
                    res_list = [f"{str(type(obj))}({id_obj})"] if full_details else ["["]
                    # keys = sorted(value.keys())
                    for el in obj:
                    # for index, el in enumerate(obj):
                    #     logger.print(f"+++++ Tools.__represent_object:     index: {index}")
                        el_str = cls.__represent_object(el, 0, True, full_details, access_type, max_level-1, _internal)
                        if '\n' in el_str:
                            res_list.append("    {")
                            res_list.append(Tools.indent_string(4, el_str))
                            res_list.append("    }")
                        else:
                            res_list.append(f"    {el_str}")
                    if not full_details:
                        res_list.append("]")
                    res = "\n".join(res_list)
                else:
                    if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"Representing object of type {Typing.get_object_class_fullname(obj)}")
                    attributes = Typing.get_object_attributes(obj, access_type=access_type)
                    # logger.print(f"+++++ Tools.__represent_object: {str(type(obj))} is object with {attributes=}")
                    if attributes:
                        res_list = [f"{str(type(obj))}({id_obj})"] if full_details else [f"{str(type(obj))}"]
                        if max_level > 0:
                            for name, value in attributes:
                                # logger.print(f"+++++ Tools.__represent_object:     attribute '{name}'")
                                res_list.append(f"    {name}: {cls.__represent_object(value, 4, False, full_details, access_type, max_level-1, _internal)}")
                        res = "\n".join(res_list)
                    else:
                        res = f"{obj} [{str(type(obj))}({id_obj})]" if full_details else f"{obj}"
                        # raise TechnicalException(f"Unmanaged representation of object of type '{Typing.get_object_class_fullname(obj)}'")
        
        return Tools.indent_string(indent, res, do_indent_first_line=do_indent_first_line)
    
    @classmethod
    def has_sub_kwargs(cls, kwargs: dict, prefix: str):
        for k in kwargs.keys():
            if k.startswith(prefix):
                return True
        return False
    
    @classmethod    
    def pop_sub_kwargs(cls, kwargs: dict, prefix: str):
        res = {}
        for k in list(kwargs.keys()):
            if k.startswith(prefix):
                res[k[len(prefix):]] = kwargs.pop(k)
        return res
    
    @classmethod
    def do_log_level(cls, log_level, max_log_level):
        """Define the log level to use: if log_level is greater than max_log_level, return max_log_level.
        """
        return min(log_level, max_log_level)
    
    @classmethod
    def do_log(cls, logger, log_level, max_log_level=logging.CRITICAL):
        return logger.isEnabledFor(cls.do_log_level(log_level, max_log_level))
    
    @classmethod
    def do_log_if_objects_are_different(cls, logger, log_level, obj1, obj2, max_log_level=logging.CRITICAL):
        try:
            return cls.do_log(logger, log_level, max_log_level) and (obj1 != obj2)
        except Exception as exc:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Assume a log is needed since usually a comparison fails on mismatching types and thus objects are different. Obtained error: {exc}")
            return True
    
    @classmethod
    def raise_same_exception_type(cls, exception, new_message, add_from=True):
        exc = type(exception)(new_message)
        if add_from:
            raise exc from exception
        else:
            raise exc
    
    @classmethod
    def timer_s(cls):
        return time.perf_counter()
    
    @classmethod
    def timer_ns(cls):
        return time.perf_counter_ns()
    

