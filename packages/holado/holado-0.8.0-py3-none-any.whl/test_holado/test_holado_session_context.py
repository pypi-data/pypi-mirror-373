from builtins import super
from holado.common.context.session_context import SessionContext
import os
import logging

logger = logging.getLogger(__name__)


class TestHoladoSessionContext(SessionContext):
    
    def __init__(self):
        super().__init__("TestHoladoSessionContext")
    
    def configure(self, session_kwargs=None):
        logger.info("Configuring TestHoladoSessionContext")
        
        super().configure(session_kwargs)
        
        # Override default registered modules
        pass
        
        # Register new modules
        pass
    
    
    def initialize(self, session_kwargs=None):
        if session_kwargs is None:
            session_kwargs = {}
        raise_if_not_exist = session_kwargs.get("raise_if_not_exist", True)
        do_import = session_kwargs.get("import_compiled_proto", True)
        
        # Call default initialization
        super().initialize(session_kwargs)
        
        # Import compiled Protobuf and gRPC packages
        if do_import:
            here = os.path.abspath(os.path.dirname(__file__))
            proto_gene_path = os.path.join(here, "resources", "proto", "generated")
            
            SessionContext.instance().protobuf_messages.import_all_compiled_proto(os.path.join(proto_gene_path, "protobuf"), raise_if_not_exist=raise_if_not_exist)
        
        
        
