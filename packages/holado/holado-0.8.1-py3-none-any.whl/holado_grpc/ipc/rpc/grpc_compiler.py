
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

from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado_protobuf.ipc.protobuf.protobuf_compiler import ProtobufCompiler
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)

try:
    import grpc_tools  # @UnusedImport
    with_grpc_tools = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"GRpcCompiler is not available. Initialization failed on error: {exc}")
    with_grpc_tools = False

class GRpcCompiler(ProtobufCompiler):
    @classmethod
    def is_available(cls):
        return with_grpc_tools
    
    def __init__(self): 
        super().__init__()
        ProtobufCompiler.protoc_exe_path.fset(self, "python -m grpc_tools.protoc")  # @UndefinedVariable
    
    @ProtobufCompiler.protoc_exe_path.setter  # @UndefinedVariable
    def protoc_exe_path(self, path):
        raise TechnicalException("An internal compiler is used for gRPC")
        
    def _build_compile_proto_command(self, proto_path, destination_path, proto_file_path):
        return f'{self.protoc_exe_path} --proto_path="{proto_path}" --python_out="{destination_path}" --grpc_python_out="{destination_path}" "{proto_file_path}"'
    
        