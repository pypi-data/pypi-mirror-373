
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


#################################################
#
# Patches are done to follow ITU recommendation:
# https://www.e-navigation.nl/sites/default/files/R-REC-M.1371-5-201402-I!!PDF-E_1.pdf
#
#################################################


import logging

logger = logging.getLogger(__name__)


# Since Django 4.1, requires_system_checks cannot be a boolean anymore.
# Framework djangogrpcframework is not maintained anymore.
# Patch it by removing reference to requires_system_checks

try:
    import django_grpc_framework  # @UnusedImport
    with_django_grpc_framework = True
except:
    with_django_grpc_framework = True

if with_django_grpc_framework:
    from django_grpc_framework.management.commands.grpcrunserver import Command  # @UnusedImport
    del Command.requires_system_checks


