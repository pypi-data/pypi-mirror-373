
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
from holado.common.handlers.undefined import undefined_value


logger = logging.getLogger(__name__)

try:
    import redis  # @UnresolvedImport
    with_redis = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"RedisClient is not available. Initialization failed on error: {exc}")
    with_redis = False


class RedisClient(object):
    """
    Redis client
    
    This class adds high level commands to a Redis client.
    All native commands (https://redis.io/docs/latest/commands/) are callable through "internal_client" property.
    """
    
    @classmethod
    def is_available(cls):
        return with_redis
    
    def __init__(self, name, **kwargs):
        self.__name = name
        self.__kwargs = kwargs

        self.__client = self.__new_client(**kwargs)
        
        # Verify server responds to ping
        try:
            self.ping_server()
        except Exception as exc:
            raise FunctionalException(f"Failed to ping Redis server with parameters: {self.__kwargs}") from exc
        
    @property
    def name(self):
        return self.__name
    
    @property
    def host(self):
        if 'host' in self.__kwargs:
            return self.__kwargs['host']
        else:
            raise TechnicalException(f"'host' is not in client parameters (defined parameters: {self.__kwargs})")
        
    @property
    def port(self):
        if 'port' in self.__kwargs:
            return self.__kwargs['port']
        else:
            raise TechnicalException(f"'port' is not in client parameters (defined parameters: {self.__kwargs})")
        
    def __new_client(self, **kwargs):
        redis_kwargs = dict(kwargs)
        if 'credential_provider.type' in redis_kwargs:
            cp_type = redis_kwargs.pop('credential_provider.type')
            if cp_type == 'UsernamePassword':
                username = redis_kwargs.pop('credential_provider.username')
                pwd = redis_kwargs.pop('credential_provider.password')
                creds_provider = redis.UsernamePasswordCredentialProvider(username, pwd)
                redis_kwargs['credential_provider'] = creds_provider
            else:
                raise TechnicalException(f"Unexpected credential provider type '{cp_type}' (possible types: 'UsernamePassword')")
            
        return redis.Redis(**redis_kwargs)
    
    if with_redis:
        @property    
        def internal_client(self) -> redis.Redis:
            return self.__client
    
    def ping_server(self, raise_exception=True):
        """
        Ping server.
        If raise_excpetion is True, raise an exception rather than returning False.
        """
        res = self.internal_client.ping()
        if not res and raise_exception:
            raise FunctionalException(f"Redis server {self.host}:{self.port} doesn't respond to ping")
        return res
        
    def exist_key(self, key):
        nb = self.internal_client.exists(key)
        return nb > 0
        
    def get_keys(self, glob_pattern=None, count=undefined_value):
        """
        Get keys of given pattern.
        WARNING: This method should not be used if the number of keys can be huge, otherwise it can take a long time.
                 In this case, it is recommended to change redis use in order to avoid any key pattern.
        @param count: if count is undefined_value (default), internal client 'keys' method is used, else internal client 'scan' method is used
        """
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Getting keys with pattern '{glob_pattern}'...")
        
        if count is undefined_value:
            res = self.internal_client.keys(pattern=glob_pattern)
        else:
            res = []
            cursor = 0
            while True:
                cursor, cur_res = self.internal_client.scan(cursor=cursor, match=glob_pattern, count=count)
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Getting keys with pattern '{glob_pattern}': add {len(cur_res)} keys ; cursor: {cursor}")
                res.extend(cur_res)
                if cursor == 0:
                    break
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Getting keys with pattern '{glob_pattern}' -> {len(res)} keys: {res}")
        return res
        
    def delete_keys_matching(self, glob_pattern=None, recursive=False, raise_exception=True, do_unlink=True):
        """
        Delete keys of given pattern.
        WARNING: This method should not be used if the number of keys can be huge, otherwise it can take a long time.
                 In this case, it is recommended to use internal client 'delete' or 'unlink' method.
        @param do_unlink: If try, internal client 'unlink' method is used instead of 'delete' (default: True)
        """
        keys = self.get_keys(glob_pattern)
        while len(keys) > 0:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Deleting {len(keys)} keys: {keys}")
            for key in keys:
                self.delete_key(key, raise_exception=False, do_unlink=do_unlink)
    
            # Verify delete succeeded
            old_keys = keys
            keys = self.get_keys(glob_pattern)
            not_deleted_keys = set(keys).intersection(set(old_keys))
            if not recursive and len(not_deleted_keys) > 0:
                msg = f"{len(keys)} keys are not deleted and still present: {keys}"
                if raise_exception:
                    raise TechnicalException(msg)
                else:
                    logger.warning(msg)
    
            # Manage recursive
            if not recursive:
                break
            
    def delete_key(self, key, check_exist_before=False, raise_exception=True, do_unlink=True):
        """
        Delete a key.
        If check_exist_before is True and key doesn't exist, it returns immediately.
        @param do_unlink: If True, internal client 'unlink' method is used instead of 'delete' (default: True)
        """
        if check_exist_before and not self.exist_key(key):
            return
        
        if do_unlink:
            result = self.internal_client.unlink(key)
        else:
            result = self.internal_client.delete(key)
        if result == 0:
            if self.exist_key(key):
                msg = f"Failed to delete key '{key}'."
                if raise_exception:
                    raise TechnicalException(msg)
                else:
                    logger.warning(msg)
            else:
                msg = f"Failed to delete key '{key}', it doesn't exist."
                logger.warning(msg)
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Deleted key '{key}'")
            
        