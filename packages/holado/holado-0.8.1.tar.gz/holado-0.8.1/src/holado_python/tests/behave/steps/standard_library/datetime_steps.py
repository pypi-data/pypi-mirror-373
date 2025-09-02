# -*- coding: utf-8 -*-

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


from holado_test.scenario.step_tools import StepTools
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
from datetime import datetime, timedelta
from holado_python.common.tools.datetime import DateTime, DurationUnit
import logging
from holado_python.common.enums import ArithmeticOperator
from holado_core.common.tools.tools import Tools
from holado_core.common.tools.comparators.comparator import CompareOperator
from holado_python.common.tools.comparators.datetime_comparator import DatetimeComparator

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()


@Given(r"(?P<varname>{Variable}) = generate date with format (?P<format_value>{Str}) (?P<duration>{Int}) (?P<duration_unit>seconds|minutes|hours|days|weeks) (?P<value>ago|ahead)")
def step_impl(context, varname, format_value, duration, duration_unit, value):
    varname = StepTools.evaluate_variable_name(varname)
    format_value = StepTools.evaluate_scenario_parameter(format_value)
    args={duration_unit:int(duration)}
    deltaT = timedelta(**args)
     
    if value == "ago": 
        date = datetime.now() - deltaT
    elif value == "ahead":
        date = datetime.now() + deltaT
        
    
    v = date.strftime(format_value)
    
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug("New date : ") 
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(v)    
    __get_variable_manager().register_variable(varname, v)

@Given(r"(?P<varname>{Variable}) = datetime now")
def step_impl(context, varname):
    varname = StepTools.evaluate_variable_name(varname)
    res = DateTime.now()
    __get_variable_manager().register_variable(varname, res)

@Given(r"(?P<varname>{Variable}) = datetime now in UTC")
def step_impl(context, varname):
    varname = StepTools.evaluate_variable_name(varname)
    res = DateTime.utcnow()
    __get_variable_manager().register_variable(varname, res)

@Given(r"(?P<varname>{Variable}) = datetime now in TAI")
def step_impl(context,varname):
    varname = StepTools.evaluate_variable_name(varname)
    res = DateTime.tainow()
    __get_variable_manager().register_variable(varname, res)

@Given(r"(?P<varname>{Variable}) = datetime (?P<date_tai>{Any}) from TAI to UTC")
def step_impl(context, varname, date_tai):
    varname = StepTools.evaluate_variable_name(varname)
    date_tai = StepTools.evaluate_scenario_parameter(date_tai)
    
    res = DateTime.datetime_tai_to_utc(date_tai)
    
    __get_variable_manager().register_variable(varname, res)

@Given(r"(?P<varname>{Variable}) = datetime (?P<date_utc>{Any}) from UTC to TAI")
def step_impl(context, varname, date_utc):
    varname = StepTools.evaluate_variable_name(varname)
    date_utc = StepTools.evaluate_scenario_parameter(date_utc)
    
    res = DateTime.datetime_utc_to_tai(date_utc)
    
    __get_variable_manager().register_variable(varname, res)

@Given(r"(?P<varname>{Variable}) = datetime (?P<date_str>{Str})")
def step_impl(context, varname, date_str):
    varname = StepTools.evaluate_variable_name(varname)
    date_str = StepTools.evaluate_scenario_parameter(date_str)
    res = DateTime.str_2_datetime(date_str)
    __get_variable_manager().register_variable(varname, res)

@Given(r"(?P<varname>{Variable}) = (?P<date_value>{Str}) (?P<operator_str>[+-]) (?P<duration>{Int}) (?P<duration_unit_str>microseconds?|milliseconds?|seconds?|minutes?|hours?|days?|weeks?|months?|years?)")
def step_impl(context, varname, date_value, operator_str, duration, duration_unit_str):
    varname = StepTools.evaluate_variable_name(varname)
    date_value = StepTools.evaluate_scenario_parameter(date_value)
    operator = ArithmeticOperator(operator_str)
    duration = StepTools.evaluate_scenario_parameter(duration)
    duration_unit = DurationUnit(duration_unit_str.rstrip('s'))
    
    res = DateTime.apply_delta_on_datetime(date_value, operator, duration, duration_unit)
    
    __get_variable_manager().register_variable(varname, res)

@Given(r"(?P<varname>{Variable}) = convert datetime (?P<date_value>{Str}) to string with format (?P<format_str>{Str})")
def step_impl(context, varname, date_value, format_str):
    varname = StepTools.evaluate_variable_name(varname)
    format_value = StepTools.evaluate_scenario_parameter(format_str)
    datev = StepTools.evaluate_scenario_parameter(date_value)
    res = DateTime.datetime_2_str(dt_value=datev, dt_format=format_value)
    __get_variable_manager().register_variable(varname, res)
    
@Given(r"(?P<varname>{Variable}) = convert datetime (?P<date_value>{Str}) to string")
def step_impl(context, varname, date_value):
    varname = StepTools.evaluate_variable_name(varname)
    datev = StepTools.evaluate_scenario_parameter(date_value)
    res = DateTime.datetime_2_str(dt_value=datev, dt_format=None)
    __get_variable_manager().register_variable(varname, res)
    
@Then(r"(?P<value_1>{Str}) (?P<operator>==|!=|<|<=|>|>=) (?P<value_2>{Str}) \(as datetimes\)")
def step_impl(context, value_1, operator, value_2):  # @DuplicatedSignature
    val1 = StepTools.evaluate_scenario_parameter(value_1)
    val2 = StepTools.evaluate_scenario_parameter(value_2)
    operator = CompareOperator(operator)

    comparator = DatetimeComparator()
    comparator.compare(val1, operator, val2)


### Timestamp conversions

@Given(r"(?P<varname>{Variable}) = convert datetime (?P<date_value>{Str}) to timestamp(?: \(EPOCH: (?P<epoch_str>{Str})\))?")
def step_impl(context, varname, date_value, epoch_str):
    varname = StepTools.evaluate_variable_name(varname)
    datev = StepTools.evaluate_scenario_parameter(date_value)
    epoch = StepTools.evaluate_scenario_parameter(epoch_str)
    
    res = DateTime.datetime_to_timestamp(datev, epoch=epoch)
    
    __get_variable_manager().register_variable(varname, res)

@Given(r"(?P<varname>{Variable}) = convert timestamp (?P<ts_value>{Str}) to datetime(?: \(EPOCH: (?P<epoch_str>{Str})\))?")
def step_impl(context, varname, ts_value, epoch_str):
    varname = StepTools.evaluate_variable_name(varname)
    ts = StepTools.evaluate_scenario_parameter(ts_value)
    epoch = StepTools.evaluate_scenario_parameter(epoch_str)
    
    res = DateTime.timestamp_to_datetime(ts, epoch=epoch)
    
    __get_variable_manager().register_variable(varname, res)


