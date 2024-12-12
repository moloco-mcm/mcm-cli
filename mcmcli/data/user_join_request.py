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
# invite-user command's example response is as below:
#
# {
# 	'user_join_request': {
# 		'id': 'I6QpJhsvb2iswMN3', 
# 		'ad_account_id': 'test', 
# 		'user_email': 'a@b.com', 
# 		'user_name': 'asfds', 
# 		'role': 'AD_ACCOUNT_OWNER', 
# 		'created_at': '2024-05-13T00:54:49.874934Z', 
# 		'updated_at': '2024-05-13T00:54:49.874934Z'
# 	}
# }

class UserJoinRequest(BaseModel):
    id: str # join request ID
    ad_account_id: str
    user_email: str
    user_name: str
    role: str
    created_at: str
    updated_at: str

class UserJoinRequestWrapper(BaseModel):
    user_join_request: UserJoinRequest
