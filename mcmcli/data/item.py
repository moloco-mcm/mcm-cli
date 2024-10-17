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
class Price(BaseModel):
    currency: str
    amount: float

class Item(BaseModel):
    id: str
    title: str
    price: Price
    sale_price: Price
    link: str
    image_link: str
    category: str
    review_count: str
    rating_score: float
    is_active: bool
    is_new: Optional[bool]
    created_timestamp: str

class ItemList(BaseModel):
    rows: list[Item]
    num_counts: int
    created_timestamp_filter: str