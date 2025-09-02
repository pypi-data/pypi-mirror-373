
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
from behave import given, when, then, step, Given, When, Then, Step  # @UnusedImport @UnresolvedImport
import behave
import re
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado.common.context.session_context import SessionContext
from behave.model_core import Status
from behave.model_describe import escape_cell
from behave.textutil import indent
from holado_core.common.exceptions.holado_exception import HAException
from holado_test.scenario.step_tools import SRE  # @UnusedImport
from holado_multitask.multitasking.multitask_manager import MultitaskManager
from holado_python.standard_library.typing import Typing

# limit import *
# pylint: disable=undefined-all-variable
__all__ = [
    "Given", "When", "Then", "Step",# "For",
    "format_step_with_context", "execute_steps", "SRE"
]

# Import and expose step parameter types
# from BehaveStepTools import SRE
# var_names = BehaveStepTools.import_types(sys.modules[__name__])
# if len(var_names) == 0:
#     raise TechnicalException(f"Module '{__name__}' is imported before registration of step parameter types")
# __all__.extend(var_names)


logger = logging.getLogger(__name__)



def __get_report_manager():
    return SessionContext.instance().report_manager

def __has_scenario_context():
    return SessionContext.instance().has_scenario_context()

def __has_step_context():
    return SessionContext.instance().has_step_context()

def __get_step_context():
    return SessionContext.instance().get_step_context()

def __get_block_manager():
    if __has_scenario_context():
        return SessionContext.instance().get_scenario_context().block_manager
    else:
        return None

def __get_scope_manager():
    if __has_scenario_context():
        return SessionContext.instance().get_scenario_context().scope_manager
    else:
        return None




def format_step(step, with_keyword=True, with_table=True, with_text=True):
    from behave.model_describe import ModelDescriptor
    
    step_str = step.name.strip()
    
    if with_keyword:
        res = u"{keyword} {step_str}".format(keyword=step.keyword, step_str=step_str)
    else:
        res = step_str
        
    if with_table and hasattr(step, "table") and step.table is not None:
        rendered_table = render_step_table(step.table, "    ")
        res = u"{res}\n{table}".format(res=res, table=rendered_table)
    elif with_text and hasattr(step, "text") and step.text is not None:
        rendered_text = ModelDescriptor.describe_docstring(step.text, "")
        # rendered_text = Tools.indent_string(4, rendered_text)
        res = u"{res}\n{text}".format(res=res, text=rendered_text)
        
    return res

def format_step_with_context(context, step_str, with_keyword=True, with_table=True, with_text=True):
    from behave.model_describe import ModelDescriptor
    
    step_str = step_str.strip()
    
    if with_keyword:
        res = u"{keyword} {step_str}".format(keyword=context.step.keyword, step_str=step_str)
    else:
        res = step_str
        
    if with_table and hasattr(context, "table") and context.table is not None:
        rendered_table = render_step_table(context.table, "    ")
        res = u"{res}\n{table}".format(res=res, table=rendered_table)
    elif with_text and hasattr(context, "text") and context.text is not None:
        rendered_text = ModelDescriptor.describe_docstring(context.text, "    ")
        res = u"{res}\n{text}".format(res=res, text=rendered_text)
        
    return res

def __step_description(context):
    return __get_report_manager().get_step_description(context.step)


def execute_steps(steps_text):
    """
    Wrapper to Context.execute_steps method, that manages scope levels of sub-steps.
    
    WARNING: The method context.execute_steps is not thread safe. 
             If it is called a second time in another thread very closely, the steps behind the second call
             will be executed two times, one time in each thread.
    TODO EKL: Do tests to make this function thread safe.
    """
    # Manage sub-step level
    thread_id = MultitaskManager.get_thread_id()
    scope_manager = __get_scope_manager()
    if scope_manager:
        level_already_exists = scope_manager.has_scope_level("steps")
        origin_level = scope_manager.scope_level("steps")
        if level_already_exists:
            scope_manager.increase_scope_level("steps")
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Executing steps (level {scope_manager.scope_level('steps')} ; thread: {thread_id}):\n{steps_text}")
    else:
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Executing steps (thread: {thread_id}):\n{steps_text}")
        
    try:
        SessionContext.instance().behave_manager.get_context().execute_steps(steps_text)
    finally:
        if scope_manager:
            scope_manager.reset_scope_level("steps", origin_level)

def render_step_table(table, indentation=None, do_escape_cell=False):
    """
    NOTE: It's a copy of behave method ModelDescriptor.describe_table, but not escaping cells by default.
          If parameter do_escape_cell is True, the behavior is identical to ModelDescriptor.describe_table.
    
    Provide a textual description of the table (as used w/ Gherkin).

    :param table:  Table to use (as :class:`behave.model.Table`)
    :param indentation:  Line prefix to use (as string, if any).
    :return: Textual table description (as unicode string).
    """
    # -- STEP: Determine output size of all cells.
    cell_lengths = []
    all_rows = [table.headings] + table.rows
    for row in all_rows:
        if do_escape_cell:
            lengths = [len(escape_cell(c)) for c in row]
        else:
            lengths = [len(c) for c in row]
        cell_lengths.append(lengths)

    # -- STEP: Determine max. output size for each column.
    max_lengths = []
    for col in range(0, len(cell_lengths[0])):
        max_lengths.append(max([c[col] for c in cell_lengths]))

    # -- STEP: Build textual table description.
    lines = []
    for r, row in enumerate(all_rows):
        line = u"|"
        for c, (cell, max_length) in enumerate(zip(row, max_lengths)):
            pad_size = max_length - cell_lengths[r][c]
            if do_escape_cell:
                line += u" %s%s |" % (escape_cell(cell), " " * pad_size)
            else:
                line += u" %s%s |" % (cell, " " * pad_size)
        line += u"\n"
        lines.append(line)

    if indentation:
        return indent(lines, indentation)
    # -- OTHERWISE:
    return u"".join(lines)


def Given(regexp, accept_scope_in_define=True, accept_condition=True):
    return _wrapped_step(behave.given, regexp, accept_scope_in_define=accept_scope_in_define, accept_condition=accept_condition)  #pylint: disable=no-member @UndefinedVariable

def Then(regexp):
    return _wrapped_step(behave.then, regexp)  #pylint: disable=no-member @UndefinedVariable

def When(regexp):
    return _wrapped_step(behave.when, regexp) #pylint: disable=no-member @UndefinedVariable

def Step(regexp):
    return _wrapped_step(behave.step, regexp) #pylint: disable=no-member @UndefinedVariable

# def For(regexp):
#     return _wrapped_step(behave.step, regexp, accept_expected_exception=False) #pylint: disable=no-member @UndefinedVariable


def _wrapped_step(step_function, regexp, accept_expected_exception=True, accept_condition=True, accept_scope_in_define=True):
    # Replace SRE types by associated regex
    try:
        regexp = regexp.format(**SRE.all_as_dict())
    except IndexError:
        # This error occurs when regexp has no {} section to format
        pass
    except KeyError:
        # This error can occur when format is already done in file defining step
        pass
    
    def wrapper(func):
        res_func = func
        if accept_expected_exception:
            res_func = _accept_expected_exception(res_func)
        if accept_condition:
            res_func = _accept_condition(res_func)
        if accept_scope_in_define:
            res_func = _accept_scope_in_define(res_func)
        return step_function(regexp)(res_func)
    return wrapper

def _accept_condition(func):
    """
    If a condition is ongoing, and current condition is not valid, bypass the step execution.
    """
    def wrapper(context, *args, **kwargs):
        # logger.debug(f"++++++++++ Wrapper begin ; func={Typing.get_object_class_fullname(func)} ; context={context.__dict__} ; args={args} ; kwargs={kwargs}")
        if __get_scope_manager().is_in_condition() and not __get_scope_manager().is_in_valid_condition():
            step_context = __get_scope_manager().get_step_context()
            step_context.status = "skipped"
        else:
            func(context, *args, **kwargs)
        
    return wrapper

def _accept_scope_in_define(func):
    """
    If a block is under definition, bypass step execution.
    Note: in before_step, the step was added in scope under define.
    """
    def wrapper(context, *args, **kwargs):
        # logger.debug(f"++++++++++ Wrapper begin ; func={Typing.get_object_class_fullname(func)} ; context={context.__dict__} ; args={args} ; kwargs={kwargs}")
        if __get_block_manager().is_in_define:
            # Bypass step execution: in before_step, the step was added in scope under define
            pass
        else:
            func(context, *args, **kwargs)
        
    return wrapper



###################################################################################################
##  Manage expected exception

def _accept_expected_exception(func):
    """
    If an error is expected, check if an error really occurs and if it matches expected error.
    Otherwise raise it again.
    """
    def wrapper(context, *args, **kwargs):
        # logger.debug(f"++++++++++ Wrapper begin ; context={context.__dict__} ; args={args} ; kwargs={kwargs}")
        try:
            func(context, *args, **kwargs)
        except Exception as exc:  #pylint: disable=W0703
            __process_step_exception(context, exc)
        
        __process_expected_exception_at_end_of_step(context)
        
    return wrapper

def __process_step_exception(context, exc):
    if not __has_scenario_context():
        raise exc
    
    # logger.debug(f"++++++++++ Wrapper: exception catched: {exc}")
    exc_verified = False
    # Verify exception if an exception was expected
    if not context.in_expected_exception_step \
            and __get_scope_manager().scope_level("steps") == context.expected_exception_step_level \
            and MultitaskManager.get_thread_id() == context.expected_exception_thread_id:
        # logger.debug(f"++++++++++ Wrapper: verify catched exception")
        exc_verified = True
        if isinstance(exc, HAException) or not hasattr(context, "sub_step_exception") or context.sub_step_exception is None:
            exc_to_verify = exc
        else:
            exc_to_verify = context.sub_step_exception

        # Reset expected exception, only try matching once.
        expected_exception_str, expected_exception_pattern = pop_expected_exception(context)
        
        # Process verification
        # logger.debug(f"++++++++++ Wrapper: process verification on exception: {exc_to_verify}")
        if expected_exception_str:
            exc_str = "{}({})".format(Typing.get_object_class_fullname(exc_to_verify), str(exc_to_verify))
            if expected_exception_str != exc_str:
                raise VerifyException(f"Obtained exception is not the expected one:\n  obtained: {exc_str}\n  expected: {expected_exception_str}")
        elif expected_exception_pattern:
            exc_str = "{}({})".format(Typing.get_object_class_fullname(exc_to_verify), str(exc_to_verify))
            regex = re.compile(expected_exception_pattern, re.DOTALL)
            
            if not regex.search(exc_str):
                raise VerifyException(f"Obtained exception is not matching the expected pattern:\n  obtained: {exc_str}\n  expected pattern: '{expected_exception_pattern}'")
        
        # Update status
        # logger.debug(f"++++++++++ Wrapper: update behave objects")
        context.do_update_step_status = Status.passed
    
    # Store as sub-step exception
    if __get_scope_manager().scope_level("steps") > 0 and not exc_verified:
        context.sub_step_exception = exc

    # If no other exception is raised, re-raise the same exception
    if not exc_verified:
        # logger.debug(f"++++++++++ Wrapper: raise catched exception")
        raise

def __process_expected_exception_at_end_of_step(context):
    if context.in_expected_exception_step:
        # logger.debug(f"++++++++++ Wrapper: Finish declaration of step setting expected exception")
        # Finish declaration of step setting expected exception
        leave_expected_exception_step(context)
    elif __get_scope_manager().scope_level("steps") == context.expected_exception_step_level \
            and MultitaskManager.get_thread_id() == context.expected_exception_thread_id:
        # logger.debug(f"++++++++++ Wrapper: Manage expected exception has not occurred")
        # Manage expected exception has not occurred
        if context.expected_exception_str:
            # Raise exception to make scenario failing, since step hasn't failed as expected
            msg = "Step passed but was expected fail on an exception:\n    step:\n{}\n    expected exception:\n{}".format(
                Tools.indent_string(8, __step_description(context)), 
                Tools.indent_string(8, context.expected_exception_str))
            if context.step.hook_failed:
                msg += "\n    Hook failed"
            logger.error(msg)
            raise FunctionalException(msg)
        elif context.expected_exception_pattern:
            # Raise exception to make scenario failing, since step hasn't failed as expected
            msg = "Step passed but was expected fail on an exception:\n    step:\n{}\n    expected exception matching: '{}'".format(
                Tools.indent_string(8, __step_description(context)), 
                Tools.indent_string(8, context.expected_exception_pattern))
            if context.step.hook_failed:
                msg += "\n    Hook failed"
            logger.error(msg)
            raise FunctionalException(msg)
        else:
            raise TechnicalException("No expected exception is configured")
            
def enter_expected_exception_step(context, expected_exception_str = None, expected_exception_pattern=None):
    context.expected_exception_str = expected_exception_str
    context.expected_exception_pattern = expected_exception_pattern
    context.in_expected_exception_step = True
    context.expected_exception_step_level = __get_scope_manager().scope_level("steps")
    context.expected_exception_thread_id = MultitaskManager.get_thread_id()

def leave_expected_exception_step(context):
    context.in_expected_exception_step = False

def pop_expected_exception(context):
    expected_exception_str = context.expected_exception_str
    expected_exception_pattern = context.expected_exception_pattern
    context.expected_exception_str = None
    context.expected_exception_pattern = None
    context.expected_exception_step_level = -1
    context.expected_exception_thread_id = None
    return expected_exception_str, expected_exception_pattern



###################################################################################################
##  Setup custom step decorators
###################################################################################################

### /!\ Not yet working, that's why next lines are commented
### Next lines enable the decorator, so that declaration of steps with this decorator is working.
### But behave has to be patched to parse .feature correctly and considering these decorators as steps:
###   - in behave/parser.py: in Parser.parse_step, manage the new step types ('for')
###   - in behave/i18n.py: add the new step types ('for')  

# def setup_step_decorators():
#     registry=behave.step_registry.registry
#     for step_type in ("for",):
#         registry.steps[step_type] = []
#         registry.make_decorator(step_type)
#
# setup_step_decorators()


