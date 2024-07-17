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
# get-token command's example response is as below:
#
# {
#     'token': 'eyJhbGciOiJpD4', 
#     'expires_at': '2024-03-09T19:57:46Z', 
#     'user': {
#         'id': 'QFrrnyjtf2bGtHDLgbno', 
#         'email': 'user@example.com', 
#         'name': 'Ada Lovelace', 
#         'roles': [
#             {
#                 'name': 'PLATFORM_STAFF', 
#                 'resource_type': 'PLATFORM', 
#                 'resource_id': 'MYPLATFORM_TEST'
#             }, 
#             {
#                 'name': 'PLATFORM_USER', 
#                 'resource_type': 'PLATFORM', 
#                 'resource_id': 'MYPLATFORM_TEST'
#             }
#         ], 
#         'status': 'NOT_REGISTERED', 
#         'created_at': '2023-10-28T16:38:47Z', 
#         'updated_at': '2023-12-12T21:27:41Z'
#     }
# }
#
class Role(BaseModel):
    name: str
    resource_type: str
    resource_id: str

class User(BaseModel):
    id: str
    email: str
    name: str
    roles: list[Role]
    status: str
    created_at: str
    updated_at: str

class Token(BaseModel):
    token: str
    expires_at: str
    user: User
