
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
from holado_report.report.builders.report_builder import ReportBuilder

logger = logging.getLogger(__name__)



class SummaryScenarioFailedReportBuilder(ReportBuilder):
    def __init__(self, filepath):
        self.__filepath = filepath
        self.__file_fail = None
        
    def build(self):
        '''
        The file is built after each scenario
        '''
        pass
        
    def after_scenario(self, scenario, scenario_report=None):
        from holado_report.report.report_manager import ReportManager
        status_validation, step_failed, step_number = ReportManager.get_current_scenario_status_information(scenario)
        
        if status_validation != "Passed":
            self.__file_fail_add_scenario(scenario, status_validation, step_failed, step_number)
            
    def after_all(self):
        # Manage file fail
        if self.__file_fail is not None:
            self.__file_fail.close()
            self.__file_fail = None
        
    def __file_fail_add_scenario(self, scenario, status_validation, step_failed, step_number):
        self.__open_file_if_needed()
        if step_failed is not None:
            self.__file_fail.write(f"scenario in {scenario.filename} at l.{scenario.line} - step {step_number} (l.{step_failed.line}) - {status_validation}\n")
        else:
            self.__file_fail.write(f"scenario in {scenario.filename} at l.{scenario.line} - step ? (missing step implementation ?) - {status_validation}\n")
        self.__file_fail.flush()
    
    def __open_file_if_needed(self):
        if self.__file_fail is None:
            self.__file_fail = open(self.__filepath, "wt")
    
