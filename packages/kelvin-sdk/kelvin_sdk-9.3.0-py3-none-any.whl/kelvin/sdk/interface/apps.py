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

from typing import Dict, List

from typeguard import typechecked

from kelvin.sdk.lib.models.operation import OperationResponse


@typechecked
def apps_list(should_display: bool = False) -> OperationResponse:
    """
    Returns the list of apps on the registry.

    Parameters
    ----------
    should_display: bool
        specifies whether or not the display should output data.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the Applications available on the platform.

    """
    from kelvin.sdk.lib.api.apps import apps_list as _apps_list

    return _apps_list(query=None, should_display=should_display)


@typechecked
def apps_search(query: str, should_display: bool = False) -> OperationResponse:
    """
    Search for apps on the registry that match the provided query.

    Parameters
    ----------
    query: str
        the query to search for.
    should_display: bool
        specifies whether or not the display should output data.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the matching Applications available on the platform.

    """
    from kelvin.sdk.lib.api.apps import apps_list as _apps_list

    return _apps_list(query=query, should_display=should_display)


@typechecked
def apps_show(app_name: str, should_display: bool = False) -> OperationResponse:
    """
    Returns detailed information on the specified application.

    Parameters
    ----------
    app_name: str
        the name with version of the app.
    should_display: bool
        specifies whether or not the display should output data.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the yielded Application instance and its data.

    """
    from kelvin.sdk.lib.api.apps import apps_show as _apps_show

    return _apps_show(app_name=app_name, should_display=should_display)


@typechecked
def apps_upload(app_dir: str, build_args: Dict[str, str] = {}, archs: List[str] = []) -> OperationResponse:
    """
    Uploads the specified application to the platform.

    - Packages the app
    - Pushes the app to the docker registry
    - Publishes the app on the apps endpoint.

    Parameters
    ----------
    app_dir: str
        the path to the application's dir.
    multiarch: bool
        If specified, will try to build the application for multiple architectures.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the upload operation.

    """
    from kelvin.sdk.lib.api.apps import apps_upload as _apps_upload

    return _apps_upload(app_dir_path=app_dir, build_args=build_args, archs=archs)


@typechecked
def apps_download(
    app_name_with_version: str, override_local_tag: bool = False, tag_local_name: bool = True
) -> OperationResponse:
    """
    Downloads the specified application from the platform's app registry.

    Parameters
    ----------
    app_name_with_version: str
        the app with version to be downloaded.
    override_local_tag: bool
        specifies whether or not it should override the local tag.
    tag_local_name: bool
        specifies whether or not the local name should be tagged (no registry).

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the app download operation.

    """
    from kelvin.sdk.lib.api.apps import apps_download as _apps_download

    return _apps_download(
        app_name_with_version=app_name_with_version,
        override_local_tag=override_local_tag,
        tag_local_name=tag_local_name,
    )


@typechecked
def apps_delete(app_name_with_version: str, ignore_destructive_warning: bool = False) -> OperationResponse:
    """
    Deletes the specified application the platform's app registry.

    Parameters
    ----------
    app_name_with_version: str
        the name with version of the app to be deleted.
    ignore_destructive_warning: bool
        indicates whether it should ignore the destructive warning.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the app deletion operation.

    """
    from kelvin.sdk.lib.api.apps import apps_delete as _apps_delete

    return _apps_delete(
        app_name_with_version=app_name_with_version, ignore_destructive_warning=ignore_destructive_warning
    )
