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

from enum import Enum
from mcmcli.data.error import Error
from mcmcli.data.wallet import Wallet, WalletsWrapper
from mcmcli.requests import CurlString, api_request

import json
import mcmcli.command.auth
import mcmcli.command.config
import mcmcli.logging
import mcmcli.requests
import shortuuid
import sys
import typer

app = typer.Typer(add_completion=False)

class FundType(Enum):
    CREDITS = "CREDITS"
    PRE_PAID = "PRE_PAID"

class OperationType(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"

@app.command()
def balance(
    account_id: str = typer.Option(help="Ad account ID"), 
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = "default",
    ):
    """
    Retrive the current balance of the given ad account's wallet.
    """
    auth = mcmcli.command.auth.AuthCommand(profile)
    curl, error, token = auth.get_token()
    if error:
        print(f"ERROR: {error.message}")
        return

    wc = WalletCommand(profile, auth, token.token)
    curl, error, wallet = wc.get_balance(account_id, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return
    if to_json:
        print(wallet.model_dump_json())
        return
    
    wa0 = wallet.accounts[0]
    wa1 = wallet.accounts[1]

    credits_amount_micro  = wa0.balance.amount_micro if wa0.type == 'CREDITS' else wa1.balance.amount_micro
    pre_paid_amount_micro = wa0.balance.amount_micro if wa0.type == 'PRE_PAID' else wa1.balance.amount_micro
    credit_amount = float(credits_amount_micro) / float(1000000)
    money_amount = float(pre_paid_amount_micro) / float(1000000)

    print(f"Ad account ID = {account_id}")
    print(f"Wallet ID = {wallet.id}")
    print(f"PRE_PAID balance = {money_amount}")
    print(f"CREDITS balance = {credit_amount}")
    return


@app.command()
def deposit(
    account_id: str = typer.Option(help="Ad account ID"), 
    fund_type: FundType = typer.Option(help="CREDITS or PREPAID"),
    fund_amount: float = typer.Option(help="The fund amount to deposit"), 
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = "default",
    ):
    """
    Add or top up the money amount to the current balance of the given ad account's wallet.
    """
    auth = mcmcli.command.auth.AuthCommand(profile)
    curl, error, token = auth.get_token()
    if error:
        print(f"ERROR: {error.message}")
        return

    wc = WalletCommand(profile, auth, token.token)

    # Check the wallet first
    curl, error, wallet = wc.get_balance(account_id, to_curl=False)
    if curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return

    # Deposit funds
    curl, error, wallet = wc.update_balance(OperationType.DEPOSIT, account_id, wallet.id, fund_type, fund_amount, to_curl)
    if curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return
    if to_json:
        print(wallet.model_dump_json())
        return

    wa0 = wallet.accounts[0]
    wa1 = wallet.accounts[1]
    credits_amount_micro  = wa0.balance.amount_micro if wa0.type == 'CREDITS' else wa1.balance.amount_micro
    pre_paid_amount_micro = wa0.balance.amount_micro if wa0.type == 'PRE_PAID' else wa1.balance.amount_micro
    credits_amount  = float(credits_amount_micro)  / float(1000000)
    pre_paid_amount = float(pre_paid_amount_micro) / float(1000000)

    print(f"Funds have been deposited into the wallet. The current balance for ad account ID {account_id} is {pre_paid_amount} in PRE_PAID and {credits_amount} in CREDITS.")
    return

@app.command()
def withdraw(
    account_id: str = typer.Option(help="Ad account ID"), 
    fund_type: FundType = typer.Option(help="CREDITS or PREPAID"),
    fund_amount: float = typer.Option(help="The amount of credit to add"), 
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = "default",
    ):    
    """
    Withdraws the money amount from the current balance of the given ad account's wallet.
    """
    auth = mcmcli.command.auth.AuthCommand(profile)
    curl, error, token = auth.get_token()
    if error:
        print(f"ERROR: {error.message}")
        return

    wc = WalletCommand(profile, auth, token.token)

    # Check the wallet first
    curl, error, wallet = wc.get_balance(account_id, to_curl=False)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return

    # Withdraw funds
    curl, error, wallet = wc.update_balance(OperationType.WITHDRAW, account_id, wallet.id, fund_type, fund_amount, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return
    if to_json:
        print(wallet.model_dump_json())
        return

    wa0 = wallet.accounts[0]
    wa1 = wallet.accounts[1]
    credits_amount_micro  = wa0.balance.amount_micro if wa0.type == 'CREDITS' else wa1.balance.amount_micro
    pre_paid_amount_micro = wa0.balance.amount_micro if wa0.type == 'PRE_PAID' else wa1.balance.amount_micro
    credits_amount  = float(credits_amount_micro)  / float(1000000)
    pre_paid_amount = float(pre_paid_amount_micro) / float(1000000)

    print(f"Funds were withdrawn out of the wallet. The current balance of ad account ID {account_id} is {pre_paid_amount} for PRE_PAID and {credits_amount} for CREDITS.")
    return

class WalletCommand:
    def __init__(
        self,
        profile,
        auth_command: mcmcli.command.auth.AuthCommand,
        token
    ):
        self.config = mcmcli.command.config.get_config(profile)
        if (self.config is None):
            print(f"ERROR: Failed to load the CLI profile", file=sys.stderr, flush=True)
            sys.exit()

        self.profile = profile
        self.auth_command = auth_command
        self.api_base_url = f"{self.config['management_api_hostname']}/rmp/mgmt/v1/platforms/{self.config['platform_id']}"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {token}"
        }


    def get_balance(
        self,
        account_id: str,
        to_curl: bool,
    ) -> tuple[
        None | CurlString,
        None | Error,
        None | Wallet,
    ]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/wallets"

        curl, error, json_obj = api_request('GET', to_curl, _api_url, self.headers)
        if curl:
            return curl, None, None
        if error:
            return None, error, None
        
        wallets_wrapper = WalletsWrapper(**json_obj)
        if not wallets_wrapper.wallets:
            return None, Error(code=0, message="Wallet doesn't exist"), None

        wallet = wallets_wrapper.wallets[0] # The MCM supports one wallet per account as of March 2024.
        return None, None, wallet

    def update_balance(
        self,
        operation_type: OperationType,
        account_id: str,
        wallet_id: str,
        fund_type: FundType,
        fund_amount: float,
        to_curl: bool,
    ) -> tuple[
        None | CurlString,
        None | Error,
        None | Wallet,
    ]:      
        if fund_amount <= 0:
            return None, Error(code=0, message="The fund amount should be greater than zero."), None

        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/wallets/{wallet_id}"
        _request_id = str(shortuuid.ShortUUID().random(length=16))
        if operation_type == OperationType.DEPOSIT:
            _api_url += f"/top-up/{_request_id}"
        else:
            _api_url += f"/withdraw/{_request_id}"

        _message = {
            "type": fund_type.value,
            "amount": {
                "currency": self.config['currency'],
                "amount_micro": int(fund_amount * 1000000)
            }
        }
        _payload = { "top_up": _message } if operation_type == operation_type.DEPOSIT else { "withdraw": _message }

        curl, error, json_obj = api_request('PUT', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        wallet = Wallet(**json_obj['wallet'])
        return None, None, wallet
