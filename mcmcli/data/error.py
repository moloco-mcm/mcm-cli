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
# get-token command's example error response is as below:
#
# {
#     "code": 16,
#     "message": "{\"reason\":\"the given credential doesn't match with database record\",\"status\":401}\n [id:Fd35MbLKRZyTQxo3]",
#     "details": [
#         {
#             "@type": "type.googleapis.com/api.adcloud.common.ErrorInfo",
#             "category": "DEFAULT_ERROR_CATEGORY"
#         }
#     ]
# }
class Error(BaseModel):
    code: int
    message: str