from builtins import super
from holado.common.context.session_context import SessionContext
import logging

logger = logging.getLogger(__name__)


class TSSessionContext(SessionContext):
    
    def __init__(self):
        super().__init__("TSSession")
        
    def configure(self, session_kwargs=None):
        logger.info("Configuring TSSessionContext")
        
        super().configure(session_kwargs)
        
        # Override default registered modules
         
        from common.tools.path_manager import TSPathManager
        self.services.register_service_type("path_manager", TSPathManager,
                            lambda m: m.initialize(),
                            raise_if_exist=False )
        
        
        # Register new modules
        
        from config.config_manager import TSConfigManager
        self.services.register_service_type("config_manager", TSConfigManager,
                            lambda m: m.initialize(lambda: self.path_manager) )
        
        
    def initialize(self, session_kwargs=None):
        if session_kwargs is None:
            session_kwargs = {}
        raise_if_not_exist = session_kwargs.get("raise_if_not_exist", True)
        
        # Call default initialization
        super().initialize(session_kwargs)
        
        # Initialize testing solution
        
        
        
        
