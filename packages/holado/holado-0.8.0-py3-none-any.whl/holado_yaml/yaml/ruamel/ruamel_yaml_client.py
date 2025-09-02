
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


logger = logging.getLogger(__name__)

try:
    import ruamel.yaml  # @UnresolvedImport
    with_ruamel_yaml = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"YAML is not available with ruamel.yaml. Initialization failed on error: {exc}")
    with_ruamel_yaml = False



class RuamelYAMLClient(YAMLClient):
    """
    Client for actions on YAML files.
    """
    
    @classmethod
    def is_available(cls):
        return with_ruamel_yaml
    
    def __init__(self, name=None, client_type=None, **kwargs):
        super().__init__(name)
        
        if client_type is None:
            client_type = kwargs.get('typ')
        self.__internal_client = ruamel.yaml.YAML(typ=client_type, **kwargs)
    
    @property
    def internal_client(self):
        return self.__internal_client
    
    def load_io_file(self, file_like_object):
        res = self.internal_client.load(file_like_object)
        self._rm_style_info(res)
        return res
    
    def load_multiple_documents_io_file(self, file_like_object):
        res = list(self.internal_client.load_all(file_like_object))
        self._rm_style_info(res)
        return res
        
    def save_in_io_file(self, file_like_object, data, **kwargs):
        self.internal_client.dump(data, file_like_object, **kwargs)
    
    def _rm_style_info(self, d):
        """Remove style info so that fields order can be preserved if saved again.
        """
        if isinstance(d, dict):
            if hasattr(d, 'fa'):
                d.fa._flow_style = None
            for k, v in d.items():
                self._rm_style_info(k)
                self._rm_style_info(v)
        elif isinstance(d, list):
            if hasattr(d, 'fa'):
                d.fa._flow_style = None
            for elem in d:
                self._rm_style_info(elem)



