
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
from holado_report.report.report_manager import BaseReport
from holado_core.common.exceptions.technical_exception import TechnicalException
import weakref
# from holado_core.scenario.scenario_duration_manager import ScenarioDurationManager

logger = logging.getLogger(__name__)



class FeatureReport(BaseReport):
    TScenarioReport = None
    
    def __init__(self, report_manager, feature_context, feature):
        super().__init__()
        
        self.__report_manager_weakref = weakref.ref(report_manager)
        self.__feature_context = feature_context
        self.__feature = feature
        
        # Auto configuration
        self.configure()
        
    def configure(self):
        from holado_report.report.reports.scenario_report import ScenarioReport
        FeatureReport.TScenarioReport = ScenarioReport
        
    def initialize_reports(self):
    #     self.__execution_historic = ExecutionHistoric()
    #
    #     fn = self.get_path("execution_historic.json")
    #     self.__report_builders.append(JsonExecutionHistoricReportBuilder(self.__execution_historic, fn))
    #
    #     fn = self.get_path("report_summary_scenario_failed.txt")
    #     self.__report_builders.append(SummaryDetailedScenarioFailedReportBuilder(fn))
    #
    #     fn = self.get_path("report_short_scenario_failed.txt")
    #     self.__report_builders.append(ShortDetailedScenarioFailedReportBuilder(fn))
    #
    #     # fn = self.get_path("report_detailed_scenario_failed.txt")
    #     fn = self.get_path("report_detailed_scenario_failed.xml")
    #     self.__report_builders.append(DetailedScenarioFailedReportBuilder(fn))
    #
    #     fn = self.get_path("report_summary.txt")
    #     self.__report_builders.append(SummaryReportBuilder(self.__execution_historic, fn))
        
        # Initialize reports
        self.before_all()
        self.before_feature(self.feature_context, self.feature, self)
    
    @property
    def feature(self):
        return self.__feature
    
    @property
    def feature_context(self):
        return self.__feature_context
    
    @property
    def report_manager(self):
        return self.__report_manager_weakref()
    
    @property
    def scenario_reports(self):
        return self.children_reports("scenario")
    
    @property
    def current_scenario_report(self):
        if self.scenario_reports:
            return self.scenario_reports[-1][1]
        else:
            return None
    
    def new_scenario_report(self, scenario_context, scenario):
        res = FeatureReport.TScenarioReport(self, scenario_context, scenario)
        self.add_child_report(res, "scenario", scenario.name, f"{scenario.filename} - l.{scenario.line}")
        res.initialize_reports()
        return res
        
    def before_scenario(self, scenario_context, scenario, scenario_report=None):
        super().before_scenario(scenario_context, scenario, scenario_report)
    
    def after_scenario(self, scenario, scenario_report=None):
        if self.current_scenario_report.scenario != scenario:
            raise TechnicalException(f"Processing after scenario '{scenario.name}' whereas current scenario is '{self.current_scenario_report.scenario.name}'")
        if self.current_scenario_report is not scenario_report:
            raise TechnicalException(f"Processing after scenario report '{scenario_report}' whereas current scenario report is '{self.current_scenario_report}'")
        self.current_scenario_report.build_reports()

        super().after_scenario(scenario, scenario_report)
    
    
    
