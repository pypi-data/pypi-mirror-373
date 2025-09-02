
import logging
import os
from holado_core.common.tools.path_manager import PathManager

logger = logging.getLogger(__name__)


class TSPathManager(PathManager):

    def __init__(self):
        super().__init__()
        
    def initialize(self):
        pass
    
    def __get_root_path(self):
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, "..", "..", "..")
        
    def get_reports_path(self, name=None):
        if os.getenv('TESTING_SOLUTION_REPORTS_PATH') is not None:
            reports_root = os.getenv('TESTING_SOLUTION_REPORTS_PATH')
        elif os.getenv('TEST_OUTPUT_BASEDIR') is not None:
            reports_root = os.path.join(os.getenv('TEST_OUTPUT_BASEDIR'), "reports")
        else:
            reports_root = super().get_reports_path()

        if name is not None:
            return os.path.join(reports_root, name)
        else:
            return reports_root

    def get_static_files_path(self, name=None):
        root_path = self.__get_root_path()
        res = os.path.normpath(os.path.join(root_path, "resources", "static_files"))
        if name is not None:
            res = os.path.join(res, name)
        return res
    
