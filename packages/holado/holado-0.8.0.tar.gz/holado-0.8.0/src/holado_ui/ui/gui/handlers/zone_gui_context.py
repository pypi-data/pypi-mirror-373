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
from holado.common.handlers.enums import AutoNumber
from holado_core.common.exceptions.technical_exception import TechnicalException


class InformationTypes(AutoNumber):
    """
    Information type
    """
    
    Id = ()
    Name = ()
    Label = ()
    

class ZoneGUIContext(UIContext):
    """ Zone context.
    """
    
    def __init__(self, previous_context, information_type:InformationTypes, information):
        super().__init__(previous_context)
        self.__information_type = information_type
        self.__information = information
    
    @property
    def information_type(self) -> InformationTypes:
        """
        @return Information type
        """
        return self.__information_type
    
    @property
    def information(self):
        """
        @return Information
        """
        return self.__information
    
    def get_description(self):
        """
        @return Context description
        """
        res = "zone "
        
        if self.information_type == InformationTypes.Id:
            res += f"of id '{self.information}'"
        elif self.information_type == InformationTypes.Label:
            res += f"'{self.information}'"
        elif self.information_type == InformationTypes.Name:
            res += f"named '{self.information}'"
        else:
            raise TechnicalException(f"Unmanaged information type '{self.information_type.name}'")
        
        return res
    
    @classmethod
    def main_zone(cls):
        """
        @return Context for main zone
        """
        return cls(None, InformationTypes.Name, "main")
        
    @classmethod
    def zones_by_labels(cls, *labels):
        """
        @param labels Labels
        @return Context for successive zones with given labels
        """
        res = None
        for label in labels:
            res = cls(res, InformationTypes.Label, label)
        return res
    
    
    
    
    
    