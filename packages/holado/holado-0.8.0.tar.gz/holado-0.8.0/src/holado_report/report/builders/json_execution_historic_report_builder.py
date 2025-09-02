
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

import json
import logging
from holado_report.report.builders.report_builder import ReportBuilder
import weakref

logger = logging.getLogger(__name__)



class JsonExecutionHistoricReportBuilder(ReportBuilder):
    def __init__(self, execution_historic, filepath):
        self.__execution_historic_weakref = weakref.ref(execution_historic)
        self.__filepath = filepath

    @property
    def __execution_historic(self):
        return self.__execution_historic_weakref()
    
    def build(self):
        with open(self.__filepath, "wt") as feh:
            eh_json = self.__convert_execution_historic_to_json()
            json_str = json.dumps(eh_json, ensure_ascii=False, indent=4)
            feh.write(json_str)
        
    def __convert_execution_historic_to_json(self):
        return [self.__convert_execution_historic_feature_to_json(eh_feat) for eh_feat in self.__execution_historic]
    
    def __convert_execution_historic_feature_to_json(self, eh_feature):
        return {
            'feature': self.__convert_feature_to_json(eh_feature.feature, eh_feature.feature_context, eh_feature.feature_report),
            'scenarios': [self.__convert_execution_historic_scenario_to_json(eh_sce) for eh_sce in eh_feature.scenarios ]
            }
    
    def __convert_feature_to_json(self, feature, feature_context, feature_report):
        res = {
            'name': feature.name,
            'description': feature.description,
            'tags': [str(tag) for tag in feature.tags],
            'status': feature.status.name,
            'duration': feature.duration,
            'start_date': feature_context.start_datetime.isoformat()
            }
        if feature_context.end_datetime:
            res['end_date'] = feature_context.end_datetime.isoformat()
        res.update({
            'filename': feature.filename,
            'report': feature_report.report_path
            })
        return res
    
    def __convert_execution_historic_scenario_to_json(self, eh_scenario):
        return {
            'scenario': self.__convert_scenario_to_json(eh_scenario.scenario, eh_scenario.scenario_context, eh_scenario.scenario_report),
            'steps_by_scope': {scope_name:[self.__convert_execution_historic_step_to_json(eh_step) for eh_step in steps] for scope_name, steps in eh_scenario.steps_by_scope.items()},
            'status_validation': eh_scenario.status_validation,
            'step_failed': self.__convert_step_to_json(eh_scenario.step_failed) if eh_scenario.step_failed is not None else None,
            'step_failed_number': eh_scenario.step_failed_number
            }
        
    def __convert_scenario_to_json(self, scenario, scenario_context, scenario_report):
        res = {
            'name': scenario.name,
            'description': scenario.description,
            'tags': [str(tag) for tag in scenario.tags],
            'status': scenario.status.name,
            'duration': scenario.duration,
            'start_date': scenario_context.start_datetime.isoformat()
            }
        if scenario_context.end_datetime:
            res['end_date'] = scenario_context.end_datetime.isoformat()
        res.update({
            'filename': scenario.filename,
            'line': scenario.line,
            'report': scenario_report.report_path
            })
        return res
        
    def __convert_execution_historic_step_to_json(self, eh_step):
        if eh_step.step is not None:
            res = self.__convert_step_to_json(eh_step.step)
        else:
            res = {}
        if eh_step.step_context is not None:
            if eh_step.step_context.status is not None:
                res['status'] = eh_step.step_context.status
            res['start_date'] = eh_step.step_context.start_datetime.isoformat()
            if eh_step.step_context.end_datetime:
                res['end_date'] = eh_step.step_context.end_datetime.isoformat()
            
        res['description'] = eh_step.step_description
        if eh_step.sub_steps:
            res['sub_steps'] = [self.__convert_execution_historic_step_to_json(eh_sub_step) for eh_sub_step in eh_step.sub_steps ]
        return res
        
    def __convert_step_to_json(self, step):
        from holado_report.report.report_manager import ReportManager
        res = {
            'status': step.status.name,
            'duration': step.duration,
            }
        step_error = ReportManager.get_step_error(step)
        if step_error:
            res['error'] = step_error
        if isinstance(step.filename, str) and step.filename != "<string>":
            res['filename'] = step.filename
            res['line'] = step.line
        return res
        
    
    
