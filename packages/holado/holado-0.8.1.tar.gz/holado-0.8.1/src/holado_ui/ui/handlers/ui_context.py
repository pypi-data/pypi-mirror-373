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



class UIContext(object):
    """ Base class for information on UI actions context.
    
    For example in GUI windows API, it is usually used as first parameter.
    
    Static or class methods should exist as helpers in sub-classes of UIContext. 
    Examples:
      - main_zone(): context describing main zone in UI.
      - zone_by_labels(...): context describing the successive zones to find by their labels before processing an action.
    """
    
    def __init__(self, previous_context=None):
        self.__previous_context = previous_context
    
    @property
    def previous_context(self):
        """
        @return Previous UI context
        """
        return self.__previous_context
    
    def get_description(self):
        """
        @return Context description
        """
        raise NotImplementedError
    
    
    
    
    
    
    