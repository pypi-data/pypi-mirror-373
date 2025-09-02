import sys
import logging
import os
import argparse
import json

logger = None



def __insert_sys_paths():
    # Insert path to folder containing script_tools
    here = os.path.abspath(os.path.dirname(__file__))
    scripts_path = os.path.abspath(os.path.join(here, "..", ".."))
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    
    from script_tools import insert_holado_helper  # @UnresolvedImport
    insert_holado_helper()
    
    
def __main(args, cwd):
    from holado_python.standard_library.csv import CsvManager
    from holado_core.common.exceptions.technical_exception import TechnicalException
    from holado_core.common.tables.converters.table_converter import TableConverter
    
    input_filepath = os.path.join(cwd, args.input_filepath)
    
    input_table = CsvManager.table_with_content_of_CSV_file(input_filepath, with_header=False, encoding='utf-8-sig', delimiter=';')
    summary_ranking_by_category = __extract_summary_ranking_by_category(input_table)
    detailed_ranking_by_category = __extract_detailed_ranking_by_category(input_table)
    
    if args.output_filepath is None:
        print("Summary ranking:")
        ranking_by_category_json = {k:TableConverter.convert_table_with_header_to_dict_list(summary_ranking_by_category[k]) for k in summary_ranking_by_category}
        print(json.dumps(ranking_by_category_json, indent=4))
        
        print("\n\nDetailed ranking:")
        ranking_by_category_json = {k:TableConverter.convert_table_with_header_to_dict_list(detailed_ranking_by_category[k]) for k in detailed_ranking_by_category}
        print(json.dumps(ranking_by_category_json, indent=4))
    else:
        output_filepath = os.path.join(cwd, args.output_filepath)
        _, ext = os.path.splitext(output_filepath)
        if ext.lower() == '.html':
            __create_html_ranking(output_filepath, summary_ranking_by_category, detailed_ranking_by_category)
        else:
            raise TechnicalException(f"Unmanaged output with extension '{ext}'")
    
def __extract_summary_ranking_by_category(table):
    res = {}
    
    categories_indexes = [(5, 0), (5, 4), (5, 8), (5, 12), (5, 16), (5, 20), (5, 24)]
    for ci in categories_indexes:
        category, ranking_table = __extract_category_ranking_table(table, *ci)
        res[category] = ranking_table
    
    return res
    
def __extract_detailed_ranking_by_category(table):
    res = {}
    
    categories_indexes = [(45, 0), (45, 8), (45, 16), (45, 24), (45, 32), (45, 40), (45, 48)]
    for ci in categories_indexes:
        category, ranking_table = __extract_category_ranking_table(table, *ci)
        res[category] = ranking_table
    
    return res

def __extract_category_ranking_table(table, row_ref_index, col_ref_index):
    from holado_core.common.tables.converters.table_converter import TableConverter
    
    category = table.rows[row_ref_index].cells[col_ref_index].content
    
    row_first_index = row_ref_index + 1
    col_first_index = col_ref_index
    
    row_last_index = row_first_index
    while row_last_index + 1 < table.nb_rows:
        if table.rows[row_last_index+1].cells[col_first_index+1].content in ['', '0']:
            break
        else:
            row_last_index += 1
    
    col_last_index = col_first_index
    while col_last_index + 1 < table.nb_columns:
        if table.rows[row_first_index].cells[col_last_index+1].content in ['']:
            break
        else:
            col_last_index += 1
    
    res_table = TableConverter.extract_table_with_header_from_table(table, row_first_index, row_last_index, col_first_index, col_last_index)
    for row in res_table.rows:
        row.cells[0].content = int(row.cells[0].content)
    res_table.sort(names=["Rang"])
    
    return category, res_table





def __create_html_ranking(output_filepath, summary_ranking_by_category, detailed_ranking_by_category):
    with open(output_filepath, 'w') as fout:
        __write_html_begin(fout)
        __write_html_ranking(fout, "Classement général", summary_ranking_by_category)
        __write_html_ranking(fout, "Détails par manche", detailed_ranking_by_category)
        __write_html_end(fout)
    
def __write_html_begin(fout):
    __writeline(fout, "<html>")
    __writeline(fout, "<body>")
    
def __write_html_ranking(fout, title, ranking_by_category):
    __writeline(fout, f"<h1>{title}</h1>")
    for category in ranking_by_category:
        __write_html_ranking_category(fout, category, ranking_by_category[category])
    
def __write_html_ranking_category(fout, category, ranking_table):
    __writeline(fout, f"<h2>{category}</h2>")
    
    __writeline(fout, f"<table>")
    
    __writeline(fout, f"<tr>")
    for hc in ranking_table.header:
        __writeline(fout, f"<th>{hc.content}</th>")
    __writeline(fout, f"</tr>")
    
    for row in ranking_table.rows:
        __writeline(fout, f"<tr>")
        for c in row:
            __writeline(fout, f"<td>{c.content}</td>")
        __writeline(fout, f"</tr>")
        
    __writeline(fout, f"</table>")
    
def __write_html_end(fout):
    __writeline(fout, "</body>")
    __writeline(fout, "</html>")
    
def __writeline(fout, line):
    fout.write(line + "\n")
    
def _parse_arguments():
    descr = """Roadmap
    
    Usage:
        1. Generate a template file for the desired action with parameter '--output-template' as in example 1.
            It is possible to specify the name of the output file with parameter '-o'.
        2. Copy the template line in order to have one line per action to do, and modify the template file with desired values. 
        3. Process actions described in a CSV file with parameter '-i'.
            If an error occurs at a line, execution is stopped.
        4. See result in output file. If parameter '-o' is not specified, the output filename is generated from parameter '-i'.
    
    In template files, a default value is set in each column. 
    For columns with enum values, the default value is a combination of each possible enum values separated by a '|', but only one value is possible.
    
    
    In input and output files, the first column 'STATUS' describes the status of execution of each line:
        - 'TODO' (or ''): the line is to process (in output file, it means that execution was stopped on an error with a previous line)
        - 'SUCCESS': the line was in success
        - 'ERROR': the line was in error
        - others: the line is not processed, you can specify your own status to skip this line
    In template files, this column is automatically initialized with status 'TODO'.
    Any output file can be used as input file, the lines that are in status 'ERROR' or 'TODO' will be processed again.
    
    Example 1: Output CSV template
            
            roadmap.sh --output-template -o {action}.csv
            
    Example 2: Process with given input CSV
            
            roadmap.sh -i {action}.csv
            
    """
    
    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--input-filepath', dest='input_filepath',
                   help='Input file path')
    
    parser.add_argument('-o', '--output-filepath', dest='output_filepath',
                   help='Output file path')
    
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
    
