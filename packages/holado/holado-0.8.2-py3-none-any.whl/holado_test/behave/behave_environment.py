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

import logging
import behave

from holado.common.context.session_context import SessionContext
from holado_core.common.tools.tools import Tools
import types
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_test.scenario.step_tools import StepTools
from holado_test.test_config import TestConfig
import time
from behave.model_core import Status
from holado.common.handlers.undefined import undefined_value


logger = logging.getLogger(__name__)


# Use regular expression in step definitions
behave.use_step_matcher(BehaveStepTools.DEFAULT_STEP_MATCHER)


def __has_scenario_context():
    return SessionContext.instance().has_scenario_context()

def __get_scope_manager():
    if __has_scenario_context():
        return SessionContext.instance().get_scenario_context().scope_manager
    else:
        return None


def before_all(context):
    try:
        SessionContext.instance().before_all(context)
    except:
        logger.exception("Hook error")
        raise

def after_all(context):
    try:
        SessionContext.instance().after_all()
    except:
        logger.exception("Hook error")
        raise
    
def before_feature(context, feature):
    try:
        SessionContext.instance().before_feature(feature)
    except:
        logger.exception(f"Hook error (feature: {feature})")
        raise

def after_feature(context, feature):
    try:
        SessionContext.instance().after_feature(feature)
    except:
        logger.exception(f"Hook error (feature: {feature})")
        raise

def before_scenario(context, scenario):
    try:
        SessionContext.instance().before_scenario(scenario)
    except:
        logger.exception(f"Hook error (scenario: {scenario})")
        raise

def after_scenario(context, scenario):
    try:
        SessionContext.instance().after_scenario(scenario)
    except:
        logger.exception(f"Hook error (scenario: {scenario})")
        raise

def before_step(context, step):
    try:
        scope_manager = __get_scope_manager()
        logger.info(f"Step [{__step_description(step)}] (level: {scope_manager.scope_level('steps') if scope_manager else '?'})")
        
        SessionContext.instance().before_step(step)
    except:
        # logger.exception(f"Hook error (step: {step})")
        logger.exception(f"Hook error (step: {step})", stack_info=True)
        raise
    
    context.step = step

def after_step(context, step):
    try:
        # Update step if needed
        if hasattr(context, "do_update_step_status"):
            # logger.warning(f"+++++++++++ Update step status to {context.do_update_step_status}")
            step.status = context.do_update_step_status
            del context.do_update_step_status
        
        # Session context
        SessionContext.instance().after_step(step)
        
        # Log step result
        step_descr = __step_description(step)
        try:
            var_step_descr = StepTools.evaluate_variable_name(step_descr, log_level=logging.NOTSET)
        except:
            var_step_descr = "[ERROR during evaluation]"
        try:
            interpreted_step_descr = StepTools.evaluate_string_parameter(step_descr, log_level=logging.NOTSET)
        except:
            interpreted_step_descr = "[ERROR during interpretation]"
        if step.status in [Status.failed, Status.error] or interpreted_step_descr != step_descr or var_step_descr != interpreted_step_descr:
            msg = "Step {}:\n    step:\n{}{}{}".format(
                step.status.name, Tools.indent_string(8, step_descr),
                "" if interpreted_step_descr == step_descr else "\n    interpreted step:\n{}".format(Tools.indent_string(8, interpreted_step_descr)),
                "" if var_step_descr == interpreted_step_descr else "\n    partially interpreted step:\n{}".format(Tools.indent_string(8, var_step_descr)) )
            
            if step.status in [Status.failed, Status.error]:
                msg += "\n    error:\n{}\n    step attributes:\n{}".format(
                    Tools.indent_string(8, __step_error(step)),
                    Tools.indent_string(8, __step_attributes(step)) )
                if step.hook_failed:
                    msg += "\n    Hook failed"
        elif '\n' in step_descr:
            msg = "Step {}:\n{}".format(step.status.name, Tools.indent_string(4, step_descr))
        else:
            msg = "Step {}: {}".format(step.status.name, step_descr)
        
        if step.status in [Status.failed, Status.error]:
            logger.error(msg)
            
            if TestConfig.wait_on_step_failure_s > 0:
                time.sleep(TestConfig.wait_on_step_failure_s)
        else:
            logger.debug(msg)
    except:
        logger.exception(f"Hook error (step: {step})")
        raise

def __step_description(step):
    return SessionContext.instance().report_manager.get_step_description(step)

def __step_error(step):
    return SessionContext.instance().report_manager.get_step_error(step)

def __step_attributes(step):
    res_list = []
    for attr_name in dir(step):
        if not attr_name.startswith("__") and type(getattr(step, attr_name)) not in [types.MethodType, types.MethodWrapperType]:
            res_list.append("{}: {}".format(attr_name, str(getattr(step, attr_name))))
    return "\n".join(res_list)
    
