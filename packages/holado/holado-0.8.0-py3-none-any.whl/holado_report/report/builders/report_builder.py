
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
import abc

logger = logging.getLogger(__name__)



class ReportBuilder():
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def build(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def before_all(self):
        pass
    
    @abc.abstractmethod
    def before_feature(self, feature_context, feature, feature_report=None):
        pass
    
    @abc.abstractmethod
    def before_scenario(self, scenario_context, scenario, scenario_report=None):
        pass
    
    @abc.abstractmethod
    def before_step(self, step_context, step, step_level):
        pass
    
    @abc.abstractmethod
    def after_step(self, step_context, step, step_level):
        pass
    
    @abc.abstractmethod
    def after_scenario(self, scenario, scenario_report=None):
        pass
        
    @abc.abstractmethod
    def after_feature(self, feature, feature_report=None):
        pass
    
    @abc.abstractmethod
    def after_all(self):
        pass
    
    
    
