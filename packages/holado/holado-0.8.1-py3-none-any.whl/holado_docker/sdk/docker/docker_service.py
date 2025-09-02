
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

from holado_docker.sdk.docker.docker_client import DockerClient
from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado_core.tools.abstracts.service import Service
from holado_system.system.command.command import CommandStates
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class DockerService(Service):
    @classmethod
    def is_available(cls):
        return DockerClient.is_available()
    
    def __init__(self, name):
        super().__init__(name) 
        self.__docker_client = None
        self.__docker_container = None
    
    @property
    def status(self):
        if self.__docker_container is not None and self.__docker_client.has_container(self.name):
            status = self.__docker_container.status
            if status in ["running", "paused", "restarting"]:
                return CommandStates.Running
            elif status == "exited":
                result = self.__docker_container.wait(timeout=10)
                error_code = result["StatusCode"]
                if error_code == 0:
                    return CommandStates.Success
                else:
                    return CommandStates.Error
            else:
                raise TechnicalException(f"Unmanaged docker status '{status}'")
        else:
            return None
    
    def run_as_docker(self, image, remove_existing=True, remove=True, auto_stop=True, **kwargs):
        """
        Run the service as a docker image.
        
        :param image: Image name
        :param remove_existing: If true (default) and docker already exists, remove docker before creating a new one 
        :param remove: If true (default), remove the docker at stop
        :param auto_stop: If true (default), automatically stop docker when docker instance is released
        """ 
        self.__docker_client = DockerClient()
        self.__docker_container = self.__docker_client.run_container(self.name, image, remove_existing=remove_existing, remove=remove, auto_stop=auto_stop, **kwargs)

    def stop(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Stopping service '{self.name}'")
        if self.__docker_container is not None:
            if self.__docker_client.has_container(self.name) and self.__docker_client.get_container(self.name).status == "running":
                self.__docker_client.stop_container(self.name)
        else:
            raise TechnicalException(f"Service '{self.name}' is not started")
