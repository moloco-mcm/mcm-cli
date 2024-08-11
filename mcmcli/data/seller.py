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

#
# API error response dataclasses
#
# list-accounts command's example response is as below:
#
# {
#     "sellers": [
#         {
#             "id": "4450",
#             "title": "1 All Good",
#             "is_registered": false
#         }
#     ]
# }

class Seller(BaseModel):
    id: str
    title: str
    is_registered: bool

class SellerListWrapper(BaseModel):
    sellers: list[Seller]