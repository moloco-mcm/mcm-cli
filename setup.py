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
    version='1.6.0',
    description='A command-line interface for Moloco Commerde Media',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license="Apache-2.0 license",
    author='Moloco MCM Team',
    author_email='mcm-help@moloco.com',
    url='https://github.com/moloco-mcm/mcm-cli',
    python_requires='>=3.6',
    packages=['mcmcli', 'mcmcli.command', 'mcmcli.data'],
    entry_points={
        'console_scripts': ['mcm = mcmcli.__main__:console_entry_point'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'colorama',
        'gitpython',
        'pydantic',
        'pygithub',
        'python-terraform',
        'requests',
        'rich',
        'setuptools',
        'shortuuid',
        'toml',
        'typer'
    ],
)
