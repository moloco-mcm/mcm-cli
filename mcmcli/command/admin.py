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

