import holado


# Initialize HolAdo with default behaviours and custom parameters

holado.initialize_for_script(log_on_console=True, log_in_file=True)

import logging
logging.print("After 'holado.initialize_for_script(log_on_console=True, log_in_file=True)', HolAdo is initialized for scripts with:")
logging.print("  - add logging levels 'trace' and 'print'")
logging.print("  - do logs on console and in file")
logging.print("  - a default session context is initialialized with all available HolAdo services")
logging.print("  - a session folder is created that will contains at least log files")
logging.print("  - launch garbage collector periodically (without specifying garbage_collector_periodicity, default periodicity is 10 s)")


