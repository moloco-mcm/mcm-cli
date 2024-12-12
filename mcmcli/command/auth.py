# Copyright 2023 Moloco, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mcmcli.data.error import Error
from mcmcli.data.token import Token
from mcmcli.requests import CurlString, api_request

import mcmcli.command.config
import mcmcli.logging
import sys
import typer

AuthHeaderName = str
AuthHeaderValue = str

app = typer.Typer(add_completion=False)

#
# Typer commands
#
@app.command()
def get_token(
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = "default",
    ):
    """
    Get a new authentication token.
    """
    auth = AuthCommand(profile)
    curl, error, token = auth.get_token(to_curl)

    if to_curl:
        print(curl)
    elif error:
        print(f"ERROR: {error.message}")
    elif to_json:
        print(token.model_dump_json())
    else:
        print(token.token)


#
# Command executors
#
class AuthCommand:
    def __init__(self, profile):
        self.config = mcmcli.command.config.get_config(profile)
        mcmcli.command.config.assert_config_exists(self.config)

        self.api_base_url = f"{self.config['management_api_hostname']}/rmp/mgmt/v1/platforms/{self.config['platform_id']}"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        self.payload = {
            "auth_type": "CREDENTIAL",
            "credential_type_payload": {
                "email": self.config['admin_email'],
                "password": self.config['admin_password']
            }
        }
    
    def get_token(self, to_curl=False) -> tuple[CurlString, Error, Token]:
        _api_url = f"{self.api_base_url}/tokens"

        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, self.payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        return None, None, Token(**json_obj)
    
    def get_auth_credential(self) -> tuple[Error, AuthHeaderName, AuthHeaderValue]:
        if 'management_api_key' in self.config:
            return None, "x-api-key", self.config['management_api_key']

        _, error, token = self.get_token(to_curl=False)
        if error:
            return error, None, None

        else:
            return None, "Authorization", f"Bearer {token.token}"

