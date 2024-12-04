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
from datetime import datetime, timedelta, timezone
from mcmcli.data.error import Error
from mcmcli.data.item_blocking_result import ItemBlockingResult
from mcmcli.requests import CurlString, api_request
from typing import Optional

import mcmcli.command.account
import mcmcli.command.auth
import mcmcli.command.config
import mcmcli.command.wallet
import mcmcli.requests
import sys
import typer

app = typer.Typer(add_completion=False)

def _create_admin_command(profile):
    auth = mcmcli.command.auth.AuthCommand(profile)
    _, error, token = auth.get_token()
    if error:
        print(f"ERROR: {error.message}")
        return None
    return AdminCommand(profile, auth, token.token)

@app.command()
def list_wallet_balances(
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    List the wallet balances of all of the ad accounts
    """
    admin = _create_admin_command(profile)
    if admin is None:
        return
    admin.list_wallet_balances()


@app.command()
def block_item(
    item_id: str = typer.Option(help="Item ID"),
    account_id: str = typer.Option(None, help="The Ad Account ID is applicable only for MSPI catalogs. If this value is provided, only the item associated with the specified seller ID will be removed from ad serving. If it is not provided, the specified item will be removed for all sellers in the MSPI catalog."),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    profile: str = typer.Option("default", help="Profile name of the MCM CLI."),
):
    """
    Item Kill Switch Command.
    This API immediately blocks an item or an ad account item from appearing in ads by marking it as “blocked.”
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # print(f"invoked block_item(item_id={item_id}, account_id={account_id}, blocked='Requested at {timestamp}')");
    admin = _create_admin_command(profile)
    if admin is None:
        return
    
    curl, error, result = admin.block_item(item_id=item_id, account_id=account_id, to_curl=to_curl)
    if curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return
    
    print(result.model_dump_json())
    return

class AdminCommand:
    def __init__(
        self,
        profile,
        auth_command: mcmcli.command.auth.AuthCommand,
        token
    ):
        self.profile = profile
        self.auth_command = auth_command
        self.config = mcmcli.command.config.get_config(profile)
        mcmcli.command.config.assert_config_exists(self.config)

        self.token = token
        self.api_base_url = f"{self.config['management_api_hostname']}/rmp/mgmt/v1/platforms/{self.config['platform_id']}"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def block_item(
        self,
        item_id,
        account_id,
        to_curl,
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        Optional[ItemBlockingResult],
    ]:
        _api_url = f"{self.api_base_url}/item-status-bulk"
        _requested_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        _payload = { 
            "items": [{
                "item_id": item_id,
                "seller_id": account_id,
                "updated_time": _requested_at,
                "blocked": f'Requested at {_requested_at}',
            }]
        }
        if account_id is None:
            del _payload["items"][0]["seller_id"]
        
        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None
        return None, None, ItemBlockingResult(**json_obj)
    
    def list_wallet_balances(
        self
    ):
        ac = mcmcli.command.account.AccountCommand(self.profile, self.auth_command, self.token)
        wc = mcmcli.command.wallet.WalletCommand(self.profile, self.auth_command, self.token)
        _, error, accounts = ac.list_accounts()
        if error:
            print(error, file=sys.stderr, flush=True)
            return

        print("ad_account_title, ad_account_id, credit_balance, prepaid_balance")
        for id in accounts:
            _, error, wallet = wc.get_balance(id, to_curl=False)
            if error:
                continue
            w0 = wallet.accounts[0]
            w1 = wallet.accounts[1]
            credits = w0 if w0.type == 'CREDITS' else w1
            prepaid = w1 if w1.type == 'PRE_PAID' else w0
            credits = int(credits.balance.amount_micro) / 1000000
            prepaid = int(prepaid.balance.amount_micro) / 1000000
            print(f'"{accounts[id].title}", {id}, {credits}, {prepaid}')

