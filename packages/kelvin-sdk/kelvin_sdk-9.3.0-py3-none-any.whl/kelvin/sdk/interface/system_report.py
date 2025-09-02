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

from typeguard import typechecked

from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.models.types import LogType


@typechecked
def kelvin_support_report(app_config: Optional[str] = None, generate_report_file: bool = True) -> OperationResponse:
    """
    Report the user's system information and log records for support purposes.

    Parameters
    ----------
    app_config: Optional[str]
        the path to the application's configuration file.
    generate_report_file: bool, Default=True
        if set to true, will generate the report file to the default location.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the host machine's system report.

    """
    from kelvin.sdk.lib.system_report.system_report_manager import kelvin_support_report as _kelvin_support_report

    return _kelvin_support_report(app_config=app_config, generate_report_file=generate_report_file)


@typechecked()
def kelvin_system_information(display: bool = True, log_type: LogType = LogType.KSDK) -> OperationResponse:
    """
    Report the entire configuration set currently in use by Kelvin SDK.

    Parameters
    ----------
    display : bool
        indicates whether the information should be logged
    log_type : LogType
        the output log type of the output type. Applicable only if 'display' is true and for display purposes.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating provided system information and the currently logged platform.

    """
    from kelvin.sdk.lib.system_report.system_report_manager import (
        kelvin_system_information as _kelvin_system_information,
    )

    return _kelvin_system_information(display=display, log_type=log_type)
