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

from __future__ import annotations

from stat import S_IEXEC
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from jinja2 import Template
from pydantic.v1 import validator

from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.exceptions import AppNameIsInvalid
from kelvin.sdk.lib.models.apps.common import ApplicationLanguage, EnvironmentVar
from kelvin.sdk.lib.models.apps.ksdk_app_configuration import (
    ApplicationFlavour,
    KelvinAppConfiguration,
    PortMapping,
    PortMappingType,
    ProjectType,
    Resources,
    Volume,
)
from kelvin.sdk.lib.models.generic import KPath, KSDKModel
from kelvin.sdk.lib.models.ksdk_docker import KSDKDockerVolume
from kelvin.sdk.lib.models.types import EmbeddedFiles
from kelvin.sdk.lib.utils.general_utils import standardize_string
from kelvin.sdk.lib.utils.logger_utils import logger


class TemplateFile(KSDKModel):
    name: str
    content: Template
    options: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


class File(KSDKModel):
    file: KPath
    content: str
    executable: bool = False

    def create(self) -> bool:
        self.file.write_content(self.content)
        if self.executable:
            self.file.chmod(self.file.stat().st_mode | S_IEXEC)
        return True

    @validator("content")
    def content_exists(cls, v: str) -> Any:  # noqa
        return v if v is not None else ""


class Directory(KSDKModel):
    directory: KPath
    files: List[File] = []

    def create(self) -> bool:
        self.directory.create_dir()
        return True

    def exists(self) -> bool:
        return self.directory.exists()

    def path(self) -> str:
        return str(self.directory.resolve())


# CREATION PARAMETERS
class ProjectCreationParametersObject(KSDKModel):
    app_dir: str
    app_name: str
    app_version: str
    app_description: str
    app_type: ProjectType
    app_flavour: ApplicationFlavour = ApplicationFlavour.default
    kelvin_app_lang: ApplicationLanguage = ApplicationLanguage.python

    @validator("app_name", pre=True)
    def single_app_name(cls, value: Any) -> str:  # noqa
        if value:
            if isinstance(value, str):
                return value
            elif isinstance(value, tuple):
                return value[0]
        raise AppNameIsInvalid()

    def get_entrypoint(self) -> str:
        standard_app_name = standardize_string(self.app_name)

        if self.app_flavour is ApplicationFlavour.pubsub:
            return f"{standard_app_name}.main:main"
        else:
            if self.app_type is ProjectType.kelvin:
                return "kelvin_python_sdk"
            return "No entrypoint"

    def get_language_block(self, requirements: Optional[str] = None) -> dict:
        from kelvin.sdk.lib.configs.general_configs import GeneralConfigs

        if self.kelvin_app_lang == ApplicationLanguage.python:
            app_lang = {"entry_point": self.get_entrypoint()}
            if self.app_type is not ProjectType.kelvin:
                app_lang.update({"requirements": requirements or GeneralConfigs.default_requirements_file})

            if self.app_flavour is not ApplicationFlavour.default:
                app_lang.update({"flavour": self.app_flavour.value})

            return {self.kelvin_app_lang.value_as_str: app_lang}
        return {}


class Inout(KSDKModel):
    name: str
    type: str


class MLFlowProjectCreationParametersObject(ProjectCreationParametersObject):
    inputs: List[Inout]
    outputs: List[Inout]


# BUILDING (PACKAGING)
class ProjectBuildingObject(KSDKModel):
    fresh_build: bool = False
    build_for_upload: bool = False
    app_name: str
    app_version: str
    app_type: str
    app_config_file_path: KPath
    app_config_raw: Dict = {}
    app_config_model: Optional[KelvinAppConfiguration] = None
    app_dir_path: KPath
    app_build_dir_path: KPath
    docker_image_labels: dict
    docker_image_name: str
    docker_registry: str = ""
    # external arguments - pypi credentials
    build_args: Optional[Dict[str, str]] = None
    archs: List[str] = []

    @property
    def full_docker_image_name(self) -> str:
        return f"{self.app_name}:{self.app_version}"


class KelvinAppBuildingObject(ProjectBuildingObject):
    dockerfile_path: KPath
    docker_build_context_path: KPath
    # base docker image configurations
    kelvin_app_builder_image: str
    kelvin_app_runner_image: str
    reduced_size_kelvin_app_runner_image: bool
    # docker image names and labels
    docker_image_version: str
    # app directories
    app_datatype_dir_path: Optional[KPath] = None
    # utility flags
    build_for_datatype_compilation: bool = False
    upload_datatypes: bool = False

    def get_wheels_dir(self) -> Optional[str]:
        wheels = (self.app_dir_path / GeneralConfigs.default_wheels_dir).glob("*.whl")
        return GeneralConfigs.default_wheels_dir if any(wheels) else None

    def get_dockerfile_template(self) -> EmbeddedFiles:
        """
        From the current application build object, yield the correct dockerfile template.

        Returns
        -------
        EmbeddedFiles
            the correct dockerfile template name.
        """
        template: EmbeddedFiles = EmbeddedFiles.KELVIN_PYTHON_APP_DOCKERFILE
        try:
            project_type = self.app_type
            if project_type == ProjectType.kelvin:
                template = EmbeddedFiles.KELVIN_PYTHON_APP_DOCKERFILE
            elif project_type == ProjectType.bridge:
                template = EmbeddedFiles.BRIDGE_PYTHON_APP_DOCKERFILE
        except Exception as exc:
            logger.debug(f"Error retrieving configuration dockerfile: {exc}")
            template = EmbeddedFiles.KELVIN_PYTHON_APP_DOCKERFILE
        return template

    def get_dockerfile_run_command(self) -> Tuple[Optional[str], Optional[str]]:
        app = self.app_config_model.app  # type: ignore
        if app.kelvin and app.kelvin.language:
            if app.kelvin.language.python:
                python_entry_point = app.kelvin.language.python.entry_point
                default_docker_cmd = f'["--configuration", "/opt/kelvin/app/{self.app_config_file_path.name}"]'
                if app.type == ProjectType.kelvin:
                    app_flavour = app.kelvin.language.python.get_flavour()
                    if app_flavour is ApplicationFlavour.pubsub:
                        module_name = standardize_string(self.app_config_model.info.name)  # type: ignore
                        return '["python3"]', f'["-m", "{module_name}"]'
                    else:
                        docker_entrypoint = f'["kelvin-app", "run", "app", "{python_entry_point}"]'
                        return docker_entrypoint, default_docker_cmd
        return None, None


class BridgeAppBuildingObject(KelvinAppBuildingObject):
    def get_dockerfile_run_command(self) -> Tuple[Optional[str], Optional[str]]:
        default_docker_cmd = f'["--configuration", "/opt/kelvin/app/{self.app_config_file_path.name}"]'
        docker_entrypoint = '["kelvin-app", "run", "bridge"]'
        return docker_entrypoint, default_docker_cmd


class DockerAppBuildingObject(ProjectBuildingObject):
    # ProjectBuildingObject already possesses everything we currently require
    pass


# EMULATION
class ProjectEmulationObject(KSDKModel):
    # Kelvin specific
    app_name: Optional[str] = None
    app_config_path: Optional[str] = None
    app_config_model: Optional[KelvinAppConfiguration] = None
    net_alias: Optional[str] = None
    attach: bool = False
    show_logs: bool = False
    is_external_app: bool = False
    # Docker specific
    detach: bool = False  # Detached mode: run container in the background and return container ID
    auto_remove: bool = False  # enable auto-removal of the container on daemon side when the container's process exits
    publish_all_ports: bool = True  # Publish all ports to the host.
    privileged: bool = False  # Give extended privileges to this container.
    entrypoint: Optional[str] = None
    ports: Optional[List[Union[int, Tuple[int, str]]]] = None
    port_mapping: Optional[Dict] = None
    volumes: Optional[List[str]] = None
    file_volumes: Optional[List[KSDKDockerVolume]] = None
    arguments: Optional[Sequence[str]] = None
    environment_variables: Optional[Dict] = None
    memory: Optional[str] = None
    cpu: Optional[str] = None
    # docker container logs specific
    stream: bool = True  # when logs from
    follow: bool = True
    should_print: bool = True
    tail: Optional[int] = None

    @property
    def emulation_app_name(self) -> str:
        from kelvin.sdk.lib.models.factories.app_setup_configuration_objects_factory import get_default_app_name

        return self.app_name or get_default_app_name()

    @classmethod
    def from_app_model(
        cls,
        app_config_model: Optional[KelvinAppConfiguration] = None,
        app_config_file_path: Optional[Union[str, KPath]] = None,
    ) -> ProjectEmulationObject:
        """
        From either an app configuration model or file path, generate the corresponding ProjectEmulationObject.

        Parameters
        ----------
        app_config_model : an application configuration model to retrieve configurations from.
        app_config_file_path : the alternative path to the application configuration file path.

        Returns
        -------
        A new instance of an ProjectEmulationObject with the necessary variables ready for a complete emulation.

        """
        # 1 - define return object
        emulation_object = ProjectEmulationObject()
        try:
            emulation_object.app_config_path = app_config_file_path
            emulation_object.app_config_model = app_config_model
            # 2 - if not app config model is provided, load it frm the provided app config file path (if existent)
            app_config_file_path = KPath(app_config_file_path)
            if not emulation_object.app_config_model and app_config_file_path and app_config_file_path.exists():
                raw_configuration = app_config_file_path.read_yaml()
                # 2.1 - Attempt to validate it
                from kelvin.sdk.lib.schema.schema_manager import validate_app_schema_from_app_config_file

                validate_app_schema_from_app_config_file(app_config=raw_configuration)
                # 2.2 - Load it
                emulation_object.app_config_model = KelvinAppConfiguration(**raw_configuration)

            # 3 - Retrieve the system configurations
            if emulation_object.app_config_model:
                emulation_object.app_name = emulation_object.app_config_model.info.app_name_with_version
                system_config = emulation_object.app_config_model.system
                if system_config:
                    emulation_object.privileged = bool(system_config.privileged)
                    # 3.1 Parse environment variables
                    env_vars = cls.process_environment_variables(environment_variables=system_config.environment_vars)
                    emulation_object.environment_variables = env_vars
                    # 3.2 Parse ports
                    port_listing, port_map_listing = cls.process_ports(ports=system_config.ports)
                    emulation_object.ports = port_listing
                    emulation_object.port_mapping = port_map_listing
                    # 3.3 Parse volumes
                    volumes, file_volumes = cls.process_volumes(volumes=system_config.volumes)
                    emulation_object.volumes = volumes
                    emulation_object.file_volumes = file_volumes
                    # 3.4 Parse resources
                    memory, cpu = cls.process_resources(resources=system_config.resources)
                    emulation_object.memory = memory
                    emulation_object.cpu = cpu
        except Exception as exc:
            error_message: str = f"Error generation Emulation Object: {exc}"
            logger.error(error_message)
        return emulation_object

    @staticmethod
    def process_environment_variables(environment_variables: Optional[List[EnvironmentVar]]) -> dict:
        """

        From the provided environment variables list, yield a docker-readable dictionary.

        Parameters
        ----------
        environment_variables : The Kelvin EnvironmentVar list.

        Returns
        -------
        A docker-readable compliant dict.
        """
        return {entry.name: entry.value for entry in environment_variables} if environment_variables else {}

    @staticmethod
    def process_ports(ports: Optional[List[PortMapping]]) -> Tuple[List, Dict]:
        """

        From the provided Port configuration list, yield a docker compliant configuration

        Parameters
        ----------
        ports : The Kelvin PortMapping list.

        Returns
        -------
        A tuple with both the list of ports to be open in the container and a port mapping dictionary.
        """
        port_listing = []
        port_map_listing = {}
        if ports:
            for port in ports:
                if port.type == PortMappingType.host and port.host:
                    port_listing.append(port.host.port)
                    port_map_listing[port.host.port] = port.host.port
                if port.type == PortMappingType.service and port.service:
                    container_port = port.service.container_port or port.service.port
                    port_listing.append(container_port)
                    port_map_listing[container_port] = port.service.port
        return port_listing, port_map_listing

    @staticmethod
    def process_volumes(volumes: Optional[List[Volume]]) -> Tuple[List[str], List[KSDKDockerVolume]]:
        """
        From the provided Volume configuration list, yield a docker compliant configuration

        Parameters
        ----------
        volumes : The Kelvin Volume list.

        Returns
        -------
        The pair of volume and volume files to be passed on to docker.

        """
        volumes_listing = []
        volume_files_listing = []
        if volumes:
            for volume in volumes:
                if volume.type.host and volume.host:
                    volume_host_path = KPath(volume.host.source).absolute()
                    volumes_listing.append(f"{str(volume_host_path)}:{volume.target}:Z")
                if volume.type.text and volume.text:
                    encoding = volume.text.encoding.value_as_str if volume.text.encoding else ""
                    data = volume.text.data
                    data_bytes = data.encode(encoding)
                    if volume.text.base64:
                        import base64

                        data_bytes = base64.b64decode(data)
                    data = data_bytes.decode(encoding)
                    docker_volume = KSDKDockerVolume(
                        source_file_path=KPath(volume.target), container_file_path=volume.target, content=data
                    )
                    volume_files_listing.append(docker_volume)
        return volumes_listing, volume_files_listing

    @staticmethod
    def process_resources(resources: Optional[Resources]) -> Tuple[Optional[str], Optional[str]]:
        """
        From the provided Resources, yield a docker compliant configuration

        Parameters
        ----------
        resources : The Resources.

        Returns
        -------
        The pair of, respectively, memory and cpu resources.

        """
        if resources is None:
            return None, None
        system_resources = resources.requests or resources.limits
        if system_resources is None:
            return None, None
        return system_resources.memory, system_resources.cpu
