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
# Platform user response dataclasses
#
# 
# {
#   "users": [
#     {
#       "id": "00YtNXn8PQGFPXiBS9oi",
#       "email": "user@email.com",
#       "name": "John Doe",
#       "roles": [
#         {
#           "name": "PLATFORM_USER",
#           "resource_type": "PLATFORM",
#           "resource_id": "DEMO_TEST"
#         },
#         {
#           "name": "AD_ACCOUNT_OWNER",
#           "resource_type": "AD_ACCOUNT",
#           "resource_id": "678acd3a-82b5-11e7-afa5-128878ebb8b6"
#         }
#       ],
#       "status": "NOT_REGISTERED",
#       "created_at": "2024-05-16T16:13:52Z",
#       "updated_at": "2024-05-16T16:13:52Z"
#     }
#   ]
# }

class Role(BaseModel):
    name: str
    resource_type: str
    resource_id: str

class PlatformUser(BaseModel):
    id: str
    email: str
    name: str
    roles: list[Role]
    status: str
    created_at: str
    updated_at: str

class PlatformUserListWrapper(BaseModel):
    users: list[PlatformUser]

class PlatformUserWrapper(BaseModel):
    user: PlatformUser
