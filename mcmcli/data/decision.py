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

from pydantic import BaseModel
from typing import Optional

#
# API response dataclasses
#
# Item decision API's response example:
#
# {
#     "request_id": "request-1",
#     "decided_items": [
#         {
#             "item_id": "1111833",
#             "auction_result": {
#                 "ad_account_id": "2444",
#                 "campaign_id": "zWHhpyNbzYcy5FAy",
#                 "win_price": {
#                     "currency": "USD",
#                     "amount_micro": "500000000"
#                 },
#                 "campaign_text_entry": ""
#             },
#             "imp_trackers": [
#                 "https://myplatform-evt.rmp-api.moloco.com/t/i/MYPLATFORM_TEST?source=2X0op"
#             ],
#             "click_trackers": [
#                 "https://myplatform-evt.rmp-api.moloco.com/t/c/MYPLATFORM_TEST?source=2X0opp"
#             ],
#             "track_id": "2X0op"
#         }
#     ]
# }

class MicroPrice(BaseModel):
    currency: str
    amount_micro: str

class AuctionResult(BaseModel):
    ad_account_id: str
    campaign_id: str
    win_price: Optional[MicroPrice]
    campaign_text_entry: Optional[str]

class DecidedItem(BaseModel):
    item_id: str
    auction_result: Optional[AuctionResult]
    imp_trackers: list[str]
    click_trackers: list[str]
    track_id: Optional[str]

class DecidedItemList(BaseModel):
    request_id: str
    decided_items: list[DecidedItem]

class CreativeBanner(BaseModel):
    creative_id: str
    image_url: str
    imp_trackers: list[str]
    click_trackers: list[str]

class CreativeItem(BaseModel):
    item_id: str
    imp_trackers: list[str]
    click_trackers: list[str] 

class LandingUrl(BaseModel):
    id: str
    url: str

class DecidedCreative(BaseModel):
    request_id: str
    auction_result: Optional[AuctionResult]
    banner: Optional[CreativeBanner]
    items: list[CreativeItem]
    landing_url:Optional[LandingUrl]

class CreativeBannerWrapper(BaseModel):
    banner: CreativeBanner

class DecidedCreativeBulk(BaseModel):
    inventory_id: str
    auction_result: Optional[AuctionResult]
    creatives: list[CreativeBannerWrapper]
    items: list[DecidedItem]
    landing_url: Optional[LandingUrl]

class DecidedCreativeBulkList(BaseModel):
    request_id: str
    results: list[DecidedCreativeBulk]

