
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


class DockerViewerClient(RestClient):
    
    def __init__(self, name, url, headers=None):
        super().__init__(name, url, headers)
    
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
    
    
    
