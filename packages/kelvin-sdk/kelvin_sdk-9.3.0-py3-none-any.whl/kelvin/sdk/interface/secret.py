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

from typeguard import typechecked

from kelvin.sdk.lib.models.operation import OperationResponse


@typechecked
def secret_create(secret_name: str, value: str) -> OperationResponse:
    """
    Create a secret on the platform.

    Parameters
    ----------
    secret_name: str
        The name of the secret to create.
    value: str
        The value corresponding to the secret.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the secrets creation operation.

    """
    from kelvin.sdk.lib.api.secret import secret_create as _secret_create

    return _secret_create(secret_name=secret_name, value=value)


@typechecked
def secret_list(query: Optional[str] = None, should_display: bool = False) -> OperationResponse:
    """
    List all the available secrets on the Platform.

    Parameters
    ----------
    query: Optional[str]
        The query to filter the secrets by.
    should_display: bool, Default=False
        specifies whether or not the display should output data.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the secrets available on the platform.

    """
    from kelvin.sdk.lib.api.secret import secret_list as _secret_list

    return _secret_list(query=query, should_display=should_display)


@typechecked
def secret_delete(secret_names: Sequence[str], ignore_destructive_warning: bool = False) -> OperationResponse:
    """
    Delete secrets on the platform.

    Parameters
    ----------
    secret_names: Sequence[str]
        The names of the secrets to delete.
    ignore_destructive_warning: bool, Default=False
        indicates whether it should ignore the destructive warning.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the secrets deletion operation.

    """
    from kelvin.sdk.lib.api.secret import secret_delete as _secret_delete

    return _secret_delete(secret_names=secret_names, ignore_destructive_warning=ignore_destructive_warning)


@typechecked
def secret_update(secret_name: str, value: str) -> OperationResponse:
    """
    Update an existing secret on the platform.

    Parameters
    ----------
    secret_name: str
        The name of the secret to update.
    value: str
        The new value for the secret.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the secret update operation.
    """
    from kelvin.sdk.lib.api.secret import secret_update as _secret_update

    return _secret_update(secret_name=secret_name, value=value)
