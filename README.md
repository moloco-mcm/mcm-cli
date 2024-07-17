# Moloco Commerce Media (MCM) CLI utility

This tool is a command-line interface for the Moloco Commerce Media Platform, formerly known as the Retail Media Platform.

Contact mcm-ce@moloco.com for more details.

## How to install

Run the command from a terminal.
```
pip install mcm-cli
```


Or if you wan to install from the source code, run the following command.
```
git clone https://github.com/moloco-mcm/mcm-cli.git && pip install mcm-cli
```

## How to upgrade

Run the command from a terminal.
```
pip install --upgrade mcm-cli
```

Or if you cloned the `moloco-mcm/mcm-cli` GitHub repository, run the command from a terminal.
```
git -C mcm-cli pull && pip install mcm-cli
```

## How to uninstall

Run the command from a terminal.
```
pip uninstall mcm-cli
```

## How to use
Run `$ mcm config init` to initialize the configuration. It saves the configuration to `~/.mcm/config.toml`.

Use `--help` option to learn more of each command.

```
$ mcm --help

 Usage: mcm [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────╮
│ auth       Authentication management                             │
│ config     Configurations                                        │
│ version                                                          │
│ wallet     Wallet management                                     │
╰──────────────────────────────────────────────────────────────────╯

$
```

© Moloco, Inc. 2023 All rights reserved. Released under Apache 2.0 License
