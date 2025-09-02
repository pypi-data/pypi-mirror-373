
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
from holado_yaml.yaml.ruamel.ruamel_yaml_client import RuamelYAMLClient
from holado_yaml.yaml.pyyaml.pyyaml_client import PyYAMLClient
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_yaml.yaml.enums import UpdateType


logger = logging.getLogger(__name__)



class YAMLManager(object):
    """
    Manage actions on YAML files.
    """
    
    @classmethod
    def is_available(cls):
        return RuamelYAMLClient.is_available() or PyYAMLClient.is_available()
    
    @classmethod
    def get_client(cls, client_type, **kwargs):
        if RuamelYAMLClient.is_available():
            return RuamelYAMLClient(client_type=client_type)
        elif PyYAMLClient.is_available():
            return PyYAMLClient(client_type=client_type)
        else:
            raise TechnicalException("Missing dependencies")
    
    
    # Manage YAML files
    
    @classmethod
    def load_file(cls, file_path, client_type=None, client=None):
        client = client if client is not None else cls.get_client(client_type)
        return client.load_file(file_path)
    
    @classmethod
    def load_multiple_documents_file(cls, file_path, client_type=None, client=None):
        client = client if client is not None else cls.get_client(client_type)
        return client.load_multiple_documents_file(file_path)
    
    @classmethod
    def save_in_file(cls, file_path, data, client_type=None, client=None):
        client = client if client is not None else cls.get_client(client_type)
        client.save_in_file(file_path, data)
    
    @classmethod
    def update_file(cls, file_path, data, update_type=UpdateType.AddOrUpdate, client_type=None, client=None, with_backup=True, backup_extension='.bak'):
        client = client if client is not None else cls.get_client(client_type)
        client.update_file(file_path, data, update_type, with_backup, backup_extension)
    
    @classmethod
    def restore_file(cls, file_path, client_type=None, client=None, backup_extension='.bak'):
        client = client if client is not None else cls.get_client(client_type)
        client.restore_file(file_path, backup_extension)
    
    
    # Manage YAML strings
    
    @classmethod
    def load_string(cls, text, client_type=None, client=None):
        client = client if client is not None else cls.get_client(client_type)
        return client.load_string(text)
    
    @classmethod
    def load_multiple_documents_string(cls, text, client_type=None, client=None):
        client = client if client is not None else cls.get_client(client_type)
        return client.load_multiple_documents_string(text)
    
    @classmethod
    def save_in_string(cls, data, client_type=None, client=None):
        client = client if client is not None else cls.get_client(client_type)
        return client.save_in_string(data)
    
    @classmethod
    def update_string(cls, text, data, update_type=UpdateType.AddOrUpdate, client_type=None, client=None):
        client = client if client is not None else cls.get_client(client_type)
        return client.update_string(text, data, update_type)


