# -*- coding: utf-8 -*-

import holado_test.behave.behave_environment


# Import default hook implementation
from holado_test.behave.behave_environment import *

# Redefine specific hook implementation
def before_all(context):
    holado_test.behave.behave_environment.before_all(context)

def after_all(context):
    holado_test.behave.behave_environment.after_all(context)

def before_feature(context, feature):
    holado_test.behave.behave_environment.before_feature(context, feature)

def after_feature(context, feature):
    holado_test.behave.behave_environment.after_feature(context, feature)

def before_scenario(context, scenario):
    holado_test.behave.behave_environment.before_scenario(context, scenario)

def after_scenario(context, scenario):
    holado_test.behave.behave_environment.after_scenario(context, scenario)

def before_step(context, step):
    holado_test.behave.behave_environment.before_step(context, step)

def after_step(context, step):
    holado_test.behave.behave_environment.after_step(context, step)

    

