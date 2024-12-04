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
# API response dataclasse of the item kill switch API
#
# The example response is as below:
# {
#   "success_items": [
#     {
#       "item_id": "item_1",
#       "seller_id": "seller_1",
#       "region": ""
#     }
#   ],
#   "failure_items": [
#     {
#       "item_id": "item_2",
#       "seller_id": "seller_2",
#       "region": "",
#       "message": "rpc error: code = Internal desc = ad account not found"
#     }
#   ]
# }

class SucceededItemBlockingAttempt(BaseModel):
    item_id: str
    seller_id: str
    region: str

class FailedItemBlockingAttempt(BaseModel):
    item_id: str
    seller_id: str
    region: str
    message: str


class ItemBlockingResult(BaseModel):
    success_items: list[SucceededItemBlockingAttempt]
    failure_items: list[FailedItemBlockingAttempt]