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
from typing import Optional

import os
import sys
import toml
import typer

DEFAULT_CONFIG_DIR = os.path.expanduser('~') + "/.mcm/"
DEFAULT_CONFIG_FILE = os.path.expanduser('~') + "/.mcm/config.toml"

#
# Enum classes
#

class Profile(Enum):
    default = "default"
    shared = "shared"

app = typer.Typer(add_completion=False)


def get_config(profile = "default") -> Optional[dict]:
    
    if not os.path.exists(DEFAULT_CONFIG_FILE):
        return None

    with open(DEFAULT_CONFIG_FILE, "r") as f:
        d = toml.load(f)

    if profile in d:
        return d[profile]

    return None

def assert_config_exists(config) -> None:
    if config is None:
        print(f"ERROR: the configuration file or the profile doesn't exist.")
        sys.exit()

@app.command()
def init(profile: str = "default"):
    """
    The tool sets up the configuration file ~/.mcm/config.toml if it does not already exist.
    By default, it creates the "default" profile.
    To specify a different profile name, use the --profile option.
    To save your GitHub token, run the following command:
    `mcm config init --profile shared`
    """
    if not os.path.exists(DEFAULT_CONFIG_DIR):
        # ~/.mcm directory doesn't exist. Create one.
        os.mkdir(DEFAULT_CONFIG_DIR)

    if not os.path.isdir(DEFAULT_CONFIG_DIR):
        print("Error: A file ~/.mcm already exists. Please delete it so we tool can create ~/.mcm directory.")
        sys.exit()

    config = {}
    if os.path.exists(DEFAULT_CONFIG_FILE):
        with open(DEFAULT_CONFIG_FILE, "r") as f:
            config = toml.load(f)

    print(f"Creating a profile [{profile}] ...")
    config[profile] = {
        "platform_id":             typer.prompt("Platform ID"),
        "admin_email":             typer.prompt("Your email address of the Campaign Manager"),
        "admin_password":          typer.prompt("Password of the Campaign Manager"),
        "currency":                typer.prompt("Currency in a three digit code like 'USD'", default="USD"),
        "timezone":                typer.prompt("Timezone", default="unknown"),
        "decision_api_hostname":   typer.prompt("Decision API hostname", default="unknown"),
        "management_api_hostname": typer.prompt("Management API hostname", default="unknown"),
        "event_api_hostname":      typer.prompt("Event API hostname", default="unknown"),
        "decision_api_key":        typer.prompt("Decision API key", default="unknown"),
        "decision_api_key_name":   typer.prompt("Friendly name of the decision API key", default="unknown"),
        "event_api_key":           typer.prompt("Event API key", default="unknown"),
        "event_api_key_name":      typer.prompt("Friendly name of the event API key", default="unknown"),
        "management_api_key":      typer.prompt("Management API key", default="unknown"),
        "management_api_key_name": typer.prompt("Friendly name of the management API key", default="unknown"),
    }
    print(f"The profile [{profile}] has been created.")

    with open(DEFAULT_CONFIG_FILE, "w") as f:
        toml.dump(config, f)
    print("Configuration saved to ~/.mcm/config.toml")

@app.command()
def list(profile: str = "default"):
    """
    This command lists the profile name, decision api, managmement api, event api,
    decision api key, event api key, admin email and password.
    It will be retrieved from the ~/.mcm/config.toml
    """
    c = get_config(profile)
    if c is None:
        return

    for k, v in c.items():
        print(f"{k}: {v}")

@app.command()
def list_profiles():
    """
    To list all your profile names, use the `mcm config list-profiles` command.
    """
    with open(DEFAULT_CONFIG_FILE) as f:
        d = toml.load(f)
        for profiles in d:
            print(profiles)
