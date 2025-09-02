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

from typeguard import typechecked

from kelvin.sdk.lib.models.operation import OperationResponse


@typechecked
def global_configuration_list(should_display: bool = False) -> OperationResponse:
    """
    List all available configurations for the Kelvin-SDK

    Parameters
    ----------
    should_display: bool, Default=False
        specifies whether or not the display should output data.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the yielded Kelvin tool configurations.

    """
    from kelvin.sdk.lib.session.session_manager import session_manager

    return session_manager.global_configuration_list(should_display=should_display)


@typechecked
def global_configuration_set(configuration: str, value: str) -> OperationResponse:
    """
    Set the specified configuration on the platform system.

    Parameters
    ----------
    configuration: str
        the configuration to change.
    value: str
        the value that corresponds to the provided config.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result the configuration set operation.

    """
    from kelvin.sdk.lib.session.session_manager import session_manager

    return session_manager.global_configuration_set(configuration=configuration, value=value)


@typechecked
def global_configuration_unset(configuration: str) -> OperationResponse:
    """
    Unset the specified configuration from the platform system

    Parameters
    ----------
    configuration: str
        the configuration to unset.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result the configuration unset operation.

    """
    from kelvin.sdk.lib.session.session_manager import session_manager

    return session_manager.global_configuration_unset(configuration=configuration)


@typechecked
def configuration_autocomplete(shell_type: str) -> bool:
    """
    Generate completion commands for shell.

    """
    from click.shell_completion import shell_complete

    from kelvin.sdk.cli.ksdk import ksdk

    shell_complete(
        cli=ksdk,  # noqa
        ctx_args={},
        prog_name="kelvin",
        complete_var="_KELVIN_COMPLETE",
        instruction=f"{shell_type}_source",
    )

    return True


@typechecked
def full_reset(ignore_destructive_warning: bool = False) -> OperationResponse:
    """
    Reset all configurations & cache used by Kelvin SDK.

    Parameters
    ----------
    ignore_destructive_warning : bool
        indicates whether or not the command should bypass the destructive prompt warning.

    Returns
    -------
    OperationResponse
        an OperationResponse encapsulating the result of the reset operation.

    """
    from kelvin.sdk.lib.session.session_manager import session_manager as _session_manager

    return _session_manager.full_reset(ignore_destructive_warning=ignore_destructive_warning)
