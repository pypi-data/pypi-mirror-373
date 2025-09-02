
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

from holado_core.common.tools.tools import Tools
import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


try:
    import pympler
    from pympler.tracker import SummaryTracker
    from pympler.tracker import ObjectTracker
    with_pympler = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Pympler is not available for memory profiling. Initialization failed on error: {exc}")
    with_pympler = False


class MemoryProfiler():
    """
    Manage many methods to profile memory.
    It uses internally different libraries, depending on profiling method.
    """
    __stored_trackers = {}
    
    @classmethod
    def is_tracker_available(cls):
        return with_pympler
    
    @classmethod
    def create_or_reset_tracker_of_objects_summary_changes(cls, name):
        if name in cls.__stored_trackers:
            cls.reset_tracker(cls.__stored_trackers[name])
        else:
            cls.__stored_trackers[name] = cls.new_tracker_of_objects_summary_changes()
        return cls.__stored_trackers[name]
    
    @classmethod
    def create_or_reset_tracker_of_objects_changes(cls, name):
        if name in cls.__stored_trackers:
            cls.reset_tracker(cls.__stored_trackers[name])
        else:
            cls.__stored_trackers[name] = cls.new_tracker_of_objects_changes()
        return cls.__stored_trackers[name]
    
    @classmethod
    def new_tracker_of_objects_summary_changes(cls):
        if cls.is_tracker_available():
            return SummaryTracker()
        else:
            raise TechnicalException("Third library 'Pympler' is needed for this profiling method")
    
    @classmethod
    def new_tracker_of_objects_changes(cls):
        if cls.is_tracker_available():
            return ObjectTracker()
        else:
            raise TechnicalException("Third library 'Pympler' is needed for this profiling method")
    
    @classmethod
    def reset_tracker(cls, tracker):
        if isinstance(tracker, SummaryTracker):
            _ = tracker.diff()
        elif isinstance(tracker, ObjectTracker):
            _ = tracker.get_diff()
        else:
            raise TechnicalException(f"Unexpected tracker type '{Typing.get_object_class_fullname(tracker)}'")
    
    @classmethod
    def log_tracker_diff(cls, name=None, tracker=None, prefix=None, level=logging.DEBUG, logger_=None):
        if logger_ is None:
            logger_ = logger
        if not logger_.isEnabledFor(level):
            return
        
        if name is not None:
            tracker = cls.__stored_trackers.get(name)
        if tracker is None:
            raise TechnicalException(f"Parameter 'tracker' or 'name' must be defined")
        
        if isinstance(tracker, SummaryTracker):
            tracker_descr = "objects summary"
        elif isinstance(tracker, ObjectTracker):
            tracker_descr = "objects summary"
        else:
            raise TechnicalException(f"Unexpected tracker type '{Typing.get_object_class_fullname(tracker)}'")
        
        logger_.log(level, f"{prefix if prefix else ''}Preparing changes in {tracker_descr}...")
        formatted_diff = "\n".join(tracker.format_diff())
        logger_.log(level, f"{prefix if prefix else ''}Changes in {tracker_descr}:\n{formatted_diff}")
        

