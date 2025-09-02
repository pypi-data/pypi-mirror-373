
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
from holado_core.common.tools.converters.converter import Converter
import os
from holado_docker.tools.docker_controller.client.rest.docker_controller_client import DockerControllerClient
from holado_rest.api.rest.rest_manager import RestManager
from holado.common.handlers.undefined import undefined_argument

logger = logging.getLogger(__name__)


class DockerControllerManager(object):
    
    @classmethod
    def new_client(cls, use_localhost=undefined_argument, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = None
        if 'url' not in kwargs:
            if use_localhost is undefined_argument:
                env_use = os.getenv("HOLADO_USE_LOCALHOST", False)
                use_localhost = Converter.is_boolean(env_use) and Converter.to_boolean(env_use)
            
            host = "localhost" if use_localhost else os.getenv("HOLADO_DOCKER_CONTROLLER_NAME", "holado_docker_controller")
            port = os.getenv("HOLADO_DOCKER_CONTROLLER_PORT", 8000)
            kwargs['url'] = f"http://{host}:{port}"
        
        manager = RestManager(default_client_class=DockerControllerClient)
        res = manager.new_client(**kwargs)
        
        return res
        
        
        
        