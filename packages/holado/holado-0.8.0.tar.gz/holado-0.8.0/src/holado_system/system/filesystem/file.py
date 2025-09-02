
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

from holado.common.handlers.object import DeleteableObject
import os
from typing import AnyStr, List


class File(DeleteableObject):
    """
    Manage a file
    """

    def __init__(self, path, **open_kwargs):
        super().__init__(f"file '{path}'")

        self.__path = path
        self.__auto_flush = True
        self.__file = None
        
        if open_kwargs:
            self.open(**open_kwargs)

    def _delete_object(self):
        self.close()
        
    @property
    def path(self):
        return self.__path

    @property
    def internal_file(self):
        return self.__file

    def open(self, auto_flush=True, **kwargs):
        self.__auto_flush = auto_flush
        self.__file = open(self.__path, **kwargs)

    def close(self):
        if self.__file:
            self.__file.close()
            self.__file = None

    def write(self, data):
        res = self.internal_file.write(data)
        if self.__auto_flush:
            self.internal_file.flush()
        return res

    def writelines(self, lines, add_line_sep=True):
        for line in lines:
            self.internal_file.write(line)
            if add_line_sep and not line.endswith(os.linesep):
                self.internal_file.write(os.linesep)
        if self.__auto_flush:
            self.internal_file.flush()

    def read(self, n: int = -1) -> AnyStr:
        return self.internal_file.read(n)

    def readline(self, limit: int = -1) -> AnyStr:
        return self.internal_file.readline(limit)

    def readlines(self, hint: int = -1) -> List[AnyStr]:
        return self.internal_file.readlines(hint)

