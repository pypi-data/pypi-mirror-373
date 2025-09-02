
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


#################################################
# GOAL: Tools when using a clone of HolAdo project.
#
# This file contains methods usefull to initialize environments using a clone of HolAdo project.
#
# USAGE: 
#   - Copy this file in projects using HolAdo.
#   - Define environment variable HOLADO_PATH with path to cloned HolAdo project.
#     If HOLADO_PATH is defined, sources of cloned HolAdo project are used, else installed holado package is used.
#################################################



import os
import sys


def insert_sys_path(path, index=0):
    """Insert a path in sys.path if it doesn't already exists.
    """
    if path not in sys.path:
        sys.path.insert(index, path)

def insert_holado_source_paths(with_test_behave=True):
    """Insert in sys.path all HolAdo source paths.
    If environment variable HOLADO_PATH is defined with path to HolAdo project, following paths are inserted in sys.path:
        - HOLADO_PATH/src: path to holado modules sources
        - HOLADO_PATH/tests/behave (if with_test_behave==True): path to holado test sources, needed by testing solutions
    """
    holado_path = os.getenv('HOLADO_PATH')
    if holado_path is None:
        try:
            import holado  # @UnusedImport
        except Exception as exc:
            if "No module named" in str(exc):
                raise Exception(f"If environment variable HOLADO_PATH is not defined with path to HolAdo project, 'holado' python package must be installed")
            else:
                raise exc
        else:
            # holado is installed, and all sources are already accessible
            pass
    else:
        print(f"Using HolAdo project installed in '{holado_path}'")
        insert_sys_path(os.path.join(holado_path, "src"))
        if with_test_behave:
            insert_sys_path(os.path.join(holado_path, "tests", "behave"))
    

