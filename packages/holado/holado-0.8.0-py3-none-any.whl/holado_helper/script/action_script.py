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
import copy
from holado_helper.script.input_output_script import InputOutputScript
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_python.standard_library.typing import Typing
from holado_helper.script.action import ActionInfo
from holado_core.common.actors.actor import Actor
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.common.tools.datetime import DateTime
from holado.common.handlers.object import Object
from holado.common.handlers.undefined import undefined_argument
from holado_helper.script.job import Job

logger = logging.getLogger(__name__)


class ActionScriptFile():
    def __init__(self, file_ext):
        super().__init__()
        self.__file_ext = file_ext
    
    @property
    def file_extension(self):
        return self.__file_ext
    
    def read_jobs(self, file_path, action_script):
        pass
    
    def write_jobs(self, file_path, jobs, action_script):
        pass
    


class ActionRegistry(Object):
    def __init__(self, name):
        super().__init__(name)
        
        self.__actions = {}
    
    def register_action(self, action, parameters_default_values=None, parameters_replacements=None, static_parameters_values=None, **kwargs):
        """ Register new action
        @param action: Action name
        @param parameters_default_values: define parameters default values (format: list of 2-uplets (parameter name, default value))
        @param parameters_replacements: define values automatic replacements (format: dictionary of {parameter name: List of 2-uplets (alias value, replacement value)})
        @param static_parameters_values: fixed parameter values known at action registration (format: dictonary of {parameter name: parameter value})
        @param kwargs: any other action arguments
        """
        action_kwargs = {
            'parameters_default_values': parameters_default_values, 
            'parameters_replacements': parameters_replacements,
            'static_parameters_values': static_parameters_values
            }
        action_kwargs.update(kwargs)
        self.__actions[action] = action_kwargs
        logger.info(f"[{self.name}] Registered action '{action}'")
    
    def get_action_names(self):
        return list(self.__actions.keys())
    
    def get_action_parameter_names(self, action):
        parameters_default_values = self.get_action_kwargs(action)['parameters_default_values']
        return [p[0] for p in parameters_default_values]
    
    def get_action_parameters_default_values(self, action):
        return self.get_action_kwargs(action)['parameters_default_values']
    
    def get_action_parameters_replacements(self, action):
        return self.get_action_kwargs(action)['parameters_replacements']
    
    def get_action_static_parameters_values(self, action):
        return self.get_action_kwargs(action)['static_parameters_values']
    
    def get_action_kwargs(self, action):
        if action in self.__actions:
            return self.__actions[action]
        else:
            raise TechnicalException(f"No registered action '{action}'")
    



class ActionScriptActor(Actor):
    def __init__(self, module_name, action_registry=None):
        super().__init__(module_name)
        self.__action_registry = action_registry
    
    @property
    def action_registry(self):
        return self.__action_registry
    
    @action_registry.setter
    def action_registry(self, action_registry):
        self.__action_registry = action_registry
    
    def act_process_action(self, action_info, action_script):
        raise NotImplementedError()


class ActionScript(InputOutputScript):
    def __init__(self, work_dir_path=None, with_input=True, with_output=True, with_template=True, with_action_parameter=True, 
                 actor=None, action_registry=None, script_file=None):
        super().__init__(work_dir_path=work_dir_path, with_input=with_input, with_output=with_output, with_template=with_template)
        
        self.__actor = actor
        self.__action_registry = action_registry if action_registry is not None else ActionRegistry("default")
        self.__script_file = script_file
        self.__with_action_parameter = with_action_parameter
        
        # Post process
        if self.__actor and self.__actor.action_registry is None:
            self.__actor.action_registry = self.__action_registry
    
    @property
    def actor(self):
        return self.__actor
    
    @property
    def action_registry(self):
        return self.__action_registry
    
    @property
    def script_file(self):
        return self.__script_file
    
    @property
    def with_action_parameter(self):
        return self.__with_action_parameter
    
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
        
        if self.__with_action_parameter:
            parser.add_argument('action', choices=self.possible_actions(), default=None, help='Action name')
        
        return parser
    
    def is_matching_file_path(self, file_path, raise_exception=False):
        file_ext = self.script_file.file_extension.lower()
        res = file_path.lower().endswith(file_ext)
        
        if not res and raise_exception:
            raise VerifyException(f"File path doesn't end by {file_ext} (case insensitive)")
        return res
    
    def is_matching_action(self, action, raise_exception=False):
        """Return if action is matching this action script
        """
        res = action in self.possible_actions()
        
        if not res and raise_exception:
            raise VerifyException(f"Action '{action}' doesn't match this script (possible actions: {self.possible_actions()})")
        return res
    
    def is_matching_action_and_input_file_path(self, action, file_path, raise_exception=False):
        """Return if action and associated input file are matching this action script
        """
        return self.is_matching_action(action, raise_exception) \
            and self.is_matching_input_file_path(file_path, raise_exception=raise_exception)
    
    def is_matching_action_and_output_file_path(self, action, file_path, raise_exception=False):
        """Return if action and associated output file are matching this action script
        """
        return self.is_matching_action(action, raise_exception) \
            and self.is_matching_output_file_path(file_path, raise_exception=raise_exception)
    
    def _build_output_template_path(self):
        if self.with_action_parameter:
            default_path = f"{self.args.action}_template{self.script_file.file_extension}"
        else:
            default_path = None
        
        try:
            return self._build_output_path(self.args.output_filename, default_path, self.user_working_dir)
        except Exception:
            raise FunctionalException(f"[{Typing.get_object_class_fullname(self)}] Please define output template file path")
    
    def possible_actions(self):
        raise NotImplementedError
    
    def build_template_jobs(self):
        if self.with_action_parameter:
            action = self.args.action
            params_default_values = self.action_registry.get_action_parameters_default_values(action)
            params = {pdv[0]:pdv[1] for pdv in params_default_values}
            # Note: for templates, add static parameters is not needed
            actions = [self.new_action_info(action, params=params)]
            job = Job(actions=actions, in_parallel=False)
            return [job]
        else:
            raise NotImplementedError()
    
    def process_jobs(self, list_jobs):
        res = []
        got_error = False
        
        for job in list_jobs:
            if got_error:
                res.append(job)
                continue
            
            res_job, got_error = self.process_job(job)
            res.append(res_job)
            
        return res, got_error
    
    def process_job(self, job):
        return self.process_actions(job.actions, job.in_parallel)
    
    def new_action_info_from_args(self):
        action = self.args.action
        static_params = self.action_registry.get_action_static_parameters_values(action)
        return self.new_action_info(action, static_params=static_params)
    
    def new_action_info(self, action, uid=None, params=None, static_params=None, index=0):
        processing_params = self.build_processing_action_params(action, action_args=self.args if self.with_action_parameter else None, action_params=params)
        if uid is None:
            dt_str = DateTime.datetime_2_str(DateTime.utcnow())
            uid = f"{dt_str} - {action} - {processing_params}"
        return ActionInfo(uid=uid, action=action, params=processing_params, static_params=static_params, index=index)
    
    def build_processing_action_params(self, action, action_args=None, action_params=None, **kwargs):  # @UnusedVariable
        if action_params is not None:
            return dict(action_params)
        else:
            return None
    
    def process_actions(self, list_action_info, in_parallel):
        if in_parallel:
            return self._process_actions_parallel(list_action_info)
        else:
            return self._process_actions_serial(list_action_info)
        
    def _process_actions_serial(self, list_action_info):
        logger.info(f"Processing {len(list_action_info)} actions in serial mode")
        res = []
        got_error = False
        
        for action_info in list_action_info:
            action_status = action_info.params['STATUS'] if 'STATUS' in action_info.params else 'TODO'
            res_action = copy.deepcopy(action_info)
            
            if not got_error and action_status in ['TODO', 'ERROR']:
                action_status = self.process_action(action_info)
                got_error |= (action_status == 'ERROR')
            elif got_error:
                logger.info(f"Skip action of index {action_info.index} since a previous action has failed")
            else:
                logger.info(f"Skip action of index {action_info.index} since its statud is '{action_status}'")
                
            res_action.params['STATUS'] = action_status
            res.append(res_action)
                
        return res, got_error
        
    def _process_actions_parallel(self, list_action_info):
        from holado_multitask.multiprocessing.function_process import FunctionProcess
        
        logger.info(f"Processing {len(list_action_info)} actions in parallel mode")
        res = []
        got_error = False
        processes = []
        
        # Start all processes
        for action_info in list_action_info:
            action_status = action_info.params['STATUS'] if 'STATUS' in action_info.params else 'TODO'
            res_action = copy.deepcopy(action_info)
            
            if action_status in ['TODO', 'ERROR']:
                proc = FunctionProcess(self.process_action, args=[action_info], name=f"Process action of index {action_info.index}")
                proc.start()
                processes.append((action_info, proc))
            
            res_action.params['STATUS'] = action_status
            res.append(res_action)
            
        # Join all processes
        for _, proc in processes:
            proc.join()
            
        # Update result
        for action_info, proc in processes:
            if proc.error is not None:
                logger.error(f"Error when processing action of index {action_info.index}: {proc.error}")
                action_status = 'ERROR'
            if proc.result is not None:
                action_status = proc.result
            
            res[action_info.index].params['STATUS'] = action_status
            got_error |= (action_status == 'ERROR')
            
        return res, got_error
        
    def _apply_replacements_on_action_params(self, action_params, params_replacements):
        from holado_core.common.tools.tools import Tools
        
        res = dict(action_params)
        
        for key in action_params:
            value = action_params[key]
            if key in params_replacements:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Checking replacable value '{key}'")
                for value_replaced, replacement in params_replacements[key]:
                    value_comp = value.lower() if isinstance(value, str) else value
                    value_replaced_comp = value_replaced.lower() if isinstance(value_replaced, str) else value_replaced
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"Evaluating value '{value_comp}' to '{value_replaced_comp}'. Value for '{key}' replaced by '{replacement}' if equals")
                    if value_comp == value_replaced_comp:
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"Value for '{key}' replaced by '{replacement}'")
                        value = replacement
                        break
                res[key] = value
        
        return res
        
    def process_action(self, action_info):
        if self.actor:
            return self.actor.act_process_action(action_info, self).execute()
        else:
            raise NotImplementedError()
    
    def read_jobs(self, input_path):
        res = self.script_file.read_jobs(input_path, self)
        
        # Verify action parameter names
        self._verify_jobs_actions_parameters(res)
        
        # Replace action parameters if needed
        self._replace_jobs_actions_parameters(res)
        
        return res
    
    def _verify_jobs_actions_parameters(self, jobs):
        for job in jobs:
            for action_info in job.actions:
                self._verify_action_parameters(action_info)
    
    def _verify_action_parameters(self, action_info):
        ai_param_names = set(action_info.params.keys())
        expected_param_names = set(self.action_registry.get_action_parameter_names(action_info.action))
        difference = ai_param_names.symmetric_difference(expected_param_names)
        # Note: parameter 'STATUS' is added in action result and is possibly present in input
        if len(difference) > 0 and difference != {'STATUS'}:
            raise FunctionalException(
                f"""Unexpected action parameter names for action '{action_info.action}':
                    obtained names: {ai_param_names}
                    expected names: {expected_param_names}""")

    def _replace_jobs_actions_parameters(self, jobs):
        for job in jobs:
            for action_info in job.actions:
                self._replace_action_parameters(action_info)
    
    def _replace_action_parameters(self, action_info):
        from holado_core.common.tools.tools import Tools
        
        # Process replacements defined in action registry
        params_replacements = self.action_registry.get_action_parameters_replacements(action_info.action)
        if params_replacements:
            for param_name in action_info.params:
                value = action_info.params[param_name]
                if param_name in params_replacements:
                    new_value = undefined_argument
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"Checking replacable value '{param_name}'")
                    for value_replaced, replacement in params_replacements[param_name]:
                        value_comp = value.lower() if isinstance(value, str) else value
                        value_replaced_comp = value_replaced.lower() if isinstance(value_replaced, str) else value_replaced
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.trace(f"Comparing value '{value_comp}' to '{value_replaced_comp}'. Value for parameter '{param_name}' replaced by '{replacement}' if equals")
                        if value_comp == value_replaced_comp:
                            new_value = replacement
                            break
                    if new_value is not undefined_argument:
                        if Tools.do_log(logger, logging.DEBUG):
                            logger.debug(f"For parameter '{param_name}', value '{value}' is replaced by '{new_value}'")
                        action_info.params[param_name] = new_value
    
    def write_jobs(self, output_path, result_jobs, got_error):
        output_path_base, _, output_ext = self._build_output_path_base(output_path)
        if got_error is not None:
            if got_error:
                output_base = f"{output_path_base}-FAIL"
            else:
                output_base = f"{output_path_base}-SUCCESS"
        else:
            output_base = output_path_base
        real_output_path = self._build_output_path_from_base(output_base, output_ext)
        
        self.script_file.write_jobs(real_output_path, result_jobs, self)
        
        return real_output_path
    
    def run_script(self):
        if self.with_template and self.args.output_template:
            output_path = self._build_output_template_path()
            template_jobs = self.build_template_jobs()
            real_output_path = self.write_jobs(output_path, template_jobs, got_error=None)
            logger.print(f"Template created in file '{real_output_path}'")
        elif self.with_input and self.args.input_filename:
            # Read file
            input_path = self._build_input_path(self.args.input_filename, self.user_working_dir)
            list_jobs = self.read_jobs(input_path)
            
            # Process jobs
            result_jobs, got_error = self.process_jobs(list_jobs)
            
            # Write file
            if self.with_output and self.args.output_filename is not None:
                output_path = self._build_output_path(self.args.output_filename, self.args.input_filename, self.user_working_dir)
                real_output_path = self.write_jobs(output_path, result_jobs, got_error)
                logger.print(f"Result outputed in file '{real_output_path}'")
        else:
            action_info = self.new_action_info_from_args()
            result_action = self.process_action(action_info)
            result_jobs=[{'actions': [result_action]}]
            
            # Write file
            if self.with_output and self.args.output_filename is not None:
                output_path = self._build_output_path(self.args.output_filename, None, self.user_working_dir)
                real_output_path = self.write_jobs(output_path, result_jobs)
                logger.print(f"Result outputed in file '{real_output_path}'")



