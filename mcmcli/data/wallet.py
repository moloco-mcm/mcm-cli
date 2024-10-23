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
# API response dataclasses
#
# The balance command's example response is as below:
#
# {
#     "wallets": [
#         {
#             "id": "TjNwMMlONkaMqNyn",
#             "title": "",
#             "ad_account_id": "1234",
#             "type": "PRE_PAYMENT",
#             "accounts": [
#                 {
#                     "type": "CREDITS",
#                     "balance": {
#                         "currency": "USD",
#                         "amount_micro": "1000000"
#                     }
#                 },
#                 {
#                     "type": "PRE_PAID",
#                     "balance": {
#                         "currency": "USD",
#                         "amount_micro": "1002011000000"
#                     }
#                 }
#             ],
#             "created_at": "2024-02-29T21:24:21.743177Z",
#             "updated_at": "2024-03-04T16:41:25.717512Z"
#         }
#     ]
# }

class MicroPrice(BaseModel):
    currency: str
    amount_micro: str

class WalletAccount(BaseModel):
    type: str
    balance: MicroPrice

class Wallet(BaseModel):
    id: str
    title: str
    ad_account_id: str
    type: str
    accounts: list[WalletAccount]
    created_at: str
    updated_at: str

class WalletsWrapper(BaseModel):
    wallets: list[Wallet]


#
# API response dataclasses for the platform balance API responses
#
#
# {
#     "result": {
#         "10054": {
#             "wallets": [
#                 {
#                     "id": "wRydQ9MhQx4ZyJED", 
#                     "title": "", 
#                     "ad_account_id": "10054", 
#                     "type": "PRE_PAYMENT", 
#                     "accounts": [
#                         {
#                             "type": "CREDITS", 
#                             "balance": {
#                                 "currency": "USD", 
#                                 "amount_micro": "1890020000"
#                             }
#                         },
#                         {
#                             "type": "PRE_PAID", 
#                             "balance": {
#                                 "currency": "USD", 
#                                 "amount_micro": "0"
#                             }
#                         }
#                     ], 
#                     "created_at": "2024-09-24T17:26:09.437580Z", 
#                     "updated_at": "2024-10-20T22:00:21.412482Z"
#                 }
#             ]
#         }
#     }
# }

class PlatformWalletsWrapper(BaseModel):
    result: dict[str, WalletsWrapper] # Dictionary with ad_account_id as keys


