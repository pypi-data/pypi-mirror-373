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
import csv
from holado_helper.script.behave_action_script import BehaveActionScript, BehaveActionScriptFile
from holado_helper.script.job import Job
from holado.common.context.session_context import SessionContext

logger = logging.getLogger(__name__)


class CSVActionScriptFile(BehaveActionScriptFile):
    def __init__(self):
        super().__init__(file_ext='.csv')
        self.__text_interpreter = SessionContext.instance().text_interpreter

    def read_jobs(self, file_path, action_script):
        action = action_script.args.action
        
        list_action_params = self._read_action_params_from_csv_file(file_path)
        
        actions = []
        for index, ap in enumerate(list_action_params):
            behave_tags = action_script.action_registry.get_action_behave_tags(action)
            behave_args = action_script._build_behave_args(tags=behave_tags)
            static_params = action_script.action_registry.get_action_static_parameters_values(action)
            action_info = action_script.new_action_info(action, behave_args=behave_args, params=ap, static_params=static_params, index=index)
            actions.append(action_info)
        
        job = Job(actions=actions, in_parallel=False)
        
        return [job]
    
    def _read_action_params_from_csv_file(self, file_path):
        res = []
        
        with open(file_path, 'r') as fin:
            dr = csv.DictReader(fin, delimiter=';', quoting=csv.QUOTE_NONE)
            
            for row in dr:
                params_csv = dict(row)
                
                # Interpret parameter values to get expected values instead of strings
                params = {}
                for key, value in params_csv.items():
                    val_to_interpret = f"${{{value}}}"
                    val_interpreted = self.__text_interpreter.interpret(val_to_interpret)
                    if val_interpreted != val_to_interpret:
                        params[key] = val_interpreted
                    else:
                        params[key] = value
                
                res.append(params)
        
        return res

    def write_jobs(self, file_path, jobs, action_script):
        list_action_infos = []
        for job in jobs:
            list_action_infos.extend(job.actions)
        
        self._write_action_params_in_csv_file(file_path, list_action_infos)
    
    def _write_action_params_in_csv_file(self, file_path, list_action_infos):
        # Define fieldnames
        if len(list_action_infos) < 1:
            return
        fieldnames = list(list_action_infos[0].params.keys())
        
        with open(file_path, 'w') as fout:
            dw = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONE)
            dw.writeheader()
            for action_info in list_action_infos:
                dw.writerow(action_info.params)



class CSVActionScript(BehaveActionScript):
    def __init__(self, work_dir_path=None, actor=None, action_registry=None, script_file=None):
        if script_file is None:
            script_file = CSVActionScriptFile()
        super().__init__(work_dir_path=work_dir_path, actor=actor, action_registry=action_registry, script_file=script_file)
    
    def get_description(self, script_command, short_description, action):
        return """{short_description}
        
        Usage:
            1. Generate a template file for the desired action with parameter '--output-template' as in example 1.
                It is possible to specify the name of the output file with parameter '-o'.
            2. Copy the template line in order to have one line per action to do, and modify the template file with desired values. 
            3. Process actions described in a CSV file with parameter '-i'.
                If an error occurs at a line, execution is stopped.
            4. See result in output file. If parameter '-o' is not specified, the output filename is generated from parameter '-i'.
        
        In template files, a default value is set in each column. 
        For columns with enum values, the default value is a combination of each possible enum values separated by a '|', but only one value is possible.
        
        
        In input and output files, the first column 'STATUS' describes the status of execution of each line:
            - 'TODO' (or ''): the line is to process (in output file, it means that execution was stopped on an error with a previous line)
            - 'SUCCESS': the line was in success
            - 'ERROR': the line was in error
            - others: the line is not processed, you can specify your own status to skip this line
        In template files, this column is automatically initialized with status 'TODO'.
        Any output file can be used as input file, the lines that are in status 'ERROR' or 'TODO' will be processed again.
        
        Example 1: Output CSV template for action '{action}'
                
                {script_command} {action} --output-template -o {action}.csv
                
        Example 2: Process action '{action}' with given input CSV
                
                {script_command} {action} -i {action}.csv
        """.format(short_description=short_description, script_command=script_command, action=action)
    
    def _new_argument_parser(self, description=None, additional_arguments=None, add_help=True):
        parser = super()._new_argument_parser(description=description, additional_arguments=additional_arguments, add_help=add_help)
        
        # Add mode serie/parallel
        parser.add_argument('-m', '--mode', choices=['serial', 'parallel'], dest='mode', default='serial', 
                     help='Define if CSV rows must be processed in serial mode or in parallel mode')
        
        return parser
    


