
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

from holado_core.common.tools.tools import Tools
import logging
from holado_report.report.builders.report_builder import ReportBuilder

logger = logging.getLogger(__name__)



class DetailedScenarioFailedReportBuilder(ReportBuilder):
    def __init__(self, filepath):
        self.__filepath = filepath.strip()
        self.__file_fail = None
        self.__is_format_xml = self.__filepath.lower().endswith(".xml")
        
    def build(self):
        '''
        The file is built after each scenario
        '''
        pass
        
    def after_scenario(self, scenario, scenario_report=None):
        from holado_report.report.report_manager import ReportManager
        status_validation, step_failed, step_number = ReportManager.get_current_scenario_status_information(scenario)
        
        if status_validation != "Passed":
            self.__file_fail_add_scenario(scenario, scenario_report, status_validation, step_failed, step_number)
            
    def after_all(self):
        # Manage file fail
        if self.__file_fail is not None:
            self.__file_fail.close()
            self.__file_fail = None
        
    def __file_fail_add_scenario(self, scenario, scenario_report, status_validation, step_failed, step_number):
        if self.__is_format_xml:
            self.__file_fail_add_scenario_xml(scenario, scenario_report, status_validation, step_failed, step_number)
        else:
            self.__file_fail_add_scenario_txt(scenario, scenario_report, status_validation, step_failed, step_number)
        
    def __file_fail_add_scenario_xml(self, scenario, scenario_report, status_validation, step_failed, step_number):
        from holado_report.report.report_manager import ReportManager
        
        self.__open_file_if_needed()
        
        msg_list = [f"<scenario>"]
        msg_list.append(f"    <file>{scenario.filename} - l.{scenario.line}</file>")
        msg_list.append(f"    <feature>{scenario.feature.name}</feature>")
        msg_list.append(f"    <scenario>{scenario.name}</scenario>")
        msg_list.append(f"    <report>{scenario_report.report_path}</report>")
        msg_list.append(f"    <tags>-t " + " -t ".join(scenario.feature.tags + scenario.tags) + "</tags>")
        msg_list.append(f"    <validation_status>{status_validation}</validation_status>")
        if step_failed is not None:
            msg_list.append(f"    <failure>")
            msg_list.append(f"        <step_number>{step_number}</step_number>")
            msg_list.append(f"        <step_line>{step_failed.line}</step_line>")
            step_descr = ReportManager.get_step_description(step_failed)
            if "\n" in step_descr:
                msg_list.append(f"        <step>")
                msg_list.append(Tools.indent_string(12, step_descr))
                msg_list.append(f"        </step>")
            else:
                msg_list.append(f"        <step>{step_descr}</step>")
            
            step_error_message = ReportManager.get_step_error_message(step_failed)
            if step_error_message:
                if "\n" in step_error_message:
                    msg_list.append(f"        <error_message>")
                    msg_list.append(Tools.indent_string(12, step_error_message))
                    msg_list.append(f"        </error_message>")
                else:
                    msg_list.append(f"        <error_message>{step_error_message}</error_message>")
            
            step_error = ReportManager.get_step_error(step_failed)
            if step_error and step_error != step_error_message:
                if "\n" in step_error:
                    msg_list.append(f"        <error>")
                    msg_list.append(Tools.indent_string(12, step_error))
                    msg_list.append(f"        </error>")
                else:
                    msg_list.append(f"        <error>{step_error}</error>")
            
            msg_list.append(f"    </failure>")
        else:
            msg_list.append(f"    <failure>No step failed, it has probably failed on a missing step implementation</failure>")
        msg_list.append(f"</scenario>")
        msg_list.append(f"")
            
        msg = "\n".join(msg_list)
        self.__file_fail.write(msg)
        self.__file_fail.flush()
        
    def __file_fail_add_scenario_txt(self, scenario, scenario_report, status_validation, step_failed, step_number):
        from holado_report.report.report_manager import ReportManager
        
        self.__open_file_if_needed()
        
        msg_list = [f"{scenario.filename} - l.{scenario.line}"]
        msg_list.append(f"    Feature: {scenario.feature.name}")
        msg_list.append(f"    Scenario: {scenario.name}")
        msg_list.append(f"    Report: {scenario_report.report_path}")
        msg_list.append(f"    Tags: -t " + " -t ".join(scenario.feature.tags + scenario.tags))
        msg_list.append(f"    Validation status: {status_validation}")
        if step_failed is not None:
            msg_list.append(f"    Failure:")
            msg_list.append(f"        Step number-line: {step_number} - l.{step_failed.line}")
            step_descr = ReportManager.get_step_description(step_failed)
            if "\n" in step_descr:
                msg_list.append(f"        Step:")
                msg_list.append(Tools.indent_string(12, step_descr))
            else:
                msg_list.append(f"        Step: {step_descr}")
                
            step_error = ReportManager.get_step_error(step_failed)
            if step_error:
                if "\n" in step_error:
                    msg_list.append(f"        Error:")
                    msg_list.append(Tools.indent_string(12, step_error))
                else:
                    msg_list.append(f"        Error: {step_error}")
        else:
            msg_list.append(f"    Failure: No step failed, it has probably failed on a missing step implementation")
        msg_list.append(f"")
        msg_list.append(f"")
            
        msg = "\n".join(msg_list)
        self.__file_fail.write(msg)
        self.__file_fail.flush()
    
    def __open_file_if_needed(self):
        if self.__file_fail is None:
            self.__file_fail = open(self.__filepath, "wt")
    
    
