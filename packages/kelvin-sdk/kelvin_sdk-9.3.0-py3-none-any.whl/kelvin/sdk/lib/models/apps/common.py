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

import re
from functools import total_ordering
from typing import TYPE_CHECKING, Optional, Tuple

from packaging.version import Version as _Version
from pydantic.v1 import Extra, Field, StrictInt, StrictStr

from kelvin.sdk.lib.models.generic import KPath, KSDKModel
from kelvin.sdk.lib.models.types import BaseEnum
from kelvin.sdk.lib.utils.general_utils import get_requirements_from_file

if TYPE_CHECKING:
    from kelvin.sdk.lib.models.apps.ksdk_app_configuration import ApplicationFlavour


class LoggingLevel(BaseEnum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class Storage(BaseEnum):
    none = "none"
    node = "node"
    node_and_cloud = "node-and-cloud"


class Protocol(BaseEnum):
    OPCUA = "OPCUA"
    MQTT = "MQTT"
    ROC = "ROC"
    MODBUS = "MODBUS"


class Access(BaseEnum):
    RO = "RO"
    RW = "RW"


class Stage(BaseEnum):
    map = "map"


@total_ordering
class Version(StrictStr):
    regex = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?$")

    def __lt__(self, other: str) -> bool:
        """Less than comparison."""

        return _Version(self) < _Version(other)


class NonEmptyString(StrictStr):
    regex = re.compile(r"^.+$")


class NameDNS(StrictStr):
    regex = re.compile(r"^[a-z]([-a-z0-9]*[a-z0-9])?$")


class Identifier(StrictStr):
    regex = re.compile(r"^[a-zA-Z]\w*$")


class Port(StrictInt):
    gt = 0
    le = 65535


class PortName(StrictStr):
    regex = re.compile("^[a-z]([-a-z0-9]*[a-z0-9])?$")


class PythonEntryPoint(StrictStr):
    regex = re.compile(r"^[a-zA-Z]\w*(\.[a-zA-Z]\w*)*(:[a-zA-Z]\w*)?$")


class DottedIdentifier(StrictStr):
    regex = re.compile(r"^([a-z][a-z0-9_]+\.)+[a-z][a-z0-9_]+$")


class Name(StrictStr):
    regex = re.compile(r"^[a-z0-9]([-_.a-z0-9]*[a-z0-9])?$")


class Credentials(KSDKModel):
    username: str
    password: str


class Authentication(KSDKModel):
    type: str
    credentials: Credentials


class Mqtt(KSDKModel):
    ip: str = Field(..., description="MQTT Broker IP address.", title="IP")
    port: Port = Field(..., description="MQTT Broker Port.", title="Port")
    authentication: Optional[Authentication] = Field(
        None, description="MQTT Broker Authentication Settings.", title="Authentication"
    )

    @staticmethod
    def default_mqtt_configuration(ip_address: str) -> dict:
        return Mqtt(
            ip=ip_address,
            port=1883,  # type: ignore
            authentication=Authentication(
                type="credentials", credentials=Credentials(username="kelvin", password="kelvin")  # nosec
            ),
        ).dict()  # nosec


class DataType(KSDKModel):
    name: DottedIdentifier = Field(..., description="Data type name.", title="Data Type Name")
    version: Version = Field(..., description="Data type version.", title="Data Type Version")
    path: Optional[str] = Field(None, description="Data type path.", title="Data Type Path")

    @property
    def name_with_version(self) -> str:
        return f"{self.name}:{self.version}"


class EnvironmentVar(KSDKModel):
    name: Identifier = Field(..., description="Environment variable name.", title="Environment Variable Name")
    value: Optional[str] = Field(None, description="Environment variable value.", title="Environment Variable Value")


class Images(KSDKModel):
    runner: Optional[str] = Field(
        None, description="Docker image that runs the Python Application.", title="Runner Image"
    )
    builder: Optional[str] = Field(
        None, description="Docker image that is used to build the Python Application.", title="Builder Image"
    )


class ApplicationLanguage(BaseEnum):
    python = "python"  # default

    def get_extension(self) -> str:
        return {ApplicationLanguage.python: ".py"}[self]


class PythonLanguageType(KSDKModel):
    class Config:
        extra = Extra.allow

    entry_point: PythonEntryPoint
    requirements: Optional[str] = Field("requirements.txt", description="Package requirements", title="Requirements")
    flavour: Optional[str] = Field(None, description="Python application flavour", title="Application Flavour")

    @property
    def app_file_system_name(self) -> str:
        # extract file path from entrypoint point
        if self.entry_point:
            entrypoint_file = self.entry_point.split(":")[0]
            # get parent folder from entrypoint
            return KPath(entrypoint_file)

        return ""

    def get_flavour(self) -> Optional["ApplicationFlavour"]:
        if self.flavour is None:
            return None

        from kelvin.sdk.lib.models.apps.ksdk_app_configuration import ApplicationFlavour

        return ApplicationFlavour[self.flavour]

    def requirements_file_path(self, app_dir_path: KPath) -> Optional[KPath]:
        """
        When provided with an application dir, yield the complete requirements.txt absolute file path

        Parameters
        ----------
        app_dir_path : KPath
            the application's directory path

        Returns
        -------
        KPath
            the complete path to the requirements.txt file considering the application's directory.

        """
        if self.requirements:
            return (app_dir_path / self.requirements).expanduser().absolute()
        return None

    def requirements_available(self, app_dir_path: KPath) -> Tuple[bool, Optional[KPath]]:
        """
        Indicates whether requirements are available within the requirements.txt file

        Parameters
        ----------
        app_dir_path : KPath
            the application's directory path

        Returns
        -------
        Tuple[bool, Optional[KPath]]
            A tuple containing (left) a bool indicating there are requirements and (right) the path to the file

        """
        requirements_file_path = self.requirements_file_path(app_dir_path=app_dir_path)
        if requirements_file_path:
            return bool(get_requirements_from_file(file_path=requirements_file_path)), requirements_file_path
        return False, None


class Language(KSDKModel):
    type: ApplicationLanguage = Field(..., description="Language type.", title="Language Type")
    python: Optional[PythonLanguageType] = None
