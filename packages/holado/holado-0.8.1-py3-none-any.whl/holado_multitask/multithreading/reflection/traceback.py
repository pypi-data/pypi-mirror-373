
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


import traceback
from holado_core.common.tools.tools import Tools


def get_stack(limit=None, start=0):
    """
    Get the call stack at the point of the caller.
    
    @param limit: the number of frames to get (default: all remaining frames)
    @param start: the offset of the first frame preceding the caller (default 0 means the method calling get_stack)
    """   
    
    stack = traceback.extract_stack(limit=limit+2 if limit is not None else None)
    return stack[:-1-start]
    
def represent_stack(limit=None, start=0, indent=0):
    frames = get_stack(limit, start+1)
    return Tools.indent_string(indent, "".join(traceback.format_list(frames)))


    