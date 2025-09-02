
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
import re
from holado.common.handlers.object import Object, DeleteableObject
from holado_core.common.tools.tools import Tools
from holado.holado_config import Config
from contextlib import contextmanager
from typing import NamedTuple
import threading
from holado.common.tools.gc_manager import GcManager
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class VariableManager(DeleteableObject):
    """
    Manage variables as couples of (name, value).
    
    Variable names can contain any character except: ".", "["
    Variable names can end by any dynamic suffix symbol, the symbol will be replaced by the associated suffix.
    """

    def __init__(self, parent=None):
        super().__init__("variable manager")
        
        self.__parent = parent
        self.__dynamic_text_manager = None
        self.__unique_value_manager = None
        self.__variables = {}
        
        # Manage temporary variables
        self.__temporary_variables_lock = threading.Lock()
        self.__temporary_variables = {}
        
    def initialize(self, dynamic_text_manager, unique_value_manager):
        self.__dynamic_text_manager = dynamic_text_manager
        self.__unique_value_manager = unique_value_manager
    
    @property
    def parent(self):
        return self.__parent
    
    def _delete_object(self):
        # Delete all variables
        names = set(self.__variables.keys())
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Removing {len(names)} variables: {names}")
        for index, name in enumerate(names):
            if name in self.__variables:
                value = self.__variables[name]
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Removing variable {index+1}/{len(names)}: '{name}' (type: {Typing.get_object_class_fullname(value)})")
                self.unregister_variable(name, through_parent=False, delete_value=True)
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Finished to remove {len(names)} variables: {names}")
                
        # # Clear variables
        # self.__variables.clear()
        
    @contextmanager
    def temporary_variables(self):
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        
        uid = MultitaskManager.get_thread_uid()
        with self.__temporary_variables_lock:
            if uid not in self.__temporary_variables:
                self.__temporary_variables[uid] = NamedTuple("TempVars", counter=int, variable_names=list)
                self.__temporary_variables[uid].counter = 0
                self.__temporary_variables[uid].variable_names = set()
            self.__temporary_variables[uid].counter += 1
            
        try:
            yield None
        finally:
            with self.__temporary_variables_lock:
                self.__temporary_variables[uid].counter -= 1
                if self.__temporary_variables[uid].counter == 0:
                    logger.info(f"Unregistering temporary variables: {self.__temporary_variables[uid].variable_names}")
                    for var_name in self.__temporary_variables[uid].variable_names:
                        if self.exists_variable(var_name, through_parent=False):
                            self.unregister_variable(var_name, through_parent=False, delete_value=True)
                    del self.__temporary_variables[uid]
                    GcManager.collect()
        
        
    def new_local_variable_name(self, sub_name=None):
        if sub_name is not None:
            return f"__VAR_{sub_name}_{self.__unique_value_manager.new_string(do_log=False)}__"
        else:
            return f"__VAR{self.__unique_value_manager.new_string(do_log=False)}__"
    
    def new_variable_name(self):
        res = None
        while True:
            res = self.new_local_variable_name()
            if not self.exists_variable(variable_name=res):
                break
        return res
    
    def evaluate_variable_name(self, var_name):
        if var_name.endswith(Config.DYNAMIC_SYMBOL):
            return self.__dynamic_text_manager.get(var_name[:-1])
        elif var_name.endswith(Config.THREAD_DYNAMIC_SYMBOL):
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            return self.__dynamic_text_manager.get(var_name[:-1], scope=MultitaskManager.get_thread_id())
        elif var_name.endswith(Config.UNIQUE_SYMBOL):
            return var_name[:-1] + self.__unique_value_manager.new_string(padding_length=Config.unique_string_padding_length)
        else:
            return var_name
    
    def register_variable(self, variable_name, value, accept_expression=True, log_level=logging.INFO):
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Setting variable: {variable_name}=[{value}] (type: {Typing.get_object_class_fullname(value)})...")
        
        names = variable_name.rsplit('.', 1)
        if accept_expression and len(names) > 1:
            if not self.exists_variable(expression=names[0]):
                self.register_variable(names[0], Object())
            var = self.get_value(names[0], through_patent=False)
            setattr(var, names[1], value)
            if Tools.do_log(logger, log_level):
                logger.log(log_level, f"Set variable expression: {variable_name}=[{value}] (type: {Typing.get_object_class_fullname(value)})")
        else:
            var_name = self.evaluate_variable_name(variable_name)
            self.__variables[var_name] = value
            if Tools.do_log(logger, log_level):
                logger.log(log_level, f"Set variable: {var_name}=[{value}] (type: {Typing.get_object_class_fullname(value)})")
                
            # Manage temporary variables
            uid = MultitaskManager.get_thread_uid()
            with self.__temporary_variables_lock:
                if uid in self.__temporary_variables:
                    self.__temporary_variables[uid].variable_names.add(var_name)
                
    def unregister_variable(self, variable_name, through_parent=False, delete_value=False):
        var_name = self.evaluate_variable_name(variable_name)
        if self.exists_variable(var_name, through_parent=False):
            value = self.__variables[var_name]
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Unregistering variable '{var_name}' (type: {Typing.get_object_class_fullname(value)})")
                
            if delete_value and isinstance(value, DeleteableObject):
                try:
                    value.delete_object()
                except Exception:
                    logger.exception(f"Catched exception while deleting object '{var_name}' (type: {Typing.get_object_class_fullname(value)})")
                else:
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"Deleted variable '{var_name}' (type: {Typing.get_object_class_fullname(value)})")
            
            del self.__variables[var_name]
        elif through_parent and self.parent:
            return self.parent.unregister_variable(variable_name, through_parent=through_parent, delete_value=delete_value)
        else:
            raise FunctionalException(f"Variable '{var_name}' has not been found. Missing initialisation ?")
        
    def pop_variable(self, variable_name):
        res = self.get_variable_value(variable_name, through_parent=False)
        self.unregister_variable(variable_name, through_parent=False, delete_value=False)
        return res
    
    def get_variable_value(self, variable_name, attributes = [], through_parent=True):
        # Get variable value
        var_name = self.evaluate_variable_name(variable_name)
        if self.exists_variable(var_name, through_parent=False):
            res = self.__variables[var_name]
        elif through_parent and self.parent:
            return self.parent.get_variable_value(variable_name, attributes)
        else:
            raise FunctionalException("Variable '{}' has not been found. Missing initialisation ?".format(variable_name))
        
        # If needed, call attributes
        for attr in attributes:
            res = getattr(res, attr)
        
        return res

    def get_value(self, expression, through_patent=True):
        res = None
        
        if self.is_variable_expression(expression, through_parent=through_patent):
            try:
                res = self.eval_variable_expression(expression, through_parent=through_patent)
            except (SyntaxError, NameError):
                raise FunctionalException("Expression '{}' is not evaluable. Is an initialization missing ?".format(expression))
        else:
            res = self.get_variable_value(expression, through_parent=through_patent)
        
        return res

    def set_value(self, expression, value, through_parent=True):
        if self.is_variable_expression(expression, through_parent=through_parent):
            try:
                self.exec_set_variable_expression(expression, value, through_parent=through_parent)
            except (SyntaxError, NameError):
                raise FunctionalException("Expression '{}' is not evaluable. Is an initialization missing ?".format(expression))
        else:
            self.register_variable(expression, value)

    def exists_variable(self, variable_name=None, expression=None, through_parent=True):
        if expression is not None:
            expression = expression.strip()
            m_operator = re.search("[.[]", expression)
            if m_operator:
                # Return directly False if found operator is not an operator
                # EKL: Why this check is done ???
                if m_operator.group(0) not in ['.', '[']:
                    return False
                # Begin by looking for variable existance
                variable_name = expression[:m_operator.start()]
            else:
                variable_name = expression
        
        var_name = self.evaluate_variable_name(variable_name)
        res = var_name in self.__variables
        
        # For expression, look if sub variable exist
        if res and expression is not None and variable_name != expression:
            try:
                _ = self.eval_variable_expression(expression, through_parent=False)
            except:
                res = False
            else:
                res = True
        
        if not res and through_parent and self.parent:
            if expression is not None:
                res = self.parent.exists_variable(expression=expression)
            else:
                res = self.parent.exists_variable(variable_name=variable_name)
        return res
    
    def is_variable_expression(self, expression, through_parent=True):
        try:
            var_name, expr_rest = self.__extract_expression_name(expression)
            return len(var_name) > 0 and self.exists_variable(var_name, through_parent=through_parent) and len(expr_rest) > 0
        except SyntaxError:
            return False
    
    def eval_variable_expression(self, expression, through_parent=True):
        var_name, expr_rest = self.__extract_expression_name(expression)
        var_value = self.get_variable_value(var_name, through_parent=through_parent)
        new_var_name = self.new_local_variable_name(sub_name=self.__regular_variable_name(var_name))
        locals()[new_var_name] = var_value
        
        new_expr = f"{new_var_name}{expr_rest}"
        try:
            return eval(new_expr)
        except Exception as exc:
            try:
                var_repr = Tools.represent_object(var_value)
            except:
                var_repr = str(var_value)
            Tools.raise_same_exception_type(exc, f"{exc}\nVariable '{var_name}': {var_repr}", add_from=True)
    
    def exec_set_variable_expression(self, expression, value, through_parent=True, log_level=logging.INFO):
        var_name, expr_rest = self.__extract_expression_name(expression)
        var_value = self.get_variable_value(var_name, through_parent=through_parent)
        new_var_name = self.new_local_variable_name(sub_name=self.__regular_variable_name(var_name))
        locals()[new_var_name] = var_value
        
        new_var_value = self.new_local_variable_name(sub_name='value')
        locals()[new_var_value] = value
        
        new_expr = f"{new_var_name}{expr_rest}={new_var_value}"
        try:
            exec(new_expr)
        except Exception as exc:
            try:
                var_repr = Tools.represent_object(var_value)
            except:
                var_repr = str(var_value)
            # Tools.raise_same_exception_type(exc, f"{exc}\nVariable '{var_name}': {var_repr}", add_from=True)
            raise FunctionalException(f"Failed to set value in variable expression (by exec): {expression}=[{value}] (type: {Typing.get_object_class_fullname(value)})\nVariable '{var_name}': {var_repr}") from exc
        else:
            if Tools.do_log(logger, log_level):
                logger.log(log_level, f"Set value in variable expression (by exec): {expression}=[{value}] (type: {Typing.get_object_class_fullname(value)})")
    
    def __regular_variable_name(self, name):
        return "".join([c if re.match(r'\w', c) else '_' for c in name])
    
    # def set_variable_expression(self, expression, value):
    #     var_name, expr_rest = self.__extract_expression_name(expression)
    #     if len(expr_rest) == 0:
    #         self.register_variable(expression, value)
    #     else:
    #         var_value = self.get_variable_value(var_name)
    #
    #     while len(expr_rest) > 0:
    #

    
    def __extract_expression_name(self, expression):
        regex_name = re.compile("^([^.[]+)(.*)")
        m = regex_name.match(expression)
        if not m:
            raise SyntaxError(f"Expression [{expression}] is not a variable expression")
        var_name, expr_rest = m.group(1), m.group(2)
        var_name = self.evaluate_variable_name(var_name)
        return var_name, expr_rest
        
        
        
        
        
