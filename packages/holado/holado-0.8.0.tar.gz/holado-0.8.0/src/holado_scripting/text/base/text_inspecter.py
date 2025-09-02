
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
from builtins import object
import re
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class TextInspecter(object):

    def __init__(self):
        self.__variable_manager = None
        self.__expression_evaluator = None
        
        self.__registered_functions = {}
        
        self.__regex_function = re.compile(r"^(\w+)\((.*)\)$")
        self.__regex_to_be_interpreted_with_function = re.compile(r"^\$\{(\w+)\((.*)\)\}$")
        
    def initialize(self, var_manager, expression_evaluator):
        self.__variable_manager = var_manager
        self.__expression_evaluator = expression_evaluator
    
    @property
    def _expression_evaluator(self):
        return self.__expression_evaluator
    
    @property
    def _variable_manager(self):
        return self.__variable_manager
    
    def is_to_interpret(self, text):
        # r_match = self.__regex_to_be_interpreted.match(text)
        # if r_match:
        #     return True
        #
        # indexes = self.__search_interpret_section(text)
        # return indexes is not None
        return self.get_number_of_sections(text) > 0
    
    def get_number_of_sections(self, text):
        section_indexes = self._search_all_interpret_sections(text)
        return len(section_indexes)
    
    def _search_all_interpret_sections(self, str_to_interpret):
        m = None
        match_failed = False
        exc_msgs = []
        
        # Try to use regex to group "${" with "}" and "{" with "}", but without skipping "{{" and "}}"
        reg = self.__build_regex_matching_interpret_sections(str_to_interpret, do_match_semicolon_open=True, do_skip_double_semicolon=False)
        try:
            m = re.match(reg, str_to_interpret, re.DOTALL)
        except Exception as exc:
            exc_msgs.append(f"Error while matching string to built regex:\n    regex: [{reg}]\n   string: [{str_to_interpret}]\n    error: {exc}")
            match_failed = True
            
        # If failed, try to use regex to group "${" with "}" and "{" with "}", and skipping "{{" and "}}"
        if match_failed:
            match_failed = False
            reg = self.__build_regex_matching_interpret_sections(str_to_interpret, do_match_semicolon_open=True, do_skip_double_semicolon=True)
            try:
                m = re.match(reg, str_to_interpret, re.DOTALL)
            except Exception as exc:
                exc_msgs.append(f"Error while matching string to built regex:\n    regex: [{reg}]\n   string: [{str_to_interpret}]\n    error: {exc}")
                match_failed = True
            
        # If failed, try to use regex to group "${" with "}", but do not group "{" with "}"
        if match_failed:
            match_failed = False
            reg = self.__build_regex_matching_interpret_sections(str_to_interpret, do_match_semicolon_open=False, do_skip_double_semicolon=False)
            try:
                m = re.match(reg, str_to_interpret, re.DOTALL)
            except Exception as exc:
                exc_msgs.append(f"Error while matching string to built regex:\n    regex: [{reg}]\n   string: [{str_to_interpret}]\n    error: {exc}")
                match_failed = True
            
        if match_failed:
            msgs = Tools.indent_string(4, '\n'.join(exc_msgs))
            raise TechnicalException("Failed to search interpret sections for string [{str_to_interpret}]:\n{msgs}"\
                                     .format(str_to_interpret=str_to_interpret, msgs=msgs))
        elif m is None:
            raise TechnicalException(f"Failed to build a working regex:\n    regex: [{reg}]\n   string: [{str_to_interpret}]")
        
        # Find all "${"
        section_start_indexes = [m.start() for m in re.finditer(r'\$\{', str_to_interpret)]
        
        # Intersect both search
        return [r for r in m.regs[1:] if r[0] in section_start_indexes]
    
    def __build_regex_matching_interpret_sections(self, str_to_interpret, do_match_semicolon_open=False, do_skip_double_semicolon=False):
        res = str_to_interpret
        
        # First, replace byte sections
        m = re.search(r"b'[^']*'", res)
        while m:
            res = res[:m.start()] + '.'*(m.end()-m.start()) + res[m.end():]
            m = re.search(r"b'[^']*'", res)
        
        res = res.replace('(','.')\
                 .replace(')','.')\
                 .replace('${','(..')
        if do_skip_double_semicolon:
            res = res.replace('{{', '..')
            res = res.replace('}}','..')
        if do_match_semicolon_open:
            res = res.replace('{','(.')
        res = res.replace('}','.)')
        res = re.sub(r'[^()]', '.', res)
        return res
        
    # Note: this first implementation of _search_interpret_section works but is slower
    # def _search_interpret_section(self, text, start=0, excluded_indexes=None):
    #     if excluded_indexes is None:
    #         excluded_indexes = []
    #
    #     sub_text = text if start == 0 else text[start:]
    #     list_indexes = self._search_all_interpret_sections(sub_text)
    #     for indexes in list_indexes:
    #         res_indexes = indexes if start == 0 else tuple(v+start for v in indexes)
    #         if res_indexes not in excluded_indexes:
    #             return res_indexes
    #     return None
    def _search_interpret_section(self, text, start=0, excluded_indexes=None):
        if excluded_indexes is None:
            excluded_indexes = []
    
        offset = start
        ind_beg = None
        ind_end = None
    
        while True:
            # Find first section delimiters after offset
            if ind_beg is None:
                ind_beg = text.find("${", offset)
                if ind_beg < 0:
                    return None
            if ind_end is None:
                ind_end = text.find("}", ind_beg)
                if ind_end < 0:
                    return None
    
            # Find closest begin separator to end separator
            ind = text.find("${", ind_beg + 2)
            if ind > 0 and ind < ind_end:
                # Continue with next begin section
                ind_beg = ind
                continue
    
            # If section not in excluded ones, section is found
            if (ind_beg, ind_end+1) not in excluded_indexes:
                return (ind_beg, ind_end+1)
    
            # Try again with new offset
            offset = ind_end + 1
            ind_beg = None
            ind_end = None
    
        raise TechnicalException("Unexpected case")
        
    def _get_args(self, args_str):
        return args_str.split(',')
        
    def _has_function(self, text, with_interpreted=True):
        func_name, _ = self._get_function_and_args_strings(text, with_interpreted)
        if func_name is not None:
            func = self._get_function(func_name)
            return func is not None
        return False
        
    def _get_function_and_args_strings(self, text, with_interpreted=True):
        if with_interpreted:
            r_match = self.__regex_to_be_interpreted_with_function.match(text)
        else:
            r_match = self.__regex_function.match(text)
        if r_match:
            return r_match.group(1), r_match.group(2)
        else:
            return None, None
        
    def _get_function(self, func_name):
        if func_name in self.__registered_functions:
            return self.__registered_functions[func_name]
        else:
            return None
        
    def register_function(self, function_name, function):
        self.__registered_functions[function_name] = function
        
    
