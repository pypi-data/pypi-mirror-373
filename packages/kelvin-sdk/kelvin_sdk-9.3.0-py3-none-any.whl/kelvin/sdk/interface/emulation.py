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

from typing import Any, Optional

from typeguard import typechecked

from kelvin.sdk.lib.models.apps.ksdk_app_setup import ProjectEmulationObject
from kelvin.sdk.lib.models.operation import OperationResponse


# 1 - Internal
@typechecked
def emulation_start_simple(
    app_name_with_version: Optional[str] = None,
    app_config: Optional[str] = None,
    show_logs: bool = False,
) -> OperationResponse:
    """
    Start an application on the emulation system.

    Parameters
    ----------
    app_name_with_version: Optional[str]
        the application's name.
    app_config: Optional[str]
        the app configuration file to be used on the emulation.
    show_logs: bool
        if provided, will start displaying logs once the app is emulated.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating whether the app was successfully started.

    """
    from kelvin.sdk.lib.emulation.emulation_manager import emulation_start_simple as _emulation_start_simple

    return _emulation_start_simple(
        app_name_with_version=app_name_with_version, app_config=app_config, show_logs=show_logs
    )


@typechecked
def emulation_start(project_emulation_object: ProjectEmulationObject) -> OperationResponse:
    """
    Start an application on the emulation system.

    Parameters
    ----------
    project_emulation_object: ProjectEmulationObject
        the application's emulation object.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating whether the app was successfully started.

    """
    from kelvin.sdk.lib.emulation.emulation_manager import emulation_start as _emulation_start

    return _emulation_start(project_emulation_object=project_emulation_object)


@typechecked
def emulation_list(should_display: bool = False) -> OperationResponse:
    """
    Retrieve the list of all running containers in the Emulation System.

    Parameters
    ----------
    should_display: bool
        specifies whether or not output data should be displayed.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the containers running in the Emulation System

    """
    from kelvin.sdk.lib.emulation.emulation_manager import get_all_emulation_system_running_containers

    return get_all_emulation_system_running_containers(should_display=should_display)


@typechecked
def emulation_reset() -> OperationResponse:
    """
    Reset the Emulation System.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the Emulation System reset.

    """
    from kelvin.sdk.lib.emulation.emulation_manager import emulation_reset as _emulation_reset

    return _emulation_reset()


@typechecked
def emulation_stop(app_name_with_version_or_container: Optional[str] = None) -> OperationResponse:
    """
    Stop a running application on the emulation system.

    Parameters
    ----------
    app_name_with_version_or_container: Optional[str]
        the name of the app to stop.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating a message indicating whether the application was successfully stopped.

    """
    from kelvin.sdk.lib.emulation.emulation_manager import emulation_stop as _emulation_stop

    return _emulation_stop(app_name_with_version=app_name_with_version_or_container)


@typechecked
def emulation_logs(
    app_name_with_version_or_container: Optional[str] = None,
    tail: Optional[int] = None,
    should_print: bool = True,
    stream: bool = True,
    follow: bool = False,
) -> OperationResponse:
    """
    Display the logs of a running application.

    Parameters
    ----------
    app_name_with_version_or_container: Optional[str]
        the name of the application or container to retrieve the logs from.
    tail: Optional[int]
        indicates whether it should tail the logs and return.
    should_print: bool
        indicates whether the logs should be printed
    stream: bool
        indicates whether it should tail the logs and return.
    follow: bool
        indicates whether it should follow the logs stream.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object containing the status whether the App was successfully started.

    """
    from kelvin.sdk.lib.emulation.emulation_manager import emulation_logs as _emulation_logs

    return _emulation_logs(
        app_name_with_version=app_name_with_version_or_container,
        tail=tail,
        should_print=should_print,
        stream=stream,
        follow=follow,
    )


# 2 - Server
@typechecked
def emulation_start_server(
    app_name_with_version: Optional[str] = None, app_config: Optional[str] = None, tail: Optional[int] = None
) -> Any:
    """
    Start an application on the emulation system.

    Parameters
    ----------
    app_name_with_version: Optional[str]
        the application's name.
    app_config: Optional[str]
        the app configuration file to be used on the emulation.
    tail: Optional[int]
        the application's emulation object.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating whether the app was successfully started.

    """
    from kelvin.sdk.lib.emulation.emulation_manager import emulation_start_server as _emulation_start_server

    return _emulation_start_server(app_name_with_version=app_name_with_version, app_config=app_config, tail=tail)


@typechecked
def emulation_stop_server(
    app_name_with_version: Optional[str] = None, container_name: Optional[str] = None
) -> OperationResponse:
    """
    Stop a running application on the emulation system.

    Parameters
    ----------
    app_name_with_version: Optional[str]
        the name of the app to stop.
    container_name : Optional[str]
        the container name to stop on the emulation system

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating whether the app was successfully stopped.

    """
    from kelvin.sdk.lib.emulation.emulation_manager import emulation_stop as _emulation_stop

    return _emulation_stop(app_name_with_version=app_name_with_version, container_name=container_name)
