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
from mcmcli.command.auth import AuthCommand, AuthHeaderName, AuthHeaderValue
from mcmcli.data.account import Account
from mcmcli.data.item_blocking_result import ItemBlockingResult
from mcmcli.data.campaign import Campaign
from mcmcli.data.error import Error
from mcmcli.data.item import Item
from mcmcli.data.platform_user import PlatformUser, PlatformUserListWrapper, PlatformUserWrapper
from mcmcli.requests import CurlString, api_request
from typing import Optional

import csv
import mcmcli.command.account
import mcmcli.command.auth
import mcmcli.command.campaign
import mcmcli.command.config
import mcmcli.command.wallet
import mcmcli.requests
import sys
import typer

from mcmcli.logging import echo, echo_newline, start_dot_printing, stop_dot_printing, print_error

app = typer.Typer(add_completion=False)

def _create_admin_command(profile):
    auth = AuthCommand(profile)
    return AdminCommand(profile, auth)

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
def list_all_campaigns(
    profile: str = "default",
):
    """
    List the campaigigns of all of the active ad accounts
    """
    admin = _create_admin_command(profile)
    if admin is None:
        return
    error, account_campaigns = admin.list_all_campaigns()
    if error:
        print(error, file=sys.stderr, flush=True)
        return

    print("Account ID,Account Title,Campaign ID,Campaign Title,Ad Type,Start,End,Budget Period,Budget Amount,Enabling State,State,Created At,Updated At")
    for account_campaign in account_campaigns:
        a, c = account_campaign

        print(f'"{a.id}","{a.title}",', end="", flush=True)
        print(f'"{c.id}","{c.title}","{c.ad_type}",', end="", flush=True)
        print(f'"{c.schedule.start}","{c.schedule.end}",', end="", flush=True)
        print(f'"{c.budget.period}","{int(c.budget.amount.amount_micro) / 1000000}",', end="", flush=True)
        print(f'"{c.enabling_state}","{c.state}",', end="", flush=True)
        print(f'"{c.created_at}","{c.updated_at}",', end="", flush=True)
        # print(f'"{";".join(c.catalog_item_ids)}"')
        print("", flush=True)

@app.command()
def list_platform_users(
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = "default",
):
    """
    List the users of the platform
    """
    admin = _create_admin_command(profile)
    if admin is None:
        return

    curl, error, users = admin.list_platform_users(to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(error, file=sys.stderr, flush=True)
        return
    if to_json:
        json_dumps = [x.model_dump_json() for x in users]
        print(f"[{','.join(json_dumps)}]")
        return

    print('User ID,Created At,Updated At,Status,Email,Name,Roles')
    for u in users:
        roles = [f'{x.name} of {x.resource_type} {x.resource_id}' for x in u.roles]
        print(f'{u.id},{u.created_at},{u.updated_at},{u.status},{u.email},{u.name},{';'.join(roles)}')


@app.command()
def get_platform_user(
    user_email: str = typer.Option(help="User's email address"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Get the email user's profile.
    """
    a = _create_admin_command(profile)
    if a is None:
        return

    curl, error, user = a.get_platform_user(user_email, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return

    if user is not None:
        print(f"{user.model_dump_json()}")
    return


@app.command()
def list_items(
    account_id: str = typer.Option(help="Ad account ID"),
    profile: str = "default",
    ):
    """
    List the itmes, item status, and attached campaigns of a given ad account
    """
    admin = _create_admin_command(profile)
    if admin is None:
        return

    error, campaigns = admin.list_campaigns(account_id)
    if error:
        print(f"ERROR: {error.message}")
        return

    campaign_item_obj = {} # build item list into item object with the item_id as an index
    # print("Campaign ID, Campaign Title, Item ID, Item Title, Item Status")

    for c in campaigns:
        error, campaign_items = admin.list_campaign_items(account_id, c.id)
        if error:
            print(f"ERROR: {error.message}")
            return
        for ci in campaign_items:
            if ci.id in campaign_item_obj:
                campaign_item_obj[ci.id].append({
                    'campaign_id': c.id,
                    'campaign_title': c.title
                })
            else:
                campaign_item_obj[ci.id] = [{
                    'campaign_id': c.id,
                    'campaign_title': c.title
                }]
            # print(f"{c['id']}, {c['title']}, {ci['id']}, {ci['title']}, {ci['is_active']}")

    error, items = admin.list_items(account_id)
    if error:
        print(f"ERROR: {error.message}")

    print("Ad Account ID,Item ID,Is Item Active,Item Title,Campaign ID,Campaign Title")
    for i in items:
        if i.id in campaign_item_obj:
            ci = campaign_item_obj[i.id]
            campaign_id_list = ""
            campaign_title_list = ""
            for c in ci:
                campaign_id_list += f"{c['campaign_id']};"
                campaign_title_list += f"{c['campaign_title']};"
            campaign_id_list = campaign_id_list[:-1]
            campaign_title_list = campaign_title_list[:-1]

            print(f"{account_id},{i.id},{i.is_active},\"{i.title}\",{campaign_id_list},\"{campaign_title_list}\"")
        else:
            print(f"{account_id},{i.id},{i.is_active},\"{i.title}\",,")

@app.command()
def list_off_campaign_items(
    account_id: str = typer.Option(help="Ad account ID"),
    profile: str = "default",
    ):
    """
    Lists the items that are not in any of campaigns
    """
    admin = _create_admin_command(profile)
    if admin is None:
        return

    error, items = admin.list_items(account_id)
    if error:
        print(f"ERROR: {error.message}")
        return
    error, campaigns = admin.list_campaigns(account_id)
    if error:
        print(f"ERROR: {error.message}")
        return

    campaign_item_obj = {} # build item list into item object with the item_id as an index
    for c in campaigns:
        error, campaign_items = admin.list_campaign_items(account_id, c.id)
        for ci in campaign_items:
            campaign_item_obj[ci.id] = ci.title

    print("Item ID, Item Title")
    for i in items:
        if i.id not in campaign_item_obj and i.is_active:
            print(f"{i.id}, {i.title}")

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
        auth_command: AuthCommand,
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
        }

        self.refresh_token()


    def refresh_token(
        self,
    ) -> None:
        error, auth_header_name, auth_header_value = self.auth_command.get_auth_credential()
        if error:
            print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
            sys.exit()

        self.headers[auth_header_name] = auth_header_value


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
                "updated_time": _requested_at,
                "blocked": f'Requested at {_requested_at}',
            }]
        }
        if account_id is not None:
            _payload["items"][0]["seller_id"] = account_id
        
        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None
        return None, None, ItemBlockingResult(**json_obj)
    
    
    def get_platform_user(
        self,
        user_email,
        to_curl = False,
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        Optional[PlatformUser],
    ]:
        _api_url = f"{self.api_base_url}/users/{user_email}"
        curl, error, json_obj = api_request('GET', to_curl, _api_url, self.headers)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        ret = PlatformUserWrapper(**json_obj).user
        return None, None, ret

    
    def list_platform_users(
        self,
        to_curl=False,
    ) -> tuple [
        Optional[CurlString],
        Optional[Error],
        list[PlatformUser],
    ]:
        _api_url = f"{self.api_base_url}/users"

        curl, error, json_obj = api_request('GET', to_curl, _api_url, self.headers)
        if curl:
            return curl, None, []
        if error:
            return None, error, []

        user_list_wrapper = PlatformUserListWrapper(**json_obj)
        users = user_list_wrapper.users
        return None, None, users

    def list_wallet_balances(
        self
    ):
        ac = mcmcli.command.account.AccountCommand(self.profile, self.auth_command)
        wc = mcmcli.command.wallet.WalletCommand(self.profile, self.auth_command)
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



    def list_all_campaigns(
        self
    ) -> tuple [
        Optional[Error],
        list[tuple[Account, Campaign]]
    ]:
        ac = mcmcli.command.account.AccountCommand(self.profile, self.auth_command)
        cc = mcmcli.command.campaign.CampaignCommand(self.profile, self.auth_command)
        _, error, accounts = ac.list_accounts()
        if error:
            return error, []

        echo('Collecting campaigns...')
        return_value = []
        for id in accounts:
            account = accounts[id]
            echo('.')
            # print(f'{account.id}, \"{account.title}\"')
            _, error, campaigns = cc.list_campaigns(account.id)
            if error:
                echo_newline(error)
                continue
            for c in campaigns:
                return_value.append((account, c))

        echo_newline(' done')
        return None, return_value


    def list_items(
        self,
        account_id
    ) -> tuple [
        Optional[Error],
        list[Item],
    ]:
        ac = mcmcli.command.account.AccountCommand(self.profile, self.auth_command)
        echo("Gathering the account's items ")
        thread, stopper = start_dot_printing()
        _, error, items = ac.list_account_items(account_id)
        stop_dot_printing(thread, stopper)
        echo_newline(" done")

        if error:
            return error, []
        if items == []:
            return Error(code=0, message=str("Cannot find items")), []

        return None, items
    
    def list_campaigns(
        self,
        ad_account_id
    ) -> tuple [
        Optional[Error],
        list[Campaign],
    ]:
        cam = mcmcli.command.campaign.CampaignCommand(self.profile, self.auth_command)

        echo("Gathering the account's campaigns ")
        thread, stopper = start_dot_printing()
        _, error, campaigns = cam.list_campaigns(ad_account_id)
        stop_dot_printing(thread, stopper)
        echo_newline(" done")

        if error:
            return error, []
        if campaigns == []:
            return Error(code=0, message=str("Cannot find campaigns")), []

        return None, campaigns


    def list_campaign_items(
        self,
        ad_account_id,
        campaign_id
    ) -> tuple [
        Optional[Error],
        list[Item]
    ]:
        cam = mcmcli.command.campaign.CampaignCommand(self.profile, self.auth_command)

        echo(f"Gathering the items of the campaign {campaign_id} ")
        thread, stopper = start_dot_printing()
        _, error, campaign_items = cam.list_campaign_items(ad_account_id, campaign_id)
        stop_dot_printing(thread, stopper)
        echo_newline(" done")

        if error:
            return error, []
        if campaign_items == []:
            return Error(code=0, message=str("Cannot find campaign items")), []

        return None, campaign_items
