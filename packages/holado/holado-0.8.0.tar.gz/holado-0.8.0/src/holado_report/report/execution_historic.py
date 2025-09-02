
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from typing import NamedTuple
from holado.common.context.session_context import SessionContext

logger = logging.getLogger(__name__)



class ExecutionHistoric():
    def __init__(self):
        self.__execution_historic = []
    
    def __iter__(self):
        return self.__execution_historic.__iter__()

    def __next__(self):
        return self.__execution_historic.__next__()

    def __has_scenario_context(self):
        return SessionContext.instance().has_scenario_context()
    
    @property
    def __multitask_manager(self):
        return SessionContext.instance().multitask_manager
    
    def before_all(self):
        pass
    
    def before_feature(self, feature_context, feature, feature_report=None):
        self.__execution_historic.append( self.__new_FeatureExecutionHistoric(feature_context, feature, feature_report) )
    
    def __new_FeatureExecutionHistoric(self, feature_context, feature, feature_report=None):
        res = NamedTuple("FeatureExecutionHistoric", feature_context=object, feature=object, feature_report=object, scenarios=list)
        res.feature_context = feature_context
        res.feature = feature
        res.feature_report = feature_report
        res.scenarios = []
        return res
    
    def before_scenario(self, scenario_context, scenario, scenario_report=None):
        seh = self.__new_ScenarioExecutionHistoric(scenario_context, scenario, scenario_report)
        self.__get_execution_historic_current_feature_scenarios().append(seh)
    
    def __new_ScenarioExecutionHistoric(self, scenario_context, scenario, scenario_report):
        res = NamedTuple("ScenarioExecutionHistoric", scenario_context=object, scenario=object, scenario_report=object, steps_by_scope=dict, status_validation=str, step_failed=object, step_failed_number=int)
        res.scenario_context = scenario_context
        res.scenario = scenario
        res.scenario_report = scenario_report
        res.steps_by_scope = {}
        res.status_validation = None
        res.step_failed = None
        res.step_failed_number = None
        return res
    
    def before_step(self, step_context, step, step_level):
        seh = self.__new_StepExecutionHistoric(step_context, step)
        self.__get_execution_historic_current_scenario_steps(step_level).append(seh)
    
    def __new_StepExecutionHistoric(self, step_context, step, step_description=None):
        if step_description is None and step is not None:
            from holado_report.report.report_manager import ReportManager
            step_description = ReportManager.get_step_description(step)
        
        res = NamedTuple("StepExecutionHistoric", step_context=object, step=object, step_description=str, sub_steps=list)
        res.step_context = step_context
        res.step = step
        res.step_description = step_description
        res.sub_steps = []
        return res
    
    def after_step(self, step_context, step, step_level):
        pass
    
    def after_scenario(self, scenario, scenario_report=None):
        from holado_report.report.report_manager import ReportManager
        status_validation, step_failed, step_number = ReportManager.get_current_scenario_status_information(scenario)
        
        # Update execution historic
        current_scenario = self.__get_execution_historic_current_scenario()
        current_scenario.status_validation = status_validation
        current_scenario.step_failed = step_failed
        current_scenario.step_failed_number = step_number
        
        # Prepare after scenario steps
        seh = self.__new_StepExecutionHistoric(step_context=None, step=None, step_description="After scenario steps")
        self.__get_execution_historic_current_scenario_steps(0).append(seh)
        
        
    def after_feature(self, feature, feature_report=None):
        pass
    
    def after_all(self):
        # logger.info(f"++++++++++ Execution historic size: {len(self.__execution_historic)}")
        pass
        
    def __get_execution_historic_current_feature_scenarios(self):
        if len(self.__execution_historic) > 0:
            return self.__execution_historic[-1].scenarios
        else:
            raise TechnicalException(f"No feature in execution historic")
        
    def __get_execution_historic_current_scenario(self):
        scenario_list = self.__get_execution_historic_current_feature_scenarios()
        if len(scenario_list) > 0:
            return scenario_list[-1]
        else:
            raise TechnicalException(f"No scenario in current feature in execution historic")
        
    def __get_execution_historic_current_scenario_steps(self, step_level):
        steps_by_scope = self.__get_execution_historic_current_scenario().steps_by_scope
        
        if self.__multitask_manager.is_main_thread:
            scope_name = "main"
        else:
            scope_name = self.__multitask_manager.get_thread_id()
        if scope_name not in steps_by_scope:
            steps_by_scope[scope_name] = []
        res = steps_by_scope[scope_name]
        
        for level in range(step_level):
            if len(res) == 0:
                logger.warning(f"Failed to get current scenario step list of level {step_level} (step list of level {level}: {res}) ; Add a fake step with description '[Missing step]'")
                res.append( self.__new_StepExecutionHistoric(None, None, "[Missing step]") )
            res = res[-1].sub_steps
        return res
    
    
