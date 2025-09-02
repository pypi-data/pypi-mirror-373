
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
import os
from holado_system.system.command.command import Command
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.path_manager import PathManager

logger = logging.getLogger(__name__)

class ProtobufCompiler(object):
    def __init__(self):
        self.__protoc_exe_path = "protoc"
        self.__proto_dest = []
        
        # If available, use protoc packaged in grpc_tools, in order to avoid a protoc installation and to use same protoc version than GRpcCompiler  
        from holado_grpc.ipc.rpc.grpc_compiler import GRpcCompiler
        if GRpcCompiler.is_available():
            self.__protoc_exe_path = "python -m grpc_tools.protoc"
    
    @property
    def protoc_exe_path(self):
        return self.__protoc_exe_path
    
    @protoc_exe_path.setter
    def protoc_exe_path(self, path):
        self.__protoc_exe_path = path
    
    def register_proto_path(self, proto_path, destination_path, file_path = None):
        """
        Register a triplet of {proto path, destination folder path, proto file path}.
        If file_path is None, all files/directories of proto_path are explored.
        """
        self.__proto_dest.append((proto_path, destination_path, file_path))
    
    def compile_all_proto(self):
        """Compile all registered proto recursively from proto paths to each associated destination folder paths."""
        for proto_path, destination_path, file_path in self.__proto_dest:
            if file_path is None:
                if os.path.isfile(proto_path):
                    proto_file_path = proto_path
                    proto_path = os.path.dirname(proto_file_path)
                    self.__compile_proto(proto_path, destination_path, proto_file_path)
                elif os.path.isdir(proto_path):
                    self.__compile_all_proto(proto_path, destination_path, proto_path)
                else:
                    raise TechnicalException(f"Unmanaged path '{proto_path}'")
            else:
                self.__compile_all_proto(proto_path, destination_path, file_path)
            
    def __compile_all_proto(self, proto_path, destination_path, current_proto_path, do_create_init_py=False):
        if os.path.isfile(current_proto_path):
            self.__compile_proto(proto_path, destination_path, current_proto_path)
        elif os.path.isdir(current_proto_path):
            lp = os.listdir(current_proto_path)
            for cp in lp:
                cur_proto_path = os.path.join(current_proto_path, cp)
                self.__compile_all_proto(proto_path, destination_path, cur_proto_path)
            if do_create_init_py:
                self.__create_init_py(proto_path, destination_path, current_proto_path)
        else:
            raise TechnicalException(f"Unmanaged path '{current_proto_path}'")
    
    def __create_init_py(self, proto_path, destination_path, proto_file_path):
        """Create __init__.py file in destination folder."""
        if not os.path.isdir(proto_file_path):
            raise TechnicalException(f"Proto path '{proto_file_path}' is not a directory")
        
        relative_proto_path = proto_file_path.replace(proto_path,'').strip('/')
        dest_proto_path = os.path.join(destination_path, relative_proto_path)
        init_path = os.path.join(dest_proto_path, '__init__.py')
        
        pm = PathManager()
        pm.makedirs(dest_proto_path, is_directory=True)
        
        open(init_path, "wt")
        
        logger.info(f"Created __init__.py in destination directory '{relative_proto_path}'")
    
    def __compile_proto(self, proto_path, destination_path, proto_file_path):
        """Compile proto file into destination folder path."""
        if not os.path.isfile(proto_file_path):
            raise TechnicalException(f"Proto path '{proto_file_path}' is not a file")
        
        ext = os.path.splitext(proto_file_path)[1]
        if ext != ".proto":
            return
        
        pm = PathManager()
        pm.makedirs(destination_path, is_directory=True)
        
        cmd = self._build_compile_proto_command(proto_path, destination_path, proto_file_path)
        command = Command(cmd, do_raise_on_stderr=True)
        command.start()
        command.join()
        
        if command.error is not None:
            raise FunctionalException(f"Error while compiling proto file '{proto_file_path}' from '{proto_path}' into '{destination_path}': {command.error}")
        logger.info(f"Compiled proto '{proto_file_path.replace(proto_path,'')}'")

    def _build_compile_proto_command(self, proto_path, destination_path, proto_file_path):
        if os.path.exists(self.protoc_exe_path) and " " in self.protoc_exe_path:
            return f'"{self.protoc_exe_path}" --proto_path="{proto_path}" --python_out="{destination_path}" "{proto_file_path}"'
        else:
            return f'{self.protoc_exe_path} --proto_path="{proto_path}" --python_out="{destination_path}" "{proto_file_path}"'
        