
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
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.technical_exception import TechnicalException
import json

logger = logging.getLogger(__name__)



class FailureReportBuilder(ReportBuilder):
    """Failure report builder
    Supported formats: 'txt', 'json', 'xml'
    """
    def __init__(self, filepath, file_format='xml'):
        if file_format not in ['txt', 'json', 'xml']:
            raise TechnicalException(f"Unmanaged format '{file_format}' (possible formats: 'txt', 'json')")
        
        self.__filepath = filepath
        self.__file_format = file_format
        self.__failures = {}
        
    def build(self):
        '''
        The file is built after each scenario
        '''
        pass
        
    def after_scenario(self, scenario, scenario_report=None):
        from holado_report.report.report_manager import ReportManager
        status_validation, step_failed, step_number = ReportManager.get_current_scenario_status_information(scenario)
        
        if status_validation != "Passed":
            step_error_message = ReportManager.get_step_error_message(step_failed).strip()
            if step_error_message not in self.__failures:
                self.__failures[step_error_message] = []
            
            if self.__file_format == 'txt':
                msg_list = []
                msg_list.append(f"scenario in {scenario.filename} at l.{scenario.line} - step {step_number} (l.{step_failed.line}) - {status_validation}")
                msg_list.append(f"    Feature/Scenario: {scenario.feature.name}  =>  {scenario.name}")
                msg_list.append(f"    Report: {scenario_report.report_path}")
                msg_list.append(f"    Tags: -t " + " -t ".join(scenario.feature.tags + scenario.tags))
                msg_scenario = "\n".join(msg_list)
                
                self.__failures[step_error_message].append(msg_scenario)
            elif self.__file_format in ['json', 'xml']:
                scenario_info = {
                    'title': f"{scenario.filename} - l.{scenario.line} - step {step_number} (l.{step_failed.line}) - {status_validation}",
                    'scenario': f"{scenario.feature.name}  =>  {scenario.name}",
                    'report': scenario_report.report_path,
                    'tags': "-t " + " -t ".join(scenario.feature.tags + scenario.tags),
                    }
                self.__failures[step_error_message].append(scenario_info)
            else:
                raise TechnicalException(f"Unmanaged format '{self.__file_format}' (possible formats: 'txt', 'json')")
            
            self.__update_file()
    
    def __update_file(self):
        with open(self.__filepath, "wt") as fout:
            if self.__file_format == 'txt':
                for failure, scenarios_messages in self.__failures.items():
                    fout.write(failure + "\n")
                    fout.write("\n")
                    for msg in scenarios_messages:
                        fout.write(Tools.indent_string(4, msg) + "\n")
                        fout.write("\n")
            elif self.__file_format == 'json':
                json_str = json.dumps(self.__failures, ensure_ascii=False, indent=4)
                fout.write(json_str)
            elif self.__file_format == 'xml':
                self.__file_write_failures(fout, self.__failures, sort_by_nb_scenario=True)
            else:
                raise TechnicalException(f"Unmanaged format '{self.__file_format}' (possible formats: 'txt', 'json')")

    def __file_write_failures(self, fout, __failures, sort_by_nb_scenario=True):
        fout.write("<failures>\n")
        
        if sort_by_nb_scenario:
            for error_message, scenarios in sorted(self.__failures.items(), key=lambda item:-len(item[1])):
                self.__file_write_failure(fout, error_message, scenarios)
        else:
            for error_message, scenarios in self.__failures.items():
                self.__file_write_failure(fout, error_message, scenarios)
    
        fout.write("</failures>\n")
    
    def __file_write_failure(self, fout, error_message, scenarios):
        msg_list = []
        
        msg_list.append("    <failure>")
        
        if "\n" in error_message:
            msg_list.append(f"        <error_message>")
            msg_list.append(Tools.indent_string(12, error_message))
            msg_list.append(f"        </error_message>")
        else:
            msg_list.append(f"        <error_message>{error_message}</error_message>")
        
        msg_list.append(f"        <scenarios>")
        for scenario_info in scenarios:
            msg_list.append(f"            <scenario>")
            for key, value in scenario_info.items():
                msg_list.append(f"                <{key}>{value}</{key}>")
            msg_list.append(f"            </scenario>")
        msg_list.append(f"        </scenarios>")
        
        msg_list.append("    </failure>")
        
        msg = "\n".join(msg_list) + "\n"
        fout.write(msg)
    



