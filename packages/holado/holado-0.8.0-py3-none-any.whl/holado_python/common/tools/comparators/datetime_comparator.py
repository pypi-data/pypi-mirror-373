
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
from holado_core.common.tools.comparators.comparator import Comparator
from holado_core.common.exceptions.functional_exception import FunctionalException
from datetime import datetime, timezone
from holado_python.common.tools.datetime import DateTime
from holado_core.common.handlers.features.resource_by_type import FeatureObjectAndClassResourceByType
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class DatetimeComparator(Comparator, FeatureObjectAndClassResourceByType):
    
    def __init__(self):
        Comparator.__init__(self, "datetime")
        FeatureObjectAndClassResourceByType.__init__(self)
    
    # Define resource description
    
    @classmethod
    def _get_class_resource_description(cls, plural=False):
        if plural:
            return 'class datetime converters'
        else:
            return 'class datetime converter'
    
    def _get_resource_description(self, plural=False):
        if plural:
            return 'datetime converters'
        else:
            return 'datetime converter'
    
    
    # Define how to convert imputs before compare
    
    def _convert_input(self, obj, name):
        convert_func = self.get_resource_for_type(obj=obj, raise_if_not_found=False)
        if convert_func:
            res = convert_func(obj)
        else:
            res = obj
        
        if not isinstance(res, datetime):
            raise FunctionalException(f"{name.capitalize()} value is not a datetime: [{res}] (type: {Typing.get_object_class_fullname(res)})")
        if res.tzinfo is None:
            res = res.replace(tzinfo=timezone.utc)
        return res


# Register default datetime converters

DatetimeComparator.register_resource_for_type_in_class('str', None, 
                                                       lambda o: isinstance(o, str) and DateTime.is_str_datetime(o), 
                                                       DateTime.str_2_datetime)

DatetimeComparator.register_resource_for_type_in_class('int or float', None, 
                                                       lambda o: isinstance(o, int) or isinstance(o, float), 
                                                       DateTime.timestamp_to_datetime)


