import os
import sys
import shutil

here = os.path.abspath(os.path.dirname(__file__))

test_path = os.path.join(here, "..", "..")
holado_path = os.path.join(test_path, "..", "..", "..")
holado_src_path = os.path.normpath(os.path.join(holado_path, "src"))
sys.path.insert(0, holado_src_path)
print(f"Inserted path: {holado_src_path}")

from holado_core.common.tools.path_manager import PathManager
from holado_protobuf.ipc.protobuf.protobuf_compiler import ProtobufCompiler
from holado_grpc.ipc.rpc.grpc_compiler import GRpcCompiler

def compile_protobuf_proto(remove_destination=True):
    # Define protoc path
#    protoc_exe_path = os.path.join(holado_path, "dependencies", "protoc", "protoc-3.17.3-linux-x86_64", "bin", "protoc")
    # protoc_exe_path = os.path.join(holado_path, "dependencies", "protoc", "protoc-21.5-linux-x86_64", "bin", "protoc")
    # protoc_exe_path = os.path.join(holado_path, "dependencies", "protoc", "protoc-21.12-linux-x86_64", "bin", "protoc")
    protoc_exe_path = os.path.join(holado_path, "dependencies", "protoc", "protoc-23.4-linux-x86_64", "bin", "protoc")
    
    # Define protobuf folder
    resources_proto_path = os.path.normpath(os.path.join(test_path, "resources", "proto"))
    
    # Define proto and generated paths
    proto_path = os.path.join(resources_proto_path, "definitions")
    destination_path = os.path.join(resources_proto_path, "generated")
    
    # Remove existing destination
    if remove_destination and os.path.exists(destination_path) and os.path.isdir(destination_path):
        shutil.rmtree(destination_path)
    
    protoc = ProtobufCompiler()
    protoc.protoc_exe_path = protoc_exe_path
    
    protoc.register_proto_path(os.path.join(proto_path, "protobuf"), os.path.join(destination_path, "protobuf"), os.path.join(proto_path, "protobuf", "protobuf.dev"))
    protoc.register_proto_path(os.path.join(proto_path, "protobuf"), os.path.join(destination_path, "protobuf"), os.path.join(proto_path, "protobuf", "custom_types"))
    
    protoc.compile_all_proto()

def compile_grpc_proto(remove_destination=True):
    # Define protobuf folder
    api_grpc_path = os.path.normpath(os.path.join(test_path, "tools", "django", "api_grpc", "api_grpc", "api1"))
    
    # Define proto and generated paths
    proto_path = os.path.join(api_grpc_path, "proto")
    destination_path = os.path.join(api_grpc_path, "proto")
    
    # Remove existing destination
    if remove_destination and os.path.exists(destination_path) and os.path.isdir(destination_path):
        if destination_path != proto_path:
            shutil.rmtree(destination_path)
        else:
            path_manager = PathManager()
            glob_pattern = os.path.join(destination_path, "*.py")
            path_manager.remove_paths(glob_pattern)
    
    protoc = GRpcCompiler()
    
    protoc.register_proto_path(proto_path, destination_path)
    
    protoc.compile_all_proto()

if __name__ == "__main__":
    compile_protobuf_proto()
    compile_grpc_proto(remove_destination=False)
    
    
