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

# This file is a helper to build generic scripts using HolAdo solution.
# Usually, it is copied and adapted for specific usage.

import os
import logging
import argparse
from holado_helper.initialize_holado import insert_sys_path, insert_sys_paths


def _chdir(path):
    res = os.getcwd()
    os.chdir(path)
    return res

def _initialize_holado(TSessionContext=None, logging_config_file_path=None, log_level=logging.WARNING, log_in_file=False, with_session_path=False, **kwargs):
    import holado
    session_kwargs={'with_session_path':with_session_path or log_in_file}
    if kwargs:
        session_kwargs.update(kwargs)
    holado.initialize_for_script(TSessionContext=TSessionContext, logging_config_file_path=logging_config_file_path,
                                 log_level=log_level, log_in_file=log_in_file, log_on_console=not log_in_file, 
                                 session_kwargs=session_kwargs)
    
def initialize(work_dir_path=None, change_work_dir=True, 
               log_level=logging.INFO, log_in_file=False, 
               TSessionContext=None, additional_sys_paths=None, with_session_path=False):
    res = None
    sys_paths = []
    if work_dir_path:
        if change_work_dir:
            res = _chdir(work_dir_path)
        sys_paths = [work_dir_path]
    
    if additional_sys_paths:
        sys_paths.extend(additional_sys_paths)
    insert_sys_paths(sys_paths)
    
    logging_config_file_path=None
    for dir_path in [res, work_dir_path, os.getcwd()]:
        if dir_path is not None:
            file_path = os.path.join(dir_path, "logging.conf")
            if os.path.exists(file_path):
                logging_config_file_path = file_path
                break
    
    _initialize_holado(TSessionContext, logging_config_file_path, log_level, log_in_file, with_session_path)
    
    return res

def change_working_dir(work_dir_path=None):
    if work_dir_path:
        res = _chdir(work_dir_path)
        insert_sys_path(work_dir_path)
        return res
    else:
        return None

def parse_logging_args():
    log_parser = get_logging_argument_parser()
    res, _ = log_parser.parse_known_args()
    return res

def get_logging_argument_parser(description=None, additional_arguments=None, add_help=False):
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter, add_help=add_help)

    parser.add_argument('-ll', '--log-level', choices=['ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'], dest='log_level', default='WARNING',
                   help='Log level')
    
    parser.add_argument('-lf', '--log-in-file', dest='log_in_file', default=False, action="store_true",
                   help='If specified, log in file rather than console')
    
    if additional_arguments:
        for add_arg in additional_arguments:
            parser.add_argument(*add_arg[0], **add_arg[1])
    
    return parser
    
def change_logging_config(log_level=logging.INFO, log_in_file=False):
    import holado
    holado.change_logging_config(log_level=log_level, log_in_file=log_in_file, log_on_console=not log_in_file)
    
