
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2023 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
import csv
import json
from holado_core.common.exceptions.technical_exception import TechnicalException
import itertools
from holado_core.common.exceptions.functional_exception import FunctionalException
import os
from holado_core.common.tools.converters.converter import Converter
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class ScenarioDurationManager(object):
    def __init__(self):
        self.__execution_historic = None
    
    def import_execution_historic(self, filepath):
        with open(filepath, "r") as fin:
            self.__execution_historic = json.load(fin)
        
    def create_file_scenario_duration_limits(self, filepath, scenario_duration_limits):
        header = ["Duration Limit", "Nb of Scenarios", "Total Spent Time", "Nb of Scenarios (limit)", "Total Spent Time (limit)", "Mean Duration (limit)"]
        with open(filepath, "w", newline='') as fout:
            dw = csv.DictWriter(fout, fieldnames=header, delimiter=';')#, quoting=csv.QUOTE_NONE)
            dw.writeheader()
            
            for sd in scenario_duration_limits:
                dw.writerow(sd)
        
    def compute_scenario_duration_limits(self, duration_limits=None):
        if duration_limits is None:
            duration_limits = sorted(set(itertools.chain(*((0.1*x, x, 10*x, 60*x, 60*60*x) for x in range(1,10))))) + [60*60*24*30]

        res = [self.__compute_scenario_duration_limit(dur_lim) for dur_lim in duration_limits]
        
        # Compute base data in limit: spent time, nb of scenario
        res[0]["Total Spent Time (limit)"] = res[0]["Total Spent Time"]
        res[0]["Nb of Scenarios (limit)"] = res[0]["Nb of Scenarios"]
        for ind in range(1,len(res)):
            res[ind]["Total Spent Time (limit)"] = res[ind]["Total Spent Time"] - res[ind-1]["Total Spent Time"]
            res[ind]["Nb of Scenarios (limit)"] = res[ind]["Nb of Scenarios"] - res[ind-1]["Nb of Scenarios"]
        
        # Compute mean duration in limit
        for ind in range(len(res)):
            if res[ind]["Nb of Scenarios (limit)"] > 0:
                res[ind]["Mean Duration (limit)"] = res[ind]["Total Spent Time (limit)"] / res[ind]["Nb of Scenarios (limit)"]
            else:
                res[ind]["Mean Duration (limit)"] = None
        
        return res
    
    def __compute_scenario_duration_limit(self, duration_limit):
        res = {"Duration Limit" : duration_limit,
               "Nb of Scenarios" : 0,
               "Total Spent Time" : 0}
        for eh_feat in self.__execution_historic:
            for eh_sce in eh_feat['scenarios']:
                if eh_sce['scenario']['status'] == 'passed':
                    sce_dur = eh_sce['scenario']['duration']
                    if sce_dur < duration_limit:
                        res["Nb of Scenarios"] += 1
                        res["Total Spent Time"] += sce_dur
        return res
        
    def create_file_scenario_duration_tags(self, filepath, scenario_duration_tags):
        header = ["Feature", "Scenario", "File", "Line", "Status", "Duration", "Current tag", "New tag"]
        if scenario_duration_tags and len(scenario_duration_tags) > 0:
            header.extend(set(scenario_duration_tags[0].keys()) - set(header))
            
        with open(filepath, "w", newline='') as fout:
            dw = csv.DictWriter(fout, fieldnames=header, delimiter=';')#, quoting=csv.QUOTE_NONE)
            dw.writeheader()
            
            for sd in scenario_duration_tags:
                dw.writerow(sd)
    
    def compute_scenario_duration_tags(self, duration_limit_tags, default_tag, tag_prefix="ScenarioDuration=", missing_tag=True, new_tag=True, unchanged_tag=False, with_failed=False, add_apply=False):
        if duration_limit_tags is None or not isinstance(duration_limit_tags, list):
            raise TechnicalException("Parameter 'duration_limit_tags' must be specified as a list of tuples (limit, tag)")
        if default_tag is None:
            raise TechnicalException("Parameter 'default_tag' must be specified")
            
        res = []
        for eh_feat in self.__execution_historic:
            for eh_sce in eh_feat['scenarios']:
                sce_res = {"Feature" : eh_feat['feature']['name'], 
                           "Scenario" : eh_sce['scenario']['name'], 
                           "File" : eh_sce['scenario']['filename'], 
                           "Line" : eh_sce['scenario']['line'], 
                           "Status" : eh_sce['scenario']['status'], 
                           "Duration" : eh_sce['scenario']['duration'], 
                           "Current tag" : None, 
                           "New tag" : None}
                
                cur_tag = None
                for tag in eh_sce['scenario']['tags']:
                    tag = str(tag)
                    if tag.startswith(tag_prefix):
                        cur_tag = tag[len(tag_prefix):]
                        break
                sce_res["Current tag"] = cur_tag
                    
                cur_status = eh_sce['scenario']['status']
                new_tag = None
                if cur_status == "passed":
                    sce_dur = float(eh_sce['scenario']['duration'])
                    for lim_tag in duration_limit_tags:
                        if sce_dur < lim_tag[0]:
                            new_tag = lim_tag[1]
                            break
                    if new_tag is None:
                        new_tag = default_tag
                    sce_res["New tag"] = new_tag
                    
                if add_apply:
                    apply = None
                    if new_tag is not None:
                        if cur_tag is None:
                            apply = True
                        elif new_tag != cur_tag:
                            if cur_tag.endswith("!fixed"):
                                apply = False
                            else:
                                apply = True
                    sce_res["Apply"] = apply
                    
                if (with_failed and cur_status != "passed" 
                    or cur_status == "passed" 
                        and (missing_tag and cur_tag is None)):
                    res.append(sce_res)
        return res
    
    def update_scenario_durations(self, scenario_duration_tags_filepath, features_path, tag_prefix="ScenarioDuration=", dry_run=False):
        sdt_by_file = {}
        with open(scenario_duration_tags_filepath, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            # Verify presence of 'Apply' column
            if 'Apply' not in reader.fieldnames:
                raise FunctionalException(f"File '{scenario_duration_tags_filepath}' doesn't have column 'Apply'. Please regenerate it with column 'Apply'.")
            
            for row in reader:
                file = row["File"]
                if file not in sdt_by_file:
                    sdt_by_file[file] = []
                sdt_by_file[file].append(row)
                
        logger.info(f"Updating scenario duration tags with prefix '{tag_prefix}' for scenarios in folder '{features_path}'")
        for file in sorted(sdt_by_file.keys()):
            sorted_sdt = sorted(sdt_by_file[file], key=lambda x: -int(x["Line"]))
            for sdt in sorted_sdt:
                self.__update_scenario_duration(sdt, features_path, tag_prefix, dry_run)
        
    def __update_scenario_duration(self, scenario_duration_tag, features_path, tag_prefix, dry_run):
        apply = scenario_duration_tag["Apply"]
        if apply and Converter.is_boolean(apply) and Converter.to_boolean(apply):
            file = scenario_duration_tag["File"]
            line_nb = int(scenario_duration_tag["Line"])
            cur_tag = scenario_duration_tag["Current tag"]
            new_tag = scenario_duration_tag["New tag"]
            
            if file.startswith('features'):
                file = file[len('features')+1:]
            filepath = os.path.join(features_path, file)
            
            logger.info(f"    in {file} l.{line_nb}: '{cur_tag}' -> '{new_tag}'")
            self.__update_scenario_duration_in_file(filepath, line_nb, cur_tag, new_tag, tag_prefix, dry_run)
        
    def __update_scenario_duration_in_file(self, filepath, line_nb, cur_tag, new_tag, tag_prefix, dry_run):
        # Read file content
        with open(filepath, 'r') as fin:
            lines = fin.readlines()
        
        # Verify line line_nb is a scenario
        if not lines[line_nb].strip().startswith("Scenario:"):
            raise FunctionalException(f"In file '{filepath}', line {line_nb} is not a scenario. This happens when scenario duration tags file is not synchronized with feature files.")
        
        # Find current tag in file
        index_duration = None
        index = line_nb - 2
        while index >= 0:
            line_content = lines[index].strip()
            if line_content.startswith("@" + tag_prefix):
                index_duration = index
                break
            elif not self.__is_line_before_scenario(line_content):
                break
            else:
                index += 1
                
        # Extract and verify current tag
        if index_duration is not None:
            scenario_tag = line_content[len("@" + tag_prefix):]
            if scenario_tag != cur_tag:
                logger.warning(f"        WARNING: Actual tag in file is '{scenario_tag}' (expected: '{cur_tag}')")
        elif cur_tag:
            logger.warning(f"        WARNING: Scenario has no actual tag in file (expected: '{cur_tag}')")
            
        # Compute new meta line
        index_sce = lines[line_nb - 1].find("Scenario")
        new_line = " " * index_sce + "@" + tag_prefix + new_tag + "\n"
        
        # Apply modification
        if index_duration is not None:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"{' '*8}Replacing line {index_duration+1}:\n{' '*12}old: [{lines[index_duration][:-1]}]\n{' '*12}new: [{new_line[:-1]}]")
            if not dry_run:
                lines[index_duration] = new_line
        else:
            index_insert = line_nb - 1
            while True:
                prev_content = lines[index_insert - 1].strip() if index_insert > 0 else None
                if prev_content is not None and len(prev_content) > 2 and prev_content[1].isupper() and prev_content > new_line.strip():
                    index_insert -= 1
                else:
                    break
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"{' '*8}Insert in line {index_insert+1}: [{new_line[:-1]}]")
            if not dry_run:
                lines.insert(index_insert, new_line)
        
        # Save in file 
        if not dry_run:
            with open(filepath, 'w') as fout:
                fout.writelines(lines)
        
    def __is_line_before_scenario(self, line):
        return not any((line.strip().startswith(txt) for txt in ['Given', 'When', 'Then', 'Feature', '|', '"""', "'''"]))
        
        