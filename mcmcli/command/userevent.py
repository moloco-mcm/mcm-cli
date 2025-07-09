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
from datetime import datetime, timezone
from mcmcli.data.error import Error
from mcmcli.requests import CurlString, api_request
from typing import Optional

UTC = timezone.utc

import mcmcli.command.config
import sys
import typer

app = typer.Typer(add_completion=False)

class UserEventCommand:
    def __init__(
        self,
        profile,
    ):
        self.config = mcmcli.command.config.get_config(profile)
        if (self.config is None):
            print(f"ERROR: Failed to load the CLI profile", file=sys.stderr, flush=True)
            sys.exit()

        self.profile = profile

        self.api_base_url = f"{self.config['event_api_hostname']}/rmp/event/v1/platforms/{self.config['platform_id']}/userevents"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": self.config['event_api_key']
        }

    def insert_purchase_event(
        self,
        user_id: str,
        account_id: str,
        item_id: str,
        to_curl: bool,
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
    ]:
        # Get current timestamp in milliseconds
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        _api_url = self.api_base_url
        _payload = {
            "id": f"event-{user_id}",
            "timestamp":timestamp_ms,
            "user_id": user_id,
            "device": {
                "persistent_id": user_id
            },
            "event_type": "PURCHASE",
            "channel_type": "SITE",
            "items": [
                {
                    "id": item_id,
                    "quantity": 1,
                    "seller_id": account_id,
                    "price": {
                        "currency": "USD",
                        "amount": 100
                    }
                }
            ],
            "revenue": {
                "currency": "USD",
                "amount": 100
            },
            "shipping_charge": {
                "currency": "USD",
                "amount": 0
            },
        }

        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None
        if error:
            return None, error

        return None, None

