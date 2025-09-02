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

from typing import Optional, Union

from kelvin.config.parser import AppConfigObj
from kelvin.sdk.lib.configs.docker_configs import DockerConfigs
from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.exceptions import AppException, InvalidApplicationConfiguration
from kelvin.sdk.lib.models.apps.bridge_app import BridgeAppType
from kelvin.sdk.lib.models.apps.common import ApplicationLanguage
from kelvin.sdk.lib.models.apps.kelvin_app import KelvinAppType
from kelvin.sdk.lib.models.apps.ksdk_app_configuration import KelvinAppConfiguration
from kelvin.sdk.lib.models.apps.ksdk_app_setup import (
    BridgeAppBuildingObject,
    KelvinAppBuildingObject,
    ProjectBuildingObject,
)
from kelvin.sdk.lib.models.generic import KPath
from kelvin.sdk.lib.models.ksdk_docker import DockerImageName
from kelvin.sdk.lib.models.ksdk_global_configuration import SDKMetadataEntry
from kelvin.sdk.lib.session.session_manager import session_manager
from kelvin.sdk.lib.utils.pypi_utils import get_pypi_credentials


def get_project_building_object(
    app_config_obj: AppConfigObj, app_dir: str, fresh_build: bool = False
) -> ProjectBuildingObject:
    """
    Create a ProjectBuildingObject from the provided app directory.

    This object will encapsulate all the necessary variables for the building of a base application, thus resulting
    in reduced, cleaner and more testable code.


    Parameters
    ----------
    app_dir : str
        the path to the application's dir.
    fresh_build : bool
        If specified will remove any cache and rebuild the application from scratch.

    Returns
    -------
    ProjectBuildingObject
        a ProjectBuildingObject containing all the necessary variables for the building of a base app.

    """
    app_dir_path: KPath = KPath(app_dir).complete_path()
    app_config_file_path: KPath = app_dir_path / GeneralConfigs.default_app_config_file
    app_build_dir_path: KPath = app_dir_path / GeneralConfigs.default_build_dir
    app_config_raw = {}
    app_config_model = None
    if app_config_obj.is_legacy():
        app_config_raw = app_config_file_path.read_yaml()
        app_config_model = KelvinAppConfiguration(**app_config_raw)

    docker_image_labels = DockerConfigs.ksdk_app_identification_label
    app_name = app_config_obj.name
    app_version = app_config_obj.version
    docker_image_name = app_name
    docker_image_labels["name"] = DockerImageName(
        name=app_name, version=app_version, raw_name=app_name
    ).name_with_version
    docker_image_labels["type"] = app_config_obj.type.value
    base_app_build_object = ProjectBuildingObject(
        # base building object
        fresh_build=fresh_build,
        app_config_file_path=app_config_file_path,
        app_config_raw=app_config_raw,
        app_config_model=app_config_model,
        app_dir_path=app_dir_path,
        app_build_dir_path=app_build_dir_path,
        app_name=app_name,
        app_version=app_version,
        app_type=app_config_obj.type.value,
        docker_image_labels=docker_image_labels,
        docker_image_name=docker_image_name,
    )
    return base_app_build_object


def get_kelvin_app_building_object(
    base_build_object: ProjectBuildingObject,
) -> KelvinAppBuildingObject:
    """
    Creates a KelvinAppBuildingObject from the specified parameters.

    This object will encapsulate all the necessary variables for the building of a kelvin application, thus resulting
    in reduced, cleaner and more testable code.

    Parameters
    ----------
    app_dir : str
        the path to the application's dir.
    app_config_raw : Optional[Dict]
        the raw app configuration dictionary.
    fresh_build : bool
        If specified will remove any cache and rebuild the application from scratch.
    build_for_upload : bool
         indicates whether or the package object aims for an upload.
    upload_datatypes : bool
         If specified, will upload locally defined datatypes.

    Returns
    -------
    KelvinAppBuildingObject
        a KelvinAppBuildingObject containing all the necessary variables for the building of a kelvin application.

    """
    # 1 - building a temp dir to copy the files into
    app_dir_path: KPath = KPath(base_build_object.app_dir_path)
    app_build_dir_path: KPath = app_dir_path / GeneralConfigs.default_build_dir
    app_datatype_dir_path: KPath = app_build_dir_path / GeneralConfigs.default_datatype_dir
    app_config_file_path: KPath = app_dir_path / GeneralConfigs.default_app_config_file
    app_config_raw = app_config_file_path.read_yaml()
    app_config_model = KelvinAppConfiguration(**app_config_raw)
    app_name = app_config_model.info.name
    app_version = app_config_model.info.version
    dockerfile_path: KPath = app_build_dir_path / GeneralConfigs.default_dockerfile

    kelvin_app_object: Optional[Union[KelvinAppType, BridgeAppType]] = app_config_model.app.app_type_configuration
    if kelvin_app_object is None:
        raise InvalidApplicationConfiguration()

    app_lang = ApplicationLanguage(kelvin_app_object.language.type)

    # Retrieve the metadata
    metadata_sdk_config: Optional[SDKMetadataEntry]
    try:
        site_metadata = session_manager.get_current_session_metadata()
        metadata_sdk_config = site_metadata.sdk
    except Exception:
        metadata_sdk_config = None

    build_args = {}
    if app_lang == ApplicationLanguage.python:
        build_args.update(get_pypi_credentials())
    else:
        raise AppException(f'Application language  "{app_lang.value}" not supported')

    # Setup the images
    kelvin_app_builder_image: Optional[str] = None
    kelvin_app_runner_image: Optional[str] = None
    reduced_size: bool = False

    if kelvin_app_object.images:
        kelvin_app_builder_image = kelvin_app_object.images.builder
        kelvin_app_runner_image = kelvin_app_object.images.runner

    if not kelvin_app_builder_image and metadata_sdk_config:
        kelvin_app_builder_image = metadata_sdk_config.components.get_builder_docker_image_for_lang(app_lang=app_lang)

    if not kelvin_app_runner_image and metadata_sdk_config:
        if app_lang == ApplicationLanguage.python and kelvin_app_object.language.python:
            are_requirements_available, _ = kelvin_app_object.language.python.requirements_available(
                app_dir_path=app_dir_path
            )
            reduced_size = not are_requirements_available
            kelvin_app_runner_image = metadata_sdk_config.components.get_runner_docker_image_for_lang(
                reduced_size=reduced_size
            )
    # Stop the process from going any further

    if not kelvin_app_builder_image:
        raise ValueError(
            """No data type builder image provided.

            1) Please login on a valid platform to retrieve the recommended version,
            or
            2) Provide one in the app.yaml under \"images -> builder\".

        """
        )
    if not kelvin_app_runner_image:
        raise ValueError(
            """No base image provided.

            1) Please login on a valid platform to retrieve the recommended version,
            or
            2) Provide one in the app.yaml under \"images -> runner\".

        """
        )

    docker_image_name = app_name
    docker_image_version = app_version
    docker_image_labels = DockerConfigs.ksdk_app_identification_label
    docker_image_labels["name"] = DockerImageName(
        name=app_name, version=app_version, raw_name=app_name
    ).name_with_version
    docker_image_labels["type"] = app_config_model.app.type.value_as_str

    return KelvinAppBuildingObject(
        app_name=app_config_model.info.name,
        app_version=app_config_model.info.version,
        app_type=app_config_model.app.type.value,
        # base building object
        fresh_build=base_build_object.fresh_build,
        build_for_upload=base_build_object.build_for_upload,
        upload_datatypes=False,
        app_config_file_path=app_config_file_path,
        app_config_raw=app_config_raw,
        app_config_model=app_config_model,
        app_dir_path=app_dir_path,
        app_build_dir_path=app_build_dir_path,
        docker_image_labels=docker_image_labels,
        docker_image_name=docker_image_name,
        docker_registry=base_build_object.docker_registry,
        # kelvin app building object
        dockerfile_path=dockerfile_path,
        docker_build_context_path=app_dir_path,
        kelvin_app_builder_image=kelvin_app_builder_image,
        kelvin_app_runner_image=kelvin_app_runner_image,
        reduced_size_kelvin_app_runner_image=reduced_size,
        docker_image_version=docker_image_version,
        build_args=build_args,
        app_datatype_dir_path=app_datatype_dir_path,
        archs=base_build_object.archs,
    )


def get_bridge_app_building_object(
    base_build_object: ProjectBuildingObject,
) -> BridgeAppBuildingObject:
    """
    Creates a BridgeAppBuildingObject from the specified parameters.

    This object will encapsulate all the necessary variables for the building of a kelvin application, thus resulting
    in reduced, cleaner and more testable code.

    Parameters
    ----------
    app_dir: str
        the path to the application's dir.
    app_config_raw: Optional[Dict]
        the raw app configuration dictionary.
    fresh_build: bool
        If specified will remove any cache and rebuild the application from scratch.
    build_for_upload: bool
        indicates whether or the package object aims for an upload.
    upload_datatypes: bool
        If specified, will upload locally defined datatypes.

    Returns
    -------
    BridgeAppBuildingObject
        a BridgeAppBuildingObject containing all the necessary variables for the building of a kelvin application.

    """
    kelvin_app_building_object = get_kelvin_app_building_object(base_build_object=base_build_object)
    return BridgeAppBuildingObject(**kelvin_app_building_object.dict())


def get_default_app_configuration(
    app_dir_path: Optional[KPath] = None, app_config_file_path: Optional[KPath] = None
) -> KelvinAppConfiguration:
    """
    Retrieve the application's configuration from either the provided app directory of app configuration.

    Parameters
    ----------
    app_dir_path : Optional[KPath]
        the path to the application's directory.
    app_config_file_path : Optional[KPath]
        the path to the application's configuration.
    Returns
    -------
    KelvinAppConfiguration
         a KelvinAppConfiguration object matching the app configuration of the app.

    """
    if app_config_file_path:
        return KelvinAppConfiguration(**app_config_file_path.read_yaml())

    app_config_file_path_aux = KPath(GeneralConfigs.default_app_config_file)

    if app_dir_path:
        app_config_file_path_aux = app_dir_path / app_config_file_path

    return KelvinAppConfiguration(**app_config_file_path_aux.read_yaml())


def get_default_app_name(app_dir_path: Optional[KPath] = None) -> str:
    """
    Retrieve the app name from the default configuration file (usually, app.yaml)

    Parameters
    ----------
    app_dir_path : Optional[KPath]
        the path to the application's directory.

    Returns
    -------
    str
        a string containing the default app name.

    """
    app_configuration = get_default_app_configuration(app_dir_path=app_dir_path)

    return app_configuration.info.app_name_with_version
