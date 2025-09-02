
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

import threading
import logging
import os
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_system.system.global_system import OSTypes, GlobalSystem
from holado_multitask.multithreading.context.thread_context import ThreadContext
from holado_multitask.multiprocessing.context.process_context import ProcessContext
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing
from holado.common.handlers.undefined import default_context
from holado.common.context.session_context import SessionContext
import psutil
import signal

logger = logging.getLogger(__name__)


class MultitaskManager(object):
    """
    Manage resources used by threads/processes run by HolAdo.
    It provides a ThreadContext/ProcessContext for each thread/process.
    """
    
    SESSION_SCOPE_NAME = "Session"
    SCENARIO_SCOPE_NAME = "Scenario"
    
    @classmethod
    def get_scope_name(cls, scope=default_context):
        if scope is default_context:
            if SessionContext.instance().has_scenario_context():
                return MultitaskManager.SCENARIO_SCOPE_NAME
            else:
                return MultitaskManager.SESSION_SCOPE_NAME
        elif scope is not None:
            return scope
        else:
            return MultitaskManager.SESSION_SCOPE_NAME
    
    
    @classmethod
    def get_process_id(cls, process=None):
        if process is None:
            return os.getpid()
        else:
            return process.pid
    
    @classmethod
    def get_parent_process_id(cls, pid=None):
        if pid is None:
            return os.getppid()
        else:
            process = psutil.Process(pid)
            return process.ppid()
    
    @classmethod
    def get_children_process_ids(cls, pid=None, recursive=False):
        if pid is None:
            pid = os.getpid()
        
        process = psutil.Process(pid)
        children = process.children(recursive=recursive)
        return [c.pid for c in children]
    
    @classmethod
    def kill_process(cls, pid, sig=signal.SIGTERM, do_kill_children=True, recursively=True):
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return
        
        # Kill children
        if do_kill_children:
            children = process.children(recursive=recursively)
            for proc in children:
                try:
                    proc.send_signal(sig)
                except signal.SIGTERM:
                    pass
        
        # Kill process
        try:
            process.send_signal(sig)
        except signal.SIGTERM:
            pass
    
    @classmethod
    def has_thread_native_id(cls):
        from holado_multitask.multithreading.threadsmanager import ThreadsManager
        return ThreadsManager.has_native_id()
    
    @classmethod
    def get_thread_uid(cls, thread=None):
        tid = cls.get_thread_id(thread=thread)
        if cls.has_thread_native_id():
            return tid
        else:
            return (cls.get_process_id(), tid)
    
    @classmethod
    def get_thread_id(cls, thread=None, native=None):
        if thread is None:
            thread = threading.current_thread()
        if native is None:
            native = cls.has_thread_native_id()
        elif native and not cls.has_thread_native_id():
            raise TechnicalException(f"System doesn't support thread native id")
        
        if native:
            return thread.native_id
        else:
            return thread.ident
        
    
    def __init__(self):
        self.__process_lock = threading.Lock()
        self.__process_context_by_uname = {}
        self.__parent_thread_uid_by_process_uname = {}
        self.__process_id_by_uname = {}
        self.__process_uname_by_id = {}
        self.__thread_uid_by_process_uname = {}
        
        self.__thread_lock = threading.Lock()
        self.__main_thread_uid = self.get_thread_uid()
        self.__thread_context_by_uname = {}
        self.__parent_thread_uid_by_thread_uname = {}
        self.__thread_uid_by_uname = {}
        self.__thread_uname_by_uid = {}
        
        self.__related_thread_uid_by_uid = {}
        
        self.__feature_context_by_thread_uid = {}
    
    @property
    def is_main_thread(self):
        thread_uid = self.get_thread_uid()
        return thread_uid == self.__main_thread_uid
    
    @property
    def main_thread_uid(self):
        return self.__main_thread_uid
    
    
    ### Manage processes
    
    def prepare_process(self, name, update_parent=True):
        """
        Create a process context and return a unique name based to given name
        """
        with self.__process_lock:
            res = name
            name_index = 0
            while res in self.__process_context_by_uname:
                name_index += 1
                res = f"{name}_{name_index}"
                
            self.__process_context_by_uname[res] = ProcessContext(name, res)
            
            if update_parent:
                uid = self.get_thread_uid()
                self.__parent_thread_uid_by_process_uname[res] = uid
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"New process context: name='{name}' ; unique name='{res}'{{}}".format(f" ; parent thread UID={uid}" if update_parent else ''))
        return res
    
    def set_process_id(self, name, pid):
        # logger.print(f"+++++++++ __parent_thread_uid_by_thread_uname: {self.__parent_thread_uid_by_thread_uname}")
        # logger.print(f"+++++++++ __feature_context_by_thread_uid: {self.__feature_context_by_thread_uid}")
        # logger.print(f"+++++++++ __thread_context_by_uname: {self.__thread_context_by_uname}")
        self.__process_id_by_uname[name] = pid
        self.__process_uname_by_id[pid] = name
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Set process PID: name='{name}' ; PID={pid}")
    
    def set_process_thread_uid(self, name, thread_uid):
        # Set main thread UID of process
        self.__thread_uid_by_process_uname[name] = thread_uid
        
        # Set parent thread of process as parent thread of process main thread 
        parent_thread_uid = self.__parent_thread_uid_by_process_uname[name]
        tuname = self._get_thread_unique_name_or_uid(thread_uid)
        self.__parent_thread_uid_by_thread_uname[tuname] = parent_thread_uid
        # logger.print(f"+++++++++ __parent_thread_uid_by_thread_uname: {self.__parent_thread_uid_by_thread_uname}")
        # logger.print(f"+++++++++ __feature_context_by_thread_uid: {self.__feature_context_by_thread_uid}")
        # logger.print(f"+++++++++ __thread_context_by_uname: {self.__thread_context_by_uname}")
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Set process thread UID: process name='{name}' ; thread name='{tuname}' ; thread UID={thread_uid} ; parent thread UID={parent_thread_uid}")
        
    def _get_process_unique_name_or_pid(self, pid=None):
        if pid is None:
            pid = self.get_process_id()
        if pid in self.__process_uname_by_id:
            return self.__process_uname_by_id[pid]
        else:
            # logger.debug(f"Using process PID {pid} as unique name")
            return pid
    
    
    ### Manage threads
    
    def prepare_thread(self, name, update_parent=True):
        """
        Create a thread context and return a unique name based to given name
        """
        with self.__thread_lock:
            res = name
            name_index = 0
            while res in self.__thread_context_by_uname:
                name_index += 1
                res = f"{name}_{name_index}"
                
            self.__thread_context_by_uname[res] = ThreadContext(name, res)
            
            this_uid = self.get_thread_uid()
            # In some cases (ex: on missing thread context), thread uid is used as name, and it can't be its own parent
            if update_parent and res != this_uid:
                # logger.print(f"+++++ Set parent thread UID: {res} -> {this_uid}")
                self.__parent_thread_uid_by_thread_uname[res] = this_uid
                
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"New thread context: name='{name}' ; unique name='{res}'{{}}".format(f" ; parent thread UID={this_uid}" if update_parent and res != this_uid else ''))
        return res
    
    def set_thread_uid(self, name, uid=None):
        if uid is None:
            uid = self.get_thread_uid()
        # logger.print(f"+++++ Set thread UID: {name} -> {uid}")
        self.__thread_uid_by_uname[name] = uid
        self.__thread_uname_by_uid[uid] = name
        self.__thread_context_by_uname[name].thread_uid = uid
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Set thread UID: name='{name}' ; UID={uid}")
            
    def _get_thread_unique_name_or_uid(self, uid=None):
        if uid is None:
            uid = self.get_thread_uid()
        if uid in self.__thread_uname_by_uid:
            return self.__thread_uname_by_uid[uid]
        else:
            # logger.debug(f"Using thread UID {uid} as unique name")
            return uid
        
    def relate_thread_to(self, from_uid, to_uid):
        self.__related_thread_uid_by_uid[from_uid] = to_uid
    
    
    
    ### Manage process context
    
    def get_process_context(self, pid=None):
        if pid is None:
            pid = self.get_process_id()
        uname = self._get_process_unique_name_or_pid(pid=pid)
        # logger.print(f"++++ get_process_context: uid={uid} ; uname={uname}", stack_info=True)
        
        if uname not in self.__process_context_by_uname:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("Creating missing process context for unique name {}".format(f"'{uname}'" if isinstance(uname, str) else f"{uname}"))
            uname = self.prepare_process(uname, update_parent=False)
            self.set_process_id(uname, pid)
            
        return self.__process_context_by_uname[uname]
    
    
    
    
    ### Manage thread context
    
    def get_thread_context(self, uid=None):
        if uid is None:
            uid = self.get_thread_uid()
        uname = self._get_thread_unique_name_or_uid(uid=uid)
        # logger.print(f"++++ get_thread_context: uid={uid} ; uname={uname}", stack_info=True)
        
        if uname not in self.__thread_context_by_uname:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("Creating missing thread context for unique name {}".format(f"'{uname}'" if isinstance(uname, str) else f"{uname}"))
            uname = self.prepare_thread(uname, update_parent=False)
            self.set_thread_uid(uname, uid)
            
        res = self.__thread_context_by_uname[uname]
        if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Thread context for tread UID '{uid}' (uname: '{uname}'): {res}")
        return res
   
    def get_parent_thread_context(self, uid=None):
        if uid is None:
            uid = self.get_thread_uid()
        uname = self._get_thread_unique_name_or_uid(uid=uid)
        if uname in self.__parent_thread_uid_by_thread_uname:
            parent_uid = self.__parent_thread_uid_by_thread_uname[uname]
            # logger.print(f"++++ get_parent_thread_context: {uid} -> {parent_uid}", stack_info=True)
            return self.get_thread_context(uid=parent_uid)
        else:
            return None
    
    def __find_thread_context_having(self, has_func, uid=None, do_log=False, _internal=None):
        if uid is None:
            uid = self.get_thread_uid()
        if _internal is None:
            _internal = []
        
        res = None
        while True:
            if uid in _internal:
                break
            else:
                _internal.append(uid)
                
            res = self.__find_thread_context_having__throw_thread_parents(has_func, uid=uid, do_log=do_log, _internal=_internal)
            if res is None:
                if uid in self.__related_thread_uid_by_uid:
                    # Try with related thread
                    old_uid = uid
                    uid = self.__related_thread_uid_by_uid[uid]
                    if do_log and Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[MultitaskManager.__find_thread_context_having] Not found in thread uid '{old_uid}', try in thread uid '{uid}'")
                else:
                    if do_log and Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[MultitaskManager.__find_thread_context_having] Not found in thread uid '{uid}', stop search")
                    return None
            else:
                if do_log and Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[MultitaskManager.__find_thread_context_having] Found in thread uid '{uid}' => {res}")
                break
        
        return res
    
    def __find_thread_context_having__throw_thread_parents(self, has_func, uid=None, do_log=False, _internal=None):
        if uid is None:
            uid = self.get_thread_uid()
            
        # logger.print(f"+++++ Find thread context having feature context: uid={uid}")
        while True:
            uname = self._get_thread_unique_name_or_uid(uid=uid)
            if uname in self.__thread_context_by_uname:
                # logger.print(f"+++++ Find thread context having feature context: {uname} not in __thread_context_by_uname => None")
                # return None
                
                thread_context = self.__thread_context_by_uname[uname]
                found = False
                if isinstance(has_func, str):
                    if hasattr(thread_context, has_func):
                        found = getattr(thread_context, has_func)()
                else:
                    found = has_func(thread_context)
                if found:
                    # logger.print(f"+++++ Find thread context having feature context => found from uid={uid}")
                    if do_log and Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[MultitaskManager.__find_thread_context_having__throw_thread_parents] Found in thread uid '{uid}' (uname: '{uname}') => {thread_context}")
                    return thread_context
                else:
                    if do_log and Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                        logger.trace(f"[MultitaskManager.__find_thread_context_having__throw_thread_parents] Thread uid '{uid}' (uname: '{uname}') has a context, but it doesn't verify {has_func}")
            
            if uname in self.__parent_thread_uid_by_thread_uname:
                # Retry with parent thread uid
                uid = self.__parent_thread_uid_by_thread_uname[uname]
                if do_log and Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[MultitaskManager.__find_thread_context_having__throw_thread_parents] Try in parent thread uid '{uid}'")
                # logger.print(f"+++++ Find thread context having feature context: in parent uid={uid}")
                return self.__find_thread_context_having(has_func, uid=uid, do_log=do_log, _internal=_internal)
            else:
                # logger.print(f"+++++ Find thread context having feature context: {uname} not in __parent_thread_uid_by_thread_uname => None")
                if do_log and Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[MultitaskManager.__find_thread_context_having__throw_thread_parents] Not found in thread uid '{uid}' (uname: '{uname}'), and it has not parent thread")
                return None
        
    
    
    ### Manage feature context
    
    def __update_feature_context_for_thread_uid(self, uid):
        if uid not in self.__feature_context_by_thread_uid:
            thread_context = self.__find_thread_context_having(ThreadContext.has_feature_context, uid)
            if thread_context is None:
                feature_context = None
            else:
                feature_context = thread_context.get_feature_context()
            # logger.print(f"+++++ Set feature context for thread UID {uid}: {feature_context}")
            is_reference = (thread_context.thread_uid == uid)
            self.__feature_context_by_thread_uid[uid] = (feature_context, is_reference)
            if Tools.do_log(logger, logging.DEBUG):
                # logger.debug(f"Updated feature context for thread: UID='{uid}' ; feature context={feature_context}")
                logger.debug(f"Updated feature context for thread: UID='{uid}' ; feature context={feature_context}   (registered list: {self.__feature_context_by_thread_uid})")
        
    def __remove_feature_context_for_any_thread_uid(self, feature_context):
        list_uid = list(self.__feature_context_by_thread_uid.keys())
        for uid in list_uid:
            if self.__feature_context_by_thread_uid[uid][0] is feature_context:
                del self.__feature_context_by_thread_uid[uid]
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Removed feature context ({id(feature_context)}) association with thread UID {uid}")
        
    def has_feature_context(self, is_reference=True, do_log=False):
        uid = self.get_thread_uid()
        # self.__update_feature_context_for_thread_uid(uid)
        # return self.__feature_context_by_thread_uid[uid] is not None
        
        if uid in self.__feature_context_by_thread_uid:
            res = self.__feature_context_by_thread_uid[uid][0] is not None
            if res and is_reference is not None:
                res &= (is_reference == self.__feature_context_by_thread_uid[uid][1])
            if do_log and Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"[MultitaskManager.has_feature_context] Thread uid '{uid}' is in __feature_context_by_thread_uid and is_reference == {is_reference} => {res}")
            return res
        
        thread_context = self.__find_thread_context_having(ThreadContext.has_feature_context, uid, do_log=do_log)
        res = thread_context is not None
        if res and is_reference is not None:
            res &= (thread_context.thread_uid == uid)
        
        return res
    
    def get_feature_context(self):
        uid = self.get_thread_uid()
        self.__update_feature_context_for_thread_uid(uid)
        res = self.__feature_context_by_thread_uid[uid][0]
        if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Feature context for tread UID '{uid}': {res}")
        return res
    
    def set_feature_context(self, feature_context, is_reference=True):
        thread_context = self.get_thread_context()
        thread_context.set_feature_context(feature_context)
        
        self.__feature_context_by_thread_uid[thread_context.thread_uid] = (feature_context, is_reference)
        
        if Tools.do_log(logger, logging.DEBUG):
            tuname = thread_context.thread_unique_name
            tuname_txt = f"'{tuname}'" if isinstance(tuname, str) else f"{tuname}"
            tuid = thread_context.thread_uid
            logger.debug(f"Set feature context: thread unique name={tuname_txt} ; thread uid={tuid} ; feature context={feature_context} ; is reference={is_reference}")
    
    def delete_feature_context(self):
        tuname = self._get_thread_unique_name_or_uid()
        if tuname not in self.__thread_context_by_uname:
            raise TechnicalException(f"No thread context for thread unique name '{tuname}' (type: {Typing.get_object_class_fullname(tuname)})")
        
        # Remove any reference to feature context before delete it
        feature_context = self.__thread_context_by_uname[tuname].get_feature_context()
        if Tools.do_log(logger, logging.DEBUG):
            tuname_txt = f"'{tuname}'" if isinstance(tuname, str) else f"{tuname}"
            logger.debug(f"Deleting feature context: thread unique name={tuname_txt} ; feature context={feature_context}")
        self.__remove_feature_context_for_any_thread_uid(feature_context)
        
        # Delete feature context
        self.__thread_context_by_uname[tuname].delete_feature_context()
    
    
    
    