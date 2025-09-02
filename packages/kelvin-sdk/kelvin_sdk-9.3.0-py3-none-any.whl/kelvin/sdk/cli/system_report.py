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

import click
from click import Choice

from kelvin.sdk.lib.configs.general_configs import KSDKHelpMessages
from kelvin.sdk.lib.models.types import LogType
from kelvin.sdk.lib.utils.click_utils import KSDKCommand


@click.command(cls=KSDKCommand)
@click.option(
    "--log-type",
    required=False,
    show_default=True,
    default=LogType.KSDK.value_as_str,
    type=Choice(LogType.as_list()),
    help=KSDKHelpMessages.report_app_config_file,
)
def info(log_type: LogType = LogType.KSDK) -> bool:
    """Provide system information and the currently logged platform."""
    from kelvin.sdk.interface import kelvin_system_information

    return kelvin_system_information(display=True, log_type=LogType(log_type)).success
