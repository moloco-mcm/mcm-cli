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
from mcmcli.command.auth import AuthCommand, AuthHeaderName, AuthHeaderValue
from mcmcli.data.error import Error
from mcmcli.data.report import Report, ReportList
from mcmcli.requests import CurlString, api_request

import json
import mcmcli.command.auth
import mcmcli.command.config
import mcmcli.logging
import mcmcli.requests
import shortuuid
import sys
import typer

app = typer.Typer(add_completion=False)

def _create_report_command(profile):
    auth = AuthCommand(profile)
    return ReportCommand(profile, auth)

@app.command()
def platform_summary(
    start_date: str = typer.Option(help="Start date of the report window (YYYY-MM-DD)."),
    end_date: str = typer.Option(help="End date of the report window (YYYY-MM-DD)."),
    group_by: str = typer.Option(False, help="Group it by DATE, AD_ACCOUNT, or CAMPAIGN"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    profile: str = "default",
    ):
    """
    Retrive the Platform-wide summary report.
    """
    c = _create_report_command(profile)
    if c is None:
        return

    curl, error, ReportList = c.report_platform_summary(start_date, end_date, group_by, to_curl)
    if error:
        print(f"ERROR: {error.message}")
        return
    if to_curl:
        print(curl)
        return
    
    print(ReportList.model_dump_json(indent=4))
    return

@app.command()
def account_summary(
    account_id: str = typer.Option(help="Ad account ID"), 
    start_date: str = typer.Option(help="Start date of the report window."),
    end_date: str = typer.Option(help="End date of the report window."),
    group_by: str = typer.Option(False, help="Group it by DATE, AD_ACCOUNT, or CAMPAIGN"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    profile: str = "default",
    ):
    """
    Retrive the ad account summary report.
    """
    c = _create_report_command(profile)
    if c is None:
        return

    curl, error, ReportList = c.report_account_summary(account_id, start_date, end_date, group_by, to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return    

    print(ReportList.model_dump_json(indent=4))
    return

class ReportCommand:
    def __init__(self, profile, auth_command):
        self.config = mcmcli.command.config.get_config(profile)
        if (self.config is None):
            print(f"ERROR: Failed to load the CLI profile", file=sys.stderr, flush=True)
            sys.exit()

        self.profile = profile
        self.auth_command = auth_command
        self.api_base_url = f"{self.config['management_api_hostname']}/rmp/mgmt/v1/platforms/{self.config['platform_id']}"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }

        self.refresh_token()

    def refresh_token(
        self,
    ) -> None:
        error, auth_header_name, auth_header_value = self.auth_command.get_auth_credential()
        if error:
            print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
            sys.exit()

        self.headers[auth_header_name] = auth_header_value


    def report_platform_summary(self, start_date, end_date, group_by, to_curl) -> tuple[CurlString, Error, ReportList]:
        _api_url = f"{self.api_base_url}/report"
        return self._report_summary(_api_url, start_date, end_date, group_by, to_curl)

    def report_account_summary(self, account_id, start_date, end_date, group_by, to_curl) -> tuple[CurlString, Error, ReportList]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/report"
        return self._report_summary(_api_url, start_date, end_date, group_by, to_curl)

    def _report_summary(self, url, start_date, end_date, group_by, to_curl) -> tuple[CurlString, Error, ReportList]:
        if group_by and group_by != 'DATE' and group_by != 'AD_ACCOUNT' and group_by != 'CAMPAIGN':
            error = Error(code=0, message="Invalid --group-by value. It should be 'DATE', 'AD_ACCOUNT', or 'CAMPAIGN'")
            return None, error, None

        _payload = {
            "timezone": self.config['timezone'],
            "date_start": start_date,
            "date_end": end_date
        }
        if group_by:
            _payload['group_by'] = [
                group_by
            ]

        curl, error, json_obj = api_request('POST', to_curl, url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None
        
        report_list = ReportList(**json_obj)
        if not report_list.rows:
            return None, Error(code=0, message="No reports generated"), None

        return None, None, report_list


