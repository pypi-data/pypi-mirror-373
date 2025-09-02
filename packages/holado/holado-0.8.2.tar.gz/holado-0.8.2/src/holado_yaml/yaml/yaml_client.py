
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
from holado.common.context.session_context import SessionContext
from holado.common.handlers.object import Object
import abc
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.typing import Typing
from holado_yaml.yaml.enums import UpdateType
import os
from holado_python.common.iterables import remove_all
from holado.common.handlers.undefined import not_applicable, undefined_value
from io import StringIO
from holado_core.common.tools.tools import Tools


logger = logging.getLogger(__name__)


class YAMLClient(Object):
    """
    Client for actions on YAML files.
    """
    __metaclass__ = abc.ABCMeta
    
    @classmethod
    def _get_path_manager(cls):
        return SessionContext.instance().path_manager
    
    def __init__(self, name=None):
        super().__init__(name)
    
    def load_file(self, file_path):
        with open(file_path, 'r') as file:
            res = self.load_io_file(file)
            
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Load YAML file '{file_path}' => [{Typing.get_object_class_fullname(res)}] {res}")
        return res
    
    def load_string(self, text):
        with StringIO(text) as file:
            res = self.load_io_file(file)
            
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Load YAML string [{text}] => [{Typing.get_object_class_fullname(res)}] {res}")
        return res
    
    def load_io_file(self, file_like_object):
        raise NotImplementedError()
    
    def load_multiple_documents_file(self, file_path):
        with open(file_path, 'r') as file:
            res = self.load_multiple_documents_io_file(file)
        return res
        
    def load_multiple_documents_string(self, text):
        with StringIO(text) as file:
            res = self.load_multiple_documents_io_file(file)
        return res
        
    def load_multiple_documents_io_file(self, file_like_object):
            raise NotImplementedError()
        
    def save_in_file(self, file_path, data, mode=None, user=None, group=None, **kwargs):
        self._get_path_manager().makefile(file_path, mode=mode, user=user, group=group)
        
        with open(file_path, 'w') as file:
            self.save_in_io_file(file, data, **kwargs)
    
    def save_in_string(self, data, **kwargs):
        with StringIO() as file:
            self.save_in_io_file(file, data, **kwargs)
            res = file.getvalue()
        return res
    
    def save_in_io_file(self, file_like_object, data, **kwargs):
        raise NotImplementedError()
    
    def update_file(self, file_path, data, update_type=UpdateType.AddOrUpdate, with_backup=True, backup_extension='.bak', mode=None, user=None, group=None, **kwargs):
        # If file doesn't exist, create an empty file
        self._get_path_manager().makefile(file_path, mode=mode, user=user, group=group)
        
        # Manage backup
        # Note: It is done after potential empty file creation, so that restore will leave the file empty or remove it  
        if with_backup:
            if backup_extension is None:
                backup_extension = '.bak'
            backup_path = file_path + backup_extension
            if not self._get_path_manager().check_file_exists(backup_path, raise_exception=False):
                self._get_path_manager().copy_path_recursively(file_path, backup_path, user=user, group=group)
                self._get_path_manager().check_file_exists(backup_path, raise_exception=True)
        
        # Update file
        dst_data = self.load_file(file_path)
        if dst_data is None:
            dst_data = data
        else:
            self.update_data(dst_data, data, update_type)
        self.save_in_file(file_path, dst_data, **kwargs)        # Note: as file already exists, it is not needed to pass parameters mode, user and group
    
    def update_string(self, text, data, update_type=UpdateType.AddOrUpdate, **kwargs):
        dst_data = self.load_string(text)
        if dst_data is None:
            dst_data = data
        else:
            self.update_data(dst_data, data, update_type)
        res = self.save_in_string(dst_data, **kwargs)
        return res
    
    def update_data(self, dst, src, update_type=UpdateType.AddOrUpdate):
        if dst is None:
            raise TechnicalException("Destination data cannot be None")
        if isinstance(src, str):
            src = self.load_string(src)
        
        self._update_data_object(dst, src, update_type)
    
    def _update_data_object(self, dst, src, update_type=UpdateType.AddOrUpdate):
        if isinstance(src, dict):
            self._update_data_dict(dst, src, update_type)
        elif isinstance(src, list):
            self._update_data_list(dst, src, update_type)
        else:
            raise TechnicalException(f"Unmanaged update of object of type {Typing.get_object_class_fullname(dst)} with data of type {Typing.get_object_class_fullname(src)}")
    
    def _update_data_dict(self, dst, src, update_type=UpdateType.AddOrUpdate):
        if update_type == UpdateType.AddOrUpdate:
            for key, value in src.items():
                if key not in dst or not (isinstance(value, dict) or isinstance(value, list)):
                    dst[key] = value
                else:
                    self._update_data_object(dst[key], value, update_type)
        elif update_type == UpdateType.Delete:
            for key, value in src.items():
                if key in dst:
                    if isinstance(value, dict) or isinstance(value, list):
                        self._update_data_object(dst[key], value, update_type)
                        if not dst[key]:
                            del dst[key]
                    else:
                        del dst[key]
        elif update_type == UpdateType.Replace:
            for key, value in src.items():
                if key in dst and isinstance(value, dict):
                    has_inner_dict = any(map(lambda x:isinstance(x, dict), value.values()))
                    if has_inner_dict:
                        self._update_data_object(dst[key], value, update_type)
                    else:
                        dst[key] = value
                else:
                    dst[key] = value
        else:
            raise TechnicalException(f"Unamanged update type {update_type}")
    
    def _update_data_list(self, dst, src, update_type=UpdateType.AddOrUpdate):
        if update_type == UpdateType.AddOrUpdate:
            for value in src:
                dst.append(value)
        elif update_type == UpdateType.Delete:
            for value in src:
                remove_all(dst, value)
        elif update_type == UpdateType.Replace:
            for index, value in enumerate(src):
                if value is not_applicable:
                    continue
                if index < len(dst):
                    if isinstance(value, dict) or isinstance(value, list):
                        self._update_data_object(dst[index], value, update_type)
                    else:
                        dst[index] = value
                else:
                    while len(dst) < index:
                        dst.append(undefined_value)
                    dst.append(value)
        else:
            raise TechnicalException(f"Unamanged update type {update_type}")
    
    def restore_file(self, file_path, backup_extension='.bak', remove_empty_file=False):
        if backup_extension is None:
            backup_extension = '.bak'
        backup_path = file_path + backup_extension
        if self._get_path_manager().check_file_exists(backup_path, raise_exception=False):
            # Replace file by backup
            self._get_path_manager().rename(backup_path, file_path, raise_if_exists=False)
            
            # Manage remove of empty file
            if remove_empty_file and os.path.getsize(file_path) == 0:
                self._get_path_manager().remove_path(file_path)



