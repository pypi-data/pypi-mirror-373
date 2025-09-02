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

from typing import Dict, List, Optional

from typeguard import typechecked

from kelvin.sdk.lib.models.apps.common import ApplicationLanguage
from kelvin.sdk.lib.models.apps.ksdk_app_configuration import ApplicationFlavour, ProjectType
from kelvin.sdk.lib.models.apps.ksdk_app_setup import ProjectCreationParametersObject
from kelvin.sdk.lib.models.operation import OperationResponse


@typechecked
def app_create_from_parameters(
    app_dir: str,
    app_name: str,
    app_description: str,
    app_type: ProjectType,
    app_flavour: ApplicationFlavour,
    kelvin_app_lang: ApplicationLanguage,
) -> OperationResponse:
    """
    The entry point for the creation of an application. (Parameters)

    - Creates the directory that will contain the app app.
    - Creates all necessary base files for the development of the app.

    Parameters
    ----------
    app_dir: str
        the app's targeted dir. Will contain all the application files.
    app_name: str
        the name of the new app.
    app_description: str
        the description of the new app.
    app_type: ProjectType, optional
        the type of the new application. # E.g. 'docker', 'kelvin'.
    app_flavour: ApplicationFlavour, optional
        the flavour of the new application. # E.g. 'default', 'injector', 'extractor'.
    kelvin_app_lang: ApplicationLanguage, optional
        the language the new app will be written on. For kelvin apps only. # E.g. python.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the result of the creation of the application.

    """
    from kelvin.sdk.lib.apps.local_apps_manager import app_create_from_parameters as _project_create_from_parameters

    return _project_create_from_parameters(
        app_dir=app_dir,
        app_name=app_name,
        app_description=app_description,
        app_type=app_type,
        app_flavour=app_flavour,
        kelvin_app_lang=kelvin_app_lang,
    )


@typechecked
def app_create(project_creation_parameters: ProjectCreationParametersObject) -> OperationResponse:
    """
    The entry point for the creation of an application. (Parameters)

    - Creates the directory that will contain the app app.
    - Creates all necessary base files for the development of the app.

    Parameters
    ----------
    project_creation_parameters: ProjectCreationParametersObject
        the object containing all the required variables for App creation.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the result of the creation of the application.
    """

    from kelvin.sdk.lib.apps.local_apps_manager import project_create as _project_create

    return _project_create(project_creation_parameters=project_creation_parameters)


@typechecked
def app_config(app_config_file_path: str) -> OperationResponse:
    """
    Yields the loaded json/dict for the provided configuration file path. (Parameters)

    Parameters
    ----------
    app_config_file_path: str
        the object containing all the required variables for App creation.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the json of the app configuration file.

    """
    from kelvin.sdk.lib.apps.local_apps_manager import app_config as _app_config

    return _app_config(app_config_file_path=app_config_file_path)


@typechecked
def app_build(
    app_dir: str, fresh_build: bool = False, build_args: Dict[str, str] = {}, archs: List[str] = []
) -> OperationResponse:
    """
    The entry point for the building of an App.

    Package the App on the provided app directory.

    Parameters
    ----------
    app_dir: str
        The path where the application is hosted.
    fresh_build: bool
        If specified, will remove any cache and rebuild the application from scratch.
    build_args: Dict[str, str]
        Key-value pairs of build arguments for the application.
    archs: List[str]
        A list of architectures to build for.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        An OperationResponse object wrapping the result of the application build process.

    """
    from kelvin.sdk.lib.apps.local_apps_manager import project_build as _project_build

    return _project_build(
        app_dir=app_dir, fresh_build=fresh_build, build_for_upload=False, build_args=build_args, archs=archs
    )


@typechecked
def app_images_list(should_display: bool = False) -> OperationResponse:
    """
    Retrieve the list of all application images available on the local registry.

    Parameters
    ----------
    should_display: bool
        specifies whether or not output data should be displayed.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the app images available on the local registry.

    """
    from kelvin.sdk.lib.emulation.emulation_manager import get_local_appregistry_images

    return get_local_appregistry_images(should_display=should_display)


@typechecked
def app_image_remove(app_name_with_version: str) -> OperationResponse:
    """
    Remove the specified application from the existing image list (in the docker instance).

    Parameters
    ----------
    app_name_with_version: str
        the app to be removed. Must include the version.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the result of the application image removal operation.

    """
    from kelvin.sdk.lib.apps.local_apps_manager import app_image_remove as _app_image_remove

    return _app_image_remove(app_name_with_version=app_name_with_version)


@typechecked
def app_image_unpack(app_name_with_version: str, container_dir: Optional[str], output_dir: str) -> OperationResponse:
    """
    Extract the content of an application from its built image.

    Parameters
    ----------
    app_name_with_version: str
        the name of the image to unpack the app from.
    container_dir: str
        The directory to extract from the container.
    output_dir: str
        the output directory to output the extracted content.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the result of the application image unpack operation.

    """
    from kelvin.sdk.lib.apps.local_apps_manager import app_image_unpack as _app_image_unpack

    return _app_image_unpack(
        app_name_with_version=app_name_with_version, container_dir=container_dir, output_dir=output_dir
    )
