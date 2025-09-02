# -*- coding: utf-8 -*-

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

# This file is a helper to build scripts using HolAdo solution, with CSV files as input.
# Usually, it is copied and adapted for specific usage.


import logging
import json
from holado_helper.script.behave_action_script import BehaveActionScript, BehaveActionScriptFile
from holado_helper.script.job import Job

logger = logging.getLogger(__name__)


class JsonMultipleActionScriptFile(BehaveActionScriptFile):
    def __init__(self):
        super().__init__(file_ext='.json')

    def read_jobs(self, file_path, action_script):
        converter = self.get_job_json_converter(action_script)
        
        with open(file_path, "r") as fin:
            file_json = json.load(fin)
        
        res = []
        for job_json in file_json:
            job = converter.from_json_to(job_json, Job)
            res.append(job)
        
        return res
    
    def write_jobs(self, file_path, jobs, action_script):
        raise NotImplementedError()
    
    def get_job_json_converter(self, action_script):
        from holado_helper.script.job import JobJsonConverter
        return JobJsonConverter(action_script)


class JsonMultipleActionScript(BehaveActionScript):
    def __init__(self, work_dir_path=None, actor=None, action_registry=None, script_file=None):
        if script_file is None:
            script_file = JsonMultipleActionScriptFile()
        super().__init__(work_dir_path=work_dir_path, with_action_parameter=False, actor=actor, action_registry=action_registry, script_file=script_file)
    
    def get_description(self, script_command, short_description):
        return """{short_description}
        
        Usage:
            1. Generate a template file with parameter '--output-template' as in example 1.
                It is possible to specify the name of the output file with parameter '-o'.
            2. Copy and modify the template file with desired actions. 
            3. Process actions described in file with parameter '-i'.
            4. See result in output file, if parameter '-o' is specified.
        
        In template files, a default value is set for each possible field. 
        For fields with enum values, the default value is a combination of each possible enum value separated by a '|', but only one value is possible.
        
        
        In input and output files, the field 'STATUS' describes the status of execution of each action:
            - 'TODO' (or ''): the action is to process (in output file, it means that execution was stopped on an error with a previous action)
            - 'SUCCESS': the action was in success
            - 'ERROR': the action was in error
            - others: the action is not processed, you can specify your own status to skip this action
        In template files, this column is automatically initialized with status 'TODO'.
        Any output file can be used as input file, the lines that are in status 'ERROR' or 'TODO' will be processed again.
        
        Example 1: Output template
                
                {script_command} --output-template -o actions.json
                
        Example 2: Process actions with given input file
                
                {script_command} -i actions.json
                
        """.format(short_description=short_description, script_command=script_command)
    
    def build_template_jobs(self):
        actions = []
        for action in self.action_registry.get_action_names():
            params_default_values = self.action_registry.get_action_parameters_default_values(action)
            params = {pdv[0]:pdv[1] for pdv in params_default_values}
            # Note: for templates, add static parameters is not needed
            act_info = self.new_action_info(action, params=params)
            actions.append(act_info)
        
        job = Job(actions=actions, in_parallel=False)
        
        return [job]



