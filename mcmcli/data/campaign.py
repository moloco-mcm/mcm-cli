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
class MicroPrice(BaseModel):
    currency: str
    amount_micro: str

class Schedule(BaseModel):
    start: str
    end: Optional[str]

class Budget(BaseModel):
    period: str
    amount: MicroPrice

class TargetCpc(BaseModel):
    target_cpc: MicroPrice

class TargetRoas(BaseModel):
    target_roas: int

class Goal(BaseModel):
    type: str
    optimize_fixed_cpc: Optional[TargetCpc] = None
    optimize_roas: Optional[TargetRoas] = None

class Campaign(BaseModel):
    id: str
    title: str
    ad_account_id: str
    creative_ids: Optional[list[str]]
    hidden: bool
    operation_type: str
    ad_type: str
    schedule: Schedule
    daily_budget: MicroPrice
    budget: Budget
    targeting: Optional[str]
    managed_setting: Optional[str]
    text_entry: str
    goal: Goal
    catalog_item_ids: list[str]
    enabling_state: str
    state: str
    created_at: str
    updated_at: str
    audience_types: list[str]
    offsite_setting: Optional[str]
    
class CampaignList(BaseModel):
    campaigns: list[Campaign]
    without_catalog_item_ids: bool
