
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

from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado_core.common.tools.tools import Tools
import os
from holado_core.tools.abstracts.blocking_command_service import BlockingCommandService
from holado_system.system.command.command import CommandStates
from holado_core.common.handlers.wait import WaitFuncResultVerifying
from holado.common.handlers.object import DeleteableObject

logger = logging.getLogger(__name__)

try:
    import django  # @UnusedImport
    with_django = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"DjangoServer is not available. Initialization failed on error: {exc}")
    with_django = False


class DjangoServer(DeleteableObject):
    """
    Django server
    """
    
    @classmethod
    def is_available(cls):
        return with_django
    
    def __init__(self, name, django_project_path, port=8000, runserver_args=None):
        super().__init__(name)
        
        self.__django_project_path = django_project_path
        self.__runserver_port = port
        self.__runserver_args = runserver_args
        self.__project_command = None
        
        if not os.path.exists(django_project_path):
            raise TechnicalException(f"Django project doesn't exist (project path: '{django_project_path}')")
    
    def _delete_object(self):
        if self.__project_command is not None and self.__project_command.status == CommandStates.Running:
            self.stop()

    @property
    def django_project_path(self):
        return self.__django_project_path

    @property
    def runserver_port(self):
        return self.__runserver_port

    @property
    def runserver_args(self):
        return self.__runserver_args
    
    def start(self):
        self.__start_server_by_command()
    
    def __start_server_by_command(self):
        self.__project_command = self._new_project_command()
        self.__project_command.start()
        self._wait_until_server_is_reachable()
    
    def _new_project_command(self):
        manage_path = os.path.join(self.django_project_path, "manage.py")
        cmd = f"python {manage_path} runserver {self.runserver_port}"
        if self.runserver_args:
            cmd += f" {self.runserver_args}"
        
        res = BlockingCommandService(f"Command running Django server '{self.name}'", cmd)
        res.auto_stop = True
        
        return res
        
    def _wait_until_server_is_reachable(self):
        import requests
        url = f"http://127.0.0.1:{self.runserver_port}"
        redo = WaitFuncResultVerifying("server is reachable", 
                                       lambda: requests.get(url), 
                                       lambda result: result and result.status_code == 200 )
        redo.ignoring(Exception)
        redo.polling_every(0.01)
        redo.execute()
        
    def stop(self):
        if self.__project_command is None or self.__project_command.status != CommandStates.Running:
            raise TechnicalException(f"Django server of project '{self.name}' is not running (status: {self.__project_command.status if self.__project_command else 'Unkown'})")
        self.__project_command.stop()
    
    def join(self, timeout=None):
        self.__project_command.join(timeout)
    




