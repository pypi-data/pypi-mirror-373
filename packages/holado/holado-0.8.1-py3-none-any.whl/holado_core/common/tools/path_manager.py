
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
from glob import glob
import shutil
import re
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from datetime import datetime
from holado_core.common.tools.tools import Tools
from pathlib import Path

logger = logging.getLogger(__name__)


class PathManager(object):

    def __init__(self):
        pass
    
    def get_user_group(self, path):
        p = Path(path)
        return p.owner(), p.group()
    
    def get_mode(self, path):
        return os.stat(path).st_mode & 0o777
    
    def makedirs(self, path, mode = None, is_directory = False, user = None, group = None):
        if not is_directory:
            path = os.path.dirname(path)
        if not os.path.exists(path):
            if mode:
                os.makedirs(path, mode)
            else:
                os.makedirs(path)
            self.chown(path, user, group)
            
    def makefile(self, path, mode = None, user = None, group = None):
        if not os.path.exists(path):
            self.makedirs(path, mode, False, user, group)
            open(path, 'a').close()
            
            if mode:
                os.chmod(path, mode)
            self.chown(path, user, group)
            
    def remove_path(self, path, ignore_errors=False):
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as exc:
                if not ignore_errors:
                    raise exc
        elif os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=ignore_errors)
            
    def remove_paths(self, glob_pattern, ignore_errors=False):
        paths = glob(glob_pattern)
        for path in paths:
            self.remove_path(path, ignore_errors)
                
    def copy_path_recursively(self, src_path, dst_path, filter_patterns = None, ignore_patterns = None, do_log = False, log_prefix = "", user = None, group = None):
    #         logging.debug("Copying path '{}' -> '{}' (ignoring {})".format(src_path, dst_path, ignore_patterns))
        # Copy path
        if os.path.isfile(src_path):
            if self.__filter_path(src_path, filter_patterns=filter_patterns, ignore_patterns=ignore_patterns, do_log=do_log, log_prefix=log_prefix):
                if do_log:
                    logger.debug("{}Copy file '{}' -> '{}".format(log_prefix, src_path, dst_path))
                self.makedirs(dst_path, user=user, group=group)
                shutil.copy2(src_path, dst_path)
                self.chown(dst_path, user, group)
        elif os.path.isdir(src_path):
            lp = os.listdir(src_path)
            for cp in lp:
                cur_src_path = os.path.join(src_path, cp)
                cur_dst_path = os.path.join(dst_path, cp)
                self.copy_path_recursively(cur_src_path, cur_dst_path, filter_patterns=filter_patterns, ignore_patterns=ignore_patterns, do_log=do_log, log_prefix=log_prefix, user=user, group=group)
    
    def __filter_paths(self, paths, filter_patterns = None, ignore_patterns = None, do_log = False, log_prefix = ""):
        if filter_patterns is not None and not isinstance(filter_patterns, list):
            raise TechnicalException("Parameter 'filter_patterns' must be None or a list of patterns")
        if ignore_patterns is not None and not isinstance(ignore_patterns, list):
            raise TechnicalException("Parameter 'ignore_patterns' must be None or a list of patterns")
        
        res = []
        for path in paths:
            if self.__filter_path(path, filter_patterns, ignore_patterns, do_log, log_prefix):
                res.append(path)
                
        return res
    
    def __filter_path(self, path, filter_patterns = None, ignore_patterns = None, do_log = False, log_prefix = ""):
        if filter_patterns is not None and not isinstance(filter_patterns, list):
            raise TechnicalException("Parameter 'filter_patterns' must be None or a list of patterns")
        if ignore_patterns is not None and not isinstance(ignore_patterns, list):
            raise TechnicalException("Parameter 'ignore_patterns' must be None or a list of patterns")
        
        if filter_patterns is not None and len(filter_patterns) > 0:
            is_matching_a_filter = False
            for pattern in filter_patterns:
                if re.match(pattern, path):
                    if do_log:
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"{log_prefix}File '{path}' is matching filter '{pattern}'")
                    is_matching_a_filter = True
                    break
            if not is_matching_a_filter:
                if do_log:
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"{log_prefix}File '{path}' is excluded by filters {filter_patterns}")
                return False

        if ignore_patterns is not None and len(ignore_patterns) > 0:
            is_ignored = False
            for pattern in ignore_patterns:
                if re.match(pattern, path):
                    if do_log:
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"{log_prefix}File '{path}' is ignored since it matches pattern '{pattern}'")
                    is_ignored = True
                    break
            if is_ignored:
                return False

        return True
    
    def rename(self, src, dst, raise_if_exists=True):
        if raise_if_exists:
            os.rename(src, dst)
        else:
            os.replace(src, dst)
    
    def get_user_home_path(self):
        import pathlib
        return str(pathlib.Path.home())
    
    def get_local_resources_path(self, name=None):
        base_path = os.getenv('HOLADO_LOCAL_RESOURCES_BASEDIR')
        if base_path is None:
            base_path = os.path.join(self.get_user_home_path(), '.holado', 'resources')
        
        if name is not None:
            return os.path.join(base_path, name)
        else:
            return base_path
    
    def get_reports_path(self, name=None):
        base_path = os.getenv('HOLADO_OUTPUT_BASEDIR')
        if base_path is None:
            base_path = os.path.join(self.get_user_home_path(), '.holado', 'output')
        
        if name is not None:
            return os.path.join(base_path, "reports", name)
        else:
            return os.path.join(base_path, "reports")
    
    def chown(self, path, user = None, group = None):
        if user is not None or group is not None:
            if user is None or group is None:
                raise TechnicalException(f"User and group (name or ID) cannot be None (user={user} ; group={group})")
            shutil.chown(path, user, group)
    
    def check_file_exists(self, path, do_exist=True, raise_exception=True):
        """
        @param path Path
        @param do_exist Define to check if file exists or not
        @param raise_exception If True, raises an exception rather than returning False
        @return True if given path is an existing file
        """
        res = (do_exist == os.path.exists(path))
        
        if not res and raise_exception:
            raise FunctionalException(f"File '{path}' " + "doesn't exist" if do_exist else "exists")
        return res
    
    def get_timestamped_path(self, prefix, ext, dt=None, dt_format="%Y%m%d-%H%M%S"):
        ext = ext.strip('.')
        if dt is None:
            dt = datetime.now()
        now_str = datetime.strftime(dt, dt_format)
        return f"{prefix}_{now_str}.{ext}"
    
    def find_files_starting_with(self, dir_path, prefix):
        res = []
        for filename in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, filename)) and filename.startswith(prefix):
                res.append(os.path.join(dir_path, filename))
        return res
    
    def find_file_starting_with(self, dir_path, prefix):
        files = self.find_files_starting_with(dir_path, prefix)
        
        if len(files) == 0:
            raise FunctionalException(f"Unable to find a file starting with '{prefix}' in folder '{dir_path}'")
        elif len(files) > 1:
            raise FunctionalException(f"Found many ({len(files)}) files starting with '{prefix}' in folder '{dir_path}': {files}")
        return files[0]
    
