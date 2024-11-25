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

from mcmcli.data.error import Error

import json
import requests
import sys

CurlString = str

def to_curl_str(method, api_base_url, headers, payload = None):
    c = f"""curl --request {method} \\
     --url {api_base_url} \\     
"""
    for k in headers:
        c = c + f"     --header '{k}: {headers[k]}' \\\n"
    if payload is None:
        c = c + "\n"
    else:
        c = c + f"     --data '\n"
        c = c + json.dumps(payload, indent=4)
        c = c + f"\n'"
    return c

def get(url, headers):
    try:
        res = requests.get(url, headers=headers)
        return None, json.loads(res.text)
    except json.JSONDecodeError:
        return Error(code=0, message=res.text), None
    except Exception as e:
        return e, None


def delete(url, headers):
    try:
        res = requests.delete(url, headers=headers)
        return None, json.loads(res.text)
    except json.JSONDecodeError:
        return Error(code=0, message=res.text), None
    except Exception as e:
        return e, None


def post(url, headers, payload):
    try:
        res = requests.post(url, headers=headers, json=payload)
        return None, json.loads(res.text)
    except json.JSONDecodeError:
        return Error(code=0, message=res.text), None
    except Exception as e:
        return  e, None

def put(url, headers, payload):
    try:
        res = requests.put(url, headers=headers, json=payload)
        return None, json.loads(res.text)
    except json.JSONDecodeError:
        return Error(code=0, message=res.text), None
    except Exception as e:
        return e, None

def api_request(method, to_curl, url, headers, payload=None) -> tuple[CurlString, Error, dict]:
    if to_curl:
        curl = to_curl_str(method, url, headers, payload)
        return curl, None, None

    if method == 'GET':
        error, json_obj = get(url, headers)
    elif method == 'DELETE':
        error, json_obj = delete(url, headers)
    elif method == 'POST':
        error, json_obj = post(url, headers, payload)
    elif method == 'PUT':
        error, json_obj = put(url, headers, payload)
    else:
        return None, Error(code=0, message="Unsupported HTTP method"), None
    
    if error:
        return None, Error(code=0, message=str(error)), None
    if 'code' in json_obj:
        return None, Error(**json_obj), None

    return None, None, json_obj
    
