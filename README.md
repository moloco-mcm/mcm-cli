# Moloco Commerce Media (MCM) CLI utility

This tool is a command-line interface for the Moloco Commerce Media Platform, formerly known as the Retail Media Platform.

Please contact the Moloco representative for more details.

## How to install

To install, run:
```
pip install mcm-cli
```

For installation from the source code, use:
```
git clone https://github.com/moloco-mcm/mcm-cli.git && pip install mcm-cli
```

## How to upgrade

To upgrade, run:
```
pip install --upgrade mcm-cli
```

Or, if installed from the source code:
```
git -C mcm-cli pull && pip install mcm-cli
```

## How to uninstall

To uninstall, run:
```
pip uninstall mcm-cli
```

## How to use
Initialize the configuration with:
```
mcm config init
```
This saves the configuration to `~/.mcm/config.toml`.

For more details on each command, use the `--help` option.
```
$ mcm --help

 Usage: mcm [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────╮
│ account    Ad account management                                 │
│ auth       Authentication management                             │
│ config     Configurations                                        │
│ decision   Decision command                                      │
│ version    Show the tool version                                 │
│ wallet     Wallet management                                     │
╰──────────────────────────────────────────────────────────────────╯

$
```

© Moloco, Inc. 2023 All rights reserved. Released under Apache 2.0 License
