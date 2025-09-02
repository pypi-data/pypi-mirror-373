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
    if not os.path.exists(args.input):
        raise FunctionalException(f"Input file '{args.input}' doesn't exist")
    if not os.path.exists(args.features):
        raise FunctionalException(f"Features folder '{args.features}' doesn't exist")
    
    features_path = os.path.abspath(args.features)
    
    sdm = ScenarioDurationManager()
    sdm.update_scenario_durations(args.input, features_path, args.tag_prefix, args.dry_run)
    
    logging.info(f"Finished")
    

if __name__ == "__main__":
    # Arguments
    descr = """Update scenario files by adding/updating the scenario duration tag.
    It needs as input the file created with script generate_scenario_duration_tags.py with '-a' option.
    
    Notes: 
        * The intermediate file between the two scripts exists to let the team the possibility to validate the automatic modifications, 
          by modifying the content of the column 'Apply' that indicates to this script if the modification has to be applied automatically or not.
        * Team can also choose another new tag by modifying the content of the column 'New Tag'. 
          It is recommended in this case to suffix the tag by "!fixed". 
          The suffix "!fixed" is recognized by the scripts as a tag fixed manually that, by default, shouldn't be overridden by automatic new tag.
          
    Example 1: Simulate the modifications the script would apply
            
            python update_scenario_duration_tags.py -i {path_to_scenario_duration_tags_file} -f {path_to_features} -d
            
    Example 2: Apply modifications 
            
            python update_scenario_duration_tags.py -i {path_to_scenario_duration_tags_file} -f {path_to_features}
    """
    
            
    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--input', dest='input', required=True,
                   help='Path to the test report folder.')
    
    parser.add_argument('-f', '--features', dest='features', required=True,
                   help='Path to the features folder.')
    
    parser.add_argument('-tp', '--tag-prefix', dest='tag_prefix', default="ScenarioDuration=", 
                   help="Prefix of the duration tag in .feature files.")
    
    parser.add_argument('-d', '--dry-run', dest='dry_run', default=False, action="store_true",
                   help='If set, no scenario file is updated, it just logs updates it would have done.')

    args = parser.parse_args()

    logging.basicConfig(format = '{asctime:s} | {thread:-5d} | {levelname:5s} | {module:35s} | {message:s}', style = '{', level=logging.DEBUG, handlers=[logging.StreamHandler()])
    
    # Execute
    try:
        __main(args)
    except FunctionalException as exc:
        logging.error(f"Update is interrupted on error: {exc}")
        sys.exit(1)
    except:
        logging.exception("An error occured")
        sys.exit(1)

    sys.exit(0)
    
    