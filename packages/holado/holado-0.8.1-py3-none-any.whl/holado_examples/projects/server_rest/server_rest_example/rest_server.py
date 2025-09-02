
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


# Uncomment next lines to insert holado sources when using a clone of holado project rather than holado package 
# from initialize_holado import insert_holado_source_paths
# insert_holado_source_paths()

import os
from holado_django.server.django_server import DjangoServer
import logging

logger = logging.getLogger(__name__)



if __name__ == "__main__":
    here = os.path.abspath(os.path.dirname(__file__))
    django_project_path = os.path.join(here, "rest_api")
     
    server = DjangoServer("Example of REST server", django_project_path)
    server.start()
    try:
        server.join()
    except (InterruptedError, KeyboardInterrupt):
        pass
    
