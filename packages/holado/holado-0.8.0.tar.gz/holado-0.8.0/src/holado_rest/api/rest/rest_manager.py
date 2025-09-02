
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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools
from holado_rest.api.rest.rest_client import RestClient
from holado.common.handlers.undefined import undefined_argument


logger = logging.getLogger(__name__)



class RestManager(object):
    """
    Manage REST features, agnostic to internal REST library.
    """
    
    def __init__(self, default_client_class=RestClient):
        self.__default_client_class = default_client_class
    
    def new_client(self, name, **kwargs):
        url = kwargs.pop("url")
        if name is None:
            name = f"RestClient({url})"
        headers = Tools.pop_sub_kwargs(kwargs, "headers.")
        authentication = Tools.pop_sub_kwargs(kwargs, "authentication.")
        ssl_kwargs = Tools.pop_sub_kwargs(kwargs, "ssl.")
        rest_client_kwargs = Tools.pop_sub_kwargs(kwargs, "rest_client.")
        rest_client_class = rest_client_kwargs.pop("class", self.__default_client_class)
        if len(kwargs) > 0:
            raise TechnicalException(f"Unmanaged arguments: {kwargs}")
    
        res = self._new_rest_client(name, url, headers, client_class=rest_client_class, **rest_client_kwargs)
        
        # Manage authentication if needed
        if len(authentication) > 0:
            if 'user' in authentication:
                if type(authentication['user']) is tuple and len(authentication['user']) == 2:
                    res.authenticate_by_user(authentication['user'][0], authentication['user'][1])
                else:
                    raise FunctionalException(f"When authenticating by user, the value has to be in format: ('{{USER}}', '{{PASSWORD}}')  (obtained: {authentication['user']})")
            elif 'token' in authentication:
                if type(authentication['token']) is tuple and len(authentication['token']) == 2:
                    res.authenticate_by_token(authentication['token'][0], authentication['token'][1])
                else:
                    raise FunctionalException(f"When authenticating by user, the value has to be in format: ('{{TOKEN_TYPE}}', '{{ACCESS_TOKEN}}')  (obtained: {authentication['token']})")
            else:
                raise TechnicalException(f"Unmanaged authentication type '{authentication.keys()}' (possible authentication types: 'user', 'token'")
        
        # Manage ssl if needed
        if len(ssl_kwargs) > 0:
            res.with_ssl(ssl_kwargs)
        
        return res
    
    def _new_rest_client(self, name, url, headers=None, client_class=RestClient, **kwargs):
        return client_class(name, url, headers=headers, **kwargs)
    
    
            