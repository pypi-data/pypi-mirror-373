
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_rest.api.rest.rest_client import RestClient
from holado_python.common.tools.datetime import DateTime
import datetime
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class MockServerClient(RestClient):
    """
    MockServer client to its exposed REST API
    """
    
    @classmethod
    def is_available(cls):
        return RestClient.is_available()
    
    def __init__(self, name, url, headers=None):
        super().__init__(name, url, headers)
    
    def retrieve_request_responses(self, since_datetime=None, format_=None):
        """
        :param since_datetime: if defined, return only responses sent after this datetime
        :param format_: define response format (default: "json" ; supported values: "json", "log_entries")
        :returns: result of API 'retrieve' with type='request_responses'.
        """
        params = {'type': 'request_responses'}
        if format_ is not None:
            params['format'] = format_
            
        result = self.put('/mockserver/retrieve', params=params)
        res = self.response_result(result)
        
        if since_datetime is not None:
            if not isinstance(since_datetime, datetime.datetime):
                raise TechnicalException(f"Unmanaged since_datetime type '{Typing.get_object_class_fullname(since_datetime)}' (expected: datetime)")
            dt_str = DateTime.datetime_2_str(since_datetime, '%Y-%m-%d %H:%M:%S.%f')[:-3]
            res = [r for r in res if r['timestamp'] >= dt_str]
        
        return res
    
    def retrieve_pushed_data(self, since_datetime=None, method=None, body_type=None):
        result = self.retrieve_request_responses(since_datetime)
        
        res = []
        for request_response in result:
            if method is not None and request_response["httpRequest"]["method"] != method:
                continue
            if body_type is not None and isinstance(request_response["httpRequest"]["body"], dict) \
                    and "type" in request_response["httpRequest"]["body"] \
                    and request_response["httpRequest"]["body"]["type"] != body_type:
                continue
            
            if isinstance(request_response["httpRequest"]["body"], dict) and "type" in request_response["httpRequest"]["body"]:
                if "string" in request_response["httpRequest"]["body"]:
                    res.append(request_response["httpRequest"]["body"]["string"])
                else:
                    raise TechnicalException(f"Unmanaged type of body: {request_response['httpRequest']['body']}")
            else:
                res.append(request_response["httpRequest"]["body"])
        
        return res




