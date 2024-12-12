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

from enum import Enum
from mcmcli.command.auth import AuthCommand, AuthHeaderName, AuthHeaderValue
from mcmcli.data.account import Account, AccountListWrapper
from mcmcli.data.account_user import User, UserWrapper, UserListWrapper
from mcmcli.data.error import Error
from mcmcli.data.item import ItemList, Item
from mcmcli.data.seller import Seller, SellerListWrapper
from mcmcli.requests import CurlString, api_request
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

import csv
import mcmcli.command.auth
import mcmcli.command.config
import mcmcli.logging
import mcmcli.requests
import sys
import time
import typer

MAX_NUM_ITEMS_PER_PAGE = 5000
T = TypeVar('T')

class UserRole(Enum):
    AD_ACCOUNT_OWNER = "AD_ACCOUNT_OWNER"

app = typer.Typer(add_completion=False)


@app.command()
def bulk_invite_ad_account_owners(
    csv_file: str = typer.Option(help="CSV file path that contains the list of ad account id, user email address, and the user name."),
    dry_run: bool = typer.Option(True, help="Perform a dry run without sending emails."),
    skip_csv_header: bool = typer.Option(False, help="Skip the first line of the CSV file."),
    create_account: bool = typer.Option(False, help="Create the ad account if it doesn't exist."),
    create_user: bool = typer.Option(False, help="Create the ad account user if it doesn't exist."),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Send campaign manager invitation emails to ad account owners. Ensure the CSV file has three columns:
    ad account ID, user email address, and user name. Extra columns are ignored.
    """
    csv_data = _read_csv_file(csv_file, skip_csv_header)
    if csv_data is None:
        return 

    a = _create_account_command(profile)
    if a is None:
        return

    if dry_run:
        print(f"Dry run initiated.")

    #
    # get the list of sellers
    #
    _, error, seller_dictionary = a.list_sellers()
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return


    print('Processing the command ', end='', file=sys.stderr, flush=True)
    total_count = len(csv_data)
    success_count = 0
    account_creation_count = 0
    for row in csv_data:
        account_id = row[0].strip()
        email_address = row[1].strip()
        user_name = row[2].strip()
        print('.', end='', file=sys.stderr, flush=True)

        # Check if the ad account exists
        if _lookup_dict(account_id, seller_dictionary) is None:
            print(f"\nERROR: Could not find the ad account ID {account_id}", file=sys.stderr, flush=True)
            continue

        # Create the ad account if the seller doesn't have one yet and the CLI command tells to create the ad account.
        seller_info = seller_dictionary[account_id]
        if not seller_info.is_registered and create_account:
            error, _ = a.create_account_with_retry(seller_info.id, seller_info.title, dry_run)
            if error:
                print(f"\nERROR: Failed to create the ad account {account_id}. {error.message}.", file=sys.stderr, flush=True)
                continue
            account_creation_count += 1

            #
            # TODO: investigate if this step is necessary
            # Activate the ad account
            #
            #if account:
            #    error = a.activate_account_with_retry(account)
            #    if error:
            #        print(f"\nERROR: Failed to activate the ad account {account_id}. {error.message}.", file=sys.stderr, flush=True)
            #        continue

        error = a.send_invitation_email_with_retry(account_id, email_address, user_name, create_user, dry_run)
        if error:
            print(f"\nERROR: Failed to send the mail for the ad account ID {account_id}. {error.message}.", file=sys.stderr, flush=True)
            continue

        success_count += 1

    print(' Done', file=sys.stderr, flush=True)
    if dry_run:
        print(f"If this wasn't a dry-run, it would have sent {success_count} out of {total_count} emails and created {account_creation_count} new ad accounts.", flush=True)
    else:
        print(f'Sent {success_count} out of {total_count} emails, and created {account_creation_count} new ad accounts.', flush=True)
    return


@app.command()
def bulk_check_user_registrations(
    csv_file: str = typer.Option(help="CSV file path that contains the list of ad account id and user email address."),
    skip_csv_header: bool = typer.Option(False, help="Skip the first line of the CSV file."),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Check user status. Ensure the CSV file has two columns: ad account ID and user email address. Extra columns are ignored.
    """
    csv_data = _read_csv_file(csv_file, skip_csv_header)
    if csv_data is None:
        return 

    a = _create_account_command(profile)
    if a is None:
        return

    _, error, account_dictionary = a.list_accounts(to_curl=False)
    if error:
        print(f"ERROR: {error.message}", file=sys.stderr, flush=True)
        return

    print('"Ad Account ID","Is Ad Account Exist","User Email","Is User Exist","User Role","User Status"')
    for row in csv_data:
        account_id = row[0].strip()
        email_address = row[1].strip()
        account = _lookup_dict(account_id, account_dictionary)
        is_account_exist = "No Account Exists" if account is None else "Account Exists"

        error, user_dictionary = a.list_account_users_with_retry(account_id)
        if error:
            print(f"\nERROR: {error.message}", file=sys.stderr, flush=True)
            return

        user = _lookup_dict(email_address, user_dictionary)
        is_user_exist = "No User Exist" if user is None else "User Exists"
        user_role = "" if user is None else user.role
        user_status = "" if user is None else user.status
        print(f'"{account_id}","{is_account_exist}","{email_address}","{is_user_exist}","{user_role}","{user_status}"')
    return

@app.command()
def delete_user(
    account_id: str = typer.Option(help="Ad account ID"),
    user_email: str = typer.Option(help="User's email address"),
    email_notification: bool = typer.Option(True, help="Send the email notification to the user"),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Delete the email user. It will send the notification email to the user by default.
    Please use the `--no-email-notification` option if you want to skip it.
    """
    a = _create_account_command(profile)
    if a is None:
        return

    err, users = a.list_account_users(account_id)
    if err:
        print(f"ERROR: {err}", file=sys.stderr, flush=True)
        sys.exit()
    if user_email not in users:
        print(f"ERROR: The email user {user_email} was not found in the ad account {account_id}.", file=sys.stderr, flush=True)
        sys.exit()

    user_id = users[user_email].id
    err = a.delete_user(account_id, user_id, email_notification)
    if err:
        print(f"ERROR: {err}", file=sys.stderr, flush=True)
        sys.exit()

    print(f'Successfully deleted the email user {user_email} from the ad account ID {account_id}.')


@app.command()
def invite_user(
    account_id: str = typer.Option(help="Ad account ID"),
    user_email: str = typer.Option(help="User's email address"),
    user_name: str = typer.Option(help="User's name"),
    user_role: UserRole = typer.Option(UserRole.AD_ACCOUNT_OWNER.value, help="User Role"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Invite a user as an ad account owner. The process creates the ad account if it doesn’t exist
    and sends an invitation email to the user.
    """
    a = _create_account_command(profile)
    if a is None:
        return

    #
    # get the list of sellers
    #
    _, error, seller_dictionary = a.list_sellers()
    if error:
        print(f"ERROR: {error.message}")
        sys.exit()

    seller = _lookup_dict(account_id, seller_dictionary)
    if seller is None:
        print(f"ERROR: Could not find the ad account ID {account_id}")
        sys.exit()

    #
    # create the ad account first
    #
    _, error, _ = a.create_account(seller.id, seller.title, to_curl=False)
    if error and error.code != 6:
        # error code 6 means the ad account already exists; we can ignore it.
        print(f"ERROR: {error.message}")
        sys.exit()

    # We can assume that the ad account exists at this line, because we checked it above.

    #
    # invite the user
    #
    curl, error, user_join_request = a.invite_user(account_id, user_email, user_name, user_role, to_curl)
    if to_curl:
        print(curl)
    elif error:
        print(f"ERROR: {error.message}")
        sys.exit()
    else:
        print(user_join_request)


@app.command()
def create_account(
    account_id: str = typer.Option(help="Ad account ID"),
    account_name: str = typer.Option(help="Ad account name"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    Create a new ad account.
    """
    a = _create_account_command(profile)
    if a is None:
        return

    curl, error, account_info = a.create_account(account_id, account_name, to_curl)
    if to_curl:
        print(curl)
        sys.exit()
    if error:
        print(f"ERROR: {error.message}")
        sys.exit()
    if account_info is None:
        print(f"ERROR: account information is None, which is not supposed to be.")
        sys.exit()

    if to_json:
        print(account_info.model_dump_json())
        sys.exit()

    print(f"""Ad account ID {account_info.id} ("{account_info.title}") has been created.""")


@app.command()
def list_accounts(
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    List all ad accounts on the platform.
    """
    a = _create_account_command(profile)
    if a is None:
        return

    curl, error, accounts = a.list_accounts(to_curl)
    if to_curl:
        print(curl)
        return
    if error:
        print(f"ERROR: {error.message}")
        return
    if to_json:
        json_dumps = [x.model_dump_json() for x in accounts.values()]
        print(f"[{','.join(json_dumps)}]")
        return

    print("Ad Account ID, State, Ad Account Title")
    for a in accounts.values():
        print(f"{a.id}, {a.state_info.state}, {a.title}")

    return

@app.command()
def list_account_items(
    account_id: str = typer.Option(help="Ad account ID"),
    to_curl: bool = typer.Option(False, help="Generate the curl command instead of executing it."),
    to_json: bool = typer.Option(False, help="Print raw output in json"),
    profile: str = typer.Option("default", help="profile name of the MCM CLI."),
):
    """
    List all items for a given ad account.
    """
    a = _create_account_command(profile)
    if a is None:
        return

    curl, error, items = a.list_account_items(account_id, to_curl)

    if to_curl:
        print(curl)
        sys.exit()
    if error:
        print(f"ERROR: {error.message}")
        sys.exit()
    if to_json:
        json_dumps = [x.model_dump_json() for x in items]
        print(f"[{','.join(json_dumps)}]")
        sys.exit()

    print("Ad Account ID, Item ID, Is Active, Created At, Item Title")
    for i in items:
        print(f"{account_id}, {i.id}, {i.is_active}, {i.created_timestamp}, {i.title}")


class AccountCommand:
    def __init__(
        self,
        profile,
        auth_command: AuthCommand,
    ):
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


    def retry_with_token_refresh(
        self,
        operation: Callable[[], Tuple[Optional[Error], Any]],
        max_retries: int = 3,
        delay: int = 1,
    ) -> Tuple[
        Optional[Error],
        Any
    ]:
        retries = 0
        while retries < max_retries:
            error, result = operation()
            if error and error.code == 16:
                print(f"\nERROR: authentication token expired. Retrying...", file=sys.stderr, flush=True)
                self.refresh_token()
                retries += 1
                time.sleep(delay)
                continue
            return error, result
        return Error(code=16, message="Failed to regain an authentication token"), None


    def send_invitation_email(
        self,
        account_id: str,
        email_address: str,
        user_name: str,
        create_user: bool,
    ) -> Optional[Error]:

        error, user_dictionary = self.list_account_users(account_id)
        if error:
            return error

        user = _lookup_dict(email_address, user_dictionary)
        if user is None:
            if not create_user:
                _msg = f"\nERROR: The ad account {account_id} exists. But we could not find the user with email {email_address}"
                print(_msg, file=sys.stderr, flush=True)
                return Error(code=1, message = _msg)

            _, error, _ = self.invite_user(account_id, email_address, user_name, to_curl=False)
            return error

        #
        # The ad account and the user exists. We can just send the password reset email
        #
        _api_url = f"{self.api_base_url}/users/{user.id}/password-reset-tokens"
        _, error, _ = api_request('POST', False, _api_url, self.headers)
        return error

    def send_invitation_email_with_retry(
        self,
        account_id: str,
        email_address: str,
        user_name: str,
        create_user: bool,
        dry_run: bool,
    ) -> Optional[Error]:
        if dry_run:
            return None

        error, _ = self.retry_with_token_refresh(
            lambda: (
                self.send_invitation_email(account_id, email_address, user_name, create_user),
                None,
            ),
        )
        return error


    def delete_user(
        self,
        account_id,
        user_id,
        send_email_notification,
    ) -> Optional[Error]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/users/{user_id}?reason=UserDeleted"
        if not send_email_notification:
            _api_url += "&bypass_notification=true"

        _, error, _ = api_request('DELETE', False, _api_url, self.headers)

        return error


    def invite_user(
        self,
        account_id,
        user_email,
        user_name,
        role = UserRole.AD_ACCOUNT_OWNER,
        to_curl = True,
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        Optional[User]
    ]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/users"
        _payload = {
            "user": {
                "ad_account_id": account_id,
                "email": user_email,
                "name": user_name,
                "role": role.value,
            }
        }
        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None

        ret = UserWrapper(**json_obj).user
        return None, None, ret

    def activate_account(
        self,
        account: Account,
        ) -> Optional[Error]:
        account.state_info.state = "ACTIVE"
        account.state_info.state_case = "ACTIVATED"

        _api_url = f"{self.api_base_url}/ad-accounts/{account.id}"
        _payload = {
            "ad_account": account.model_dump_json()
        }
        _, error, _ = api_request('POST', False, _api_url, self.headers, _payload)
        if error:
            return error

        _api_url = f"{self.api_base_url}/ad_accounts/{account.id}/state-info"
        _payload = account.state_info.model_dump_json()
        _, error, _ = api_request('POST', False, _api_url, self.headers, _payload)
        if error:
            return error

        return None


    
    def activate_account_with_retry(
        self,
        account: Account,
    ) -> Optional[Error]:
        retries = 0
        delay = 1
        max_retries = 3
        while retries < max_retries:
            error = self.activate_account(account)
            if error and error.code == 16:
                print(f"\nERROR: authentication token expired. Retrying...", file=sys.stderr, flush=True)
                self.refresh_token()
                retries += 1
                time.sleep(delay)
                continue
            return error
        return Error(code=16, message="Failed to regain an authentication token")


    def create_account(
        self,
        account_id,
        account_name,
        to_curl
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        Optional[Account]
    ]:
        _api_url = f"{self.api_base_url}/ad-accounts"
        _payload = {
            "ad_account": {
                "id": account_id,
                "title": account_name                
            }
        }

        curl, error, json_obj = api_request('POST', to_curl, _api_url, self.headers, _payload)
        if curl:
            return curl, None, None
        if error:
            return None, error, None
        
        account_info = Account(**json_obj['ad_account'])
        return None, None, account_info


    def create_account_with_retry(
        self,
        account_id: str,
        account_name: str,
        dry_run: bool,
    ) -> tuple[
        Optional[Error],
        Optional[Account],
    ]:
        if dry_run:
            #print(f"\nDRY RUN: create_account({account_id}, {account_name})")
            return None, None

        retries = 0
        delay = 1
        max_retries = 3
        while retries < max_retries:
            _, error, account = self.create_account(account_id, account_name, to_curl=False)
            if error and error.code == 16:
                print(f"\nERROR: authentication token expired. Retrying...", file=sys.stderr, flush=True)
                self.refresh_token()
                retries += 1
                time.sleep(delay)
                continue
            return error, account
        return Error(code=16, message="Failed to regain an authentication token"), None


    def list_accounts(
        self,
        to_curl=False
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        Dict[str, Account],
    ]:
        _api_url = f"{self.api_base_url}/ad-accounts"

        curl, error, json_obj = api_request('GET', to_curl, _api_url, self.headers)
        if curl:
            return curl, None, {}
        if error:
            return None, error, {}

        account_list = AccountListWrapper(**json_obj).ad_accounts

        accounts = {}
        for x in account_list:
            accounts[x.id] = x
        return None, None, accounts


    def list_sellers(
        self,
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        Dict[str, Seller],
    ]:
        _api_url = f"{self.api_base_url}/sellers"

        curl, error, json_obj = api_request('GET', False, _api_url, self.headers)
        if curl:
            return curl, None, {}
        if error:
            return None, error, {}

        seller_list = SellerListWrapper(**json_obj).sellers

        sellers = {}
        for x in seller_list:
            sellers[x.id] = x
        return None, None, sellers


    def list_account_users(
        self,
        account_id: str,
    ) -> tuple [
        Optional[Error],
        Dict[str, User],
    ]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/users"

        _, error, json_obj = api_request('GET', False, _api_url, self.headers)
        if error:
            return error, {}
        user_list = UserListWrapper(**json_obj).users

        users = {}
        for x in user_list:
            users[x.email] = x

        return None, users

    def list_account_users_with_retry(
        self,
        account_id: str
    ) -> tuple [
        Optional[Error],
        Dict[str, User],
    ]:
        return self.retry_with_token_refresh(
            lambda: self.list_account_users(account_id),
        )


    def list_account_items(
        self,
        account_id,
        to_curl=False
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        list[Item]
    ]:
        _api_url = f"{self.api_base_url}/ad-accounts/{account_id}/items"
        _payload = {
            "ad_account_id": account_id,
            "search_keyword":[],
            "order_by": [{
                "column": "ID",
                "direction": "ASC"
            }],
            "filter": [
                {
                    "column": "IS_ACTIVE",
                    "filter_operator": "EQ",
                    "value": "true or false",
                }
            ],
            "page_index": 1,
            "page_size": MAX_NUM_ITEMS_PER_PAGE,
        }

        #
        # Get active items
        #
        curl, error, active_items = self.list_account_items_(to_curl, _api_url, self.headers, _payload, True)
        if curl:
            return curl, None, []
        if error:
            return None, error, []
        #
        # Get inactive items
        #
        _, error, inactive_items = self.list_account_items_(to_curl, _api_url, self.headers, _payload, False)
        if error:
            return None, error, []

        return None, None, active_items + inactive_items


    def list_account_items_(
        self, 
        to_curl,
        _api_url,
        _headers,
        _payload,
        _is_active
    ) -> tuple[
        Optional[CurlString],
        Optional[Error],
        list[Item]
    ]:
        items = []
        num_items = 0
        page_index = 1
        while True:
            _payload["page_index"] = page_index
            _payload["filter"][0]["value"] = "true" if _is_active else "false"

            curl, error, json_obj = api_request('POST', to_curl, _api_url, _headers, _payload)
            if curl:
                return curl, None, []
            if error:
                return None, error, []

            item_group = ItemList(**json_obj)
            items += item_group.rows
            num_items += len(item_group.rows)

            if num_items >= item_group.num_counts:
                break
            page_index += 1

        return None, None, items
    


#
# Helper functions
#
def _create_account_command(
        profile: str
) -> Optional[AccountCommand]:
    auth = AuthCommand(profile)
    return AccountCommand(profile, auth)


def _read_csv_file(
    csv_file: str,
    skip_csv_header: bool,
) -> Optional[list[list]]:
    try:
        with open(csv_file, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            if skip_csv_header:
                next(csv_reader)
            return list(csv_reader)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr, flush=True)
        return None


def _lookup_dict(
    id: str,
    dictionary: Dict[str, T],
) -> Optional[T]:
    if id in dictionary:
        return dictionary[id]
    return None


