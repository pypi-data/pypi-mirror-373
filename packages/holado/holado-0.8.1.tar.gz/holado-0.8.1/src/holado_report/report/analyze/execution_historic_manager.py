
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
import json
from holado_core.common.exceptions.functional_exception import FunctionalException
import os

logger = logging.getLogger(__name__)



class ExecutionHistoricManager(object):
    def __init__(self, report_path):
        self.__report_path = report_path
        self.__report_execution_historic = []
        
        self.__import_report_execution_historic()
    
    @property
    def report_execution_historic(self):
        return self.__report_execution_historic
    
    def __import_report_execution_historic(self):
        features_path = os.path.join(self.__report_path, "Features")
        if os.path.exists(features_path):
            lp = sorted(os.listdir(features_path))
            for cp in lp:
                cur_feature_path = os.path.join(features_path, cp)
                if os.path.isdir(cur_feature_path):
                    feature_execution_historic = self.__extract_feature_execution_historic(cur_feature_path)
                    if feature_execution_historic:
                        self.__report_execution_historic.append(feature_execution_historic)
        else:
            raise FunctionalException(f"No feature in report path '{self.__report_path}'")
    
    def __extract_feature_execution_historic(self, feature_path):
        res = None
        
        scenarios_path = os.path.join(feature_path, "Scenarios")
        if os.path.exists(scenarios_path):
            lp = sorted(os.listdir(scenarios_path))
            
            # Extract feature info
            if len(lp) > 1:
                last_scenario_path = os.path.join(scenarios_path, lp[-2])
                scenario_execution_historic = self.__extract_scenario_execution_historic(last_scenario_path)
                res = {'feature': scenario_execution_historic[0]['feature'],
                       'scenarios': []}
            
            for cp in lp:
                cur_scenario_path = os.path.join(scenarios_path, cp)
                if os.path.isdir(cur_scenario_path):
                    scenario_execution_historic = self.__extract_scenario_execution_historic(cur_scenario_path)
                    if scenario_execution_historic:
                        res['scenarios'].extend(scenario_execution_historic[0]['scenarios'])
        
        return res
    
    def __extract_scenario_execution_historic(self, scenario_path):
        filepath = os.path.join(scenario_path, "execution_historic.json")
        with open(filepath, "r") as fin:
            return json.load(fin)
        
    def extract_execution_historic_data(self, execution_historic, data_fullnames):
        res = []
        
        for fullname in data_fullnames:
            data = self.__extract_object_data(execution_historic, fullname)
            if fullname.endswith('tags') and len(data) > 0:
                data = "-t " + "-t ".join(data)
            res.append((fullname, data))
        
        return res
    
    def __extract_object_data(self, obj, fullname):
        names = fullname.split('.', maxsplit=1)
        if names[0] in obj:
            res = obj[names[0]]
            if len(names) > 1:
                return self.__extract_object_data(res, names[1])
            else:
                return res
        else:
            raise FunctionalException(f"Not found data '{fullname}' in object: {obj}")
        