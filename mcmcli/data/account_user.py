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
# Ad account users response example is as below:f
#
# {
#     "users": [
#         {
#             "ad_account_id": "1234",
#             "id": "CEdyiC4f1yyyySGEOGj7",
#             "email": "user@example.com",
#             "name": "John Doe",
#             "role": "AD_ACCOUNT_OWNER",
#             "status": "NOT_REGISTERED",
#             "created_at": "2024-06-06T14:29:42Z",
#             "updated_at": "2024-06-06T14:29:42Z"
#         }
#     ]
# }

class User(BaseModel):
    ad_account_id: str
    id: str
    email: str
    name: str
    role: str
    status: str
    created_at: str
    updated_at: str

class UserListWrapper(BaseModel):
    users: list[User]

class UserWrapper(BaseModel):
    user: User

