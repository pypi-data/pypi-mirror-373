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


def dependencies():
    return ['holado_value']

def register():
    from holado.common.context.session_context import SessionContext
    
    from holado_scripting.common.tools.dynamic_text_manager import DynamicTextManager
    SessionContext.instance().services.register_service_type("dynamic_text_manager", 
                            lambda: DynamicTextManager("global"),
                            lambda m: m.initialize(SessionContext.instance().unique_value_manager) )
    
    from holado_scripting.common.tools.variable_manager import VariableManager
    SessionContext.instance().services.register_service_type("variable_manager", VariableManager,
                            lambda m: m.initialize(SessionContext.instance().dynamic_text_manager, 
                                                   SessionContext.instance().unique_value_manager) )
    
    
    from holado_scripting.common.tools.expression_evaluator import ExpressionEvaluator
    SessionContext.instance().services.register_service_type("expression_evaluator", ExpressionEvaluator,
                            lambda m: m.initialize(SessionContext.instance().dynamic_text_manager, 
                                                   SessionContext.instance().unique_value_manager,
                                                   SessionContext.instance().text_interpreter, 
                                                   SessionContext.instance().variable_manager) )
    
    from holado_scripting.text.interpreter.text_interpreter import TextInterpreter
    SessionContext.instance().services.register_service_type("text_interpreter", TextInterpreter,
                            lambda m: m.initialize(SessionContext.instance().variable_manager, 
                                                   SessionContext.instance().expression_evaluator, 
                                                   SessionContext.instance().text_verifier, 
                                                   SessionContext.instance().dynamic_text_manager) )
    
    from holado_scripting.text.verifier.text_verifier import TextVerifier
    SessionContext.instance().services.register_service_type("text_verifier", TextVerifier,
                            lambda m: m.initialize(SessionContext.instance().variable_manager, 
                                                   SessionContext.instance().expression_evaluator, 
                                                   SessionContext.instance().text_interpreter) )


