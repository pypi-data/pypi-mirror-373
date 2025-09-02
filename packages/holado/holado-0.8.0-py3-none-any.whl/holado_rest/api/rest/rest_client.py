
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

from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
from holado_core.common.tools.tools import Tools
import json
from holado_core.common.tools.converters.converter import Converter
from holado_json.ipc.json_converter import JsonConverter
from holado.common.handlers.object import Object
from holado.holado_config import Config

logger = logging.getLogger(__name__)

try:
    import requests
    from requests.auth import HTTPBasicAuth
    with_requests = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"RestClient is not available. Initialization failed on error: {exc}")
    with_requests = False


class RestClient(Object):
    """
    REST client
    """
    
    @classmethod
    def is_available(cls):
        return with_requests
    
    def __init__(self, name, url, headers=None):
        super().__init__(name)
        self.__url = url.rstrip('/')
        self.__headers = headers if headers is not None else {}
        self.__kwargs = {}
            
        self.__request_log_level = Config.log_level_rest_request
        
    @property
    def request_log_level(self):
        return self.__request_log_level
    
    @request_log_level.setter
    def request_log_level(self, log_level):
        self.__request_log_level = log_level
    
    def authenticate_by_user(self, user, pwd):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Authenticate with user ({user},{pwd})")
        self.__kwargs['auth'] = HTTPBasicAuth(user, pwd)
    
    def authenticate_by_token(self, token_type, access_token):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Authenticate with token type '{token_type}' and access token '{access_token}'")
        self.__headers['Authorization'] = f'{token_type} {access_token}'
    
    def with_ssl(self, ssl_kwargs):
        unexpected_keys = set(ssl_kwargs.keys()).difference(['verify', 'cert'])
        if len(unexpected_keys) > 0:
            raise TechnicalException(f"Unmanaged SSL arguments: {unexpected_keys}")
        
        self.__kwargs.update(ssl_kwargs)
    
    def add_parameters_to_path(self, path, parameters:dict):
        res = path
        if parameters:
            res += "&" if '?' in res else "?"
            res += "&".join([f"{k}={v}" for k,v in parameters.items()])
        return res
    
    def response_result(self, response, status_ok=200):
        # Get result
        if response.status_code == 204:
            # 204 == "No Content" => return None
            res = None
        else:
            if "application/json" in response.headers['Content-Type'] and len(response.content) > 0:
                res = response.json()
            elif response.headers['Content-Type'].startswith('text'):
                res = response.text
            else:
                res = response.content
        
        # Verify status
        is_ok = isinstance(status_ok, list) and response.status_code in status_ok or response.status_code == status_ok
        if not is_ok:
            raise FunctionalException(f"[{self.name}] Request failed with status {response.status_code} (expected success status: {status_ok}) on error: {res}")
        
        return res
    
    def request(self, method, path, path_parameters=None, **kwargs):
        path = self.add_parameters_to_path(path, path_parameters)
        url = self.__build_url(path=path)
        r_kwargs = self.__build_kwargs(**kwargs)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Calling {method} on url '{url}' with arguments {r_kwargs}")
        try:
            res = requests.request(method, url, **r_kwargs)
        except Exception as exc:
            raise TechnicalException(f"[{self.name}] Failed to process {method} '{url}' with arguments {r_kwargs}") from exc
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"[{self.name}] {method} on url '{url}' => {Tools.represent_object(res, 4)}")
        elif Tools.do_log(logger, self.request_log_level):
            logger.log(self.request_log_level, f"[{self.name}] {method} on url '{url}' => {Tools.represent_object(res, 4, max_level=1)}")
        return res
        
    def delete(self, path, data=None, path_parameters=None, **kwargs):
        return self.request("DELETE", path, path_parameters=path_parameters, data=data, **kwargs)
        
    def get(self, path, data=None, path_parameters=None, **kwargs):
        return self.request("GET", path, path_parameters=path_parameters, data=data, **kwargs)
        
    def patch(self, path, data=None, path_parameters=None, **kwargs):
        return self.request("PATCH", path, path_parameters=path_parameters, data=data, **kwargs)
        
    def post(self, path, data=None, json=None, path_parameters=None, **kwargs):
        return self.request("POST", path, path_parameters=path_parameters, data=data, json=json, **kwargs)
        
    def put(self, path, data=None, path_parameters=None, **kwargs):
        return self.request("PUT", path, path_parameters=path_parameters, data=data, **kwargs)
    
    def __build_url(self, path):
        return f"{self.__url}/{path.lstrip('/')}" 
        
    def __build_kwargs(self, **request_kwargs):
        res = dict(self.__kwargs)
        if self.__headers:
            res['headers'] = self.__headers
        if request_kwargs:
            # Add all kwargs except data
            data = request_kwargs.pop('data', None)
            for key in list(request_kwargs.keys()):
                if key in res and isinstance(res[key], dict):
                    res[key].update(request_kwargs.pop(key))
            res.update(request_kwargs)
            
            # Ensure data is in right format
            if data is not None:
                # Convert data to json object for types not supported by requests.request
                if not (isinstance(data, str) or Converter.is_dict(data) or Converter.is_list(data) or isinstance(data, bytes) or Converter.is_file_like(data)):
                    converter = JsonConverter()
                    data = converter.to_json(data)
                
                # Convert data to string for some content types
                if not isinstance(data, str):
                    content_type = res['headers']['Content-Type'] if 'headers' in res and 'Content-Type' in res['headers'] else None
                    if content_type is not None and 'application/json' in content_type:
                        data = json.dumps(data)
                res['data'] = data
            
        return res 
        
        
