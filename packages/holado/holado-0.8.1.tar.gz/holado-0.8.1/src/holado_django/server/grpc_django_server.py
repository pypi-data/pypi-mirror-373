
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
from holado_core.tools.abstracts.blocking_command_service import BlockingCommandService
from holado_django.server.django_server import DjangoServer
from holado_core.common.handlers.wait import WaitFuncResultVerifying

logger = logging.getLogger(__name__)


class GrpcDjangoServer(DjangoServer):
    """
    gRPC Django server
    """
    
    def __init__(self, name, django_project_path, runserver_args=None):
        super().__init__(name, django_project_path, port=50051, runserver_args=runserver_args)
    
    def _new_project_command(self):
        manage_path = os.path.join(self.django_project_path, "manage.py")
        cmd = f"python {manage_path} grpcrunserver"
        if self.runserver_args:
            cmd += f" {self.runserver_args}"
        
        res = BlockingCommandService(f"Command running gRPC Django server '{self.name}'", cmd)
        res.auto_stop = True
        
        return res
        
    def _wait_until_server_is_reachable(self):
        import grpc_requests
        
        endpoint = f"localhost:{self.runserver_port}"
        def request_is_unimplemented():
            try:
                grpc_requests.Client.get_by_endpoint(endpoint)
            except Exception as exc:
                if "status = StatusCode.UNIMPLEMENTED" in str(exc):
                    return True
            return False
        redo = WaitFuncResultVerifying("server is reachable", request_is_unimplemented, lambda result: result )
        redo.polling_every(0.01)
        redo.execute()


