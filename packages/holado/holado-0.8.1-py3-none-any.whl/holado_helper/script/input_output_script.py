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

# This file is a helper to build scripts using HolAdo solution, with CSV files as input.
# Usually, it is copied and adapted for specific usage.


import logging
import os
import re
from holado_helper.script.script import Script
from holado_core.common.exceptions.technical_exception import TechnicalException

logger = logging.getLogger(__name__)


class InputOutputScript(Script):
    
    def __init__(self, work_dir_path=None, with_input=True, with_output=True, with_template=False):
        super().__init__()
        self.__work_dir_path = work_dir_path
        self.__with_input = with_input
        self.__with_output = with_output
        self.__with_template = with_template
    
    @property
    def with_input(self):
        return self.__with_input
    
    @property
    def with_output(self):
        return self.__with_output
    
    @property
    def with_template(self):
        return self.__with_template
    
    def initialize(self):
        super().initialize()
        
        if self.__work_dir_path is not None:
            self.change_working_dir(self.__work_dir_path)
    
    def is_matching_file_path(self, input_file_path, raise_exception=False):
        raise NotImplementedError
    
    def is_matching_input_file_path(self, input_file_path, raise_exception=False):
        return self.is_matching_file_path(input_file_path, raise_exception)
    
    def is_matching_output_file_path(self, input_file_path, raise_exception=False):
        return self.is_matching_file_path(input_file_path, raise_exception)
    
    def _new_argument_parser(self, description=None, additional_arguments=None, add_help=True):
        parser = super()._new_argument_parser(description=description, additional_arguments=additional_arguments, add_help=add_help)
        
        if self.__with_input:
            parser.add_argument('-i', '--input', dest='input_filename', default=None,
                           help='Input file name')
        
        if self.__with_output:
            parser.add_argument('-o', '--output', dest='output_filename', default=None,
                           help='Output file name (no output by default)')
        
        if self.__with_template:
            parser.add_argument('-ot', '--output-template', dest='output_template', default=False, action="store_true",
                           help='If specified, output a template')
        
        return parser
    
    def _build_input_path(self, input_filename, cwd):
        if input_filename is None:
            logger.print(f"Input filename must be specified with parameter '-i' (-h for help)")
            exit(1)
            
        input_path = self._build_path(input_filename, cwd)
        if not os.path.exists(input_path):
            logger.print(f"Input file '{input_path}' doesn't exist")
            exit(1)
        
        return input_path
    
    def _build_output_template_path(self):
        """Return output template path.
        It should be overriden, and call _build_output_path with appropriate base_default_path argument.
        """
        return self._build_output_path(self.args.output_filename, None, self.user_working_dir)
    
    def _build_output_path(self, output_filename, base_default_path, cwd, raise_exception=True):
        res = None
        if output_filename is not None:
            res = self._build_path(output_filename, cwd)
        elif base_default_path is not None:
            output_path_base, with_suffix, ext = self._build_output_path_base(base_default_path)
            if with_suffix:
                res = self._build_path(f"{output_path_base}-SUCCESS{ext}", cwd)
            else:
                res = self._build_path(f"{output_path_base}{ext}", cwd)
        elif raise_exception:
            raise TechnicalException("Failed to build output path, one of parameters 'output_filename' and 'base_default_path' must be defined")
        return res
    
    def _build_output_path_base(self, output_path):
        res, ext = os.path.splitext(output_path)
        with_suffix = False
        if res.endswith('-SUCCESS'):
            res = res[:-len('-SUCCESS')]
            with_suffix = True
        else:
            m = re.match(r'^(.*)-FAIL(_\d+)?$', res)
            if m:
                res = m.group(1)
                with_suffix = True
        return res, with_suffix, ext
    
    def _build_output_path_from_base(self, output_path_base, ext):
        output_path = f"{output_path_base}{ext}"
        if os.path.exists(output_path):
            suffix_index = 1
            output_path = f"{output_path_base}_{suffix_index}{ext}"
            while os.path.exists(output_path):
                suffix_index += 1
                output_path = f"{output_path_base}_{suffix_index}{ext}"
        return output_path
    

