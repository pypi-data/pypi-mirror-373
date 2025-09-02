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

from flask.views import MethodView
from holado.common.context.session_context import SessionContext

def _get_session_context():
    return SessionContext.instance()


class RestartView(MethodView):
    
    def put(self, name, body: dict):
        if not _get_session_context().docker_client.has_container(name):
            return f"Container '{name}' doesn't exist", 410
        
        res = _get_session_context().docker_client.restart_container(name, wait_running=False)
        return res

class StartView(MethodView):
    
    def put(self, name, body: dict):
        if not _get_session_context().docker_client.has_container(name, all_=True):
            return f"Container '{name}' doesn't exist", 410
        
        res = _get_session_context().docker_client.start_container(name, wait_running=False)
        return res

class StopView(MethodView):
    
    def put(self, name, body: dict):
        if not _get_session_context().docker_client.has_container(name):
            return f"Container '{name}' doesn't exist", 410
        
        res = _get_session_context().docker_client.stop_container(name)
        return res

class WaitView(MethodView):
    
    def put(self, name, body: dict):
        if not _get_session_context().docker_client.has_container(name):
            return f"Container '{name}' doesn't exist", 410
        
        res = _get_session_context().docker_client.get_container(name).wait()
        return res
    
