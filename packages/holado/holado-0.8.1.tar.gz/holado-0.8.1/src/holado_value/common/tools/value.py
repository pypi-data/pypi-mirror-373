
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

from builtins import str
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools
from holado.common.context.session_context import SessionContext
import logging
from holado_value.common.tools.value_types import ValueTypes
from functools import total_ordering
from holado_scripting.common.tools.evaluate_parameters import EvaluateParameters
from holado.holado_config import Config
from holado.common.handlers.undefined import undefined_value, undefined_argument, to_be_defined, not_applicable, is_undefined
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


@total_ordering
class Value(object):
    
    def __init__(self, original_value=undefined_argument, value=undefined_argument, do_eval_once=True, eval_params=undefined_argument):
        """
        @summary: Constructor
        @param original_value: Original value (before value expression evaluation) - can be a string or any object
        @param value: Value - can be a string or any object
        """
        self.__original_value = to_be_defined
        self.__value = to_be_defined
        self.__value_type = None
        
        # Manage value evaluation
        self.__value_to_eval = to_be_defined
        self.__evaluated_value = to_be_defined
        self.__evaluated_value_type = to_be_defined
        # By default, raise on interpret and variable evaluation error, but not on eval error
        self.__eval_params_default = eval_params if eval_params is not undefined_argument else EvaluateParameters.default().with_raise_on_eval_error(False)
        self.__do_eval_once = do_eval_once
        
        self.__extract_value_information(original_value, value)
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"New Value: original_value=[{self.__original_value}] ; type=[{self.__value_type.name}] ; value=[{self.__value}] ; value_to_eval=[{self.__value_to_eval}]")
        
    def _verify_valid_compared_object(self, other, raise_exception=True):
        res = isinstance(other, Value)
        if not res and raise_exception:
            return TechnicalException(f"Unmanaged comparison between types '{self.__class__.__name__}' and '{other.__class__.__name__}'")
        
    def __eq__(self, other):
        self._verify_valid_compared_object(other)
        if isinstance(other, Value):
            return (self.get_value() == other.get_value())
        else:
            return TechnicalException(f"Unmanaged comparison between types '{self.__class__.__name__}' and '{other.__class__.__name__}'")
    
    def __lt__(self, other):
        self._verify_valid_compared_object(other)
        if isinstance(other, Value):
            return (self.get_value() < other.get_value())
        else:
            return TechnicalException(f"Unmanaged comparison between types '{self.__class__.__name__}' and '{other.__class__.__name__}'")
    
    @property
    def do_eval_once(self):
        return self.__do_eval_once
    
    @property
    def string_value(self):
        value = self.get_value()
        
        if value in [undefined_value, not_applicable]:
            return Config.NOT_APPLICABLE_SYMBOL
        if value is None:
            return Config.NONE_SYMBOL
        else:
            return str(value)
    
    @property
    def original_value(self):
        """
        @summary: Return the original value
        """
        return self.__original_value
    
    @property
    def original_value_type(self):
        """
        @summary: Return the original value type
        """
        return self.__value_type
    
    @property
    def value_type(self):
        return self.get_value_type()
    
    @property
    def value_before_eval(self):
        """
        @summary: Return the value before evaluation
        """
        return self.__value_to_eval
    
    @property
    def value(self):
        """
        @summary: Return the value, after evaluation if needed
        """
        return self.get_value(raise_if_undefined=True)
    
    def get_value(self, raise_if_undefined=False, eval_params=undefined_argument):
        if self.__value_to_eval is not undefined_value:
            self.__evaluate_value_if_needed(eval_params=eval_params)
            res = self.__evaluated_value
        else:
            res = self.__value
        
        if is_undefined(res) and raise_if_undefined:
            msg = "Value is undefined"
            if self.value_type == ValueTypes.NotApplicable:
                msg += " (Not Applicable)"
            raise ValueError(f"Value is undefined (value type: {self.value_type.name} ; original value: [{self.original_value}] (type: {Typing.get_object_class_fullname(self.original_value)}))")
        return res
    
    def get_value_type(self, eval_params=undefined_argument):
        if self.__value_to_eval is not undefined_value:
            self.__evaluate_value_if_needed(eval_params=eval_params)
            res = self.__evaluated_value_type
        else:
            res = self.__value_type
        return res
    
    def __evaluate_value_if_needed(self, eval_params=undefined_argument):
        if self.__evaluated_value is to_be_defined or not self.__do_eval_once:
            eval_params = eval_params if eval_params is not undefined_argument else self.__eval_params_default
            if ValueTypes.is_string(self.__value_type):
                eval_params = eval_params.with_result_type(str)
            self.__evaluated_value_type, self.__evaluated_value = self.__get_expression_evaluator().evaluate_expression_of_information(self.__value_type, self.__value_to_eval, eval_params=eval_params)
        
    def represent(self, indent = 0, do_evaluation = False):
        res_list = []
        
        res_list.append(Tools.get_indent_string(indent))
        
        if ValueTypes.is_string(self.__value_type):
            if do_evaluation:
                res_list.append("'")
                res_list.append(self.string_value)
                res_list.append("'")
            else:
                res_list.append(str(self.original_value))
        elif self.__value_type in [ValueTypes.Boolean, ValueTypes.Integer, ValueTypes.Float, ValueTypes.Null, ValueTypes.NotApplicable, ValueTypes.Symbol, ValueTypes.Generic]:
            if do_evaluation:
                res_list.append(self.string_value)
            else:
                res_list.append(str(self.original_value))
        else:
            raise TechnicalException("Unmanaged value type '{}'".format(self.__value_type.name))
        
        return "".join(res_list)
        
    def __extract_value_information(self, original_value, value):
        # Define original value
        if original_value is not undefined_argument and not (original_value in [undefined_value, None] and value not in [undefined_argument, undefined_value, None]):
            self.__original_value = original_value
        elif value is not undefined_argument:
            if value is not None and isinstance(value, str):
                self.__original_value = f"'{value}'"
            else:
                self.__original_value = value
        
        # Define value information from original value
        self.__value_type, self.__value, self.__value_to_eval = self.__get_expression_evaluator().extract_expression_information(self.original_value)
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"extracted value info: {self.__value_type=}, {self.__value=}, {self.__value_to_eval=}")
        
    def __get_expression_evaluator(self):
        if SessionContext.instance().has_scenario_context():
            return SessionContext.instance().get_scenario_context().get_expression_evaluator()
        else:
            return SessionContext.instance().expression_evaluator
        
