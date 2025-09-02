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

from typing import Optional

import click

from kelvin.sdk.lib.configs.general_configs import KSDKHelpMessages
from kelvin.sdk.lib.utils.click_utils import KSDKCommand, KSDKGroup


@click.group(cls=KSDKGroup)
def auth() -> None:
    """Platform authentication."""


@auth.command(cls=KSDKCommand, name="reset")
def reset_config() -> bool:
    """Reset all authentication and configuration cache."""
    from kelvin.sdk.interface import reset as _reset

    return _reset().success


@auth.command(cls=KSDKCommand)
@click.argument("url", type=click.STRING, nargs=1, required=False)
@click.option("--username", type=click.STRING, required=False, help=KSDKHelpMessages.login_username)
@click.option("--password", type=click.STRING, required=False, help=KSDKHelpMessages.login_password)
@click.option("--totp", type=click.STRING, required=False, help=KSDKHelpMessages.login_totp)
@click.option("--browser", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.browser)
@click.option("--reset", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.reset)
def login(url: Optional[str], username: str, password: str, totp: Optional[str], browser: bool, reset: bool) -> bool:
    """Login on the platform."""
    from kelvin.sdk.interface import login as _login

    return _login(
        url=url, username=username, password=password, totp=totp, browser=browser, reset_credentials=reset
    ).success


@auth.command(cls=KSDKCommand)
@click.option("-y", "--yes", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.yes)
def logout(yes: bool) -> bool:
    """Logout from the platform."""
    from kelvin.sdk.interface import logout as _logout

    return _logout(ignore_destructive_warning=yes).success


@auth.command(cls=KSDKCommand)
@click.option("-f", "--full", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.token_full)
@click.option("-m", "--margin", type=click.FLOAT, default=10.0, show_default=True, help=KSDKHelpMessages.token_margin)
def token(full: bool, margin: float) -> bool:
    """Obtain an authentication token for the platform."""

    from kelvin.sdk.interface import authentication_token as _authentication_token

    return _authentication_token(full=full, margin=margin).success
