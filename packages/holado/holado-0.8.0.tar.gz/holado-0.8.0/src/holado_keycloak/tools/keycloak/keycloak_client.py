
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
import json
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_system.system.command.command import Command, CommandStates


logger = logging.getLogger(__name__)

class KeycloakClient(object):
    
    def get_token_by_grant_type_password(self, server_url, realm_name, client_id, client_secret, username, password):
        cmd = f"curl --location --request POST '{server_url}/auth/realms/{realm_name}/protocol/openid-connect/token' \
                    --header 'Content-Type: application/x-www-form-urlencoded' \
                    --data-urlencode 'client_id={client_id}' \
                    --data-urlencode 'client_secret={client_secret}' \
                    --data-urlencode 'grant_type=password' \
                    --data-urlencode 'username={username}' \
                    --data-urlencode 'password={password}'"
        command = Command(cmd, do_log_output=True, do_raise_on_stderr=False)
        command.start()
        command.join()
        
        if command.state is not CommandStates.Success:
            raise TechnicalException(f"Error while executing token command [{cmd}] : [{command.stderr}]")
        if command.stdout is not None and 'error' in command.stdout.lower():
            raise FunctionalException(f"Error while getting token for {{server '{server_url}', realm '{realm_name}', client id '{client_id}', username '{username}'}}:\n{command.stdout}")
        
        return json.loads(command.stdout)
    
    def get_token_by_grant_type_refresh_token(self, server_url, realm_name, client_id, client_secret, refresh_token):
        cmd = f"curl --location --request POST '{server_url}/auth/realms/{realm_name}/protocol/openid-connect/token' \
                    --header 'Content-Type: application/x-www-form-urlencoded' \
                    --data-urlencode 'client_id={client_id}' \
                    --data-urlencode 'client_secret={client_secret}' \
                    --data-urlencode 'grant_type=refresh_token' \
                    --data-urlencode 'refresh_token={refresh_token}'"
        command = Command(cmd, do_log_output=True, do_raise_on_stderr=False)
        command.start()
        command.join()
        
        if command.state is not CommandStates.Success:
            raise TechnicalException(f"Error while executing token command [{cmd}] : [{command.stderr}]")
        if command.stdout is not None and 'error' in command.stdout.lower():
            raise FunctionalException(f"Error while getting token for {{server '{server_url}', realm '{realm_name}', client id '{client_id}', refresh_token '{refresh_token}'}}:\n{command.stdout}")
        
        return json.loads(command.stdout)
    
