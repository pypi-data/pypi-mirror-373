"""
Copyright 2021 Kelvin Inc.

Licensed under the Kelvin Inc. Developer SDK License Agreement (the "License"); you may not use
this file except in compliance with the License.  You may obtain a copy of the
License at

http://www.kelvininc.com/developer-sdk-license

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
"""

from typing import Optional, Sequence

import click

from kelvin.sdk.lib.configs.general_configs import KSDKHelpMessages
from kelvin.sdk.lib.utils.click_utils import KSDKCommand, KSDKGroup


@click.group(cls=KSDKGroup)
def secret() -> None:
    """Manage platform 'secrets'."""


@secret.command(cls=KSDKCommand)
@click.argument("secret_name", nargs=1, type=click.STRING, required=False)
@click.option("--value", type=click.STRING, required=False, help=KSDKHelpMessages.secret_create_value)
def create(secret_name: str, value: str) -> bool:
    """Create a secret on the platform."""
    from kelvin.sdk.interface import secret_create

    if not secret_name and not value:
        secret_name = input("Enter the name of the secret you want to create: ")
        value = input("Enter the value of the secret you want to create: ")

    return secret_create(secret_name=secret_name, value=value).success


@secret.command(cls=KSDKCommand)
@click.option("query", "--filter", type=click.STRING, required=False, help=KSDKHelpMessages.secret_list_filter)
def list(query: Optional[str]) -> bool:
    """List all the available secrets on the platform."""
    from kelvin.sdk.interface import secret_list

    return secret_list(query=query, should_display=True).success


@secret.command(cls=KSDKCommand)
@click.argument("secret_names", nargs=-1, required=True, type=click.STRING)
@click.option("-y", "--yes", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.yes)
def delete(secret_names: Sequence[str], yes: bool) -> bool:
    """Delete secrets on the platform."""
    from kelvin.sdk.interface import secret_delete

    if not secret_names:
        secret_names = input("Enter the name of the secret you want to delete: ")

    return secret_delete(secret_names=secret_names, ignore_destructive_warning=yes).success


@secret.command(cls=KSDKCommand)
@click.argument("secret_name", nargs=1, type=click.STRING, required=True)
@click.option("--value", type=click.STRING, required=True, help="The new value for the secret.")
def update(secret_name: str, value: str) -> bool:
    """Update an existing secret on the platform."""
    from kelvin.sdk.interface import secret_update

    return secret_update(secret_name=secret_name, value=value).success
