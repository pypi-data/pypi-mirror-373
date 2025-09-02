import os
import sys
import argparse
import logging

here = os.path.abspath(os.path.dirname(__file__))

holado_path = os.path.join(here, "..", "..")
sys.path.insert(0, os.path.join(holado_path, "src"))

from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_report.report.analyze.execution_historic_manager import ExecutionHistoricManager
from holado_core.common.tools.tools import Tools


def print_execution_historic(args):
    if not os.path.exists(args.report_path):
        raise FunctionalException(f"Report path '{args.report_path}' doesn't exist")
    
    ehm = ExecutionHistoricManager(args.report_path)
    
    with_feature_data = len(args.feature_data_names) > 0 if args.feature_data_names else False
    with_scenario_data = len(args.scenario_data_names) > 0 if args.scenario_data_names else False
    scenario_indent = 8 if with_feature_data else 0
    
    for feat_index, feature_eh in enumerate(ehm.report_execution_historic):
        if args.feature_number > 0 and args.feature_number != feat_index + 1:
            continue
        
        if with_feature_data:
            feature_data = ehm.extract_execution_historic_data(feature_eh, args.feature_data_names)
            logging.info(f"Feature {feat_index+1}:")
            for data in feature_data:
                logging.info(f"    {data[0]}: {data[1]}")
            if with_scenario_data:
                logging.info(f"    Scenarios:")
                
        if with_scenario_data:
            for scen_index, scenario_eh in enumerate(feature_eh["scenarios"]):
                if args.scenario_number > 0 and args.scenario_number != scen_index + 1:
                    continue
                
                scenario_data = ehm.extract_execution_historic_data(scenario_eh, args.scenario_data_names)
                logging.info(Tools.indent_string(scenario_indent, f"Scenario {feat_index+1}.{scen_index+1}:"))
                for data in scenario_data:
                    logging.info(Tools.indent_string(scenario_indent, f"    {data[0]}: {data[1]}"))
                
    logging.info(f"Finished")
    
def parse_arguments(descr=None):
    # Arguments
    if descr is None:
        descr = """Display information on scenarios executed in a campaign.
        It extracted from execution_historic.json files.
        It needs as input the folder of a campaign, and it will explore all execution_historic.json files of each scenario, in order of execution.
              
        Example 1: Display feature durations
                
                python print_execution_historic.py -r {path_to_report} -f feature.name -f feature.duration
                
        Example 1: Display scenario durations of feature n°12
                
                python print_execution_historic.py -r {path_to_report} -fn 12 -f feature.name -f feature.filename -s scenario.name -s scenario.line -s scenario.duration
                
        """
    
            
    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-r', '--report-path', dest='report_path',
                   help='Path to the test report folder.')
    
    parser.add_argument('-rd', '--report-dirname', dest='report_dirname',
                   help='Directory name of the test report folder.')
    
    parser.add_argument('-fn', '--feature-number', dest='feature_number', type=int, default=-1,
                   help="Number of the feature to print.")
    
    parser.add_argument('-sn', '--scenario-number', dest='scenario_number', type=int, default=-1,
                   help="Number of the scenario to print.")
    
    parser.add_argument('-f', '--feature-data', dest='feature_data_names', action='append',
                   help="Fullnames of a feature data to print.")
    
    parser.add_argument('-s', '--scenario-data', dest='scenario_data_names', action='append',
                   help="Fullnames of a scenario data to print.")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    logging.basicConfig(format = '{asctime:s} | {thread:-5d} | {levelname:5s} | {module:35s} | {message:s}', style = '{', level=logging.INFO, handlers=[logging.StreamHandler()])
    
    # Execute
    try:
        print_execution_historic(args)
    except FunctionalException as exc:
        logging.error(f"Update is interrupted on error: {exc}")
        sys.exit(1)
    except:
        logging.exception("An error occured")
        sys.exit(1)

    sys.exit(0)
    
