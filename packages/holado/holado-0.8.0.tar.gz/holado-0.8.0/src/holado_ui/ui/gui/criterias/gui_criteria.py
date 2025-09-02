#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_core.common.criterias.tools.criteria_context import CriteriaContext
from holado_core.common.criterias.tools.criteria_parameters import CriteriaParameters
import logging
from holado_ui.ui.gui.criterias.enums import CheckEditableModes
from holado_core.common.criterias.criteria import Criteria

logger = logging.getLogger(__name__)



class GUICriteria(Criteria):
    """ Base class of GUI criteria.
    """
    
    def __init__(self, check_editable:CheckEditableModes=CheckEditableModes.NoCheck):
        self.__check_editable = check_editable
    
    @property
    def check_editable_mode(self):
        return self.__check_editable
    
    def validate_element(self, element, criteria_context: CriteriaContext, criteria_parameters: CriteriaParameters):
        return super().validate_element(element, criteria_context, criteria_parameters) \
            and self.__validate_editable(element, criteria_context, criteria_parameters)

    def __validate_editable(self, element, criteria_context, criteria_parameters):
        if self.check_editable_mode == CheckEditableModes.NoCheck:
            return True
        else:
            if self.check_editable_mode == CheckEditableModes.CheckEditable and self._is_editable(element):
                return True
            elif self.check_editable_mode == CheckEditableModes.CheckNotEditable and not self._is_editable(element):
                return True
        return False
    
    def _is_editable(self, element):
        return False

    def __str__(self):
        res = super().__str__()
        if self.check_editable_mode != CheckEditableModes.NoCheck:
            res += f"&check_editable_mode={self.check_editable_mode.name}"
        return res
    
    