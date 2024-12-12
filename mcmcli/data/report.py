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
# The report command's example response is as below:
#
# {
#   "rows": [
#     {
#       "date": "",
#       "timezone": "America/New_York",
#       "currency": "",
#       "ad_account_id": "",
#       "ad_account_title": "",
#       "campaign_id": "",
#       "campaign_title": "",
#       "catalog_item_id": "",
#       "catalog_item_title": "",
#       "creative_id": "",
#       "creative_title": "",
#       "inventory_id": "",
#       "audience_type": "",
#       "imp_count": "14452078",
#       "click_count": "271062",
#       "money_spent": "11180060000",
#       "purchase_count": "552",
#       "purchase_breakdown": {
#         "direct": "355",
#         "indirect": "197",
#         "total": "552"
#       },
#       "revenue": "54189164206",
#       "revenue_breakdown": {
#         "direct": "33440120100",
#         "indirect": "20749044106",
#         "total": "54189164206"
#       },
#       "roas": 484.6947530335258,
#       "roas_breakdown": {
#         "direct": 299.1050146421397,
#         "indirect": 185.58973839138608,
#         "total": 484.6947530335258
#       },
#       "cr": 0.20364344688669012,
#       "ctr": 1.8755918699027225,
#       "imp_to_purchase": 0.0038195199333964295,
#       "num_ad_accounts": "34",
#       "items_per_ad_account": 462.44117647058823,
#       "cpc": 41245.397731884215,
#       "acos": null,
#       "cpm": 773595.3265682624
#     }
#   ]
# }

class NumberBreakdown(BaseModel):
    direct: float
    indirect: float
    total: float

class Report(BaseModel):
    date: str
    timezone: str
    currency: str
    ad_account_id: str
    ad_account_title: str
    campaign_id: str
    campaign_title: str
    catalog_item_id: str
    catalog_item_title: str
    creative_id: str
    creative_title: str
    inventory_id: str
    audience_type: str
    imp_count: str
    click_count: str
    money_spent: str
    purchase_count: str
    purchase_breakdown: NumberBreakdown
    revenue: str
    revenue_breakdown: NumberBreakdown
    roas: float
    roas_breakdown: NumberBreakdown
    cr: float
    ctr: float
    imp_to_purchase: float
    num_ad_accounts: str
    items_per_ad_account: float
    cpc: float
    acos: Optional[float]
    cpm: float

class ReportList(BaseModel):
    rows: list[Report]