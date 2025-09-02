
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
from builtins import object
import threading
import gc
from holado.common.handlers.undefined import default_value

logger = None
default_collect_periodicity = 10

def initialize_logger():
    global logger
    logger = logging.getLogger(__name__)


class GcManager(object):
    """
    Manage Garbage Collector
        
    Note: When working with HolAdo, it is highly recommended to call collect_periodically method at process start in order to avoid deadlocks.
          This is done by default in holado.initialize method.
    Explanation:
        HolAdo is using object finalizers (define __del__ methods) to properly release objects resources.
        But in current garbage collector default mecanism, objects are technically finalized (call of __del__) in any yielded thread.
        Thus, depending on what thread is doing when an object is finalized, a deadlock can occur.
        Example: current thread is logging a message, garbage collector is finalizing an object in this thread when logger flushes its stream,
                 and object finalizer tries to log an other message => it results to a deadlock in logging library in its lock mecanism.
    """
    
    # Manage running and pended collect
    __collect_run_lock = threading.Lock()
    __is_collect_running = False
    __is_collect_pending = False
    __duration_until_pended_collect = default_collect_periodicity
    
    # Manage scheduled collect as timer
    __collect_timer_lock = threading.RLock()
    __collect_periodicity = None
    __collect_timer = None
    __collect_timer_at = None
    
    @classmethod
    def is_collect_threaded(cls):
        return cls.__collect_periodicity is not None
    
    @classmethod
    def get_collect_periodicity(cls):
        return cls.__collect_periodicity
    
    @classmethod
    def collect_periodically(cls, collect_periodicity=default_value):
        """
        Call this method to periodically process gargage collector collect.
        By calling this method, default behaviour of garbage collector is disabled.
        """
        gc.disable()
        with cls.__collect_timer_lock:
            cls.__collect_periodicity = default_collect_periodicity if collect_periodicity is default_value else collect_periodicity
        cls.__schedule_next_timer(cls.__collect_periodicity)
    
    @classmethod
    def collect(cls, max_duration_until_next_collect_in_seconds=default_value):
        max_duration = default_collect_periodicity if max_duration_until_next_collect_in_seconds is default_value else max_duration_until_next_collect_in_seconds
        
        with cls.__collect_run_lock:
            # If a collect is already pended, update duration until pended collect
            if cls.__is_collect_pending:
                if max_duration < cls.__duration_until_pended_collect:
                    cls.__duration_until_pended_collect = max_duration
                return
            # If a collect is already running, pend a collect
            if cls.__is_collect_running:
                cls.__is_collect_pending = True
                cls.__duration_until_pended_collect = max_duration
                return
        
        # Else schedule next collect
        with cls.__collect_timer_lock:
            if cls.__collect_timer is not None:
                cls.__schedule_next_timer(max_duration_until_next_collect_in_seconds)
            else:
                cls.__schedule_next_timer(0)
        
    @classmethod
    def __collect(cls):
        # Start running
        with cls.__collect_run_lock:
            cls.__is_collect_running = True
        
        # Process collect
        gc.collect()
        
        # Schedule next timer
        duration_until_next_collect = None
        with cls.__collect_run_lock:
            if cls.__is_collect_pending:
                duration_until_next_collect = cls.__duration_until_pended_collect
        with cls.__collect_timer_lock:
            if cls.__collect_periodicity is not None:
                if duration_until_next_collect is None:
                    duration_until_next_collect = cls.__collect_periodicity
                else:
                    duration_until_next_collect = min(duration_until_next_collect, cls.__collect_periodicity)
            
            cls.__schedule_next_timer(duration_until_next_collect)
        
        # Stop running
        with cls.__collect_run_lock:
            cls.__is_collect_running = False
            # Reinitialize pending variables
            cls.__is_collect_pending = False
            cls.__duration_until_pended_collect = default_collect_periodicity
            
    @classmethod
    def __schedule_next_timer(cls, duration_until_next_collect_seconds):
        import holado_multitask.multithreading.timer as mmt
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        from holado_python.common.tools.datetime import DateTime, DurationUnit
        from holado_python.common.enums import ArithmeticOperator
        
        if duration_until_next_collect_seconds is default_value:
            duration_until_next_collect_seconds = default_collect_periodicity
        
        with cls.__collect_timer_lock:
            if duration_until_next_collect_seconds is not None:
                now = DateTime.now()
                next_timer_at = DateTime.apply_delta_on_datetime(now, ArithmeticOperator.Addition, duration_until_next_collect_seconds, DurationUnit.Second)
                
                if cls.__collect_timer_at is not None and cls.__collect_timer_at > now and next_timer_at > cls.__collect_timer_at:
                    # Current scheduled collect is not running and will occur before newly schedule, it is preserved
                    return
                elif cls.__collect_timer_at is not None:
                    # Current scheduled collect is canceled and replaced
                    cls.__collect_timer.cancel()
                
                # Schedule timer with given duration
                cls.__collect_timer = mmt.Timer("GcManager-collect", duration_until_next_collect_seconds, cls.__collect, register_scope=MultitaskManager.SESSION_SCOPE_NAME)
                cls.__collect_timer.start()
                cls.__collect_timer_at = next_timer_at
            else:
                cls.__collect_timer = None
                cls.__collect_timer_at = None

