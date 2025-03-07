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

from pydantic import BaseModel, RootModel
from typing import Any, Optional

class AnyCampaign(RootModel[Any]):
    pass

#
# API response dataclasses
#
class MicroPrice(BaseModel):
    currency: str
    amount_micro: int

class Schedule(BaseModel):
    start: str
    end: Optional[str] = None

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

class TargetingEvent(BaseModel):
    event_type: str
    matching_param: Optional[str] = None
    negative: bool
    matching_date: Optional[str] = None

class AudienceSetting(BaseModel):
    event_based: Optional[list[TargetingEvent]] = None
    label: Optional[str] = None
    event_based_include_list: Optional[list[str]] = None
    event_based_exclude_list: Optional[list[str]] = None

class Targeting(BaseModel):
    campaign_targeting_placement_type: str
    placement_setting: Optional[str]
    audience_setting: Optional[AudienceSetting]

class TargetInventoryDimension(BaseModel):
    width: int
    height: int

class BannerAsset(BaseModel):
    creative_id: str
    image_url: str
    width: int
    height: int
    target_inventory_dimension: TargetInventoryDimension

class LogoAsset(BaseModel):
    creative_id: str
    image_url: str

class HeadlineAsset(BaseModel):
    text: str

class CTAAsset(BaseModel):
    text: str

class ReviewInformation(BaseModel):
    status: str
    rejection_reason: str
    updated_at: str

class Asset(BaseModel):
    id: str
    banner: BannerAsset
    logo: LogoAsset
    headline: HeadlineAsset
    cta: CTAAsset
    review_information: ReviewInformation
    created_at: str
    updated_at: str

class CustomURLSetting(BaseModel):
    url: str

class LandPage(BaseModel):
    type: str
    custom_url_setting: CustomURLSetting
    id: str
    review_information: ReviewInformation
    created_at: str
    updated_at: str

class ItemSelection(BaseModel):
    type: str

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
    targeting: Optional[Targeting]
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
    item_selection: Optional[ItemSelection]
    assets: Optional[list[Asset]]
    landing_pages: Optional[list[LandPage]]
    landing_url_suffix: Optional[str]
    catalog_brand_id: Optional[str]
    catalog_category: Optional[str]
    
class CampaignList(BaseModel):
    campaigns: list[Campaign]
    without_catalog_item_ids: bool
