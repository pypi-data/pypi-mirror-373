
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
from holado_report.report.builders.json_execution_historic_report_builder import JsonExecutionHistoricReportBuilder
from holado_report.report.builders.detailed_scenario_failed_report_builder import DetailedScenarioFailedReportBuilder
from holado_report.report.report_manager import BaseReport
import weakref

logger = logging.getLogger(__name__)



class ScenarioReport(BaseReport):
    def __init__(self, feature_report, scenario_context, scenario):
        super().__init__()
        
        self.__feature_report_weakref = weakref.ref(feature_report)
        self.__scenario_context = scenario_context
        self.__scenario = scenario
        
    def initialize_reports(self):
        self.set_execution_historic()

        if self.has_report_path:
            fn = self.get_path("execution_historic.json")
            self.add_report_builder(JsonExecutionHistoricReportBuilder(self.execution_historic, fn))
            
            fn = self.get_path("report_detailed_scenario_failed.xml")
            self.add_report_builder(DetailedScenarioFailedReportBuilder(fn))
        
        # Initialize reports
        self.before_all()
        self.before_feature(self.feature_report.feature_context, self.feature_report.feature, self.feature_report)
        self.before_scenario(self.scenario_context, self.scenario, self)
        
    @property
    def feature_report(self):
        return self.__feature_report_weakref()
        
    @property
    def report_manager(self):
        return self.feature_report.report_manager
    
    @property
    def scenario(self):
        return self.__scenario
    
    @property
    def scenario_context(self):
        return self.__scenario_context
    
    
    
