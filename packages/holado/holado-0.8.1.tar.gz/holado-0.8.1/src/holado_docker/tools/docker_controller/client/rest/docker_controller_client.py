
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
from holado_rest.api.rest.rest_client import RestClient

logger = logging.getLogger(__name__)


class DockerControllerClient(RestClient):
    
    def __init__(self, name, url, headers=None):
        super().__init__(name, url, headers)
    
    # Common features
    
    def get_environment_variable_value(self, var_name):
        data = [var_name]
        response = self.get(f"os/env", data=data)
        return self.response_result(response, status_ok=[200])
    
    def get_directory_filenames(self, path):
        data = {'path':path}
        response = self.get(f"os/ls", data=data)
        return self.response_result(response, status_ok=[200])
    
    
    # Manage containers
    
    def get_containers_status(self, all_=False):
        if all_:
            response = self.get("container?all=true")
        else:
            response = self.get("container")
        return self.response_result(response, status_ok=[200,204])
    
    def get_container_info(self, name, all_=False):
        if all_:
            response = self.get(f"container/{name}?all=true")
        else:
            response = self.get(f"container/{name}")
        return self.response_result(response, status_ok=[200,204])
    
    def restart_container(self, name, start_if_gone=False):
        response = self.put(f"container/{name}/restart")
        if start_if_gone and response.status_code == 410:
            return self.start_container(name)
        else:
            return self.response_result(response, status_ok=[200,204])
    
    def start_container(self, name):
        response = self.put(f"container/{name}/start")
        return self.response_result(response, status_ok=[200,204])
    
    def stop_container(self, name, raise_if_gone=True):
        response = self.put(f"container/{name}/stop")
        if not raise_if_gone and response.status_code == 410:
            return None
        else:
            return self.response_result(response, status_ok=[200,204])
    
    def wait_container(self, name, raise_if_gone=True):
        response = self.put(f"container/{name}/wait")
        if not raise_if_gone and response.status_code == 410:
            return None
        else:
            return self.response_result(response, status_ok=[200,204])
    
    
    # Manage configuration
    
    def update_yaml_file(self, file_path, text, with_backup=True, backup_extension='.ha_bak'):
        data = {
            'file_path': file_path,
            'yaml_string': text,
            'with_backup': with_backup,
            'backup_extension': backup_extension
            }
        response = self.patch(f"config/yaml_file", data=data)
        return self.response_result(response, status_ok=[200,204])
    
    def restore_yaml_file(self, file_path, backup_extension='.ha_bak'):
        data = {
            'action': 'restore',
            'file_path': file_path,
            'backup_extension': backup_extension
            }
        response = self.put(f"config/yaml_file", data=data)
        return self.response_result(response, status_ok=[200,204])
    
    
    
