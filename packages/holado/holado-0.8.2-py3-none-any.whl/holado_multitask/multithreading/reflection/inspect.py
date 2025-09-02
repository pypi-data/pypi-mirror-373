
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


import inspect
from holado_core.common.tools.tools import Tools


def get_stack(limit=None, start=0):
    """
    Get the call stack at the point of the caller.
    
    @param limit: the number of frames to get (default: all remaining frames)
    @param start: the offset of the first frame preceding the caller (default 0 means the method calling get_stack)
    """   
    
    # The call stack.
    stack = inspect.stack()
    
    # The index of the first frame to print.
    begin = start + 1
    if limit:
        end = min(begin + limit, len(stack))
    else:
        end = len(stack)
    
    return stack[begin:end]
    
def represent_stack(limit=None, start=0, indent=0):
    res_list = []
    for frame in get_stack(limit, start+1):
        file, line, func = frame[1:4]
        res_list.append(f"{file}, line {line} in function {func}")
    return Tools.indent_string(indent, "\n".join(res_list))


    