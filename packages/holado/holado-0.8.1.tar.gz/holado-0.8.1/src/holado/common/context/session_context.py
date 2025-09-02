
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

from builtins import super
from _datetime import datetime
import logging
import os.path
from holado.common.context.context import Context
from holado_core.common.tools.tools import Tools
import threading
from holado.common.handlers.enums import ObjectStates


logger = logging

def initialize_logger():
    global logger
    logger = logging.getLogger(__name__)


class SessionContext(Context):
    TSessionContext = None
    
    # Singleton management
    __instance = None
    __is_resetting_instance = False
    
    @staticmethod
    def instance() -> TSessionContext:
        # Note: If session context istance is under reset, consider it is already None
        if SessionContext.__is_resetting_instance:
            return None
        
        if SessionContext.__instance is None:
            SessionContext.__instance = SessionContext.TSessionContext()
            logger.debug(f"Created session context of type {SessionContext.TSessionContext}")
            # logging.log(45, f"Created session context of type {SessionContext.TSessionContext}")
            # import traceback
            # logging.log(45, "".join(traceback.format_list(traceback.extract_stack())))
        return SessionContext.__instance
    
    @staticmethod
    def has_instance() -> bool:
        if SessionContext.__is_resetting_instance:
            return False
        else:
            return SessionContext.__instance is not None
    
    @staticmethod
    def _reset_instance():
        if SessionContext.__instance is not None:
            logger.debug(f"Resetting session context")
            SessionContext.__is_resetting_instance = True
            SessionContext.__instance = None
            SessionContext.__is_resetting_instance = False
            logger.debug(f"Reset of session context")
    
    def __init__(self, name="Session"):
        super().__init__(name, with_post_process=True)
        
        self.__with_session_path = None
        
        from holado.common.context.service_manager import ServiceManager
        self.__service_manager = ServiceManager(type(self))
        
        # Manage multitasking
        self.__multitask_lock = threading.RLock()
        self.__multitask_step_lock = threading.RLock()
        
    def __del__(self):
        # Note: Override Object.__del__ since it supposes that SessionContext is initialized, whereas SessionContext is deleting
        try:
            if self.object_state in [ObjectStates.Deleting, ObjectStates.Deleted]:
                return
            
            self.delete_object()
        except Exception as exc:
            if "Python is likely shutting down" in str(exc):
                # Simply return
                return
            else:
                raise exc
    
    def _delete_object(self):
        # if Tools.do_log(logger, logging.DEBUG):
        #     logger.debug("Interrupting and unregistering all threads for scenario [{}]".format(scenario.name))
        if self.has_threads_manager:
            logger.info(f"Delete session context - Interrupting and unregistering all threads...")
            self.threads_manager.interrupt_all_threads(scope="Session")
            self.threads_manager.unregister_all_threads(scope="Session", keep_alive=False)
        
        # Delete session context
        logger.info(f"Delete session context - Deleting context objects...")
        super()._delete_object()
        
    def configure(self, session_kwargs=None):
        """
        Override this method to configure the session context before new session creation.
        It is usually used to register new services.
        """
        if session_kwargs is None:
            session_kwargs = {}
            
        self.__with_session_path = session_kwargs.get("with_session_path", True)
        
        # Create this thread context
        self.multitask_manager.get_thread_context()
    
    def initialize(self, session_kwargs=None):
        """
        Override this method to initialize the session context after its configuration and new session creation.
        """
        pass
        
    @property
    def services(self):
        return self.__service_manager
    
    @property
    def with_session_path(self):
        return self.__with_session_path
    
    def get_object_getter_eval_string(self, obj, raise_not_found=True):
        from holado_python.standard_library.typing import Typing
        
        name = self.get_object_name(obj)
        if name is not None:
            if self.__service_manager.has_service(name):
                return f"{Typing.get_object_class_fullname(self)}.instance().{name}"
            else:
                return f"{Typing.get_object_class_fullname(self)}.instance().get_object('{name}')"
        
        if raise_not_found:
            from holado_core.common.exceptions.element_exception import ElementNotFoundException
            raise ElementNotFoundException(f"[{self.name}] Failed to find object of id {id(obj)}")
        else:
            return None

    def new_session(self, session_kwargs=None):
        # Report session
        report_path = None
        if self.with_session_path:
            # Create new report path for this session
            name = "session_{}".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            report_path = self.path_manager.get_reports_path(name)
            logger.info(f"Reports location: {report_path}")
            print(f"Reports location: {report_path}")
        self.report_manager.new_session(report_path)
            
        # Logging configuration
        if self.with_session_path and SessionContext.instance().log_manager.in_file:
            log_filename = os.path.join(report_path, "logs", "report.log")
            self.path_manager.makedirs(log_filename)
            SessionContext.instance().log_manager.set_root_log_file(log_filename)
            SessionContext.instance().log_manager.set_config()
    
    def before_all(self, behave_context):
        log_prefix = f"[Before session] "
        
        with self.__multitask_lock:
            self.behave_manager.set_main_context(behave_context)
            self.report_manager.before_all()
        
        # Set variable with session context instance
        self.variable_manager.register_variable("SESSION_CONTEXT", self)
        
        logger.info(f"{log_prefix}Doing previous session post processes if needed...")
        self.do_persisted_post_processes()
        
    def after_all(self):
        log_prefix = f"[After session] "
            
        # Post processes
        logger.info(f"{log_prefix}Post processing...")
        self.do_post_processes()
        
        with self.__multitask_lock:
            self.report_manager.after_all()
            self.behave_manager.clear()

    def before_feature(self, feature):
        from holado_system.system.global_system import GlobalSystem
        from holado_helper.debug.memory.memory_profiler import MemoryProfiler
        from holado_test.common.context.feature_context import FeatureContext
        from holado_test.test_config import TestConfig
        
        log_prefix = f"[Before feature '{feature.name}'] "
        
        with self.__multitask_lock:
            # Logs
            logger.info("="*150)
            logger.info(f"Feature [{feature.name}]")
            
            logger.info(f"{log_prefix}Begin")
            if self.has_feature_context(is_reference=True):
                from holado_core.common.exceptions.technical_exception import TechnicalException
                raise TechnicalException(f"{log_prefix}A feature context is already defined")
            
            GlobalSystem.log_resource_usage(prefix=log_prefix, level=logging.INFO, logger_=logger)
            if TestConfig.profile_memory_in_features and MemoryProfiler.is_tracker_available():
                MemoryProfiler.create_or_reset_tracker_of_objects_summary_changes("features summary")
                # MemoryProfiler.create_or_reset_tracker_of_objects_changes("features objects")
                
            # Feature context
            feature_context = FeatureContext(feature)
            self.__set_feature_context(feature_context)
            
            # Set variable with feature context instance
            self.variable_manager.register_variable("FEATURE_CONTEXT", feature_context)
            
            # Report
            try:
                self.report_manager.before_feature(feature_context, feature)
            except:
                logger.exception(f"{log_prefix}Error while updating report before feature")
            
            logger.info(f"{log_prefix}End")
        
    def after_feature(self, feature):
        from holado_system.system.global_system import GlobalSystem
        from holado_helper.debug.memory.memory_profiler import MemoryProfiler
        from holado_test.test_config import TestConfig
        
        log_prefix = f"[After feature '{feature.name}'] "
        
        with self.__multitask_lock:
            logger.info(f"{log_prefix}Begin")
            if not self.has_feature_context(is_reference=True):
                from holado_core.common.exceptions.technical_exception import TechnicalException
                raise TechnicalException(f"{log_prefix}No feature context is defined")
            
            if TestConfig.profile_memory_in_features and MemoryProfiler.is_tracker_available():
                MemoryProfiler.log_tracker_diff(name="features summary", prefix=log_prefix, level=logging.INFO, logger_=logger)  # @UndefinedVariable
                # MemoryProfiler.log_tracker_diff(name="features objects", prefix="[After feature] ", level=logging.INFO, logger_=logger)  # @UndefinedVariable
            GlobalSystem.log_resource_usage(prefix=log_prefix, level=logging.INFO, logger_=logger)
            
            # End feature context
            self.get_feature_context().end()
            
            # Report
            try:
                self.report_manager.after_feature(feature)
            except:
                logger.exception(f"{log_prefix}Error while updating report after feature")
            
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"{log_prefix}Deleting feature context")
            self.__delete_feature_context()
            
            logger.info(f"{log_prefix}End")
            logger.info(f"Finished feature [{feature.name}]")
        
    def has_feature_context(self, is_reference=None, do_log=False):
        return self.multitask_manager.has_feature_context(is_reference=is_reference, do_log=do_log)
    
    def get_feature_context(self):
        return self.multitask_manager.get_feature_context()
    
    def __set_feature_context(self, feature_context):
        return self.multitask_manager.set_feature_context(feature_context)
    
    def __delete_feature_context(self):
        return self.multitask_manager.delete_feature_context()
    
    def before_scenario(self, scenario):
        from holado_system.system.global_system import GlobalSystem
        from holado_helper.debug.memory.memory_profiler import MemoryProfiler
        from holado_test.common.context.scenario_context import ScenarioContext
        from holado_test.test_config import TestConfig
        
        log_prefix = f"[Before scenario '{scenario.name}'] "
        
        with self.__multitask_lock:
            logger.info("-"*150)
            logger.info(f"Scenario [{scenario.name}]")
            
            logger.info(f"{log_prefix}Begin")
            if not self.has_feature_context(is_reference=True):
                from holado_core.common.exceptions.technical_exception import TechnicalException
                raise TechnicalException(f"{log_prefix}No feature context is defined")
            
            # Create and initialize ScenarioContext
            scenario_context = ScenarioContext(scenario)
            self.get_feature_context().add_scenario(scenario_context)
            
            # Set variable with scenario context instance
            self.get_scenario_context().get_variable_manager().register_variable("SCENARIO_CONTEXT", self.get_scenario_context())
            
            # Report
            try:
                self.report_manager.before_scenario(scenario_context, scenario)
            except:
                logger.exception(f"{log_prefix}Error while updating report before scenario")
            
            # Behave context
            try:
                self.behave_manager.before_scenario()
            except:
                logger.exception(f"{log_prefix}Error while updating behave context before scenario")
            
            GlobalSystem.log_resource_usage(log_prefix, level=logging.INFO, logger_=logger)
            if TestConfig.profile_memory_in_scenarios and MemoryProfiler.is_tracker_available():
                MemoryProfiler.create_or_reset_tracker_of_objects_summary_changes("scenarios summary")
                # MemoryProfiler.create_or_reset_tracker_of_objects_changes("scenarios objects")
        
            logger.info(f"{log_prefix}Doing previous scenario post processes if needed...")
            self.get_scenario_context().do_persisted_post_processes()
            
            logger.info(f"{log_prefix}End")
            logger.info(f"Start scenario [{scenario.name}]")
        
        
    def after_scenario(self, scenario):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        from holado_system.system.global_system import GlobalSystem
        from holado_helper.debug.memory.memory_profiler import MemoryProfiler
        from holado_test.test_config import TestConfig
        from holado_report.report.report_manager import ReportManager
        
        log_prefix = f"[After scenario '{scenario.name}'] "
        
        with self.__multitask_lock:
            # Log error on failing scenario
            status_validation, step_failed, step_number = ReportManager.get_current_scenario_status_information(scenario)
            if status_validation != "Passed":
                msg_list = []
                if step_failed is not None:
                    msg_list.append(f"Scenario {status_validation}:  [scenario in {scenario.filename} at l.{scenario.line} - step {step_number} (l.{step_failed.line})]")
                else:
                    msg_list.append(f"Scenario {status_validation}:  [scenario in {scenario.filename} at l.{scenario.line} - step ? (missing step implementation ?)]")
                step_error_message = ReportManager.get_step_error_message(step_failed)
                if step_error_message:
                    msg_list.append(step_error_message)
                msg = "\n".join(msg_list)
                logger.error(msg)
            
            
            # Process after scenario
            logger.info(f"{log_prefix}Begin")
            # logger.printf"++++++++++++ scenario: {Tools.represent_object(scenario)}")
            
            logger.info(f"{log_prefix}Resource usage:")
            if TestConfig.profile_memory_in_scenarios and MemoryProfiler.is_tracker_available():
                MemoryProfiler.log_tracker_diff(name="scenarios summary", prefix=log_prefix, level=logging.INFO, logger_=logger)  # @UndefinedVariable
                # MemoryProfiler.log_tracker_diff(name="scenarios objects", prefix="[After scenario] ", level=logging.INFO, logger_=logger)  # @UndefinedVariable
            GlobalSystem.log_resource_usage(prefix=log_prefix, level=logging.INFO, logger_=logger)
            
            if not self.has_feature_context(is_reference=True):
                raise TechnicalException(f"{log_prefix}No feature context is defined")
            if not self.has_scenario_context(is_reference=True):
                raise TechnicalException(f"{log_prefix}No scenario context is defined")
            
            self.get_scenario_context().end()
            
            # Post processes
            logger.info(f"{log_prefix}Post processing...")
            self.get_scenario_context().scope_manager.reset_scope_level()
            self.get_scenario_context().do_post_processes()
            
            # Report
            logger.info(f"{log_prefix}Generating reports...")
            try:
                self.report_manager.after_scenario(scenario)
            except:
                logger.exception(f"{log_prefix}Error while updating report after scenario")
            
            # Delete scenario context
            logger.info(f"{log_prefix}Deleting scenario context...")
            # if Tools.do_log(logger, logging.DEBUG):
            #     logger.debug("Deleting context of scenario [{}]".format(scenario.name))
            self.__delete_scenario_context()
            
            # Remove all threads
            logger.info(f"{log_prefix}Interrupting and unregistering all threads...")
            # if Tools.do_log(logger, logging.DEBUG):
            #     logger.debug("Interrupting and unregistering all threads for scenario [{}]".format(scenario.name))
            #TODO: For case of multiple scenarios launched in parallel, interrupt only threads related to current scenario (scenario launched by this thread)
            self.threads_manager.interrupt_all_threads(scope="Scenario")
            self.threads_manager.unregister_all_threads(scope="Scenario", keep_alive=False)
            
            logger.info(f"{log_prefix}End")
            logger.info(f"Finished scenario [{scenario.name}]")
        
    def has_scenario_context(self, is_reference=None):
        return self.has_feature_context(is_reference=is_reference) and self.get_feature_context().has_scenario
    
    def get_scenario_context(self):
        return self.get_feature_context().current_scenario
    
    def __delete_scenario_context(self):
        self.get_scenario_context().delete_object()
        
    def before_step(self, step):
        log_prefix = f"[Before step '{step}'] "
        
        with self.__multitask_step_lock:
            from holado_test.common.context.step_context import StepContext
            from holado_core.common.exceptions.technical_exception import TechnicalException
            
            if not self.has_feature_context(is_reference=None):
                # Look again but do logs before raising exception
                self.has_feature_context(is_reference=None, do_log=True)
                raise TechnicalException(f"{log_prefix}No feature context is defined (step: {step})")
            if not self.has_scenario_context(is_reference=None):
                raise TechnicalException(f"{log_prefix}No scenario context is defined (step: {step})")
            scenario_context = self.get_scenario_context()
            
            # Manage step context
            step_context = StepContext(step)
            scenario_context.scope_manager.set_step_context(step_context)
            
            # Update scenario context
            step_level = scenario_context.scope_manager.scope_level("steps")
            if step_level == 0:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"{log_prefix}Add step {step_context} in scenario {scenario_context}")
                scenario_context.add_step(step_context)
            
            # Manage scope in define
            if scenario_context.block_manager.is_in_define \
                    and (scenario_context.block_manager.is_in_sub_define         # needed to add in define the "end define" steps of sub-define \
                         or step.name not in ["end for", "end while", "end function"]):     # needed to not add in define the "end define" steps of current define
                from holado_test.behave.behave import format_step
                step_str = format_step(step)
                scenario_context.block_manager.scope_in_define.add_steps(step_str)
                
                # Set step status
                step_context.status = "defined"
            
            # Report
            try:
                self.report_manager.before_step(step_context, step, step_level)
            except:
                logger.exception(f"{log_prefix}Error while updating report before step")
    
    def after_step(self, step):
        log_prefix = f"[After step '{step}'] "
        
        with self.__multitask_step_lock:
            from holado_core.common.exceptions.technical_exception import TechnicalException
            
            if not self.has_feature_context(is_reference=None):
                raise TechnicalException(f"{log_prefix}No feature context is defined (step: {step})")
            if not self.has_scenario_context(is_reference=None):
                raise TechnicalException(f"{log_prefix}No scenario context is defined (step: {step})")
            scenario_context = self.get_scenario_context()
            
            # Manage step context
            step_context = scenario_context.scope_manager.get_step_context()
            step_context.end()
            if step_context.status is None:
                step_context.status = step.status.name
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"{log_prefix}Ended step {step_context} in scenario {scenario_context}")
            
            # Report
            try:
                step_level = scenario_context.scope_manager.scope_level("steps")
                self.report_manager.after_step(step_context, step, step_level)
            except:
                logger.exception(f"{log_prefix}Error while updating report after step")
    
    def has_step_context(self):
        return self.has_feature_context() and self.get_feature_context().has_scenario and self.get_scenario_context().has_step()
    
    def get_step_context(self):
        return self.get_scenario_context().get_current_step()
        


SessionContext.TSessionContext = SessionContext


