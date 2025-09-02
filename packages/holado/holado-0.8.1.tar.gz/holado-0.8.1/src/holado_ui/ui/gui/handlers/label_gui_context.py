#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_ui.ui.handlers.ui_context import UIContext



class LabelGUIContext(UIContext):
    """ Label context.
    Context used to find an element associated to a label
    """
    
    def __init__(self, previous_context, label):
        super().__init__(previous_context)
        self.__label = label
    
    @property
    def label(self):
        """
        @return Label
        """
        return self.__label
    
    def get_description(self):
        """
        @return Context description
        """
        return f"label '{self.label}'"
    
    @classmethod
    def for_label(cls, previousContext, label):
        """
        @param previousContext Previous context
        @param label Label
        @return Context for given label
        """
        return cls(previousContext, label)
    
    
    
    
    
    