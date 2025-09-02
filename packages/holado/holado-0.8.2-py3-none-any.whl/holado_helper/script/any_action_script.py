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
from holado_helper.script.action_script import ActionScript
from holado_core.common.exceptions.element_exception import ElementNotFoundException
from holado_helper.script.script import Script

logger = logging.getLogger(__name__)

class AnyActionScript(ActionScript):
    def __init__(self, work_dir_path=None, actor=None):
        super().__init__(work_dir_path=work_dir_path, actor=actor)
        
        self.__action_script_by_type = {}
    
    @Script.user_working_dir.setter  # @UndefinedVariable
    def user_working_dir(self, wd):
        Script.user_working_dir.fset(self, wd)  # @UndefinedVariable
        for action_type in self.__action_script_by_type.values():
            action_type.user_working_dir = wd
    
    def get_description(self, script_command, short_description, action):
        return """{short_description}
        
        Usage:
            1. Generate a template file for the desired action with parameter '--output-template' as in example 1.
                It is possible to specify the name of the output file with parameter '-o'.
            2. Modify the generated file to define actions parameters. 
            3. Process actions described in file with parameter '-i'.
            4. See result in output file. If parameter '-o' is not specified, the output filename is generated from parameter '-i'.
        
        In template files, a default value is set for each parameter. 
        For parameters with enum values, the default value is a combination of each possible enum values separated by a '|', but only one value is possible.
        
        
        In input and output files, a parameter 'STATUS' describes the status of execution of each action:
            - 'TODO' (or ''): the action is to process (in output file, it means that execution was stopped on an error on a previous action)
            - 'SUCCESS': the action was in success
            - 'ERROR': the action was in error
            - others: the action is not processed, you can specify your own status to skip this action
        In template files, this parameter is automatically initialized with status 'TODO'.
        Any output file can be used as input file, the actions that are in status 'ERROR' or 'TODO' will be processed again.
        
        Example 1: Output template for action '{action}' (case with CSV input file)
                
                {script_command} {action} --output-template -o {action}.csv
                
        Example 2: Process action '{action}' (case with CSV input file)
                
                {script_command} {action} -i {action}.csv
        """.format(short_description=short_description, script_command=script_command, action=action)
    
    def register_action_type(self, action_type_name, action_type):
        self.__action_script_by_type[action_type_name] = action_type
    
    def _get_action_type_for_action(self, action):
        for action_type in self.__action_script_by_type.values():
            if action_type.is_matching_action(action):
                return action_type
        raise ElementNotFoundException(f"Action '{action}' is not matching any registered action type (registered action types: {list(self.__action_script_by_type.keys())})")
    
    def _get_action_type_for_action_and_input_file(self, action, file_path):
        for action_type in self.__action_script_by_type.values():
            if action_type.with_input and action_type.is_matching_action_and_input_file_path(action, file_path):
                return action_type
        raise ElementNotFoundException(f"Action '{action}' with input file '{file_path}' is not matching any registered action type (registered action types: {list(self.__action_script_by_type.keys())})")
    
    def _get_action_type_for_action_and_output_file(self, action, file_path):
        for action_type in self.__action_script_by_type.values():
            if action_type.is_matching_action_and_output_file_path(action, file_path):
                return action_type
        raise ElementNotFoundException(f"Action '{action}' with output file '{file_path}' is not matching any registered action type (registered action types: {list(self.__action_script_by_type.keys())})")
    
    def _get_action_type_for_input_file(self, file_path):
        for action_type in self.__action_script_by_type.values():
            if action_type.is_matching_input_file_path(file_path):
                return action_type
        raise ElementNotFoundException(f"Input file '{file_path}' is not matching any registered action type (registered action types: {list(self.__action_script_by_type.keys())})")
    
    def _get_action_type_for_output_file(self, file_path):
        for action_type in self.__action_script_by_type.values():
            if action_type.is_matching_output_file_path(file_path):
                return action_type
        raise ElementNotFoundException(f"Output file '{file_path}' is not matching any registered action type (registered action types: {list(self.__action_script_by_type.keys())})")
    
    def possible_actions(self):
        res = set()
        for act_type in self.__action_script_by_type.values():
            res.update(act_type.possible_actions())
        return sorted(res)
    
    def run_script(self):
        # Note: At this step it is not possible to build real output path, thus action type is defined with action and filename given by user (if given)
        if self.with_action_parameter:
            if self.args.output_template and self.args.output_filename:
                action_type = self._get_action_type_for_action_and_output_file(self.args.action, self.args.output_filename)
            elif self.args.input_filename is not None:
                action_type = self._get_action_type_for_action_and_input_file(self.args.action, self.args.input_filename)
            else:
                action_type = self._get_action_type_for_action(self.args.action)
        elif self.args.output_template and self.args.output_filename:
            action_type = self._get_action_type_for_output_file(self.args.output_filename)
        elif self.args.input_filename is not None:
            action_type = self._get_action_type_for_input_file(self.args.input_filename)
        else:
            raise ElementNotFoundException(f"Unable to define a matching registered action type with script args {self.args} (registered action types: {list(self.__action_script_by_type.keys())})")
        
        action_type.run()


