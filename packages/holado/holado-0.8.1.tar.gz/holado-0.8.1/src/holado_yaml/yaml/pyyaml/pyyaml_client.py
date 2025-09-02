
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
from holado_core.common.tools.tools import Tools
from holado_yaml.yaml.yaml_client import YAMLClient
from holado_core.common.exceptions.technical_exception import TechnicalException


logger = logging.getLogger(__name__)

try:
    import yaml  # @UnresolvedImport
    with_yaml = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"YAML is not available with pyyaml. Initialization failed on error: {exc}")
    with_yaml = False



class PyYAMLClient(YAMLClient):
    """
    Client for actions on YAML files.
    """
    
    @classmethod
    def is_available(cls):
        return with_yaml
    
    def __init__(self, name=None, client_type=None):
        super().__init__(name)
        
        if client_type == "base":
            self.__loader_type = yaml.BaseLoader
            self.__dumper_type = yaml.BaseDumper
        elif client_type == "full":
            self.__loader_type = yaml.FullLoader
            self.__dumper_type = yaml.Dumper
        elif client_type == "safe" or client_type is None:
            self.__loader_type = yaml.SafeLoader
            self.__dumper_type = yaml.SafeDumper
        elif client_type == "unsafe":
            self.__loader_type = yaml.UnsafeLoader
            self.__dumper_type = yaml.Dumper
        else:
            raise TechnicalException(f"Unmanaged client type '{client_type}'")
    
    def load_io_file(self, file_like_object):
        return yaml.load(file_like_object, self.__loader_type)
    
    def load_multiple_documents_io_file(self, file_like_object):
        return list(yaml.load_all(file_like_object, self.__loader_type))
        
    def save_in_io_file(self, file_like_object, data, **kwargs):
        if 'sort_keys' not in kwargs:
            kwargs['sort_keys'] = False
        yaml.dump(data, file_like_object, **kwargs)
    



