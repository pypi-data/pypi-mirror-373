
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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_test.scenario.step_tools import StepTools
from holado_value.common.tables.value_table import ValueTable
from holado_scripting.common.tools.evaluate_parameters import EvaluateParameters
import behave
from holado_core.common.tools.tools import Tools



logger = logging.getLogger(__name__)


class BehaveStepTools(StepTools):
    """
    Gives usefull tools for steps files.
    
    Warning: In some cases, use of both step matcher "parse" and a parameter type 
             will have mistake behaviours.
             For example, the result can be that steps of other files are missing at execution for behave
             whereas they are well found and imported in behave.
             If this happens, use step matcher "re"
    """
    
    ############################################################################
    ## Manage step definitions



    
    DEFAULT_STEP_MATCHER = "re"
    
    @classmethod    
    def use_step_matcher(cls, name):
        behave.use_step_matcher(name)
    
    @classmethod    
    def use_step_matcher_default(cls):
        cls.use_step_matcher(cls.DEFAULT_STEP_MATCHER)
    
    # @classmethod
    # def import_types(cls, module, prefix="SRE_", do_upper=False):
    #     res = []
    #     for type_name in cls.__registered_types:
    #         var_name = f"{prefix}{type_name}"
    #         if do_upper:
    #             var_name = var_name.upper()
    #         if not hasattr(module, var_name):
    #             setattr(module, var_name, cls.get_registered_type_pattern(type_name))
    #             res.append(var_name)
    #     logger.debug(f"Imported step parameter types in module '{module.__name__}' as variables: {res}")
    #     return res
    
    @classmethod    
    def register_type(cls, type_name, pattern, eval_func, **eval_func_kwargs):
        super().register_type(type_name, pattern, eval_func, **eval_func_kwargs)
        
        # Register type in parse step matcher
        func = cls.get_registered_type_function(type_name)
        cls.use_step_matcher('parse')
        behave.register_type(**{type_name:func})
        cls.use_step_matcher_default()
    
    
    
    ############################################################################
    ## Manage step multiline text
    
    @classmethod    
    def get_step_multiline_text(cls, context, eval_params=EvaluateParameters.default_without_raise(), raise_exception_if_none=True, log_level=logging.DEBUG):
        """
        Get the step multiline text interpreted.
        Note: parameter context can be the step context or the step object.
        """
        res = None
        if hasattr(context, "text") and context.text is not None:
            res = context.text.strip()
            if eval_params.do_interpret:
                res = cls._get_text_interpreter().interpret(res, eval_params=eval_params, log_level=log_level)
            
        if res is None and raise_exception_if_none:
            raise FunctionalException(f"Multiline text is required under this step\n  context: {context}")
        
        return res
        
    
    ############################################################################
    ## Manage step table
    
    @classmethod
    def _is_scenario_step_table(cls, table):
        return isinstance(table, behave.model.Table)
    
    @classmethod
    def get_step_table(cls, context, do_eval_once=True):
        """
        Get the step table interpreted.
        Note: parameter context can be the step context or the step object.
        """
        if hasattr(context, "table") and context.table is not None:
            if cls.has_table_header(context.table):
                res = cls.convert_step_table_2_value_table_with_header(context.table, do_eval_once=do_eval_once)
            else:
                res = cls.convert_step_table_2_value_table(context.table, do_eval_once=do_eval_once)
            return res
        else:
            return None
        
    @classmethod        
    def _get_table_header(cls, table):
        return table.headings

    @classmethod
    def _get_table_rows(cls, table):
        return table
 
    @classmethod
    def convert_step_table_2_value_table(cls, table, do_eval_once=True):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting step table to scenario table (step table = {table})")

        res = ValueTable()
        
        # Set header as row
        previous_row = None
        srow = cls._convert_step_table_row_2_value_table_row(cls._get_table_header(table), previous_row, do_eval_once=do_eval_once)
        res.add_row(row=srow)
        
        # Set body
        previous_row = srow
        for row in cls._get_table_rows(table):
            srow = cls._convert_step_table_row_2_value_table_row(row, previous_row, do_eval_once=do_eval_once)
            res.add_row(row=srow)
            previous_row = srow
            
        # Manage one cell table referencing a variable containing a table
        res = cls._extract_inner_table_if_present(res, do_eval_once=do_eval_once)
            
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting step table to scenario table (step table = {table}) => {res}")
        return res
        
        
        
