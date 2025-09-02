
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
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.client import BaseClient
    with_boto3 = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"Boto3S3Client is not available. Initialization failed on error: {exc}")
    with_boto3 = False


class Boto3S3Client(object):
    
    FAKE_DELIMITER = "#$@"
    MAX_KEYS = 1000000
    
    @classmethod
    def is_available(cls):
        return with_boto3
    
    def __init__(self, **kwargs): 
        self.__init_kwargs = dict(kwargs)
        self.__internal_client = boto3.client('s3', **kwargs)
    
    if with_boto3:
        @property
        def internal_client(self) -> BaseClient:
            return self.__internal_client
    
    @property
    def endpoint(self) -> str:
        return self.__init_kwargs['endpoint_url']
    
    @property
    def access_key(self) -> str:
        return self.__init_kwargs['aws_access_key_id']
    
    @property
    def secret_key(self) -> str:
        return self.__init_kwargs['aws_secret_access_key']
    

