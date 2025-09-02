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
from holado_helper.script.initialize_script import get_logging_argument_parser
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)

class Script(object):
    
    def __init__(self, with_args=True):
        self.__with_args = with_args
        
        self.__args = None
        self.__cwd = None
        self.__user_work_dir=None
    
    @property
    def args(self):
        return self.__args
    
    @property
    def cwd(self):
        """ Current working directory
        A script can change its working directory by calling 'change_working_dir' method.
        """
        if self.__cwd is not None:
            return self.__cwd
        else:
            return os.getcwd()
    
    @property
    def user_working_dir(self):
        """ User working directory
        Although the user working directory is persisted.
        """
        if self.__user_work_dir is not None:
            return self.__user_work_dir
        else:
            return os.getcwd()
    
    @user_working_dir.setter
    def user_working_dir(self, wd):
        self.__user_work_dir = wd
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Changed user working dir to '{self.__user_work_dir}'")
    
    def parse_args(self):
        arg_parser = self.new_argument_parser()
        self.__args = arg_parser.parse_args()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Parsed args: {self.__args}")
    
    def new_argument_parser(self):
        raise NotImplementedError
    
    def _new_argument_parser(self, description=None, additional_arguments=None, add_help=True):
        parser = get_logging_argument_parser(description=description, additional_arguments=additional_arguments, add_help=add_help)
        return parser
    
    def change_working_dir(self, work_dir_path):
        from holado_helper.script.initialize_script import change_working_dir as init_cd    # @UnresolvedImport
        
        # If user working dir is not yet defined, save current working dir as user working dir
        if self.__user_work_dir is None:
            self.user_working_dir = os.getcwd()
        
        # Change working dir
        new_cwd = init_cd(work_dir_path)
        self.__cwd = new_cwd
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Changed script working dir to '{self.__cwd}'")
    
    def initialize(self):
        if self.args is not None and hasattr(self.args, 'log_level') and hasattr(self.args, 'log_in_file'):
            from holado_helper.script.initialize_script import change_logging_config # @UnresolvedImport
            change_logging_config(log_level=self.args.log_level, log_in_file=self.args.log_in_file)
    
    def run(self):
        self.parse_args()
        self.initialize()
        self.run_script()
        
    def run_script(self):
        raise NotImplementedError
    
    def _build_path(self, filename, cwd):
        if os.path.isabs(filename):
            return filename
        else:
            return os.path.join(cwd, filename)


