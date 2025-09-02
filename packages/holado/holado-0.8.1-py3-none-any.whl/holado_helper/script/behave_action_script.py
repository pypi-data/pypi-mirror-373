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
from holado_python.common.tools.datetime import DateTime
from holado_helper.script.action_script import ActionScript, ActionScriptActor, ActionScriptFile, ActionRegistry
from holado_helper.script.action import BehaveActionInfo
from holado_core.common.actors.actions import Action
import copy

logger = logging.getLogger(__name__)


class BehaveActionScriptFile(ActionScriptFile):
    def __init__(self, file_ext):
        super().__init__(file_ext)


class BehaveActionRegistry(ActionRegistry):
    def __init__(self, name):
        super().__init__(name)
    
    def register_action(self, action, parameters_default_values=None, parameters_replacements=None, behave_tags=None, **kwargs):
        action_kwargs = {}
        if behave_tags is not None:
            action_kwargs['behave_tags'] = behave_tags
        action_kwargs.update(kwargs)
        super().register_action(action, parameters_default_values=parameters_default_values, parameters_replacements=parameters_replacements, **action_kwargs)
    
    def get_action_behave_tags(self, action, action_parameters=None):
        return self.get_action_kwargs(action).get('behave_tags', None)


class BehaveActionScriptActor(ActionScriptActor):
    def __init__(self, module_name, action_registry=None):
        super().__init__(module_name, action_registry)
    
    def act_process_action(self, action_info, action_script):
        def process_action():
            from holado.common.context.session_context import SessionContext
            from holado_helper.script.action import BehaveActionRunner
            
            var_manager = SessionContext.instance().multitask_manager.get_thread_context().get_variable_manager()
            behave_runner = BehaveActionRunner(action_info, var_manager)
            res_main = behave_runner.run()
            
            res = copy.deepcopy(action_info)
            if res.params is None:
                res.params = {}
            res.params['STATUS'] = 'SUCCESS' if res_main else 'ERROR'
            
            return res
        return Action(action_info.action, process_action)


class BehaveActionScript(ActionScript):
    def __init__(self, work_dir_path=None, with_input=True, with_output=True, with_template=True, with_action_parameter=True, 
                 actor=None, action_registry=None, script_file=None):
        if actor is None:
            actor = BehaveActionScriptActor("default_behave", action_registry)
        super().__init__(work_dir_path=work_dir_path, with_input=with_input, with_output=with_output, with_template=with_template, 
                         with_action_parameter=with_action_parameter, actor=actor, action_registry=action_registry, script_file=script_file)
    
    def build_action_tags(self, action, action_args=None):
        return list(self.action_registry.get_action_behave_tags(action))
    
    def _build_behave_args(self, tags=None):
        res = f'--no-source --no-skipped --format null --no-summary --no-capture --no-capture-stderr --no-logcapture'
        if tags:
            for tag in tags:
                res += f' -t {tag}'
        return res
    
    def new_action_info_from_args(self):
        action = self.args.action
        static_params = self.action_registry.get_action_static_parameters_values(action)
        behave_args = self._build_behave_args(self.action_registry.get_action_behave_tags(action))
        return self.new_action_info(action, static_params=static_params, behave_args=behave_args)
    
    def new_action_info(self, action, uid=None, behave_args=None, params=None, static_params=None, index=0):
        return BehaveActionInfo(uid=uid, action=action, params=params, static_params=static_params, index=index, behave_args=behave_args)
    


