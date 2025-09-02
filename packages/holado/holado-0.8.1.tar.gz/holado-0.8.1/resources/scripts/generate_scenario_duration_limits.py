import os
import sys
import argparse
import logging

here = os.path.abspath(os.path.dirname(__file__))

holado_path = os.path.join(here, "..", "..")
sys.path.insert(0, os.path.join(holado_path, "src"))


from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_report.report.analyze.scenario_duration_manager import ScenarioDurationManager

def __main(args):
    if not os.path.exists(args.report_path):
        raise FunctionalException(f"Report path '{args.report_path}' doesn't exist")
    eh_path = os.path.join(args.report_path, "execution_historic.json")
    if not os.path.exists(eh_path):
        raise FunctionalException(f"Report path '{args.report_path}' doesn't contain an 'execution_historic.json' file")
    
    output_path = args.output_path
    if output_path is None:
        output_path = os.path.join(args.report_path, "scenario_duration_limits.csv")
        
    sdm = ScenarioDurationManager()
    sdm.import_execution_historic(eh_path)
    
    scenario_duration_limits = sdm.compute_scenario_duration_limits()
    sdm.create_file_scenario_duration_limits(output_path, scenario_duration_limits)
    
    logging.info(f"Finished")
    

if __name__ == "__main__":
    # Arguments
    descr = """Generate file with statistics on scenario duration.
    It needs as input the folder of the test report for which generating statistics.

    Example 1: Generate file with default duration limits
               
            python generate_scenario_duration_limits.py -r {path_to_report}
            
    Example 2: Generate file with default duration limits and specific output filename
    
            python generate_scenario_duration_limits.py -r {path_to_report} -o {path_to_report}/scenario_duration_limits.csv
            
        Note: With this "-o" parameter, it is equivalent to Example 1.
    """
    
            
    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-r', '--report', dest='report_path', required=True,
                   help='Path to the test report folder.')
    
    parser.add_argument('-o', '--output', dest='output_path', default=None,
                   help='Path to the output file. If not defined, a new file will be generated in report folder')

    args = parser.parse_args()

    logging.basicConfig(format = '{asctime:s} | {thread:-5d} | {levelname:5s} | {module:35s} | {message:s}', style = '{', level=logging.DEBUG, handlers=[logging.StreamHandler()])
    
    # Execute
    try:
        __main(args)
    except:
        logging.exception("An error occured")
        sys.exit(1)

    sys.exit(0)
    
    