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

# setup.py

from setuptools import setup, find_packages

setup(
    name='mcm-cli',
    version='0.45',
    license="Apache-2.0 license",
    entry_points={
        'console_scripts': ['mcm = mcmcli.__main__:console_entry_point'],
    },
    packages=['mcmcli', 'mcmcli.command', 'mcmcli.data'],
    install_requires=[
        'colorama',
        'gitpython',
        'pydantic',
        'pygithub',
        'python-terraform',
        'requests',
        'rich',
        'shortuuid',
        'toml',
        'typer'
    ],
)

