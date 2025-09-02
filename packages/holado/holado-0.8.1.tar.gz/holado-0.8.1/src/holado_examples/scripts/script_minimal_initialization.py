import holado


# Minimal HolAdo initialization for scripts
holado.initialize_for_script()

import logging
logging.print("After 'holado.initialize_for_script()', HolAdo is initialized minimally for scripts with:")
logging.print("  - add logging levels 'trace' and 'print'")
logging.print("  - do logs on console but not in file")
logging.print("  - a default session context is initialialized with all available HolAdo services")
logging.print("  - no session folder is created")


# Launch manually garbage collector periodically
from holado.common.tools.gc_manager import GcManager
from holado.common.handlers.undefined import default_value
GcManager.collect_periodically(collect_periodicity=default_value) 
logging.print("After 'GcManager.collect_periodically(collect_periodicity=default_value)', garbage collector is launched periodically (with default periodicity that is 10 s)")




