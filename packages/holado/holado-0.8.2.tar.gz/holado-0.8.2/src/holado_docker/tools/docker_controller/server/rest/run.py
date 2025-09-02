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

import connexion
from connexion.resolver import MethodViewResolver

# For debug with HolAdo sources, insert HolAdo source paths
from initialize_holado import insert_holado_source_paths  # @UnresolvedImport
insert_holado_source_paths(with_test_behave=False)

# Initialize HolAdo
from holado import initialize_minimal
initialize_minimal()


app = connexion.FlaskApp(__name__, pythonic_params=True)
app.add_api('openapi.yaml', 
            resolver=MethodViewResolver('api'), resolver_error=501, 
            pythonic_params=True)
