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

import re
from typing import Any, List, Optional, Union

from pydantic.v1 import Field, StrictInt, StrictStr

from kelvin.sdk.lib.models.apps.bridge_app import BridgeAppType
from kelvin.sdk.lib.models.apps.common import EnvironmentVar, NameDNS, Port, PortName, Version
from kelvin.sdk.lib.models.apps.docker_app import DockerAppType
from kelvin.sdk.lib.models.apps.kelvin_app import KelvinAppType
from kelvin.sdk.lib.models.generic import KSDKModel
from kelvin.sdk.lib.models.types import BaseEnum


class Encoding(BaseEnum):
    utf_8 = "utf-8"
    ascii = "ascii"
    latin_1 = "latin_1"


class Info(KSDKModel):
    name: NameDNS = Field(..., description="Application name.", title="Application name")
    version: Version = Field(..., description="Application version.", title="Application Version")
    title: str = Field(..., description="Application title.", title="Application title")
    description: str = Field(..., description="Application description.", title="Application description")

    @property
    def app_name_with_version(self) -> str:
        return f"{self.name}:{self.version}"


# Internal
class ProjectType(BaseEnum):
    app = "app"
    importer = "importer"
    exporter = "exporter"
    docker = "docker"

    kelvin = "kelvin"
    legacy_docker = "legacy_docker"
    bridge = "bridge"
    kelvin_legacy = "kelvin_legacy"

    @classmethod
    def app_types_as_str(cls) -> List[str]:
        """
        Applications supported by the schema in a string list for enumeration purposes

        Returns
        -------

        """
        return [
            cls.app.value,
            cls.importer.value,
            cls.exporter.value,
            cls.docker.value,
        ]

    def project_class_name(self) -> str:
        return "application"

    def app_type_on_config(self) -> str:
        return {
            ProjectType.app: "app",
            ProjectType.importer: "importer",
            ProjectType.exporter: "exporter",
            ProjectType.docker: "docker",
            ProjectType.kelvin: "kelvin",
        }[self]


class ApplicationFlavour(BaseEnum):
    default = "default"
    pubsub = "pubsub"
    mlflow = "mlflow"


class App(KSDKModel):
    type: ProjectType = Field(..., description="Application type.", title="Application Type")
    kelvin: Optional[KelvinAppType] = Field(None, description="Kelvin application.", title="Kelvin Application")
    bridge: Optional[BridgeAppType] = Field(
        None, description="Kelvin Bridge application.", title="Kelvin Bridge Application"
    )
    docker: Optional[DockerAppType] = None

    @property
    def app_type_configuration(self) -> Optional[Union[KelvinAppType, BridgeAppType]]:
        if self.type in [ProjectType.kelvin, ProjectType.kelvin_legacy]:
            return self.kelvin
        elif self.type == ProjectType.bridge:
            return self.bridge
        return None


class Memory(StrictStr):
    regex = re.compile(r"^[0-9]+(\.[0-9]+)?(K|M|G|Ki|Mi|Gi)$")


class CPU(StrictStr):
    regex = re.compile(r"^[0-9]+(\.[0-9]+)?(m|)$")


class SystemResources(KSDKModel):
    memory: Optional[Memory] = Field("256Mi", description="Memory requirements.", title="Memory Requirements")
    cpu: Optional[CPU] = Field(
        "0.4",
        description="CPU requirements defined as units. One CPU is equivalent of 1 vCPU/Core.",
        title="CPU Requirements",
    )


class Resources(KSDKModel):
    limits: Optional[SystemResources] = Field(
        None,
        description="Limits ensure that a container never goes above a certain value.",
        title="Container CPU and Memory limits",
    )
    requests: Optional[SystemResources] = Field(
        None,
        description="Requests are what the container is guaranteed to get.",
        title="Container CPU and Memory requests",
    )


class PortMappingType(BaseEnum):
    host = "host"
    service = "service"


class ExternalPort(StrictInt):
    gt = 30000
    le = 32767


class PortMappingService(KSDKModel):
    container_port: Optional[Port] = Field(None, description="Container Port", title="Container Port")
    port: Port = Field(..., description="Port", title="Port")
    exposed: Optional[bool] = Field(False, description="Exposed", title="Exposed")
    exposed_port: Optional[ExternalPort] = Field(None, description="Exposed port.", title="Exposed Port")


class PortMappingHostPort(KSDKModel):
    port: Port = Field(..., description="Port", title="Port")


class PortMapping(KSDKModel):
    name: PortName = Field(..., description="Port name.", title="Port Name")
    type: PortMappingType = Field(..., description="Port Type.", title="Port Type")
    host: Optional[PortMappingHostPort] = Field(None, description="Host Port.", title="Host Port")
    service: Optional[PortMappingService] = Field(None, description="Service Port.", title="Service Port")


class VolumeType(BaseEnum):
    text = "text"
    host = "host"
    persistent = "persistent"


class VolumeText(KSDKModel):
    data: str
    base64: Optional[bool] = False
    encoding: Optional[Encoding] = Field(Encoding.utf_8, description="File encoding.", title="File Encoding")


class VolumeHost(KSDKModel):
    source: str


class Volume(KSDKModel):
    name: Optional[NameDNS] = Field(None, description="Volume name.", title="Volume Name")
    target: str = Field(..., description="Volume target directory.", title="Volume Target")
    type: VolumeType = Field(..., description="Volume type.", title="Volume Type")
    text: Optional[VolumeText] = Field(None, description="Text volume.", title="Text Volume")
    host: Optional[VolumeHost] = Field(None, description="Host directory or file.", title="Host Volume")
    persistent: Optional[Any] = Field(None, description="Persistent volume.", title="Persistent Volume")


class System(KSDKModel):
    resources: Optional[Resources] = Field(
        None,
        description="The runtime prevents the container from using more than the configured resource limits.",
        title="Resource Requirements",
    )
    privileged: Optional[bool] = Field(
        False,
        description="Give extended privileges to this application. Allows the application to access any devices on the host (ex: Serial).",
        title="Privileged Flag",
    )
    environment_vars: Optional[List[EnvironmentVar]] = Field(
        None,
        description="Environment variables. Non-strings will be json-encoded as strings.",
        title="Environment Variables",
    )
    ports: Optional[List[PortMapping]] = Field(None, description="Network port mappings.", title="Port Mappings")
    volumes: Optional[List[Volume]] = Field(None, description="Volume definitions.", title="Volumes")


class Environment(KSDKModel):
    node_name: Optional[NameDNS] = Field(None, description="The name of the Node", title="Node Name")
    workload_name: Optional[NameDNS] = Field(
        None, description="The name of the Workload, unique to the Node", title="Workload Name"
    )

    @staticmethod
    def default_environment_configuration(node_name: str, app_name: str) -> dict:
        return Environment(node_name=node_name, workload_name=app_name).dict()  # type: ignore


class KelvinAppConfiguration(KSDKModel):
    spec_version: Version = Field(..., description="Specification version.", title="Specification Version")
    environment: Optional[Environment] = None
    info: Info
    system: Optional[System] = None
    app: App
