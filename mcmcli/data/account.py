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
#     "ad_accounts": [
#         {
#             "id": "0d139a1b-abcd-11ee-b5f8-12f12be0eb51",
#             "title": "Smoke Distribution Inc.",
#             "timezone": "America/New_York",
#             "state_info": {
#                 "ad_account_id": "0d139a1b-abcd-11ee-b5f8-12f12be0eb51",
#                 "state": "ACTIVE",
#                 "state_case": "INIT_BY_PLATFORM",
#                 "state_updated_at": "2023-10-23T12:43:31.542660Z",
#                 "updated_at": "2023-10-23T12:43:31.542660Z"
#             },
#             "available_features": [],
#             "created_at": "2023-10-23T12:43:31.542660Z",
#             "updated_at": "2023-10-23T12:43:31.542660Z"
#         }
#     ]
# }

class State(BaseModel):
    ad_account_id: str
    state: str
    state_case: str
    state_updated_at: str
    updated_at: str

class Account(BaseModel):
    id: str
    title: str
    timezone: str
    state_info: State
    # available_features: []
    created_at: str
    updated_at: str

class AccountListWrapper(BaseModel):
    ad_accounts: list[Account]
