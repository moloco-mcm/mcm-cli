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
from mcmcli.data.decision import DecidedCreative, DecidedCreativeBulkList, DecidedItemList
from mcmcli.requests import CurlString, api_request
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

import json
import mcmcli.command.auth
import mcmcli.command.config
import mcmcli.logging
import sys
import typer

MAX_NUM_ITEMS_PER_PAGE = 5000

app = typer.Typer(add_completion=False)

@app.command()
def decide_items(
    inventory_id: str = typer.Option(help="Ad inventory ID"),
    num_items: int = typer.Option(help="Number of items requested for the inventory."),
    items: str = typer.Option(None, help="The main item ids of the page. For example, homepage inventories don't have any main items, and product-detail-page inventories have one main item."),
    location_filter: str = typer.Option(None, help="Location filter value"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Request item decision by auction.
    """
    d = DecisionCommand(profile)

    curl, error, ret = d.decide_items(inventory_id, num_items, items, location_filter, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return
    if ret is None:
        print(f"ERROR: Unknown error")
        return

    print(ret.model_dump_json())
    return


@app.command()
def decide_creative(
    inventory_id: str = typer.Option(help="Ad inventory ID"),
    items: str = typer.Option(None, help="The main item ids of the page. For example, homepage inventories don't have any main items, and product-detail-page inventories have one main item."),
    location_filter: str = typer.Option(None, help="Location filter value"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Request item decision by creative auction.
    """
    d = DecisionCommand(profile)

    curl, error, ret = d.decide_creative(inventory_id, items, location_filter, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return
    if ret is None:
        print(f"ERROR: Unknown error")
        return

    print(ret.model_dump_json())
    return


@app.command()
def decide_creative_bulk(
    inventory_id_list: str = typer.Option(help="Ad inventory IDs separated by comma(,)"),
    items: str = typer.Option(None, help="The main item ids of the page. For example, homepage inventories don't have any main items, and product-detail-page inventories have one main item."),
    location_filter: str = typer.Option(None, help="Location filter value"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Request item decision by creative auction for multiple inventories.
    """
    d = DecisionCommand(profile)

    curl, error, ret = d.decide_creative_bulk(inventory_id_list, items, location_filter, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return
    if ret is None:
        print(f"ERROR: Unknown error")
        return

    print(ret.model_dump_json())
    return
    


class DecisionCommand:
    def __init__(
        self,
        profile,
    ):
        self.config = mcmcli.command.config.get_config(profile)
        if (self.config is None):
            print(f"ERROR: Failed to load the CLI profile", file=sys.stderr, flush=True)
            sys.exit()
        
        if 'decision_api_key' not in self.config or self.config['decision_api_key'] is None or self.config['decision_api_key'] == "":
            print(f"ERROR: Decision API key is not set in the profile [{profile}]", file=sys.stderr, flush=True)
            sys.exit()

        self.profile = profile
        self.api_base_url = f"{self.config['decision_api_hostname']}/rmp/decision/v1/platforms/{self.config['platform_id']}"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": self.config['decision_api_key']
        }
    
    def decide_items(
        self, 
        inventory_id, 
        num_items, 
        items,
        location_filter, 
        to_curl,
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        Optional[DecidedItemList],
    ]:
        _api_url = f"{self.api_base_url}/auction"
        _payload = {
            "request_id": "request-1",
            "inventory": {
                "inventory_id": inventory_id,
                "num_items": num_items
            },
            "user": {
                "user_id": "user-1"
            },
            "device": {
                "persistent_id": "persistent-device-1"
            },
        }
        if items:
            _payload["inventory"]["items"] = items.split(',')

        if location_filter:
            _payload["filtering"] = {
                "location": {
                    "locations": location_filter.split(',')
                }
            }
        
        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        decided_items = DecidedItemList(**json_obj)
        return None, None, decided_items


    def decide_creative(
        self,
        inventory_id,
        items,
        location_filter,
        to_curl
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        Optional[DecidedCreative],
    ]:
        _api_url = f"{self.api_base_url}/creative-auction"
        _payload = {
            "request_id": "request-1",
            "inventory": {
                "inventory_id": inventory_id
            },
            "user": {
                "user_id": "user-1"
            },
            "device": {
                "persistent_id": "persistent-device-1"
            },
        }
        if items:
            _payload["inventory"]["items"] = items.split(',')

        if location_filter:
            _payload["filtering"] = {
                "location": {
                    "locations": location_filter.split(',')
                }
            }
        
        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        decided_creative = DecidedCreative(**json_obj)
        return None, None, decided_creative


    def decide_creative_bulk(
        self, 
        inventory_id_list, 
        items,
        location_filter, 
        to_curl
    ) -> tuple[
        Optional[CurlString],
        Optional[Error], 
        Optional[DecidedCreativeBulkList],
    ]:
        _api_url = f"{self.api_base_url}/creative-auction-bulk"
        _payload = {
            "request_id": "request-1",
            "inventories": list(map(lambda x: { "inventory_id": x }, inventory_id_list.split(','))),
            "user": {
                "user_id": "user-1"
            },
            "device": {
                "persistent_id": "persistent-device-1"
            },
        }
        if items:
            for inventory in _payload["inventories"]:
                inventory["items"] = items.split(',')

        if location_filter:
            _payload["filtering"] = {
                "location": {
                    "locations": location_filter.split(',')
                }
            }

        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        return None, None, DecidedCreativeBulkList(**json_obj)

