
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

from holado.common.context.session_context import SessionContext
import logging
import re
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_scripting.common.tools.variable_manager import VariableManager
from holado_core.common.tools.tools import Tools
from holado_value.common.tables.value_table import ValueTable
from holado_value.common.tables.value_table_with_header import ValueTableWithHeader
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_core.common.tables.table import Table
from holado_core.common.tables.table_row import TableRow
from holado_core.common.tables.table_cell import TableCell
from holado_value.common.tables.value_table_row import ValueTableRow
from holado_value.common.tables.value_table_cell import ValueTableCell
from holado_value.common.tools.value_types import ValueTypes
from holado_value.common.tables.comparators.table_2_value_table_with_header_comparator import Table2ValueTable_WithHeaderComparator
from holado_value.common.tables.comparators.table_2_value_table_comparator import Table2ValueTable_Comparator
from holado_core.common.tables.table_manager import TableManager
from holado_scripting.common.tools.evaluate_parameters import EvaluateParameters
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado.holado_config import Config
from holado_python.standard_library.typing import Typing
from holado_value.common.tables.value_table_manager import ValueTableManager

logger = logging.getLogger(__name__)



class SRE(object):
    """
    Step RegExp
    All registered step parameter types are added in this class as public attributes,
    with type name as attribute name, and pattern as associated value
    """
    
    @staticmethod
    def all_as_dict():
        return Typing.get_object_attribute_values_by_name(SRE)


#TODO: make it a service in SessionContext
class StepTools(object):
    
    __registered_types = {}
    
    @staticmethod
    def _get_scenario_context():
        return SessionContext.instance().get_scenario_context()

    @staticmethod
    def _get_expression_evaluator():
        return StepTools._get_scenario_context().get_expression_evaluator()

    @staticmethod
    def _get_text_interpreter():
        return StepTools._get_scenario_context().get_text_interpreter()

    @staticmethod
    def _get_variable_manager() -> VariableManager:
        return StepTools._get_scenario_context().get_variable_manager()

    @staticmethod
    def unescape_string(text):
        #res = bytes(text, "utf-8").decode("unicode_escape")
        res = text.encode('latin-1').decode('unicode-escape')
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace("unescaping string [{}] -> [{}]".format(text, res))
        return res
    
    @staticmethod
    def extract_string_value(text_param):
        return StepTools._get_expression_evaluator().extract_string_value(text_param)
    
    @staticmethod
    def evaluate_string_parameter(text_param, do_interpret=True, log_level=logging.DEBUG):
        eval_params = EvaluateParameters.default().with_interpret(do_interpret).with_eval(False).with_result_type(str)
        _, res = StepTools._get_expression_evaluator().evaluate_expression(text_param, eval_params=eval_params, log_level=Tools.do_log_level(log_level, logging.TRACE))  # @UndefinedVariable
        if Tools.do_log_if_objects_are_different(logger, log_level, text_param, res):
            logger.log(log_level, "evaluate_string_parameter: [{}] -> [{}]".format(text_param, res))
        return res
    
    @staticmethod
    def evaluate_variable_name(text_param, log_level=logging.DEBUG):
        if text_param is None:
            return None
        
        eval_params = EvaluateParameters.default_without_eval(False).with_result_type(str)
        res = StepTools._get_text_interpreter().interpret(text_param, eval_params=eval_params, log_level=Tools.do_log_level(log_level, logging.TRACE))  # @UndefinedVariable
        if Tools.do_log_if_objects_are_different(logger, log_level, text_param, res):
            logger.log(log_level, f"evaluate_variable_name: [{text_param}] -> [{res}] (type: {Typing.get_object_class_fullname(res)})")
        return res
    
    @staticmethod
    def evaluate_variable_value(text_param, log_level=logging.DEBUG):
        if text_param is None:
            return None
        
        eval_params = EvaluateParameters.default_without_eval(False)
        _, res = StepTools._get_expression_evaluator().evaluate_expression(text_param, eval_params=eval_params, log_level=Tools.do_log_level(log_level, logging.TRACE))  # @UndefinedVariable
        if Tools.do_log_if_objects_are_different(logger, log_level, text_param, res):
            logger.log(log_level, f"evaluate_variable_name: [{text_param}] -> [{res}] (type: {Typing.get_object_class_fullname(res)})")
        return res
    
    @staticmethod
    def evaluate_scenario_parameter(text_param, log_level=logging.DEBUG):
        if text_param is None:
            return None
        
        eval_params = EvaluateParameters.default().with_raise_on_eval_error(False)
        _, res = StepTools._get_expression_evaluator().evaluate_expression(text_param, eval_params=eval_params, log_level=Tools.do_log_level(log_level, logging.TRACE))  # @UndefinedVariable
        if Tools.do_log_if_objects_are_different(logger, log_level, text_param, res):
            logger.log(log_level, f"evaluate_scenario_parameter: [{text_param}] -> [{res}] (type: {Typing.get_object_class_fullname(res)})")
        return res
 
    @staticmethod
    def evaluate_list_scenario_parameter(text_param, param_name, log_level=logging.DEBUG):
        res = StepTools.evaluate_scenario_parameter(text_param, log_level=log_level)
        if isinstance(res, str):
            regex = re.compile(r"^\s*\[(.*)\]\s*$")
            m = regex.match(res)
            if m:
                param_names = m.group(1).split(',')
                res = [StepTools.evaluate_scenario_parameter(pn.strip()) for pn in param_names]
            else:
                raise FunctionalException(f"Parameter '{param_name}' must be specified in a list format (ex: \"['Name1', 'Name2',...]\")")
        if Tools.do_log_if_objects_are_different(logger, log_level, text_param, res):
            logger.log(log_level, f"evaluate_list_scenario_parameter for parameter '{param_name}': {text_param} -> {res}")
        return res
    
    @classmethod
    def replace_variable_names(cls, text, log_level=logging.DEBUG):
        res = text
        if res is None:
            return None
        
        pattern_var = re.compile(SRE.VariableName)
        pos = 0
        m = pattern_var.search(res, pos)
        while m:
            var_name = cls._get_variable_manager().evaluate_variable_name(m.group())
            if cls._get_variable_manager().exists_variable(var_name):
                res = res[:m.start()] + var_name + res[m.end():]
                pos = m.start() + len(var_name)
            else:
                pos = m.end()
            m = pattern_var.search(res, pos)
        
        if res != text:
            if Tools.do_log(logger, log_level):
                logger.log(log_level, f"replace_variable_names: [{text}] -> [{res}]")
        return res
    
    @classmethod    
    def get_step_multiline_text(cls, *args, **kwargs):
        """
        Get the step multiline text interpreted.
        Note: parameter context can be the step context or the step object.
        """
        raise NotImplementedError
        
    
    @classmethod    
    def get_step_table(cls, *args, **kwargs):
        """
        Get the step table interpreted.
        Note: parameter context can be the step context or the step object.
        """
        raise NotImplementedError
        
    
    @classmethod
    def convert_step_table_2_value_table(cls, table, do_eval_once=True):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting step table to scenario table (step table = {table})")

        res = ValueTable()
        
        # Set body
        previous_row = None
        for row in cls._get_table_rows(table):
            srow = cls._convert_step_table_row_2_value_table_row(row, previous_row, do_eval_once=do_eval_once)
            res.add_row(row=srow)
            previous_row = srow
            
        # Manage one cell table referencing a variable containing a table
        res = cls._extract_inner_table_if_present(res, do_eval_once=do_eval_once)
            
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting step table to scenario table (step table = {table}) => {res}")
        return res
        
    @classmethod        
    def convert_step_table_2_value_table_with_header(cls, table, do_eval_once=True) -> ValueTableWithHeader :
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converting step table to scenario table with header (step table = {table})")
        if table is None:
            raise FunctionalException("This step needs a table")

        res = ValueTableWithHeader()
        
        # Set header
        res.header = cls._convert_step_table_header_2_table_header(cls._get_table_header(table))
        
        # Set body
        previous_row = None
        for row in cls._get_table_rows(table):
            srow = cls._convert_step_table_row_2_value_table_row(row, previous_row, do_eval_once=do_eval_once)
            res.add_row(row=srow)
            previous_row = srow
            
        # Manage one cell table referencing a variable containing a table
        res = cls._extract_inner_table_if_present(res, do_eval_once=do_eval_once)
            
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Converting step table to scenario table with header (step table = {table}) => {res}")
        return res

    @classmethod
    def _extract_inner_table_if_present(cls, table, do_eval_once=True):
        res = table
        if isinstance(table, TableWithHeader):
            if res.nb_columns == 1 and res.nb_rows == 0:
                cell_content = res.header.get_cell(0).content
                if cls._get_variable_manager().exists_variable(variable_name=cell_content):
                    value = cls._get_variable_manager().get_variable_value(cell_content)
                    if ValueTableManager.is_value_table(value):
                        res = value
                    elif isinstance(value, TableWithHeader):
                        res = ValueTableConverter.convert_table_2_value_table(value, do_eval_once=do_eval_once)
                    elif isinstance(value, Table):
                        raise FunctionalException(f"The table in variable '{cell_content}' is expected to be with header")
        elif isinstance(table, Table):        
            if res.nb_columns == 1 and res.nb_rows == 1:
                value = res.get_row(0).get_cell(0).value
                if ValueTableManager.is_value_table(value):
                    res = value
                elif isinstance(value, Table):
                    res = ValueTableConverter.convert_table_2_value_table(value, do_eval_once=do_eval_once)
                    
        if res != table and Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Extracted inner table: {table} => {res}")
        return res
            
    @classmethod
    def _convert_step_table_header_2_table_header(cls, header):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace("Converting step table header to table header")

        res = TableRow()
        
        for hcell in header:
            cell = TableCell(hcell)
            
            # TODO: manage merged header cells
            
            res.add_cell(cell=cell)
           
        return res
        
    @classmethod
    def _convert_step_table_row_2_value_table_row(cls, row, previous_row, do_eval_once=True):  # @UnusedVariable
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace("Converting behave table row to scenario table row")
        
        res = ValueTableRow()
        
        for cell in row:
            scell = ValueTableCell(cell, do_eval_once=do_eval_once)
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace("Converting cell [{}] -> scenario table cell (content=[{}] ; value_type='{}')".format(cell, scell.content, scell.value_type.name))
            
            # TODO: manage merged cells
            
            res.add_cell(cell=scell)
           
        return res
    

    @classmethod
    def has_table_header(cls, table):
        """
        Return True if scenario table has a header (for HolAdo framework).
        For HolAdo framework, table header names are all texts without quotes.
        """
        internal_header = cls._get_table_header(table)
        if internal_header is None:
            return False
        
        for cell in internal_header:
            scell = ValueTableCell(cell)
            if not scell.content_type == ValueTypes.Symbol:
                return False
        
        return True

    @classmethod
    def _has_table_header(cls, table):
        """Return True if scenario table has a header (for internal tool interpreting scenario text)."""
        return cls._get_table_header(table) is not None
    
    @classmethod
    def _is_scenario_step_table(cls, table):
        """Return if a table is a scenario step table."""
        raise NotImplementedError()

    @classmethod
    def _get_table_header(cls, table):
        """Return iterable object on scenario table header (for internal tool interpreting scenario text)."""
        raise NotImplementedError()

    @classmethod
    def _get_table_rows(cls, table):
        """Return iterable object on scenario table rows (for internal tool interpreting scenario text)."""
        raise NotImplementedError()
        
    @classmethod
    def represent_step_table(cls, table, indent=0):
        res_list = []
        
        header = cls._get_table_header(table)
        if header:
            res_list.append("| " + " | ".join(header) + " |")
        
        for row in cls._get_table_rows(table):
            res_list.append("| " + " | ".join(row) + " |")
            
        return Tools.indent_string(indent, "\n".join(res_list))
        

    @classmethod
    def then_table_is(cls, table_obtained, table_expected, raise_exception=True):
        is_with_header = TableManager.is_table_with_header(table_obtained)
        if cls._is_scenario_step_table(table_expected):
            if is_with_header:
                table_expected = cls.convert_step_table_2_value_table_with_header(table_expected)
            else:
                table_expected = cls.convert_step_table_2_value_table(table_expected)
        
        if is_with_header:
            comparator = Table2ValueTable_WithHeaderComparator()
        else:
            comparator = Table2ValueTable_Comparator()
        try:
            return comparator.equals(table_obtained, table_expected, is_obtained_vs_expected=True, raise_exception=raise_exception)
        except FunctionalException as exc:
            raise FunctionalException(f"Tables are different (obtained = table 1 ; expected = table 2):\n{Tools.indent_string(4, exc.message)}") from exc

    @classmethod
    def then_table_contains(cls, table_obtained, table_expected, raise_exception=True):
        is_with_header = TableManager.is_table_with_header(table_obtained)
        if cls._is_scenario_step_table(table_expected):
            if is_with_header:
                table_expected = cls.convert_step_table_2_value_table_with_header(table_expected)
            else:
                table_expected = cls.convert_step_table_2_value_table(table_expected)
        
        if is_with_header:
            comparator = Table2ValueTable_WithHeaderComparator()
        else:
            comparator = Table2ValueTable_Comparator()
            
        try:
            return comparator.contains_rows(table_obtained, table_expected, is_obtained_vs_expected=True, raise_exception=raise_exception)
        except FunctionalException as exc:
            raise FunctionalException(f"Obtained table doesn't contain expected table (obtained = table 1 ; expected = table 2):\n{Tools.indent_string(4, exc.message)}") from exc

    @classmethod
    def then_table_doesnt_contain(cls, table_obtained, table_expected, raise_exception=True):
        is_with_header = TableManager.is_table_with_header(table_obtained)
        if cls._is_scenario_step_table(table_expected):
            if is_with_header:
                table_expected = cls.convert_step_table_2_value_table_with_header(table_expected)
            else:
                table_expected = cls.convert_step_table_2_value_table(table_expected)
        
        if is_with_header:
            comparator = Table2ValueTable_WithHeaderComparator()
        else:
            comparator = Table2ValueTable_Comparator()
            
        try:
            return comparator.doesnt_contain_rows(table_obtained, table_expected, is_obtained_vs_expected=True, raise_exception=raise_exception)
        except FunctionalException as exc:
            raise FunctionalException(f"Obtained table contains at least a row of expected table (obtained = table 1 ; expected = table 2):\n{Tools.indent_string(4, exc.message)}") from exc
    
    @classmethod
    def format_step(cls, step_str, keyword=None, table=None, text=None):
        step_str = step_str.strip()
        
        if keyword is not None:
            res = f"{keyword} {step_str}"
        else:
            res = step_str
            
        if table is not None:
            if isinstance(table, Table):
                rendered_table = table.represent(indent=4)
            else:
                raise TechnicalException(f"Unmanaged table of type '{Typing.get_object_class_fullname(table)}'")
            res = u"{res}\n{table}".format(res=res, table=rendered_table)
        elif text is not None:
            rendered_text = text.replace(u'"""', u'\\"\\"\\"')
            rendered_text = Tools.indent_string(4, u'"""\n' + rendered_text + '\n"""\n')
            res = u"{res}\n{text}".format(res=res, text=rendered_text)
            
        return res
        
    @classmethod
    def format_steps_with(cls, steps, format_with_list):
        res = steps
        for form in format_with_list:
            _, form_eval = cls._get_expression_evaluator().evaluate_expression(form, log_level=logging.TRACE)  # @UndefinedVariable
            if form_eval == form:
                raise FunctionalException(f"Not able to evaluation expression [{form}]. Is missing its initialization ?")
            res = res.replace(f"${{{form}}}", str(form_eval))
        return res
    
    @classmethod
    def format_steps_as_parameter(cls, steps, indent):
        return "\n" + Tools.indent_string(indent, steps+'\n')
    
    @classmethod    
    def register_type(cls, type_name, pattern, eval_func, **eval_func_kwargs):
        # Register type in behave
        def func(text):
            return eval_func(text, **eval_func_kwargs)
        func.pattern = pattern
        
        # Add type in SRE class
        setattr(SRE, type_name, pattern)
        
        # Store type as registered
        new_type = {'pattern':pattern, 'function':func}
        if type_name in cls.__registered_types:
            logger.warning(f"Overriding step parameter type '{type_name}': {cls.__registered_types[type_name]['pattern']} -> {new_type['pattern']}")
            import traceback
            logging.warning("".join(traceback.format_list(traceback.extract_stack())))
        cls.__registered_types[type_name] = new_type
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Registered step parameter type '{type_name}'")
        
    @classmethod    
    def get_registered_type_names(cls):
        return list(cls.__registered_types)
        
    @classmethod    
    def get_registered_type_pattern(cls, type_name):
        if type_name not in cls.__registered_types:
            raise TechnicalException(f"Type '{type_name}' is not registered")
        return cls.__registered_types[type_name]['pattern']
        
    @classmethod    
    def get_registered_type_function(cls, type_name):
        if type_name not in cls.__registered_types:
            raise TechnicalException(f"Type '{type_name}' is not registered")
        return cls.__registered_types[type_name]['function']
        
    @classmethod    
    def register_default_types(cls):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Registering step parameter types...")
        ##### Old implementation:
        # __step_regex = {
        #     'variable name': r"[\w${}]+",
        #     'variable expression': r"(?:(?! = | by )[^=])+",
        #     'any parameter': r"(?:[^' ]+|.*)",
        #     'float parameter': r"(?:[^' ]+|\d+(?:\.\d*)?)",
        #     'int parameter': r"(?:[^' ]+|\d+)",
        #     'str parameter': r"(?:[^' ]+|'[^']*'(?:%|#)?)",
        #     'str parameter with quotes': r"(?:[^' ]+|'.*'(?:%|#)?)",
        #     }
        
        regex_suffix = f"(?:{Config.DYNAMIC_SYMBOL}|{Config.THREAD_DYNAMIC_SYMBOL}|{Config.UNIQUE_SYMBOL})?"
        regex_suffix_chars = f"{Config.DYNAMIC_SYMBOL}{Config.THREAD_DYNAMIC_SYMBOL}{Config.UNIQUE_SYMBOL}"
        
        # Variable types
        cls.register_type('VariableName', 
                          r"[\w$\{{\}}]+{suffix}".format(suffix=regex_suffix), 
                          StepTools.evaluate_variable_name)
        # cls.register_type('VariableExpression', r"(?:(?! = | by )[^=])+", StepTools.evaluate_variable_name)
        cls.register_type('VariableExpression', 
                          r"[\w\-\+$\{{\}}\[\]\(\)\.:,'{suffix_chars}]+".format(suffix_chars=regex_suffix_chars), 
                          StepTools.evaluate_variable_name)
        cls.register_type('Variable', 
                          cls.get_registered_type_pattern('VariableExpression'), 
                          StepTools.evaluate_variable_name)
        
        cls.register_type('Any', 
                          r".*", 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('AnyLazy', 
                          r".*?", 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('Float', 
                          r"{Variable}|(?:-)?\d+(?:\.\d*)?".format(Variable=cls.get_registered_type_pattern('Variable')), 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('Int', 
                          r"{Variable}|(?:-)?\d+".format(Variable=cls.get_registered_type_pattern('Variable')), 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('Boolean', 
                          r"{Variable}|True|False".format(Variable=cls.get_registered_type_pattern('Variable')), 
                          StepTools.evaluate_scenario_parameter)
        
        # String types
        cls.register_type('Bytes', 
                          r"{Variable}|b'[^']*'".format(Variable=cls.get_registered_type_pattern('Variable')), 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('Str', 
                          r"{Variable}|r?'[^']*'{suffix}".format(Variable=cls.get_registered_type_pattern('Variable'), suffix=regex_suffix), 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('RawStr', 
                          r"{Variable}|'.*'{suffix}".format(Variable=cls.get_registered_type_pattern('Variable'), suffix=regex_suffix), 
                          StepTools.evaluate_string_parameter)
        cls.register_type('AnyStr', 
                          r"{Variable}|'.*'{suffix}".format(Variable=cls.get_registered_type_pattern('Variable'), suffix=regex_suffix), 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('Code', 
                          r"[^ ]+", 
                          StepTools.evaluate_scenario_parameter)
        
        # Generic types
        cls.register_type('Enum', 
                          r"{Variable}|\w+".format(Variable=cls.get_registered_type_pattern('Variable')), 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('Dict', 
                          r"{Variable}|\{{.*\}}".format(Variable=cls.get_registered_type_pattern('Variable')), 
                          StepTools.evaluate_scenario_parameter)
        cls.register_type('List', 
                          r"{Variable}|\[.*\]".format(Variable=cls.get_registered_type_pattern('Variable')), 
                          StepTools.evaluate_list_scenario_parameter)


