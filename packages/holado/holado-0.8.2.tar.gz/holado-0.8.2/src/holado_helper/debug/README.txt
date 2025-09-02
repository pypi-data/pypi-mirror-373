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

This module gives some tools for debugging purposes.
Each tool uses internally a third party library.


Existing external tools can be found in following links:
    https://wiki.python.org/moin/PythonDebuggingTools
    
    For memory profiling:
        https://www.datacamp.com/tutorial/memory-profiling-python
        https://stackify.com/top-5-python-memory-profilers/

    For deadlock analyse:
        pystack, py-spy
        
        Commands with py-spy:
            sudo env "PATH=$PATH" py-spy dump --pid XXX --full-filenames > py-spy_dump_summary.txt
            sudo env "PATH=$PATH" py-spy dump --pid XXX --full-filenames --locals --subprocesses > py-spy_dump_details.txt
            sudo env "PATH=$PATH" py-spy dump --pid XXX --full-filenames --locals --subprocesses --json > py-spy_dump_details.json
        

