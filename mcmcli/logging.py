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

import sys
import threading
import time
import typer

def print_error(api_url, message):
    # Something's wrong. Print error and exit.

    _msg = typer.style(f"\nERROR: {message}", fg=typer.colors.RED, bold=True)
    typer.echo(_msg, file=sys.stderr)

    _msg = typer.style(f"URL = {api_url}", fg=typer.colors.YELLOW, bold=True)
    typer.echo(_msg, file=sys.stderr)

    friendly_message = "Check if you used the accurate values of the API hostname, Platform ID, and Ad Account ID."
    _msg = typer.style(friendly_message, fg=typer.colors.WHITE, bold=True)
    typer.echo(_msg, file=sys.stderr)

def _print_dot(stopper):
    while not stopper.is_set():
        print(".", file=sys.stderr, end="", flush=True)
        time.sleep(1)

def start_dot_printing():
    stopper = threading.Event()
    thread = threading.Thread(target=_print_dot, args=[stopper])
    thread.setDaemon(True)
    thread.start()
    return (thread, stopper)

def stop_dot_printing(thread, stopper):
    stopper.set()
    thread.join()

def echo(message):
    print(message, file=sys.stderr, end="", flush=True)

def echo_newline(message):
    print(message, file=sys.stderr, flush=True)