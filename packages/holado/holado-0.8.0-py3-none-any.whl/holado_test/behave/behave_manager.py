
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
import copy
import weakref
import behave
from holado.common.context.session_context import SessionContext
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_multitask.multitasking.multitask_manager import MultitaskManager

logger = logging.getLogger(__name__)


##### Implementation working but not working when launching behave in parallel in multiple threads

# class BehaveManager(object):
#     """
#     Manage Behave features.
#     """
#
#     def __init__(self):
#         self.__main_pid = None
#         self.__main_context_by_pid = {}
#         self.__context_by_pid_and_tid = {}
#
#
#     def clear(self):
#         # TODO EKL: clear only current (pid, tid), since behave can be launched in parallel threads
#         # pid = os.getpid()
#         # if pid in self.__main_context_by_pid:
#         #     del self.__main_context_by_pid[pid]
#         # if pid in self.__context_by_pid_and_tid:
#         #     del self.__context_by_pid_and_tid[pid]
#         pass
#
#     def has_main_pid(self):
#         return self.__main_pid is not None
#
#     def get_main_pid(self):
#         return self.__main_pid
#
#     def get_main_context(self, pid=None, raise_exception=True):
#         context_info = self.__get_main_context_info(pid, raise_exception)
#         if context_info is None:
#             return None
#         else:
#             return context_info[0]
#
#     def __get_main_context_info(self, pid=None, raise_exception=True):
#         if pid is None:
#             pid = os.getpid()
#         if pid not in self.__main_context_by_pid:
#             if raise_exception:
#                 raise TechnicalException("Main behave context is not defined")
#             else:
#                 return None
#         return self.__main_context_by_pid[pid]
#
#     def set_main_context(self, context, runner=None, raise_if_already_exists=True):
#         if self.get_main_context(raise_exception=False) is not None:
#             if self.__is_main_context_with_indendant_runner(raise_exception=False):
#                 SessionContext.instance().after_scenario(SessionContext.instance().get_scenario_context().scenario)
#                 SessionContext.instance().after_feature(SessionContext.instance().get_feature_context().feature)
#             else:
#                 if raise_if_already_exists:
#                     raise TechnicalException(f"Main behave context is already set: [{self.get_main_context(raise_exception=False)}]")
#                 else:
#                     logger.warning(f"Resetting main behave context: [{self.get_main_context(raise_exception=False)}] -> [{context}]")
#
#         pid = os.getpid()
#         thread_id = MultitaskManager.get_thread_id()
#
#         if self.__main_pid is None:
#             self.__main_pid = pid
#             # logger.print(f"+++++ set main pid: {self.__main_pid}")
#
#         self.__main_context_by_pid[pid] = (context, runner)
#         if pid not in self.__context_by_pid_and_tid:
#             self.__context_by_pid_and_tid[pid] = {}
#         self.__context_by_pid_and_tid[pid][thread_id] = (context, runner)
#         # logger.print(f"+++++ set main context: pid={self.__main_pid} ; tid={thread_id} ; {context=} ; {runner=}")
#
#     def __is_main_context_with_indendant_runner(self, raise_exception=True):
#         import holado_test.behave.independant_runner
#
#         context_info = self.__get_main_context_info(raise_exception=raise_exception)
#         if context_info is None:
#             return False
#
#         runner = context_info[1] if context_info[1] is not None else context_info[0]._runner
#         if not isinstance(runner, behave.runner.Runner):
#             raise TechnicalException(f"Wrong runner instance is verified")
#
#         return isinstance(runner, holado_test.behave.independant_runner.IndependantRunner)
#
#     def use_independant_runner(self, step_paths=None):
#         """
#         Use this method to run an independant behave runner,
#         so that a main context is set that can be used to execute steps
#         with method "execute_steps" without executing behave features.
#
#         WARNING: Current implementation has limitations.
#                  Current working directory must contain:
#                     - a folder "features" with at least one .feature file, even empty
#                     - a folder "steps" with a x_steps.py file importing all step files
#                     - a file "environment.py" containing "from XXX.behave_environment import *"
#         """
#         ### Current working implementation
#         from holado_test.behave.behave_function import BehaveFunction
#         from holado_multitask.multithreading.functionthreaded import FunctionThreaded
#         import time
#         behave_args = f'--no-source --no-skipped --format null --no-summary --no-capture --no-capture-stderr --no-logcapture -r holado_test.behave.independant_runner:IndependantRunner'
#         behave_func = BehaveFunction(behave_args)
#         thread = FunctionThreaded(behave_func.run, args=[], name=f"Thread with fake behave run")
#         thread.start()
#         time.sleep(1)
#
#         ### Other tried implementation:
#
#         # from holado_multitask.multithreading.functionthreaded import FunctionThreaded
#         # import time
#         #
#         # behave_args = f'--no-source --no-skipped --format null --no-summary --no-capture --no-capture-stderr --no-logcapture -r holado_test.behave.independant_runner:IndependantRunner'
#         # def run(behave_args):
#         #     from behave.configuration import Configuration
#         #     from behave.runner_plugin import RunnerPlugin
#         #     from behave.runner_util import reset_runtime
#         #
#         #     # Copy of useful code in behave.__main__.main
#         #     config = Configuration(behave_args)
#         #     if not config.format:
#         #         config.format = [config.default_format]
#         #     elif config.format and "format" in config.defaults:
#         #         # -- CASE: Formatter are specified in behave configuration file.
#         #         #    Check if formatter are provided on command-line, too.
#         #         if len(config.format) == len(config.defaults["format"]):
#         #             # -- NO FORMATTER on command-line: Add default formatter.
#         #             config.format.append(config.default_format)
#         #
#         #     reset_runtime()
#         #     runner = RunnerPlugin().make_runner(config, step_paths=step_paths)
#         #     runner.run()
#         # thread = FunctionThreaded(run, args=[behave_args], name=f"Thread with independant behave run")
#         # thread.start()
#         # time.sleep(1)
#
#         ### Other tried implementation:
#
#         # context = behave.runner.Context(runner)
#         # runner.context = context
#         #
#         # runner.load_hooks()
#         # runner.load_step_definitions()
#         # feature_locations = [filename for filename in runner.feature_locations()
#         #                      if not runner.config.exclude(filename)]
#         # features = runner.parse_features(feature_locations, language=self.config.lang)
#         # runner.features.extend(features)
#         # runner.feature = runner.features[0]
#         #
#         # self.set_main_context(context, runner=runner)
#
#
#     def get_context(self, raise_exception=True):
#         context_info = self.__get_context_info(raise_exception)
#         if context_info is None:
#             return None
#         else:
#             return context_info[0]
#
#     def __get_context_info(self, raise_exception=True):
#         pid = os.getpid()
#         if pid not in self.__context_by_pid_and_tid:
#             # Initialize main context of this pid as a sub context of main pid
#             # raise TechnicalException(f"Process {pid} doesn't exist in __context_by_pid_and_tid")
#             new_context, new_runner = self.__new_context_runner(pid_ref=self.__main_pid, raise_exception=raise_exception)
#             self.set_main_context(new_context, new_runner)
#
#         tid = MultitaskManager.get_thread_id()
#         if tid not in self.__context_by_pid_and_tid[pid]:
#             new_context, new_runner = self.__new_context_runner(raise_exception)
#             # new_context.thread_id = tid
#             # logger.debug(f"New context ({id(new_context)}) for thread {tid}")
#
#             self.__context_by_pid_and_tid[pid][tid] = (new_context, new_runner)
#
#         res = self.__context_by_pid_and_tid[pid][tid]
#         # self.__verify_context(res)
#         return res
#
#     def __new_context_runner(self, raise_exception, pid_ref=None):
#         ref_context = self.get_main_context(pid=pid_ref, raise_exception=raise_exception)
#
#         # Create a copy of the runner
#         res_run = copy.copy(ref_context._runner.__repr__.__self__)   # Context._runner is a weakref.proxy
#
#         # Create new context
#         res_con = behave.runner.Context(res_run)
#         res_con.feature = copy.copy(ref_context.feature)
#         res_con.feature.parser = copy.copy(ref_context.feature.parser)
#
#         # Update cross references
#         res_run.context = res_con
#         res_con._runner = weakref.proxy(res_run)    # Context._runner is a weakref.proxy
#
#         # Update context with attributes used by HolAdo
#         self.before_scenario(res_con)
#
#         return res_con, res_run
#
#     def before_scenario(self, context=None):
#         if context is None:
#             context = self.get_main_context()
#
#         # Initialize step information
#         context.sub_step_exception = None
#
#         # Manage expected exception
#         context.expected_exception_str = None
#         context.expected_exception_pattern = None
#         context.in_expected_exception_step = False
#         context.expected_exception_step_level = -1
#         context.expected_exception_thread_id = None
#
#     # def __log_registered_contexts(self, name=None):
#     #     msg_list = []
#     #     if name:
#     #         msg_list.append(f"[{name}] Registered contexts:")
#     #     else:
#     #         msg_list.append("Registered contexts:")
#     #     msg_list.append(f"    Main context: id={id(self.__main_context)} (thread: {self.__main_context.thread_id})")
#     #     for tid, con_run in self.__context_by_pid_and_tid.items():
#     #         context, _ = con_run
#     #         msg_list.append(f"    Context of thread {tid}: id={id(context)} (thread: {context.thread_id})")
#     #     logger.debug("\n".join(msg_list))
#
#     # def __verify_context(self, context):
#     #     thread_id = MultitaskManager.get_thread_id()
#     #     if context.thread_id != thread_id:
#     #         raise TechnicalException(f"Current thread and context thread are different (current thread: {thread_id} ; context thread: {context.thread_id} ; context: {id(context)})")
#






##### Implementation working when launching behave in parallel in multiple threads

class BehaveManager(object):
    """
    Manage Behave features.
    """
    
    def __init__(self):
        self.__context_by_pid_and_tid = {}
    
    def clear(self):
        pid = MultitaskManager.get_process_id()
        tid = MultitaskManager.get_thread_id()
        if pid in self.__context_by_pid_and_tid:
            if tid in self.__context_by_pid_and_tid[pid]:
                del self.__context_by_pid_and_tid[pid][tid]
                # TODO: delete related threads
            if len(self.__context_by_pid_and_tid[pid]) == 0:
                del self.__context_by_pid_and_tid[pid]
            # TODO: delete related processes
        
    def has_main_pid(self):
        return self.get_main_pid() is not None
    
    def get_main_pid(self):
        if len(self.__context_by_pid_and_tid) == 0:
            return None
        return next(iter(self.__context_by_pid_and_tid))
    
    def get_main_context(self, pid=None, raise_exception=True):
        context_info = self.__get_main_context_info(pid, raise_exception)
        return self.__get_context_from_info(context_info)
    
    def __get_context_from_info(self, context_info):
        return context_info[0] if context_info is not None else None
    
    def __get_runner_from_info(self, context_info):
        return context_info[1] if context_info is not None else None
    
    def __is_reference_from_info(self, context_info):
        return context_info[2] if context_info is not None else None
    
    def __get_main_context_info(self, pid=None, raise_exception=True):
        custom_pid = pid is not None and pid != MultitaskManager.get_process_id()
        if pid is None:
            pid = MultitaskManager.get_process_id()
        
        if pid not in self.__context_by_pid_and_tid or len(self.__context_by_pid_and_tid[pid]) == 0:
            if custom_pid:
                raise TechnicalException(f"Not managed to get main behave context on custom PID {pid}")
            else:
                ppid = MultitaskManager.get_parent_process_id()
            if ppid not in self.__context_by_pid_and_tid or len(self.__context_by_pid_and_tid[ppid]) == 0:
                if raise_exception:
                    raise TechnicalException(f"Main behave context is not defined either for current process PID {pid} and parent process PID {ppid} (existing context: {self.__context_by_pid_and_tid})")
                else:
                    return None
            else:
                # Use same context than parent process
                context, runner, _ = next(iter(self.__context_by_pid_and_tid[ppid].values()))
                tid = MultitaskManager.get_thread_id()
                self.__set_context(pid, tid, context, runner, is_reference=False)
        
        return next(iter(self.__context_by_pid_and_tid[pid].values()))
    
    def set_main_context(self, context, runner=None, raise_if_already_exists=True):
        context_info = self.__get_main_context_info(raise_exception=False)
        if context_info is not None and self.__get_context_from_info(context_info) is not None:
            if not self.__is_reference_from_info(context_info):
                self.__remove_context()
            elif self.__is_context_info_with_indendant_runner(context_info, raise_exception=False):
                if SessionContext.instance().has_scenario_context(is_reference=True):
                    SessionContext.instance().after_scenario(SessionContext.instance().get_scenario_context().scenario)
                if SessionContext.instance().has_feature_context(is_reference=True):
                    SessionContext.instance().after_feature(SessionContext.instance().get_feature_context().feature)
            else:
                if raise_if_already_exists:
                    raise TechnicalException(f"Main behave context is already set: [{self.get_main_context(raise_exception=False)}]")
                else:
                    logger.warning(f"Resetting main behave context: [{self.get_main_context(raise_exception=False)}] -> [{context}]")
        
        # Initialize context with HolAdo needs
        self.__init_context(context)
        
        pid = MultitaskManager.get_process_id()
        tid = MultitaskManager.get_thread_id()
        self.__set_context(pid, tid, context, runner, is_reference=True)
        # logger.print(f"+++++ set main context: pid={pid} ; tid={tid} ; {context=} ; {runner=}")
    
    def __is_context_info_with_indendant_runner(self, context_info, raise_exception=True):
        import holado_test.behave.independant_runner
        
        runner = self.__get_runner_from_info(context_info)
        if runner is None:
            runner = self.__get_context_from_info(context_info)._runner
            
        if not isinstance(runner, behave.runner.Runner):
            raise TechnicalException(f"Wrong runner instance is verified")
        
        return isinstance(runner, holado_test.behave.independant_runner.IndependantRunner)
    
    def use_independant_runner(self, step_paths=None):
        """
        Use this method to run an independant behave runner,
        so that a main context is set that can be used to execute steps
        with method "execute_steps" without executing behave features.
        
        WARNING: Current implementation has limitations.
                 Current working directory must contain:
                    - a folder "features" with at least one .feature file, even empty
                    - a folder "steps" with a x_steps.py file importing all step files
                    - a file "environment.py" containing "from XXX.behave_environment import *"
        """
        ### Current working implementation
        from holado_test.behave.behave_function import BehaveFunction
        from holado_multitask.multithreading.functionthreaded import FunctionThreaded
        from holado_core.common.handlers.wait import WaitFuncResult
        
        # Run behave with runner IndependantRunner in a thread
        behave_args = f'--no-source --no-skipped --format null --no-summary --no-capture --no-capture-stderr --no-logcapture -r holado_test.behave.independant_runner:IndependantRunner'
        behave_func = BehaveFunction(behave_args)
        thread = FunctionThreaded(behave_func.run, args=[], name=f"Thread with fake behave run")
        thread.start()
        thread_uid = MultitaskManager.get_thread_uid(thread)
        
        # Use the same thread context for this thread
        SessionContext.instance().multitask_manager.relate_thread_to(MultitaskManager.get_thread_uid(), thread_uid)
        
        # Wait until associated behave context exists
        def context_exists(pid, tid):
            return pid in self.__context_by_pid_and_tid and tid in self.__context_by_pid_and_tid[pid]
        wait_context = WaitFuncResult(f"wait independent behave context exists", 
                                      lambda: context_exists(MultitaskManager.get_process_id(), thread_uid))
        wait_context.redo_until(True)
        wait_context.execute()
        
        ### Other tried implementation:
        
        # from holado_multitask.multithreading.functionthreaded import FunctionThreaded
        # import time
        #
        # behave_args = f'--no-source --no-skipped --format null --no-summary --no-capture --no-capture-stderr --no-logcapture -r holado_test.behave.independant_runner:IndependantRunner'
        # def run(behave_args):
        #     from behave.configuration import Configuration
        #     from behave.runner_plugin import RunnerPlugin
        #     from behave.runner_util import reset_runtime
        #
        #     # Copy of useful code in behave.__main__.main
        #     config = Configuration(behave_args)
        #     if not config.format:
        #         config.format = [config.default_format]
        #     elif config.format and "format" in config.defaults:
        #         # -- CASE: Formatter are specified in behave configuration file.
        #         #    Check if formatter are provided on command-line, too.
        #         if len(config.format) == len(config.defaults["format"]):
        #             # -- NO FORMATTER on command-line: Add default formatter.
        #             config.format.append(config.default_format)
        #
        #     reset_runtime()
        #     runner = RunnerPlugin().make_runner(config, step_paths=step_paths)
        #     runner.run()
        # thread = FunctionThreaded(run, args=[behave_args], name=f"Thread with independant behave run")
        # thread.start()
        # time.sleep(1)
        
        ### Other tried implementation:
        
        # context = behave.runner.Context(runner)
        # runner.context = context
        #
        # runner.load_hooks()
        # runner.load_step_definitions()
        # feature_locations = [filename for filename in runner.feature_locations()
        #                      if not runner.config.exclude(filename)]
        # features = runner.parse_features(feature_locations, language=self.config.lang)
        # runner.features.extend(features)
        # runner.feature = runner.features[0]
        #
        # self.set_main_context(context, runner=runner)
        
        
    def get_context(self, raise_exception=True):
        context_info = self.__get_context_info(raise_exception)
        return self.__get_context_from_info(context_info)
        
    def __get_context_info(self, raise_exception=True):
        pid = MultitaskManager.get_process_id()
        if pid not in self.__context_by_pid_and_tid:
            # Initialize main context of this pid as a sub context of main pid
            # raise TechnicalException(f"Process {pid} doesn't exist in __context_by_pid_and_tid")
            # new_context, new_runner = self.__new_context_runner(pid_ref=self.__main_pid, raise_exception=raise_exception)
            # self.set_main_context(new_context, new_runner)
            self.__context_by_pid_and_tid[pid] = {}
        
        tid = MultitaskManager.get_thread_id()
        if tid not in self.__context_by_pid_and_tid[pid]:
            # Create a new context using as reference the first context of current process
            new_context, new_runner = self.__new_context_runner(raise_exception, pid_ref=pid)
            # new_context.thread_id = tid
            # logger.debug(f"New context ({id(new_context)}) for thread {tid}")
            self.__set_context(pid, tid, new_context, new_runner, is_reference=True)
            
        res = self.__context_by_pid_and_tid[pid][tid]
        # self.__verify_context(res)
        return res
    
    def __set_context(self, pid, tid, context, runner, is_reference=True):
        if pid not in self.__context_by_pid_and_tid:
            self.__context_by_pid_and_tid[pid] = {}
        self.__context_by_pid_and_tid[pid][tid] = (context, runner, is_reference)
        
    def __remove_context(self, pid=None, tid=None):
        if pid is None:
            pid = MultitaskManager.get_process_id()
        if tid is None:
            tid = MultitaskManager.get_thread_id()
            
        if pid in self.__context_by_pid_and_tid and tid in self.__context_by_pid_and_tid[pid]:
            del self.__context_by_pid_and_tid[pid][tid]
        else:
            raise TechnicalException(f"No context is set for thread ID {tid} and process ID {pid}")
        
    def __new_context_runner(self, raise_exception, pid_ref=None):
        ref_context = self.get_main_context(pid=pid_ref, raise_exception=raise_exception)
        
        # Create a copy of the runner
        res_run = copy.copy(ref_context._runner.__repr__.__self__)   # Context._runner is a weakref.proxy
        
        # Create new context
        res_con = behave.runner.Context(res_run)
        res_con.feature = copy.copy(ref_context.feature)
        res_con.feature.parser = copy.copy(ref_context.feature.parser)
        
        # Update cross references
        res_run.context = res_con
        res_con._runner = weakref.proxy(res_run)    # Context._runner is a weakref.proxy
        
        # Update context with attributes used by HolAdo
        self.before_scenario(res_con)
        
        # Initialize context with HolAdo needs
        self.__init_context(res_con)
        
        return res_con, res_run
    
    def before_scenario(self, context=None):
        if context is None:
            context = self.get_main_context()
            
        self.__reset_context(context)
        
    def __init_context(self, context):
        # Initialize step information
        if not hasattr(context, 'sub_step_exception'):
            context.sub_step_exception = None
        
        # Manage expected exception
        if not hasattr(context, 'expected_exception_str'):
            context.expected_exception_str = None
        if not hasattr(context, 'expected_exception_pattern'):
            context.expected_exception_pattern = None
        if not hasattr(context, 'in_expected_exception_step'):
            context.in_expected_exception_step = False
        if not hasattr(context, 'expected_exception_step_level'):
            context.expected_exception_step_level = -1
        if not hasattr(context, 'expected_exception_thread_id'):
            context.expected_exception_thread_id = None
        
    def __reset_context(self, context):
        # Initialize step information
        context.sub_step_exception = None
        
        # Manage expected exception
        context.expected_exception_str = None
        context.expected_exception_pattern = None
        context.in_expected_exception_step = False
        context.expected_exception_step_level = -1
        context.expected_exception_thread_id = None
        
    # def __log_registered_contexts(self, name=None):
    #     msg_list = []
    #     if name:
    #         msg_list.append(f"[{name}] Registered contexts:")
    #     else:
    #         msg_list.append("Registered contexts:")
    #     msg_list.append(f"    Main context: id={id(self.__main_context)} (thread: {self.__main_context.thread_id})")
    #     for tid, con_run in self.__context_by_pid_and_tid.items():
    #         context, _ = con_run
    #         msg_list.append(f"    Context of thread {tid}: id={id(context)} (thread: {context.thread_id})")
    #     logger.debug("\n".join(msg_list))

    # def __verify_context(self, context):
    #     thread_id = MultitaskManager.get_thread_id()
    #     if context.thread_id != thread_id:
    #         raise TechnicalException(f"Current thread and context thread are different (current thread: {thread_id} ; context thread: {context.thread_id} ; context: {id(context)})")
    


