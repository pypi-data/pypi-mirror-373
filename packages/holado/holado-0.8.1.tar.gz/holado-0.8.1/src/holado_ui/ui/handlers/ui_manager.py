#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import queue
import logging
from holado.common.context.context import Context
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_ui.ui.drivers.ui_driver_info import UIDriverInfo
from holado_ui.ui.exceptions.focus_driver_exception import FocusDriverException
from holado_ui.ui.actors.actions import UIDriverAction, UIDriverCloser
from holado.common.context.session_context import SessionContext
from holado_ui.ui.gui.drivers.gui_driver import GUIDriver
from holado_ui_mss.ui.mss.mss_manager import MssManager
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class UIManager(Context):
    """ Class managing existing UIs (web browsers,...).
    The UI in top of stack is supposed active.
    """
    
    def __init__(self):
        super().__init__("UIManager")
        
        self.__focus_uid_stack = queue.LifoQueue()
        self.__driver_by_uid = {}
        
        self.__default_ui_lifetime_context = None
        self.__driver_initializers = []
        self.__driver_closers = []
        self.__default_driver_closer = None
        
        self.set_ui_lifetime_to_default()
        self.register_default_ui_driver_closer()
    
    def _delete_object(self):
        # Close all opened UIs
        self.close_uis()
        
        super()._delete_object()
    
    def has_focused_driver(self, uid=None):
        """
        @param uid Driver UID
        @return True if given driver (or any driver if uid is None) is registered in focus.
        """
        if uid is not None:
            return uid in self.__focus_uid_stack
        else:
            return not self.__focus_uid_stack.empty()
    
    def has_driver(self, uid):
        """
        @param uid Driver UID.
        @return True if driver of given UID is registered.
        """
        return uid in self.__driver_by_uid

    def get_driver_info(self, uid):
        """
        @param uid Driver UID
        @return UI driver info
        """
        if not self.has_driver(uid):
            raise TechnicalException(f"Driver '{uid}' is not registered")
        return self.__driver_by_uid[uid]
    
    def _get_driver_uids(self):
        return list(self.__driver_by_uid.keys())
    
    def _get_focused_driver_uids(self):
        return list(self.__focus_uid_stack.queue)

    @property
    def in_focus_driver(self):
        """
        @return Driver currently in focus.
        """
        self.verify_has_in_focus_driver()
        return self.in_focus_driver_info().driver

    @property
    def in_focus_driver_info(self):
        """
        @return Driver info of driver currently in focus.
        """
        return self.__driver_by_uid[self.__focus_uid_stack.queue[-1]]

    def pop_focused_driver(self, uid):
        """
        Unregister driver of given UID and return it.
        @param uid Driver UID.
        @return Driver instance.
        """
        return self.pop_focused_driver_info(uid).driver

    def pop_focused_driver_info(self, uid):
        """
        Unregister driver of given UID and return it as a driver info.
        @param uid Driver name.
        @return Driver info.
        """
        if Tools.do_log(logger, logging.DEBUG):
            msg_list = []
            msg_list.append(f"Popped driver '{uid}' (previous current: '{self.in_focus_driver_info().uid}'")
        
        # Search driver of given name
        if self.has_focused_driver(uid):
            res = self.get_driver_info(uid)
        else:
            raise FunctionalException(f"Driver '{uid}' is not registered in focus")

        # Remove it
        try:
            self.__focus_uid_stack.remove(uid)
        except Exception as exc:
            raise TechnicalException(f"Unable to remove driver '{uid}'") from exc

        if Tools.do_log(logger, logging.DEBUG):
            msg_list.append(f" ; new current: {self.in_focus_driver_info().uid if self.has_focused_driver() else 'None'})")
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("".join(msg_list))
        
        return res

    def pop_in_focus_driver(self):
        """
        Unregister driver currently in focus and return it.
        @return Driver instance.
        """
        return self.pop_in_focus_driver_info().driver

    def pop_in_focus_driver_info(self):
        """
        Unregister driver currently in focus and return it as a driver info.
        @return Driver info
        """
        if Tools.do_log(logger, logging.DEBUG):
            msg_list = []
            msg_list.append(f"Popped current driver (popped: '{self.in_focus_driver_info().uid}'")
        
        res = self.__driver_by_uid[self.__focus_uid_stack.pop()]

        if Tools.do_log(logger, logging.DEBUG):
            msg_list.append(f" ; new current: {self.in_focus_driver_info().uid if self.has_focused_driver() else 'None'})")
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("".join(msg_list))
        
        return res

    def push_driver(self, uid, driver, is_hidden):
        """
        Register a new driver and set it in focus if not hidden.
        @param uid Driver UID.
        @param driver Driver instance.
        @param is_hidden If true, driver is considered hidden and is not added in focused drivers
        """
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Pushing{' hidden' if is_hidden else ''} driver '{uid}' (current driver: {self.in_focus_driver_info().uid if self.has_focused_driver() else 'None'})")
        
        self.__driver_by_uid[uid] = UIDriverInfo(uid, driver, is_hidden)
        if not is_hidden:
            self.__focus_uid_stack.put(uid)
        
        self.set_object(uid, driver, self.__default_ui_lifetime_context)

    def repush_driver_in_focus(self, uid):
        """
        Repush driver of given UID in focus
        @param uid Driver UID
        """
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Repushing driver '{uid}' (current driver: {self.in_focus_driver_info().uid if self.has_focused_driver() else 'None'})")
        
        # Search driver of given name
        if not self.has_driver(uid):
            raise FunctionalException(f"Driver '{uid}' does not exist")
        driver_info = self.get_driver_info(uid)
        if driver_info.is_hidden:
            raise FunctionalException(f"Driver '{uid}' is hidden")

        # Remove it
        try:
            self.__focus_uid_stack.remove(uid)
        except Exception as exc:
            raise TechnicalException(f"Unable to remove driver '{uid}' before repushing it") from exc
        
        # Repush it
        self.__focus_uid_stack.put(uid)
        
    def switch_to_driver(self, uid):
        """
        Set focus on driver of given UID
        @param uid UID of already opened driver
        """
        # Repush driver
        self.repush_driver_in_focus(uid)

    
    def check_driver_is_in_focus(self, uid):
        """
        @param uid Drive UID
        @return True if driver of given UID is currently in focus
        """
        if self.has_focused_driver():
            return (self.in_focus_driver_info().uid == uid)
        else:
            return False
    
    def verify_driver_is_in_focus(self, uid):
        """
        If driver currently in focus is not of given UID, raise an exception.
        @param uid Driver UID
        """
        self.verify_has_in_focus_driver()
        if not self.check_driver_is_in_focus(uid):
            raise FocusDriverException(f"Driver '{uid}' is not in focus, it is driver '{self.in_focus_driver_info().uid}' (focused drivers: {self._represent_focused_driver_uids()})")
    
    def verify_has_in_focus_driver(self):
        """
        Raise an exception if no driver is currently registered.
        """
        if not self.has_focused_driver():
            raise FunctionalException("No driver is currently registered in focus")
    
    def register_ui_driver_initializer(self, driver_initializer:UIDriverAction):
        """
        Register a new UI driver initializer
        @param driver_initializer Driver initializer
        """
        self.__driver_initializers.append(driver_initializer)
    
    def initialize_ui_driver(self, uid, driver):
        """
        Apply all registered UI driver initializer
        @param uid Driver UID
        @param driver UI driver to initialize
        """
        for initializer in self.__driver_initializers:
            try:
                initializer.execute(uid)
            except Exception as exc:
                logger.error(f"Unable to initialize driver '{uid}' with initializer '{initializer.name}': {str(exc)}")
        
    def register_default_ui_driver_closer(self, driver_closer:UIDriverCloser=None):
        """
        Register default UI driver closer
        @param driver_closer Driver closer implementation
        """
        if driver_closer is None:
            driver_closer = UIDriverCloser("default", self)
        self.__default_driver_closer = driver_closer
    
    def register_ui_driver_closer(self, driver_closer:UIDriverCloser):
        """
        Register a new UI driver closer
        @param driver_closer Driver closer implementation
        """
        self.__driver_closers.append(driver_closer)
    
    def set_ui_lifetime_to_default(self):
        """
        Set UI lifetime to default context
        """
        self.set_ui_lifetime_to("Session")
    
    def set_ui_lifetime_to(self, lifetime_context):
        """
        Set default UI lifetime to given context
        @param lifetime_context Lifetime context
        """
        # Store context for UI created later
        self.__default_ui_lifetime_context = lifetime_context
        
        # Update lifetime of currently created UIs
        for uid in self._get_driver_uids():
            self.set_driver_lifetime_to(lifetime_context, uid)
    
    def set_driver_lifetime_to(self, lifetime_context, uid):
        """
        Set driver lifetime to given context
        @param lifetime_context Lifetime context
        @param uid Driver UID
        """
        if self.has_driver(uid):
            SessionContext.instance().lifetime_manager.update_object_lifetime(uid, self, lifetime_context)
        else:
            raise TechnicalException(f"No driver '{uid}' is registered")
    
    def close_uis(self):
        """
        Close all UIs
        """
        logger.info("Closing all UIs...")
        
        # Close other drivers
        for uid in self._get_driver_uids():
            self.close_driver(uid)
    
    def close_uis(self, lifetime_context):
        """
        Close UIs with lifetime of given context
        @param lifetime_context Lifetime context
        """
        logger.info(f"Closing UIs at {lifetime_context} context end...")
        
        # Close other drivers
        for uid in self._get_driver_uids():
            self.close_driver(lifetime_context, uid)
    
        logger.info(f"Finished closing UIs at {lifetime_context} context end.")
    
    def close_driver(self, uid, lifetime_context=None):
        """
        Close driver of given UID
        @param uid Driver UID
        @param lifetime_context Lifetime context
        @return True if a driver was closed
        """
        res = False
        
        if self.has_driver(uid):
            if lifetime_context is not None:
                driver_lifetime = SessionContext.instance().lifetime_manager.get_object_lifetime(uid, self)
                if driver_lifetime is not None and driver_lifetime == lifetime_context:
                    logger.info(f"Closing driver '{uid}' at {lifetime_context} context end")
                else:
                    return False
            else:
                logger.info(f"Closing driver '{uid}'")

            # Apply registered drivers
            for closer in self.__driver_closers:
                try:
                    res = closer.execute(uid)
                except Exception as exc:
                    logger.error(f"Unable to close driver '{uid}' with closer '{closer.name}': {str(exc)}")
                
                if res:
                    break
            
            # Else apply default closer
            if not res:
                self.__default_driver_closer.execute(uid)
        
        return res
    
    def make_screenshots_for_debug(self, destination_path, context_description):
        """
        Make screenshots for debug (monitors, current UI in focus).
        @param destination_path Destination path
        @param context_description Context description that will be inserted in file names
        """
        # Monitors
        MssManager.make_monitors_screenshots(destination_path, context_description)
        # PyAutoGUIManager.make_monitors_screenshots(destination_path, context_description)
        
        # Current UI in focus
        if self.has_focused_driver():
            driver = self.in_focus_driver()
            if isinstance(driver, GUIDriver):
                driver.make_screenshots_for_debug(destination_path, context_description)
    

    def _representDriverUIDs(self):
        return f"[{', '.join(self._get_driver_uids())}]"

    def _represent_focused_driver_uids(self):
        return f"[{', '.join(self._get_focused_driver_uids())}]"

    def _remove(self, name, remove_from_lifetime_manager):
        if self.has_focused_driver(name):
            self.pop_focused_driver_info(name)
        if self.has_driver(name):
            del self.__driver_by_uid[name]
        
        super.remove(name, remove_from_lifetime_manager)
    
    
    
    
    