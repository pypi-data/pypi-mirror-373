
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

import os
import logging
from holado_report.report.execution_historic import ExecutionHistoric
from holado.common.context.session_context import SessionContext
from holado_core.common.tools.tools import Tools
import threading

logger = logging.getLogger(__name__)



class BaseReport():
    def __init__(self):
        self.__report_path = None
        self.__execution_historic = None
        self.__report_builders = []
        
        self.__children_reports_lock = threading.RLock()
        self.__children_reports_by_prefix = {}
        
    def initialize(self):
        """
        Implement this method to initialize report.
        """
        pass
        
    def initialize_reports(self):
        """
        Implement this method to configure and initialize execution historic and report builders.
        """
        pass
    
    @property
    def has_report_path(self):
        return self.__report_path is not None
    
    @property
    def report_path(self):
        return self.__report_path
    
    @report_path.setter
    def report_path(self, report_path):
        self.__report_path = report_path
    
    @property
    def execution_historic(self):
        return self.__execution_historic
    
    @property
    def report_builders(self):
        return self.__report_builders
    
    def children_reports(self, prefix):
        with self.__children_reports_lock:
            if prefix in self.__children_reports_by_prefix:
                return self.__children_reports_by_prefix[prefix]
            else:
                return None
        
    def get_path(self, *args):
        return os.path.join(self.__report_path, *args)
        
    def set_execution_historic(self):
        self.__execution_historic = ExecutionHistoric()
        
    def add_report_builder(self, report_builder):
        self.__report_builders.append(report_builder)
        
    def build_reports(self):
        for rb in self.__report_builders:
            rb.build()

    def add_child_report(self, report, report_prefix, report_name, report_details=None):
        with self.__children_reports_lock:
            if report_prefix not in self.__children_reports_by_prefix:
                self.__children_reports_by_prefix[report_prefix] = []
                
            # Define child report path
            if self.has_report_path:
                report_dir_name = f"{report_prefix}_{len(self.__children_reports_by_prefix[report_prefix])+1:03d}"
                report.report_path = self.get_path(f"{report_prefix}s".capitalize(), report_dir_name)
                SessionContext.instance().path_manager.makedirs(report.report_path, is_directory=True)
            
            # Add child report
            self.__children_reports_by_prefix[report_prefix].append((report_name, report))
            
            # Update text file describing children reports
            if self.has_report_path:
                with open(self.get_path(f"{report_prefix}s".capitalize(), f"{report_prefix}_names.txt"), "at") as f:
                    f.write(f"{report_dir_name}: {report_name}\n")
                    if report_details:
                        f.write(Tools.indent_string(len(report_dir_name)+2, report_details) + "\n")
            

    def before_all(self):
        if self.__execution_historic:
            self.__execution_historic.before_all()
        for rb in self.__report_builders:
            rb.before_all()
    
    def before_feature(self, feature_context, feature, feature_report=None):
        if self.__execution_historic:
            self.__execution_historic.before_feature(feature_context, feature, feature_report)
        for rb in self.__report_builders:
            rb.before_feature(feature_context, feature, feature_report)
    
    def before_scenario(self, scenario_context, scenario, scenario_report=None):
        if self.__execution_historic:
            self.__execution_historic.before_scenario(scenario_context, scenario, scenario_report)
        for rb in self.__report_builders:
            rb.before_scenario(scenario_context, scenario, scenario_report)
    
    def before_step(self, step_context, step, step_level):
        if self.__execution_historic:
            self.__execution_historic.before_step(step_context, step, step_level)
        for rb in self.__report_builders:
            rb.before_step(step_context, step, step_level)
    
    def after_step(self, step_context, step, step_level):
        if self.__execution_historic:
            self.__execution_historic.after_step(step_context, step, step_level)
        for rb in self.__report_builders:
            rb.after_step(step_context, step, step_level)
    
    def after_scenario(self, scenario, scenario_report=None):
        if self.__execution_historic:
            self.__execution_historic.after_scenario(scenario, scenario_report)
        for rb in self.__report_builders:
            rb.after_scenario(scenario, scenario_report)
    
    def after_feature(self, feature, feature_report=None):
        if self.__execution_historic:
            self.__execution_historic.after_feature(feature, feature_report)
        for rb in self.__report_builders:
            rb.after_feature(feature, feature_report)
    
    def after_all(self, build_reports=True):
        if self.__execution_historic:
            self.__execution_historic.after_all()
        for rb in self.__report_builders:
            rb.after_all()
        
        if build_reports:
            self.build_reports()
        
    def release_resources(self):
        if self.__execution_historic:
            self.__execution_historic = None


