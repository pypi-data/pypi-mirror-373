
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
logger_trace = logging.getLogger(__name__ + ".trace")

try:
    import minio  # @UnusedImport
    from minio.api import Minio
    with_minio = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"MinioS3Client is not available. Initialization failed on error: {exc}")
    with_minio = False


class MinioS3Client(object):
    class _TraceStreamWriter(object):
        def write(self, data):
            logger_trace.debug(f"HTTP trace: {data}")
            
    @classmethod
    def is_available(cls):
        return with_minio
    
    def __init__(self, **kwargs): 
        self.__init_kwargs = dict(kwargs)
        do_trace = kwargs.pop('trace') if 'trace' in kwargs else False
        self.__internal_client = Minio(**kwargs)
        
        if do_trace:
            self.activate_trace(True)
    
    if with_minio:
        @property
        def internal_client(self) -> Minio:
            return self.__internal_client
    
    @property
    def endpoint(self) -> str:
        return self.__init_kwargs['endpoint']
    
    @property
    def access_key(self) -> str:
        return self.__init_kwargs['access_key']
    
    @property
    def secret_key(self) -> str:
        return self.__init_kwargs['secret_key']
    
    def activate_trace(self, status):
        if status and self.internal_client._trace_stream is not None or not status and self.internal_client._trace_stream is None:
            return
        
        if status:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("Activating HTTP trace in Minio client")
            self.internal_client.trace_on(MinioS3Client._TraceStreamWriter())
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug("Deactivating HTTP trace in Minio client")
            self.internal_client.trace_off()
