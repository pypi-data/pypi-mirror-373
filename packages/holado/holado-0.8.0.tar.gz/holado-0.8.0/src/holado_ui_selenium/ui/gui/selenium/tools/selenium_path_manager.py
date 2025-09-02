
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_system.system.global_system import GlobalSystem, OSTypes

logger = logging.getLogger(__name__)


class SeleniumPathManager(object):

    def __init__(self, path_manager):
        self.__internal_path_manager = path_manager

    def __get_selenium_dependencies_path(self):
        here = os.path.abspath(os.path.dirname(__file__))
        holado_path = os.path.abspath(os.path.join(here, "..", "..", "..", "..", "..", ".."))
        return os.path.join(holado_path, "dependencies", "selenium")

    @property
    def path_manager(self):
        return self.__internal_path_manager
    
    def get_chromedriver_path(self):
        """
        @return Absolute path to Chrome driver executable
        """
        driver_version = AppContext.getInstance().getProperties().getProperty("browser.chromedriver.version")
        return self.__get_driver_path("chromedriver", driver_version)

    def get_geckodriver_path(self):
        """
        @return Absolute path to Gecko driver executable
        """
        driver_version = AppContext.getInstance().getProperties().getProperty("browser.geckodriver.version")
        return self.__get_driver_path("geckodriver", driver_version)

    def __get_driver_path(self, driver_type_name, driver_version):
        """
        @return Absolute path to driver executable
        """
        if GlobalSystem.get_os_type() == OSTypes.Linux:
            res = os.path.join(self.__get_selenium_dependencies_path(), driver_type_name, driver_version, "linux64", driver_type_name)
        elif GlobalSystem.get_os_type() == OSTypes.MacOS:
            res = os.path.join(self.__get_selenium_dependencies_path(), driver_type_name, driver_version, "mac64", driver_type_name)
        elif GlobalSystem.get_os_type() == OSTypes.Windows:
            res = os.path.join(self.__get_selenium_dependencies_path(), driver_type_name, driver_version, "win32", driver_type_name)
        else:
            raise TechnicalException(f"Unmanaged system type '{GlobalSystem.get_os_type().name}'")
        
        # Check that file exists
        self.__internal_path_manager.check_file_exists(res, True)

        return res



