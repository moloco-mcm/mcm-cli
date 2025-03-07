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
from mcmcli.command.auth import AuthCommand, AuthHeaderName, AuthHeaderValue
from mcmcli.data.campaign import AnyCampaign, Campaign, CampaignList
from mcmcli.data.error import Error
from mcmcli.data.item import Item, ItemList
from mcmcli.requests import CurlString, api_request

import json
import mcmcli.command.auth
import mcmcli.command.config
import mcmcli.logging
import sys
import typer

MAX_NUM_ITEMS_PER_PAGE = 5000

app = typer.Typer(add_completion=False)

def _create_campaign_command(profile):
    auth = AuthCommand(profile)
    return CampaignCommand(profile, auth)

@app.command()
def list_campaigns(
    account_id: str = typer.Option(help="Ad account ID"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = typer.Option("default", help="Profile Name – The MCM CLI configuration profile to use."), 
    ):
    """
    List all the campaigns of an ad account.
    """
    c = _create_campaign_command(profile)
    if c is None:
        return
    curl, error, campaigns = c.list_campaigns(account_id, to_curl)

    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return
    if to_json:
        json_dumps = [x.model_dump_json() for x in campaigns]
        print(f"[{','.join(json_dumps)}]")
        return
    
    print("Ad Account ID, Campaign ID, Ad Type, Starts At, Ends At, Is Enabled, Is Active,  Campaign Title")
    for c in campaigns:
        print(f"{c.ad_account_id}, {c.id}, {c.ad_type}, {c.schedule.start}, {c.schedule.end}, {c.enabling_state}, {c.state}, {c.title}")
    
    return

@app.command()
def read_campaign(
    account_id: str = typer.Option(help="Ad account ID"),
    campaign_id: str = typer.Option(help="Campaign ID"), 
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    profile: str = typer.Option("default", help="Profile Name – The MCM CLI configuration profile to use."), 
    ):
    """
    Read the campaign information
    """
    command = _create_campaign_command(profile)
    if command is None:
        return
    curl, error, c = command.read_campaign(account_id, campaign_id, to_curl)

    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return

    json_dumps = c.model_dump_json()
    print(json_dumps)
    return

class BudgetPeriod(Enum):
    DAILY = "DAILY"
    WEEKLY = 'WEEKLY'

def validate_budget_period_amount(budget_period: BudgetPeriod = None, budget_amount: int = None):
    if (budget_period is None) != (budget_amount is None): # XOR logic: One is given, the other isn't
        raise typer.BadParameter("Both --budget-period and --budget-amount mube be provided together.")

def validate_exclusive_params(target_roas: int = None, target_cpc: float = None):
    if target_roas is not None and target_cpc is not None:
        raise typer.BadParameter("You can only provide one of --target_roas or --target-cpc, not both.")

@app.command()
def update_campaign(
    account_id: str = typer.Option(help="Ad account ID"),
    campaign_id: str = typer.Option(help="Campaign ID"),
    target_roas: int = typer.Option(None, help='Target ROAS (%) – Applies only to campaigns with the Optimize ROAS goal type.'),
    target_cpc: float = typer.Option(None, help='Target CPC – Set in the platform currency. Applies only to campaigns with the Manual CPC goal type.'),
    budget_period: BudgetPeriod = typer.Option(None, help='Budget Period – Choose between DAILY or WEEKLY.'),
    budget_amount: int = typer.Option(None, help='Budget Amount – Set the spending limit for the chosen period.'),
    profile: str = typer.Option("default", help="Profile Name – The MCM CLI configuration profile to use."), 
    ):
    """
    Update the campaign information
    """
    command = _create_campaign_command(profile)
    if command is None:
        return

    _, error, c = command.read_campaign(account_id, campaign_id)
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return

    if budget_period is not None or budget_amount is not None:
        validate_budget_period_amount(budget_period, budget_amount)
    
    if target_roas is not None or target_cpc is not None:
        validate_exclusive_params(target_roas, target_cpc)

    if budget_period is not None:
        budget = c.root.get('budget')
        budget['period'] = budget_period.value
        budget['amount']['amount_micro'] = int(budget_amount * 1_000_000)

    if target_roas is not None:
        goal = c.root.get('goal')
        if goal and goal.get('type') != 'OPTIMIZE_ROAS':
            raise typer.BadParameter(f"The campaign goal type is not OPTIMIZE_ROAS and cannot update the target ROAS. Ad Account ID = {account_id}, Campaign ID = {campaign_id}")
        goal['optimize_roas']['target_roas'] = target_roas
    
    if target_cpc is not None:
        goal = c.root.get('goal')
        if goal and goal.get('type') != 'FIXED_CPC':
            raise typer.BadParameter(f"The campaign goal type is not FIXED_CPC and cannot update the target CPC. Ad Account ID = {account_id}, Campaign ID = {campaign_id}")
        goal['optimize_fixed_cpc']['target_cpc']['amount_micro'] = int(target_cpc * 1_000_000)

    _, error, c = command.update_campaign(c)
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return

    print(f'Successfully updated campaign ID: {campaign_id} for ad account ID: {account_id}')
    return

@app.command()
def archive_campaign(
    account_id: str = typer.Option(help="Ad account ID"),
    campaign_id: str = typer.Option(help="Campaign ID"), 
    profile: str = typer.Option("default", help="Profile Name – The MCM CLI configuration profile to use."),
):
    """
    Turn off (pause and disable) the campaign and archive it.
    """
    c = _create_campaign_command(profile)
    if c is None:
        return

    _, error, campaign = c.read_campaign(account_id, campaign_id)
    if error:
        print(f"ERROR: Failed to read the campaign {campaign_id} of the ad account {account_id}: {error.message}", file=sys.stderr, flush=True)
        return
    
    if campaign.state == 'ARCHIVED':
        print(f"The campaign {campaign_id} of the ad account {account_id} is already archived.")
        return

    # Turn off the campaign
    campaign.enabling_state = 'DISABLED'
    campaign.state = 'PAUSED'
    #campaign.daily_budget.amount_micro = (campaign.daily_budget.amount_micro // 10000) * 10000
    _, error, campaign = c.update_campaign(campaign)
    if error:
        print(f"ERROR: Failed to turn off the campaign {campaign_id} of the ad account {account_id}: {error.message}", file=sys.stderr, flush=True)
        return

    # Archive the campaign
    campaign.hidden = True
    campaign.state = 'ARCHIVED'
    _, error, campaign = c.update_campaign(campaign)
    if error:
        print(f"ERROR: Failed to archive the campaign {campaign_id} of the ad account {account_id}: {error.message}", file=sys.stderr, flush=True)
        return

    print(f"Archived the campaign {campaign_id} of the ad account {account_id}.")

@app.command()
def list_campaign_items(
    account_id: str = typer.Option(help="Ad account ID"), 
    campaign_id: str = typer.Option(help="Campaign ID"), 
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = typer.Option("default", help="Profile Name – The MCM CLI configuration profile to use."),
    ):
    """
    List all the items of a given campaign.
    """
    c = _create_campaign_command(profile)
    if c is None:
        return


    curl, error, items = c.list_campaign_items(account_id, campaign_id, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return   
    if to_json:
        json_dumps = [x.model_dump_json() for x in items]
        print(f"[{','.join(json_dumps)}]")
        return

    print("Ad Account Id, Campaign ID, Item ID, Is Listed In Campaign, Created At, Item Title")
    for i in items:
        listing_status = "Listed" if i.is_active else "Not Listed"
        print(f'{account_id}, {campaign_id}, {i.id}, {listing_status}, {i.created_timestamp}, "{i.title}"')

    return

@app.command()
def add_items_to_campaign(
    account_id: str = typer.Option(help="Ad account ID"), 
    campaign_id: str = typer.Option(help="Campaign ID"), 
    item_ids: str = typer.Option(help="Item IDs to add separated by comma(,) like 'p123,p456"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = typer.Option("default", help="Profile Name – The MCM CLI configuration profile to use."),
    ):
    """
    Add the item IDs to the given campaign of the account
    """
    c = _create_campaign_command(profile)
    if c is None:
        return

    _, error, campaign = c.read_campaign(account_id, campaign_id)
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return

    #
    # Add the item ID to the campaign
    #
    x = set(campaign.catalog_item_ids) | set(item_ids.split(','))
    campaign.catalog_item_ids = list(x)

    #
    # Update the campaign
    #
    curl, error, campaign = c.update_campaign(campaign, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return
    if to_json:
        print(campaign.model_dump_json())
        return

    print(f"Added the item IDs ({item_ids}) to the campaign.")
    return

class CampaignCommand:
    def __init__(self, profile, auth_command):
        self.config = mcmcli.command.config.get_config(profile)
        if (self.config is None):
            print(f"ERROR: Failed to load the CLI profile", file=sys.stderr, flush=True)
            sys.exit()

        self.profile = profile
        self.auth_command = auth_command
        self.api_base_url = f"{self.config['management_api_hostname']}/rmp/mgmt/v1/platforms/{self.config['platform_id']}"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json"
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


    def read_campaign(self, account_id, campaign_id, to_curl=False) -> tuple[CurlString, Error, AnyCampaign]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/campaigns/{campaign_id}"
        curl, error, json_obj = api_request('GET', to_curl, _api_url, self.headers)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        campaign = AnyCampaign(**json_obj['campaign'])
        return None, None, campaign
    
    def update_campaign(self, campaign: AnyCampaign, to_curl=False) -> tuple[CurlString, Error, AnyCampaign]:
        if campaign is None:
            return Error(code=0, message="invalid campaign info"), None

        # Remove 'daily_budget' as it's unnecessary
        campaign.root.pop("daily_budget", None)

        _api_url = f"{self.api_base_url}/ad-accounts/{campaign.root['ad_account_id']}/campaigns/{campaign.root['id']}"
        _payload = {
            "campaign": campaign.model_dump()
        }
        curl, error, json_obj = api_request('PUT', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None
        
        c = AnyCampaign(**json_obj['campaign'])
        return None, None, c 

    def list_campaigns(self, account_id, to_curl=False) -> tuple[CurlString, Error, list[Campaign]]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/campaigns"
        
        curl, error, json_obj = api_request('GET', to_curl, _api_url, self.headers)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        campaigns = CampaignList(**json_obj)
        return None, None, campaigns.campaigns

    def list_campaign_items(self, account_id, campaign_id, to_curl=False) -> tuple[CurlString, Error, list[Item]]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/campaigns/{campaign_id}/items"
        _payload = {
            "ad_account_id": account_id,
            "campaign_id": campaign_id,
            "search_keyword":[],
            "order_by": [{
                "column": "ID",
                "direction": "ASC"
            }],
            "filter": [
                {
                    "column": "IS_ACTIVE",
                    "filter_operator": "EQ",
                    "value": "true",
                }
            ],
            "page_index": 1,
            "page_size": MAX_NUM_ITEMS_PER_PAGE,
        }

        #
        # Get active items
        #
        curl, error, active_items = self.list_campaign_items_(to_curl, _api_url, self.headers, _payload, _is_active=True)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        #
        # Get inactive items
        #
        _, error, inactive_items = self.list_campaign_items_(to_curl, _api_url, self.headers, _payload, _is_active=False)
        if error:
            return None, error, None

        return None, None, active_items + inactive_items


    def list_campaign_items_(self, to_curl, _api_url, _headers, _payload, _is_active) -> tuple[CurlString, Error, list[Item]]:
        items = []
        num_items = 0
        page_index = 1
        while True:
            _payload["page_index"] = page_index
            _payload["filter"][0]["value"] = "true" if _is_active else "false"

            curl, error, json_obj = api_request('POST', to_curl, _api_url, _headers, _payload)
            if curl:
                return curl, None, None
            if error:
                return None, error, None

            item_group = ItemList(**json_obj)
            items += item_group.rows
            num_items += len(item_group.rows)

            if num_items >= item_group.num_counts:
                break
            page_index += 1

        return None, None, items

