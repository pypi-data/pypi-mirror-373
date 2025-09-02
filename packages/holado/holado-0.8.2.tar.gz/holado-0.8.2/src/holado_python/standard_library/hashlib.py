# -*- coding: utf-8 -*-

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
import hashlib
from holado_core.common.exceptions.technical_exception import TechnicalException

logger = logging.getLogger(__name__)




class HashTools(object):
    
    @classmethod
    def code(cls, content, code_size=None, prefix=None):
        hex_size = code_size
        if hex_size is not None:
            if prefix is not None:
                hex_size = hex_size - len(prefix)
            hex_size = hex_size // 2 * 2
        
        res = cls.hexblake2(content, hex_size=hex_size)
        
        if prefix is not None:
            res = prefix + res
        
        return res
    
    @classmethod
    def hash(cls, algorithm_name, content, hash_size=None, **hash_kwargs):
        hash_obj = hashlib.new(algorithm_name, **hash_kwargs)
        cls._update_hash(hash_obj, content)
        res = hash_obj.digest()
        
        # Truncate result size if needed
        if hash_size is not None:
            if not isinstance(hash_size, int):
                raise TechnicalException(f"Parameter size must be an integer")
            res = res[:hash_size]
        
        return res
    
    @classmethod
    def hexhash(cls, algorithm_name, content, hex_size=None, **hash_kwargs):
        hash_obj = hashlib.new(algorithm_name, **hash_kwargs)
        cls._update_hash(hash_obj, content)
        res = hash_obj.hexdigest()
        
        # Truncate result size if needed
        if hex_size is not None:
            if not isinstance(hex_size, int):
                raise TechnicalException(f"Parameter hex_size must be an integer")
            res = res[:hex_size]
        
        return res
        
    @classmethod
    def hexmd5(cls, content):
        hash_obj = hashlib.md5()
        cls._update_hash(hash_obj, content)
        return hash_obj.hexdigest()
    
    @classmethod
    def hexblake2(cls, content, hex_size=None, **hash_kwargs):
        if hex_size is not None:
            if isinstance(hex_size, int):
                digest_size = hex_size // 2
            else:
                raise TechnicalException(f"Parameter hex_size must be an integer")
            hash_kwargs['digest_size'] = digest_size
        
        hash_obj = hashlib.blake2b(**hash_kwargs)
        cls._update_hash(hash_obj, content)
        return hash_obj.hexdigest()
    
    @classmethod
    def _update_hash(cls, hash_obj, content):
        # Manage list separately for memory purpose
        done = False
        if not isinstance(content, str): 
            try:
                for cont in content:
                    if type(cont) != bytes:
                        cont = cont.encode('utf-8')
                    hash_obj.update(cont)
                done = True
            except TypeError:
                done = False
    
        if not done:
            if type(content) != bytes:
                content = content.encode('utf-8')
            hash_obj.update(content)
    
    
    
    
    
