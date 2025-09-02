#TODO: change use of this module by holado_helper.initialize_holado


import os
import sys


def insert_holado_helper_script():
    # Insert path to holado_helper
    holado_path = os.getenv('HOLADO_PATH')
    if holado_path is None:
        # If HolAdo sources are not cloned on this environment, use path within this installation
        from holado import get_holado_path
        holado_path = get_holado_path()
    sys.path.insert(0, os.path.join(holado_path, "src", "holado_helper", "script") )
    

