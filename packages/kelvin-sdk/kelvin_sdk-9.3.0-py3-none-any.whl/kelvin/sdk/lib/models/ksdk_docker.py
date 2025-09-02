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

from datetime import datetime
from typing import List, Optional

from docker_image import reference
from docker_image.reference import InvalidReference
from pydantic.v1 import Field

from kelvin.sdk.lib.configs.general_configs import GeneralMessages
from kelvin.sdk.lib.models.generic import KPath, KSDKModel


class KSDKDockerVolume(KSDKModel):
    source_file_path: KPath  # e.g. /anything/regardless/of/operative_system/mosquitto.conf
    container_file_path: str  # e.g. /mosquitto/config/mosquitto.conf - linux
    content: str


class KSDKNetworkConfiguration(KSDKModel):
    network_name: str
    network_driver: str


class KSDKDockerAuthentication(KSDKModel):
    registry_url: str
    registry_port: str
    username: str
    password: str

    @property
    def full_registry_url(self) -> str:
        return f"{self.registry_url}:{self.registry_port}"

    @property
    def docker_client_credentials(self) -> dict:
        return {"username": self.username, "password": self.password}


class DockerPort(KSDKModel):
    port_type: str = Field(None, alias="Type")
    private_port: str = Field(None, alias="PrivatePort")
    public_port: str = Field(None, alias="PublicPort")

    @property
    def port_mapping(self) -> str:
        return f"{self.port_type}:{self.private_port}->{self.public_port}"

    def __repr__(self) -> str:
        return self.port_mapping


class DockerMount(KSDKModel):
    mount_type: str = Field(None, alias="Type")
    source: str = Field(None, alias="Source")
    destination: str = Field(None, alias="Destination")
    mode: str = Field(None, alias="Mode")
    rw: str = Field(None, alias="RW")
    bind_propagation: str = Field(None, alias="Propagation")

    @property
    def pretty_display_format(self) -> str:
        from kelvin.sdk.lib.utils.display_utils import pretty_colored_content

        return pretty_colored_content(content=self.dict())


class DockerContainer(KSDKModel):
    # 1 - internal fields
    id: str
    container_names: Optional[List[str]] = []
    image_name: str
    running: bool = False
    status: str = "N/A"
    labels: Optional[dict] = {}
    ip_address: Optional[str] = None
    mounts: Optional[List[DockerMount]] = []
    ports: List[DockerPort] = []

    @property
    def container_status_for_display(self) -> str:
        is_running: str = "Running" if self.running else "Not Running"
        return f"{is_running} - {self.status}"

    @property
    def container_ports_for_display(self) -> str:
        result = ""
        if self.ports:
            result = "\n".join(list(set([item.port_mapping for item in self.ports])))
        return result

    @property
    def container_mounts_for_display(self) -> str:
        result = ""
        if self.mounts:
            result = "\n".join([item.pretty_display_format for item in self.mounts])
        return result

    @staticmethod
    def get_docker_container_object(raw_container_object: dict) -> "DockerContainer":
        """
        From a raw container object provided by the Docker API, yield a valid DockerContainer Object for better
        data handling.

        Parameters
        ----------
        raw_container_object : dict
            a raw container data object provided by the Docker Client API

        Returns
        -------
        DockerContainer
            the final object that contains all the its simplified variables

        """
        _container_id = raw_container_object.get("Id", "")
        _container_names: List[str] = [name.replace("/", "") for name in raw_container_object.get("Names", []) or []]
        _container_image = raw_container_object.get("Image", "")
        _container_is_running = raw_container_object.get("State", "") == "running"
        _container_status = raw_container_object.get("Status", "")
        _container_labels: dict = raw_container_object.get("Labels", {}) or {}
        _container_ports: List = raw_container_object.get("Ports", [])
        _container_mounts: List = raw_container_object.get("Mounts", [])

        _container_network_settings: dict = raw_container_object.get("NetworkSettings", {})
        _container_networks: dict = _container_network_settings.get("Networks", {})
        from kelvin.sdk.lib.configs.docker_configs import DockerConfigs

        _container_network_ksdk: dict = _container_networks.get(DockerConfigs.default_ksdk_network, {})
        _container_network_ip: str = _container_network_ksdk.get("IPAddress", "")

        return DockerContainer(
            id=_container_id,
            container_names=[name.replace("/", "") for name in _container_names],
            image_name=_container_image,
            running=_container_is_running,
            status=_container_status,
            labels=_container_labels,
            ip_address=_container_network_ip,
            ports=_container_ports,
            mounts=_container_mounts,
        )


class DockerImage(KSDKModel):
    id: str
    parent_id: str
    tags: List[str]
    created: int
    labels: Optional[dict]
    size: Optional[int]

    @property
    def readable_created_date(self) -> str:
        value = datetime.fromtimestamp(self.created)
        return f"{value:%Y-%m-%d %H:%M:%S}"

    @staticmethod
    def get_docker_image_object(raw_image_object: dict) -> "DockerImage":
        """
        From a raw image object provided by the Docker API, yield a valid DockerImage Object for better
        data handling.

        Parameters
        ----------
        raw_image_object : dict
            a raw image data object provided by the Docker Client API

        Returns
        -------
        DockerImage
            the final object that contains all the its simplified variables

        """
        _image_id = raw_image_object.get("Id", "")
        _image_parent_id = raw_image_object.get("ParentId", "")
        _image_tags = raw_image_object.get("RepoTags", []) or []
        _image_created = raw_image_object.get("Created", "")
        _image_labels: dict = raw_image_object.get("Labels", {}) or {}
        _image_size: int = raw_image_object.get("Size", 0) or 0

        return DockerImage(
            id=_image_id,
            parent_id=_image_parent_id,
            tags=_image_tags,
            created=_image_created,
            labels=_image_labels,
            size=_image_size,
        )


class DockerImageName(KSDKModel):
    """Docker image name parser
    >>> image = DockerImageName.parse('alpha.kelvininc.com:5000/someapp:1.0.0@sha256:14bf...')
    >>> image
    DockerImageName(hostname='alpha.kelvininc.com:5000', name='someapp', tag='1.0.0', digest='sha256:14bf...')

    """

    hostname: Optional[str] = None
    name: str
    raw_name: str
    version: Optional[str] = None
    digest: Optional[str] = None

    @classmethod
    def parse(cls, name: str) -> "DockerImageName":
        try:
            ref = reference.Reference.parse(name)
            tag = ref.get("tag")
            digest = ref.get("digest")
            hostname, app_name = ref.split_hostname()
            app_name = app_name.split("/")[-1] if "/" in app_name else app_name

            return cls(hostname=hostname, name=app_name, version=tag, digest=digest, raw_name=name)
        except InvalidReference as exc:
            raise ValueError(GeneralMessages.invalid_name.format(reason=exc))

    @property
    def name_with_version(self) -> str:
        return ":".join([self.name, self.version or "latest"])

    @property
    def repository_image_name(self) -> str:
        return "/".join(filter(None, [self.hostname, self.name_with_version]))

    @property
    def repository_image_name_without_version(self) -> str:
        return "/".join(filter(None, [self.hostname, self.name]))

    @property
    def container_name(self) -> str:
        return f"{self.name}.app"


class DockerNetwork(KSDKModel):
    name: str = Field(None, alias="Name")
    id: str = Field(None, alias="Id")
    driver: str = Field(None, alias="Driver")
    created: str = Field(None, alias="Created")


class DockerProgressEntry(KSDKModel):
    id: Optional[str]
    status: Optional[str]
    progress: Optional[str]
