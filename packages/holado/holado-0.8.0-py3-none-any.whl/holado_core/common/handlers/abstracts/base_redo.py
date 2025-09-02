
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
import abc
import time
from holado_multitask.multithreading.functionthreaded import FunctionThreaded
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.timeout_exception import TimeoutException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.handlers.exceptions.redo_exceptions import RedoIgnoredException,\
    RedoStopRetryException
from holado.holado_config import Config
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class BaseRedo(object):
    """ Base class managing redo of a process until timeout.
    """
    __metaclass__ = abc.ABCMeta

    """
    Default timeout.
    """
    DEFAULT_TIMEOUT_S = 30
    """
    Default timeout for each process.
    """
    DEFAULT_PROCESS_TIMEOUT_S = None
    """
    Default polling delay between each process.
    """
    DEFAULT_POLLING_INTERVAL_S = 0.1
    """
    Default number of allowed retries.
    """
    DEFAULT_NB_RETRIES = 0
    """
    Number of successive failures that must appear before throwing an error.
    """
    DEFAULT_NB_SUCCESSIVE_FAILURES_BEFORE_ERROR = 1
    """
    Default waiting interval after a failure and before a new retry.
    """
    DEFAULT_WAITING_INTERVAL_AFTER_FAILURE_S = 0.1


    def __init__(self, name):
        """
        @param name Name describing redo
        """
        self.__name = name
        
        self.__timeout = BaseRedo.DEFAULT_TIMEOUT_S
        self.__process_timeout = BaseRedo.DEFAULT_PROCESS_TIMEOUT_S
        self.__accepted_time = None
        self.__interval = BaseRedo.DEFAULT_POLLING_INTERVAL_S
        self.__interval_after_failure = BaseRedo.DEFAULT_WAITING_INTERVAL_AFTER_FAILURE_S
        self.__nb_retries = BaseRedo.DEFAULT_NB_RETRIES
        self.__nb_successive_failures_before_error = BaseRedo.DEFAULT_NB_SUCCESSIVE_FAILURES_BEFORE_ERROR
        
        self.__ignored_exceptions = [RedoIgnoredException]
        self.__stop_retry_exceptions = [RedoStopRetryException]
        self.__do_process_in_thread = True
        self.__do_raise_on_stop_retry = True
        self.__do_raise_on_timeout = True              # Specify if a TimeoutException must be raised on timeout
        self.__do_raise_last_exception = True       # Specify if last exception must be raised after timeout, whereas it is configured to not raise a timeout exception
        
        self.__run_counter = 0
        self.__interrupt_counter = 0
        self.__failure_counter = 0
        
        self.__current_process_result = None
        self.__current_process_exception = None
        self.__previous_process_exception_stack_trace = None
        self.__previous_process_exception_counter = 0
        
        self.__start_time = None
        self.__end_time = None
    
    @property
    def name(self):
        """
        @return redo name
        """
        return self.__name
    
    @property
    def process_timeout(self):
        """
        @return The process timeout in seconds
        """
        if self.__process_timeout is not None:
            return self.__process_timeout
        else:
            return self.timeout
    
    @property
    def timeout(self):
        """
        @return The timeout in seconds
        """
        return self.__timeout
    
    @property
    def accepted_time(self):
        """
        @return The accepted spent time
        """
        return self.__accepted_time
    
    @property
    def run_counter(self):
        return self.__run_counter
    
    @property
    def start_time(self):
        return self.__start_time
    
    @property
    def end_time(self):
        return self.__end_time
    
    @property
    def spent_time(self):
        if self.start_time is None:
            return None
        elif self.__end_time is None:
            return Tools.timer_s() - self.start_time
        else:
            return self.__end_time - self.start_time
    
    def _process(self):
        """
        @return Result of a run
        """
        raise NotImplementedError

    def _process_interrupt(self, thread):
        """
        Method launched after a run interruption
        Note: for process implementation that launch uninterruptible code, self method can be used to stop the thread by calling thread.stop()
        @param thread Thread running the process method
        """
        # Nothing by default
        pass
    
    def _is_redo_needed(self, result):
        """
        @param result Current run result.
        @return True if a redo is needed according given result.  
        """
        raise NotImplementedError

    def execute(self):
        """
        @return Result of execution
        """
        if self.__do_process_in_thread:
            return self.__execute_with_thread()
        else:
            return self.__execute_without_thread()

    def __execute_without_thread(self):
        """
        @return Result of execution without executing process in a thread
        """
        last_exception = None
        stop_retry = False
        self.__start_time = Tools.timer_s()
        
        try:
            while not stop_retry:
                try:
                    self.__run_counter += 1
                    if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[{self.name} - {self.__run_counter}] Processing run {self.__run_counter}")
                    
                    self.__execute_process()
                    
                    if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[{self.name} - {self.__run_counter}] Post processing")
                    do_return, result = self.__post_process(interrupted=False)
                    if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[{self.name} - {self.__run_counter}] do return: {do_return} ; result: [{result}] (type: {Typing.get_object_class_fullname(result)})")
                except Exception as exc:
                    has_failure, stop_retry = self.__manage_process_exception(exc, last_exception)
                    last_exception = exc
                else:
                    has_failure = False
                    self.__failure_counter = 0
                    if do_return: # Expected result has appeared
                        # Verify result doesn't appeared too late compared to accepted time
                        self.__raise_accepted_time_if_needed()
                        # Return obtained result
                        return result
                    
                if not stop_retry:
                    stop_retry = self.__manage_process_timeout(last_exception)
                    if stop_retry:
                        # Timeout is reached, but it is configured to not raise an exception ; return last polled result
                        return result
                    self.__wait_after_process(has_failure)
        finally:
            self.__end_time = Tools.timer_s()
            if self.run_counter > 1 or self.__interrupt_counter > 0:
                logger.info(f"redo [{self.name}] has made {self.run_counter} runs and {self.__interrupt_counter} interrupts (process timeout: {self.process_timeout} s)")

    def __execute_with_thread(self):
        """
        @return Result of execution with process execution in a thread
        """
        last_exception = None
        stop_retry = False
        self.__start_time = Tools.timer_s()
        
        try:
            while not stop_retry:
                # Create new thread to process
                thread = self.__get_execute_thread()
                
                try:
                    self.__run_counter += 1
                    if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[{self.name} - {self.__run_counter}] Processing run {self.__run_counter}")
                    
                    thread.start()
                    self.__wait_process(thread)
                    interrupted = self.__interrupt_thread_if_still_alive(thread)
                    
                    if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[{self.name} - {self.__run_counter}] Post processing (interrupted: {interrupted})")
                    do_return, result = self.__post_process(interrupted)
                    if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[{self.name} - {self.__run_counter}] do return: {do_return} ; result: [{result}] (type: {Typing.get_object_class_fullname(result)})")
                except Exception as exc:
                    has_failure, stop_retry = self.__manage_process_exception(exc, last_exception)
                    last_exception = exc
                else:
                    has_failure = False
                    self.__failure_counter = 0
                    if do_return: # Expected result has appeared
                        # Verify result doesn't appeared too late compared to accepted time
                        self.__raise_accepted_time_if_needed()
                        # Return obtained result
                        return result
                    
                if not stop_retry:
                    stop_retry = self.__manage_process_timeout(last_exception)
                    if stop_retry:
                        # Timeout is reached, but it is configured to not raise an exception ; return last polled result
                        return result
                    self.__wait_after_process(has_failure)
        finally:
            self.__end_time = Tools.timer_s()
            if self.run_counter > 1 or self.__interrupt_counter > 0:
                logger.info(f"redo [{self.name}] has made {self.run_counter} runs and {self.__interrupt_counter} interrupts (process timeout: {self.process_timeout} s)")

    def __execute_process(self):
        self.__current_process_result = None
        self.__current_process_exception = None
        
        try:
            # Execute before run
            self._execute_before_process()
            
            # Process
            self.__current_process_result = self._process()
            
            # Execute after run
            self._execute_after_process(self.__current_process_result)
        except Exception as exc:
            self.__current_process_exception = exc
    
    def __get_execute_thread(self):
        return FunctionThreaded(self.__execute_process, [])

    def __wait_process(self, thread, wait_interval_s = None):
        if wait_interval_s is None:
            refs = filter(lambda x: x is not None, (Config.redo_wait_process_max_interval_s, self.__interval/100, self.__interval_after_failure/100))
            wait_interval_s = max(Config.redo_wait_process_min_interval_s, min(refs))
            
        while True:
            if not thread.is_alive():
                break
            
            # Stop wait on timeout
            if Tools.timer_s() > self.start_time + self.timeout:
                logger.warning(f"redo [{self.name}] - run {self.run_counter} - stop waiting process, timeout of {self.timeout} s is reached")
                break
            
            # Stop wait on process timeout
            if self.spent_time > self.process_timeout:
                logger.warning(f"redo [{self.name}] - run {self.run_counter} - stop waiting process, process timeout of {self.process_timeout} s is reached")
                break
            
            time.sleep(wait_interval_s)
    
    def __interrupt_thread_if_still_alive(self, thread):
        res = False
        if thread.is_alive():
            self.__interrupt_counter += 1
            if thread.is_interruptable:
                thread.interrupt()
            
            # Manage specific interrupt
            # Note: for process implementation that launch uninterruptible code, this method can be used to stop the thread by calling thread.stop()
            self._process_interrupt(thread)
            
            res = True
            logger.warning(f"redo [{self.name}] interrupted after {self.spent_time} seconds ({self.run_counter} runs ; {self.__interrupt_counter} interrupts ; process timeout: {self.process_timeout} s)")
        return res
    
    def __post_process(self, interrupted):
        if interrupted:
            self.__current_process_exception = None
            
            # Manage exception logs
            self.__previous_process_exception_stack_trace = None
            self.__previous_process_exception_counter = 0
        elif self.__current_process_exception is None:
            if not self._is_redo_needed(self.__current_process_result):
#                            logger.trace("   --- redo [{}] -> return: {}", name, (self.__current_process_result != None ? self.__current_process_result.toString() : "None")))
                return True, self.__current_process_result
            
            # Manage exception logs
            self.__previous_process_exception_stack_trace = None
            self.__previous_process_exception_counter = 0
        else:
            # Manage exception logs
            current_process_exception_stack_trace = Tools.represent_exception(self.__current_process_exception)
            if self.__previous_process_exception_stack_trace is not None and current_process_exception_stack_trace == self.__previous_process_exception_stack_trace:
                self.__previous_process_exception_counter += 1
                
                if self.__previous_process_exception_counter % 10 == 0:
                    logger.warning(f"redo [{self.name}] - run {self.run_counter} - got previous process exception 10 more times ({self.__previous_process_exception_counter} times in total): {self.__get_error_description(self.__current_process_exception)}")
            else:
                logger.warning(f"redo [{self.name}] - run {self.run_counter} - got process exception {self.__get_error_description(self.__current_process_exception)}:\n{Tools.indent_string(4, current_process_exception_stack_trace)}")
                self.__previous_process_exception_stack_trace = current_process_exception_stack_trace
                self.__previous_process_exception_counter = 1
            
            raise self.__current_process_exception
        
        # Don't stop retries, and return current result
        return False, self.__current_process_result
    
    def __manage_process_exception(self, exc, last_exception):
        has_failure = False
        stop_retry = False
        
        # Begin by calling enabling to replace exception considered ignored or stopping retry
        try:
            self._execute_after_failure(exc)
        except Exception as exc_2:
            exc = exc_2
        
        if self._is_stop_retry(exc):
            stop_retry = True
            self.__process_stop_retry(exc)
        elif self._is_ignored(exc):
            self.__process_ignored(exc)
        else:
            has_failure = True
            self.__process_failure(exc, last_exception)
        
        return has_failure, stop_retry
    
    def __process_ignored(self, exc):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"redo [{self.name}] - run {self.run_counter} - ignored process exception {self.__get_error_description(exc)}")
        self._execute_after_ignored(exc)
    
    def __process_stop_retry(self, exc):
        logger.info(f"redo [{self.name}] - run {self.run_counter} - stop retries due to exception {self.__get_error_description(exc)}")
        self._execute_after_stop_retry(exc)
        if self.__do_raise_on_stop_retry:
            raise exc
    
    def __process_failure(self, exception, last_exception):
        self.__failure_counter += 1
        if self.__failure_counter >= self.__nb_successive_failures_before_error:
            if self.__failure_counter > 1:
                logger.info(f"redo [{self.name}] - run {self.run_counter} - maximum successive failure ({self.__nb_successive_failures_before_error}) is reached - following previous failure is skipped: {self.__get_error_description(last_exception) if last_exception else '[None]'}")
            logger.info(f"redo [{self.name}] - run {self.run_counter} - maximum successive failure ({self.__nb_successive_failures_before_error}) is reached - following failure is considered as an error: {self.__get_error_description(exception)}")

            # Raise exception
            new_message = f"redo [{self.name}] - run {self.run_counter} - maximum successive failure ({self.__nb_successive_failures_before_error}) is reached"
            Tools.raise_same_exception_type(exception, new_message)
        else:
            if self.__failure_counter > 1:
                logger.info(f"redo [{self.name}] - run {self.run_counter} - {self.__failure_counter}'th successive failure - following previous failure is skipped: {self.__get_error_description(last_exception) if last_exception else '[None]'}")

    def __raise_accepted_time_if_needed(self):
        if self.accepted_time is not None and self.spent_time > self.accepted_time:
            accepted_msg = self._get_accepted_time_message()
            accepted_msg = f"{accepted_msg}\n -> " if accepted_msg is not None and len(accepted_msg) > 0 else ""
            msg = f"{accepted_msg}Too long after {self.spent_time} s in redo [{self.name}] ({self.run_counter} runs ; {self.__interrupt_counter} interrupts ; timeout: {self.timeout} s ; process timeout: {self.process_timeout} s ; allowed retries: {self.__nb_retries})"
            raise FunctionalException(msg)
    
    def __manage_process_timeout(self, last_exception):
        res = False
        if self.spent_time > self.timeout or self.__nb_retries > 0 and self.run_counter >= self.__nb_retries:
            if self.__do_raise_on_timeout:
                timeout_msg = self._get_timeout_message()
                timeout_msg = f"{timeout_msg}\n -> " if timeout_msg is not None and len(timeout_msg) > 0 else ""
                msg = f"{timeout_msg}Timed out after {self.spent_time} s in redo [{self.name}] ({self.run_counter} runs ; {self.__interrupt_counter} interrupts ; timeout: {self.timeout} s ; process timeout: {self.process_timeout} s ; allowed retries: {self.__nb_retries})"
                raise TimeoutException(msg) from last_exception
            elif self.__do_raise_last_exception and last_exception is not None:
                raise last_exception
            else:
                # Return a timeout has occured to stop retries
                res = True
        return res
    
    def __wait_after_process(self, has_failure):
        # Manage waits
        if has_failure:
            if self.__interval_after_failure > 0:
                try:
                    time.sleep(self.__interval_after_failure)
                except InterruptedError as e:
                    # Thread.currentThread().interrupt()
                    raise TechnicalException(self.__get_error_message(e)) from e
        elif self.__interval > 0:
            try:
                time.sleep(self.__interval)
            except InterruptedError as e:
                # Thread.currentThread().interrupt()
                raise TechnicalException(self.__get_error_message(e)) from e
    
    def _get_waited_description(self):
        return None
    
    def _get_timeout_message(self):
        waited_description = self._get_waited_description()
        if waited_description is not None:
            return f"Timeout ({self.timeout} s) when waiting {waited_description}"
        else:
            return None
    
    def _get_accepted_time_message(self):
        waited_description = self._get_waited_description()
        if waited_description is not None:
            return f"Too long ({self.spent_time} s) to wait {waited_description} (accepted time: {self.__accepted_time} s)"
        else:
            return None
    
    def __get_error_description(self, exc):
        return f"{Typing.get_object_class_name(exc)}('{self.__get_error_message(exc)}')"
        
    def __get_error_message(self, exc):
        if hasattr(exc, 'message'):
            return exc.message
        else:
            return str(exc)
        
    def _execute_before_process(self):
        """
        Method launched before each run.
        If an exception occurs in self method, the run will not be done.
        """
        # Nothing is done by default
        pass
        
    def _execute_after_process(self, result):
        """
        Method launched after each run.
        If an exception occurs in self method, it is managed as a run failure exception.
        """
        # Nothing is done by default
        pass
    
    def _execute_after_failure(self, exception):
        """
        Method launched after a failure and before considering if an exception is ignored or stopping retry.
        By implementing this method, it is possible to ignore/stop retry on an exception with a specific message,
        by replacing it by a custom exception (or dedicated RedoIgnoredException and RedoStopRetryException).
        """
        # Nothing is done by default
        pass
    
    def _execute_after_ignored(self, exception):
        """
        Method launched after an exception is ignored and before a redo.
        """
        # Nothing is done by default
        pass
    
    def _execute_after_stop_retry(self, exception):
        """
        Method launched after an exception is stopping retry.
        """
        # Nothing is done by default
        pass
    
    def with_unlimited_number_retries(self):
        """
        Sets unlimited number of allowed retries.
        @return A self reference.
        """
        return self.with_allowed_number_retries(0)
    
    def with_allowed_number_retries(self, nb_retries):
        """
        Sets the number of allowed retries.
        If not successful after self number of retries, a timeout exception is thrown.
        If the number of retries is set to 0, it retries infinitely until timeout.
        {@link #DEFAULT_NB_RETRIES}.
        @param nb_retries Number of allowed retries.
        @return A self reference.
        """
        self.__nb_retries = nb_retries
        return self
    
    def with_accepted_time(self, accepted_time):
        """
        Sets the max waiting time that is acceptable, otherwise it is considered as an error.
        @param accepted_time Accepted time in seconds.
        @return A self reference.
        """
        self.__accepted_time = accepted_time
        return self
    
    def with_timeout(self, timeout):
        """
        Sets how long to wait for the evaluated condition to be True. The default timeout is
        {@link #DEFAULT_TIMEOUT_S}.
        @param timeout Timeout in seconds.
        @return A self reference.
        """
        self.__timeout = timeout
        return self
    
    def update_timeout(self, timeout):
        """
        Update how long to still wait from now for the evaluated condition to be True.
        @param timeout Timeout in seconds.
        @return A self reference.
        """
        self.__timeout = self.spent_time + timeout
        return self
    
    def without_timeout(self):
        """
        @return A self reference.
        """
        self.__timeout = 24 * 3600
        return self
    
    def with_raise_on_timeout(self, do_raise=True):
        """
        @param do_raise If raise the exception that has stopped retry
        @return A self reference.
        """
        self.__do_raise_on_timeout = do_raise
        return self
    
    def without_raise_on_timeout(self):
        """
        @return A self reference.
        """
        return self.with_raise_on_timeout(False)
    
    def with_process_in_thread(self, do_process_in_thread=True):
        """
        Set if 'process' must be executed in a thread.
        @return A self reference.
        """
        self.__do_process_in_thread = do_process_in_thread
        return self
    
    def without_process_in_thread(self):
        """
        Set 'process' must be executed without thread.
        @return A self reference.
        """
        return self.with_process_in_thread(do_process_in_thread=False)
    
    def with_process_timeout(self, timeout):
        """
        Sets how much time is let to process method until it is interrupted and relaunched. The default timeout is
        {@link #DEFAULT_PROCESS_TIMEOUT_S}.
        @param timeout Timeout in seconds.
        @return A self reference.
        """
        self.__process_timeout = timeout
        return self
    
    def with_process_timeout_for_retry(self, nb_retry):
        """
        Set appropriate process timeout in order to make at least given number of retries until global timeout.
        @param nb_retry Number of retries to do at least.
        @return A self reference.
        """
        return self.with_process_timeout(self.timeout / nb_retry)
    
    def polling_every(self, duration):
        """
        Sets how often the condition should be evaluated.
        
        In reality, the interval may be greater as the cost of actually evaluating a condition function
        is not factored in. The default polling interval is {@link #DEFAULT_POLLING_INTERVAL_S}.
        @param duration The duration between two polling.
        @return A self reference.
        """
        self.__interval = duration
        return self
    
    def with_nb_successive_failure_before_error(self, nb_successive_failures_before_error):
        """
        Sets the number of successive failures that must occur before considering being in error.
        {@link #DEFAULT_NB_SUCCESSIVE_FAILURES_BEFORE_ERROR}.
        @param nb_successive_failures_before_error Number of successive failures.
        @return A self reference.
        """
        self.__nb_successive_failures_before_error = nb_successive_failures_before_error
        return self
    
    def with_waiting_after_failure(self, duration):
        """
        Sets how much time must be waited after a failure before a new retry.
        The default interval is {@link #DEFAULT_WAITING_INTERVAL_AFTER_FAILURE_S}.
        @param duration Duration to wait in seconds.
        @return A self reference.
        """
        self.__interval_after_failure = duration
        return self
    
    def ignoring(self, *exception_types):
        """
        Configures to ignore specific types of exceptions while waiting for a condition.
        Any exceptions not whitelisted will be allowed to propagate, terminating the wait.
        @param exception_types The types of exceptions to ignore.
        @return A self reference.
        """
        if exception_types:
            self.__ignored_exceptions.extend(exception_types)
        return self
    
    def _is_ignored(self, exception):
        for exception_type in self.__ignored_exceptions:
            if isinstance(exception, exception_type):
                return True
        return False
    
    def stop_retry_on(self, *exception_types):
        """
        Configures to stop retries on specific types of exceptions while waiting for a condition.
        @param exception_types The types of exceptions that would stop retries.
        @return A self reference.
        """
        if exception_types:
            self.__stop_retry_exceptions.extend(exception_types)
        return self
    
    def _is_stop_retry(self, exception):
        for exception_type in self.__stop_retry_exceptions:
            if isinstance(exception, exception_type):
                return True
        return False
    
    def with_raise_on_stop_retry(self, do_raise=True):
        """
        @param do_raise If raise the exception that has stopped retry
        @return A self reference.
        """
        self.__do_raise_on_stop_retry = do_raise
        return self
    
    def without_raise_on_stop_retry(self):
        """
        @return A self reference.
        """
        return self.with_raise_on_stop_retry(False)
    
    def _print_run_counter(self):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"   --- redo ({self.name}) : run {self.run_counter}")
    
        
        
        
