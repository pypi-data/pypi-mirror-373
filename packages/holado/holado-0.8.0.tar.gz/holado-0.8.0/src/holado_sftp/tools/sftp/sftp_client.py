
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
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado.common.handlers.object import DeleteableObject
import io
import paramiko
from holado_core.common.tools.path_manager import PathManager
from holado.common.context.session_context import SessionContext

logger = logging.getLogger(__name__)

try:
    import pysftp
    with_pysftp = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"SFTPClient is not available. Initialization failed on error: {exc}")
    with_pysftp = False


class SFTPClient(DeleteableObject):
    @classmethod
    def is_available(cls):
        return with_pysftp
    
    def __init__(self, **connection_kwargs):
        super().__init__("sFTP client")
        
        self.__connection = None
        if len(connection_kwargs) > 0:
            self.connect(**connection_kwargs)
    
    def _delete_object(self):
        if self.__connection:
            self.close_connection()
            
    @property
    def connection(self) -> pysftp.Connection:
        return self.__connection
    
    def connect(self, **connection_kwargs):
        kwargs = dict(connection_kwargs)
        
        if Tools.has_sub_kwargs(kwargs, "cnopts."):
            cnopts_kwargs = Tools.pop_sub_kwargs(kwargs, "cnopts.")
            cnopts = pysftp.CnOpts()
            if "hostkeys" in cnopts_kwargs:
                cnopts.hostkeys = cnopts_kwargs.pop("hostkeys")
            if "log" in cnopts_kwargs:
                cnopts.log = cnopts_kwargs.pop("log")
                SessionContext.instance().path_manager.makedirs(cnopts.log)
            if cnopts_kwargs:
                raise FunctionalException(f"Unmanaged cnopts parameters: {cnopts_kwargs}")
            kwargs["cnopts"] = cnopts
        
        if 'private_key' in kwargs:
            pk = kwargs['private_key']
            if isinstance(pk, str) and pk.startswith('-----'):
                # Replace private key text by a paramiko RSAKey
                privkey = io.StringIO(pk)
                key = paramiko.RSAKey.from_private_key(privkey)
                kwargs['private_key'] = key
        
        local_path = kwargs.pop("local_path") if "local_path" in kwargs else None
        if local_path is not None:
            SessionContext.instance().path_manager.makedirs(local_path)
        
        self.__connection = pysftp.Connection(**kwargs)
        
        if local_path:
            self.lcd(local_path)
        
    def close_connection(self):
        if self.__connection is None:
            raise TechnicalException("Client is not connected")
        
        try:
            self.__connection.close()
        except Exception as exc:  # @UnusedVariable
            #TODO: When this warning is logged during self.__del__, the log is cleared before, thus it is commented
            # logger.warn(f"Error catched while closing RabbitMQ client connection:\n{Tools.represent_exception(exc)}")
            pass
        finally:
            self.__connection = None
        
    @classmethod
    def lcd(cls, path):
        pysftp.cd(path)
    