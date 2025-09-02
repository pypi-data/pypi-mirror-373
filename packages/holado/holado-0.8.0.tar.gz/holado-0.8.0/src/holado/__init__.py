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


import os
import importlib
import logging
import copy
from holado.common.handlers.undefined import default_value
from holado.common.tools.gc_manager import GcManager

try:
    import behave
    with_behave = True
except:
    with_behave = False

logger = None
__initialized = False

def __initialize_holado_loggers():
    global logger
    logger = logging.getLogger(__name__)
    
    import holado.common
    holado.common.initialize_loggers()
    
    
    
def _initialize_logging(use_holado_logger=True, logging_config_file_path=None, log_level=None, log_on_console=False, log_in_file=True):
    # print_imported_modules("[initialize]")
    import holado_logging
    # print_imported_modules("[after import holado_logging]")

    # Configure logging module
    holado_logging.configure(use_holado_logger=use_holado_logger, logging_config_file_path=logging_config_file_path, log_level=log_level, log_on_console=log_on_console, log_in_file=log_in_file)
    # print_imported_modules("[after import holado_logging]")

    # Initialize holado loggers
    __initialize_holado_loggers()
    
    # Create session context
    from holado.common.context.session_context import SessionContext
    if SessionContext.has_instance():
        from holado_core.common.exceptions.technical_exception import TechnicalException
        raise TechnicalException(f"Session context was initialized to early (before logging configuration)")
    SessionContext.instance()
    
    # Initialize log manager and register it in session context
    holado_logging.initialize_and_register()
    
    # Set whole logging configuration
    SessionContext.instance().log_manager.set_config()
    
def change_logging_config(log_level=None, log_on_console=False, log_in_file=True):
    from holado.common.context.session_context import SessionContext
    SessionContext.instance().log_manager.set_level(log_level, do_set_config=False)
    SessionContext.instance().log_manager.on_console = log_on_console
    SessionContext.instance().log_manager.in_file = log_in_file
    SessionContext.instance().log_manager.set_config()


def initialize_minimal():
    # initialize(TSessionContext=None, use_holado_logger=False, logging_config_file_path=None,
    #            log_level=None, log_on_console=True, log_in_file=False,
    #            session_kwargs={'with_session_path':False}, 
    #            garbage_collector_periodicity=None)
    initialize(TSessionContext=None, use_holado_logger=True, logging_config_file_path=None,
               log_level=None, log_on_console=True, log_in_file=False,
               garbage_collector_periodicity=None)

def initialize(TSessionContext=None, use_holado_logger=True, logging_config_file_path=None, 
               log_level=None, log_on_console=False, log_in_file=True, session_kwargs=None,
               garbage_collector_periodicity=default_value):
    global __initialized
    if __initialized:
        from holado_core.common.exceptions.technical_exception import TechnicalException
        raise TechnicalException(f"HolAdo was already initialized")
    
    from holado_core.common.tools.tools import Tools
    
    if session_kwargs is None:
        session_kwargs = {}
    with_session_path = session_kwargs.get("with_session_path", True)
    
    # Reset session context before initializing logging
    # Note: Session context must not be created before logging initialization
    from holado.common.context.session_context import SessionContext
    SessionContext._reset_instance()
    if TSessionContext is not None:
        if isinstance(TSessionContext, str):
            module_name, class_type = TSessionContext.rsplit('.', maxsplit=1)
            module = importlib.import_module(module_name)
            TSessionContext = getattr(module, class_type)
        
        SessionContext.TSessionContext = TSessionContext
    
    # Initialize logging
    _initialize_logging(use_holado_logger=use_holado_logger, logging_config_file_path=logging_config_file_path,
                        log_level=log_level, log_on_console=log_on_console, log_in_file=log_in_file and with_session_path)
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug("Configured logging")
    
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug("Importing HolAdo modules")
    _import_modules(get_holado_module_names())
    
    _initialize_session_context(session_kwargs)
    
    # Initialize garbage collector
    if garbage_collector_periodicity is not None:
        GcManager.collect_periodically(garbage_collector_periodicity)
        logger.debug(f"Garbage collector is disabled, and collects are automatically done in a dedicated thread (periodicity: {GcManager.get_collect_periodicity()} s)")
    
    if with_behave:
        # Register default behave parameter types
        #TODO: make step tools a service
        from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
        BehaveStepTools.register_default_types()
    
    __initialized = True
    
def initialize_for_script(TSessionContext=None, use_holado_logger=True, logging_config_file_path=None, 
                          log_level=logging.WARNING, log_on_console=True, log_in_file=False, session_kwargs=None,
                          garbage_collector_periodicity=None):
    if session_kwargs is None:
        session_kwargs={'with_session_path':log_in_file, 'raise_if_not_exist':False}
        
    initialize(TSessionContext=TSessionContext, use_holado_logger=use_holado_logger, logging_config_file_path=logging_config_file_path, 
               log_level=log_level, log_on_console=log_on_console, log_in_file=log_in_file,
               session_kwargs=session_kwargs,
               garbage_collector_periodicity=garbage_collector_periodicity )
    
    
def _initialize_session_context(session_kwargs=None):
    from holado_core.common.tools.tools import Tools
    
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug("Initializing SessionContext")
    from holado.common.context.session_context import SessionContext
    
    SessionContext.instance().configure(session_kwargs)
    SessionContext.instance().new_session(session_kwargs)
    SessionContext.instance().initialize(session_kwargs)
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug("Initialized SessionContext")
    
def _is_in_holado_package(here=None):
    if here is None:
        here = os.path.abspath(os.path.dirname(__file__))
    return 'site-packages' in here
    
def get_holado_path():
    here = os.path.abspath(os.path.dirname(__file__))
    if _is_in_holado_package(here):
        from holado_core.common.exceptions.technical_exception import TechnicalException
        raise TechnicalException(f"When using installed 'holado' package, the project HolAdo is not available")
    else:
        return os.path.normpath(os.path.join(here, "..", ".."))
    
def get_holado_src_path():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.normpath(os.path.join(here, ".."))
    
def get_holado_module_names():
    lp = sorted(os.listdir(get_holado_src_path()))
    return [name for name in lp if name.startswith("holado_") and name not in ['holado_logging']]

def _import_modules(module_names):
    from holado_core.common.tools.tools import Tools
    
    imported_modules = __import_modules(module_names)
    remaining_imported_modules = __register_modules_with_dependencies(imported_modules)
    
    # Register modules with cross dependencies
    if remaining_imported_modules:
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Registering modules with cross dependencies: {list(remaining_imported_modules.keys())}...")
        for module_name in remaining_imported_modules:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Registering HolAdo module '{module_name}'...")
            remaining_imported_modules[module_name].register()
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Registered HolAdo module '{module_name}'")

def __import_modules(module_names):
    from holado_core.common.tools.tools import Tools
    
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Importing HolAdo modules: {module_names}")
    
    res = {}
    for module_name in module_names:
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Importing HolAdo module '{module_name}'...")
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Failed to import HolAdo module '{module_name}':\n{Tools.represent_exception(exc)}")
            if "No module named" not in str(exc):
                logger.warning(f"Failed to import HolAdo module '{module_name}': {str(exc)} (see debug logs for more details)")
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Imported HolAdo module '{module_name}'")
            res[module_name] = module
    return res
    
def __register_modules_with_dependencies(imported_modules):
    from holado_core.common.tools.tools import Tools
    
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Registering imported HolAdo modules: {sorted(imported_modules.keys())}")
    
    registered_modules = set()
    remaining_imported_modules = copy.copy(imported_modules)
    has_new_registered = True
    while has_new_registered:
        has_new_registered = False
        imported_module_names = list(remaining_imported_modules.keys())
        for module_name in imported_module_names:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Registering HolAdo module '{module_name}'...")
            module = remaining_imported_modules[module_name]
            module_dependencies = set(module.dependencies()) if hasattr(module, 'dependencies') and module.dependencies() is not None else None
            if module_dependencies is None or registered_modules.issuperset(module_dependencies):
                if hasattr(module, 'register'):
                    module.register()
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"Registered HolAdo module '{module_name}'")
                else:
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"Nothing to register for HolAdo module '{module_name}'")
                del remaining_imported_modules[module_name]
                registered_modules.add(module_name)
                has_new_registered = True
            else:
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"Pending registration of HolAdo module '{module_name}' due to dependencies: {module_dependencies.difference(registered_modules)}")
    return remaining_imported_modules
    
def import_steps():
    from holado_core.common.exceptions.technical_exception import TechnicalException
    from holado_core.common.tools.tools import Tools
    
    lp = sorted(os.listdir(get_holado_src_path()))
    for module_name in lp:
        if module_name.startswith("holado_"):
            if with_behave:
                module_steps_package = f"{module_name}.tests.behave.steps"
            else:
                raise TechnicalException(f"'behave' is needed for steps")
            try:
                importlib.import_module(module_steps_package)
            except Exception as exc:
                if "No module named" in str(exc):
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"No steps in HolAdo module '{module_name}'")
                    # logger.warning(f"No steps in HolAdo module '{module_name}'")
                else:
                    raise TechnicalException(f"Failed to import steps of HolAdo module '{module_name}'") from exc
            else:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Imported steps of HolAdo module '{module_name}'")
            
def import_private_steps():
    from holado_core.common.tools.tools import Tools
    
    lp = sorted(os.listdir(get_holado_src_path()))
    for module_name in lp:
        if module_name.startswith("holado_"):
            if with_behave:
                module_steps_package = f"{module_name}.tests.behave.steps.private"
            else:
                from holado_core.common.exceptions.technical_exception import TechnicalException
                raise TechnicalException(f"'behave' is needed for steps")
            try:
                importlib.import_module(module_steps_package)
            except:
                pass
            else:
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Imported private steps of HolAdo module '{module_name}'")
            
def print_imported_modules(prefix):
    import sys
    import types

    sys_modules = [v.__name__ for _,v in sys.modules.items() if isinstance(v, types.ModuleType)]
    print(f"{prefix} sys modules: {sys_modules}")
    
    # globals_modules = [v.__name__ for _,v in globals().items() if isinstance(v, types.ModuleType)]
    # print(f"{prefix} globals modules: {globals_modules}")
    
    

# Process minimal initialization of HolAdo
# Note: Currently, initialization can be done only once, thus minimal initialization is commented.
#       As a consequence, the call of an initialize method is mandatory
# initialize_minimal()


