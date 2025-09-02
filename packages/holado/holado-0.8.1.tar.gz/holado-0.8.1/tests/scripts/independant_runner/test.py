import sys
import logging
import os
import argparse

logger = None



def __insert_sys_paths():
    # Insert path to folder containing initialize_script
    here = os.path.abspath(os.path.dirname(__file__))
    scripts_path = os.path.abspath(os.path.join(here, ".."))
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    
    from script_tools import insert_holado_helper  # @UnresolvedImport
    insert_holado_helper()
    
    
def __main(args, cwd):
    from holado.common.context.session_context import SessionContext
    from holado_test.behave.behave import execute_steps

    here = os.path.abspath(os.path.dirname(__file__))
    step_path = os.path.join(here, "steps")
    step_paths = [step_path]

    SessionContext.instance().behave_manager.use_independant_runner(step_paths)

    execute_steps("""
        Given DATE = datetime now
        """)
    
    
def _parse_arguments():
    descr = """Independant runner
    """
    
    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-ll', '--log-level', choices=['ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'], dest='log_level', default='WARNING',
                   help='Log level')
    
    parser.add_argument('-lf', '--log-in-file', dest='log_in_file', default=False, action="store_true",
                   help='If specified, log in file rather than console')
    
    res = parser.parse_args()
    
    return res


if __name__ == "__main__":
    __insert_sys_paths()
    from holado_helper.script.initialize_script import initialize  # @UnresolvedImport
    
    script_path = os.path.abspath(os.path.dirname(__file__))
    
    args = _parse_arguments()
    
    # Initialize HolAdo framework
    cwd = initialize(args.log_level, script_path, log_in_file=args.log_in_file)
    
    from holado_core.common.exceptions.functional_exception import FunctionalException
    
    try:
        __main(args, cwd)
    except FunctionalException as exc:
        logging.error(f"Action is interrupted on error: {exc}")
        sys.exit(1)
    except SystemExit as exc:
        raise exc
    except:
        logging.exception("An error occured")
        sys.exit(1)
    
    sys.exit(0)
    
