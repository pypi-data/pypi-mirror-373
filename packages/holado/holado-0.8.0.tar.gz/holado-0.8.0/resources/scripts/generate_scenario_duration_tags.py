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
        output_path = os.path.join(args.report_path, "scenario_duration_tags.csv")
        
    sdm = ScenarioDurationManager()
    sdm.import_execution_historic(eh_path)
    
    if args.all_scenarios:
        scenario_duration_tags = sdm.compute_scenario_duration_tags(
            duration_limit_tags = args.duration_tags, 
            default_tag = args.default_tag, 
            tag_prefix = args.tag_prefix, 
            missing_tag = True, 
            new_tag = True, 
            unchanged_tag = True, 
            with_failed = True,
            add_apply = args.add_apply_column)
    else:
        scenario_duration_tags = sdm.compute_scenario_duration_tags(
            duration_limit_tags = args.duration_tags, 
            default_tag = args.default_tag, 
            tag_prefix = args.tag_prefix,
            add_apply = args.add_apply_column)
    
    sdm.create_file_scenario_duration_tags(output_path, scenario_duration_tags)
    
    logging.info(f"Finished")
    

if __name__ == "__main__":
    # Arguments
    descr = """Generate file with scenario duration tags.
    It needs as input the folder of the test report for which generating scenario duration tags.

    Example 1: Generate file with duration tags [(0.2, 'very_fast'), (1, 'fast'), (10, 'normal'), (60, 'slow')] and default tag 'very_slow' 
               
            python generate_scenario_duration_tags.py -r {path_to_report} -t 0.2:very_fast 1:fast 10:normal 60:slow -d very_slow
            
    Example 2: Same as Example 1 but with specific output filename. 
    
            python generate_scenario_duration_tags.py -r {path_to_report} -t 0.2:very_fast 1:fast 10:normal 60:slow -d very_slow -o {path_to_report}/scenario_duration_tags.csv
            
        Note: With this "-o" parameter, it is equivalent to Example 1.
    """
    
            
    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-r', '--report', dest='report_path', required=True,
                   help='Path to the test report folder.')
    
    parser.add_argument('-o', '--output', dest='output_path', default=None,
                   help='Path to the output file. If not defined, a new file will be generated in report folder')

    def duration_tag(s):
        try:
            dur, tag = s.split(':')
            return float(dur), tag
        except:
            raise argparse.ArgumentTypeError("Duration tag must in format '{int}:{str}'")
    parser.add_argument('-t', '--duration-tags', dest='duration_tags', type=duration_tag, nargs="*", required=True,
                   help='List of tuples (duration, tags). If a scenario has a duration inferior to tuple duration, tuple tag is associated to the scenario.')
    parser.add_argument('-d', '--default-tag', dest='default_tag', required=True, 
                   help="Tag associated to scenario whose duration is greater than all durations of parameter '--duration-tags'.")

    parser.add_argument('-a', '--add-apply-column', dest='add_apply_column', default=False, action="store_true",
                   help="If set, the column 'Apply' will be added in output file.")
    
    parser.add_argument('-tp', '--tag-prefix', dest='tag_prefix', default="ScenarioDuration=", 
                   help="Prefix of the duration tag in .feature files.")
    parser.add_argument('-as', '--all-scenarios', dest='all_scenarios', default=False, action="store_true",
                   help='If set, all scenario are in output file, otherwise output file contains only scenarios that have passed and changing tag.')

    args = parser.parse_args()

    logging.basicConfig(format = '{asctime:s} | {thread:-5d} | {levelname:5s} | {module:35s} | {message:s}', style = '{', level=logging.DEBUG, handlers=[logging.StreamHandler()])
    
    # Execute
    try:
        __main(args)
    except:
        logging.exception("An error occured")
        sys.exit(1)

    sys.exit(0)
    
    