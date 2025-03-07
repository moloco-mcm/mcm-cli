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

#!/usr/bin/env python3

"""mcm cli entry point script."""
# mcmcli/__main__.py

from typing import Optional

import mcmcli.command.account
import mcmcli.command.admin
import mcmcli.command.auth
import mcmcli.command.campaign
import mcmcli.command.config
import mcmcli.command.decision
import mcmcli.command.report
import mcmcli.command.wallet
import mcmcli.logging
import typer

app = typer.Typer(add_completion=False)

@app.command()
def version():
	"""
	Show the tool version
	"""
	typer.echo(f"Version: mcm-cli v1.6.0")

app.add_typer(mcmcli.command.account.app, name="account", help="Ad account management")
app.add_typer(mcmcli.command.admin.app, name="admin", help="Platform administration")
app.add_typer(mcmcli.command.auth.app, name="auth", help="Authentication management")
app.add_typer(mcmcli.command.campaign.app, name="campaign", help="Campaign management")
app.add_typer(mcmcli.command.config.app, name="config", help="Configurations")
app.add_typer(mcmcli.command.decision.app, name="decision", help="Decision command")
app.add_typer(mcmcli.command.report.app, name="report", help="Report commands")
app.add_typer(mcmcli.command.wallet.app, name="wallet", help="Wallet management")

if __name__ == "__main__":
	app()

def console_entry_point():
	app()
