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

from typing import Any, Optional, Tuple

from filelock import FileLock, Timeout
from pydantic.v1 import Field, validator

from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.models.apps.common import ApplicationLanguage
from kelvin.sdk.lib.models.generic import KPath, KSDKModel, KSDKSettings

LOCK_TIMEOUT = 1.0


# 1 - Metadata oriented classes
class GenericMetadataEntry(KSDKModel):
    url: Optional[str] = None
    path: Optional[str] = None
    realm: Optional[str] = None
    port: Optional[str] = None
    client_id: Optional[str] = None


class DockerMetadataEntry(GenericMetadataEntry):
    @property
    def full_docker_registry_url(self) -> str:
        return f"{self.url}:{self.port}"


class SchemaMetadataEntry(GenericMetadataEntry):
    minimum_spec_version: str
    latest_spec_version: str


class ComponentsMetadataEntry(GenericMetadataEntry):
    kelvin_broker: str = Field(None, alias="kelvin-mqtt-broker")
    kelvin_studio: str = Field(None, alias="kelvin-studio")
    kelvin_python_app_builder: str = Field(None, alias="kelvin-python-app-builder")
    kelvin_python_app_runner: str = Field(None, alias="kelvin-python-app-runner")
    kelvin_python_app_runner_slim: str = Field(None, alias="kelvin-python-app-runner-slim")
    kelvin_control_change_manager: str = Field(None, alias="kelvin-control-change-manager")

    def get_runner_docker_image_for_lang(
        self, reduced_size: bool = True, app_lang: Optional[ApplicationLanguage] = None
    ) -> str:
        return self.kelvin_python_app_runner_slim if reduced_size else self.kelvin_python_app_runner

    def get_builder_docker_image_for_lang(self, app_lang: Optional[ApplicationLanguage] = None) -> str:
        return self.kelvin_python_app_builder

    class Config:
        allow_population_by_field_name = True


class SDKMetadataEntry(GenericMetadataEntry):
    docker_minimum_version: Optional[str]
    ksdk_minimum_version: str
    ksdk_latest_version: str
    components: ComponentsMetadataEntry


class CompanyMetadata(KSDKModel):
    authentication: GenericMetadataEntry
    docker: DockerMetadataEntry
    documentation: GenericMetadataEntry
    sdk: SDKMetadataEntry
    kelvin_schema: SchemaMetadataEntry = Field(None, alias="schema")

    def get_min_and_latest_schema_versions(self) -> Tuple[str, str]:
        """
        Return the latest schema version from the metadata.

        Returns
        -------
        Tuple[str, str]
            the tuple including both minimum and latest versions allowed from the schema.

        """
        return self.kelvin_schema.minimum_spec_version, self.kelvin_schema.latest_spec_version


# 2 - Top level configuration classes
class KelvinSDKEnvironmentVariables(KSDKSettings):
    ksdk_version_warning: bool = True
    ksdk_colored_logs: bool = True
    ksdk_debug: bool = False

    class Config:
        extra = "allow"
        fields = {
            "ksdk_version_warning": {
                "env": "KSDK_VERSION_WARNING",
                "description": "If outdated, KSDK will warn the user. If the minimum version is not respected, "
                "it will block any operation until upgrade.",
            },
            "ksdk_colored_logs": {
                "env": "KSDK_COLORED_LOGS",
                "description": "If disabled, all logs will be output in the default OS color, ready to be captured.",
            },
            "ksdk_debug": {
                "env": "KSDK_DEBUG",
                "description": "If enabled, display debug information for errors.",
            },
        }

    @validator(
        "ksdk_version_warning",
        "ksdk_colored_logs",
        "ksdk_debug",
        pre=True,
    )
    def invalid_value(cls, value: Any) -> Any:  # noqa
        if value is None or value in ["True", "False", "1", "0", True, False, 1, 0]:
            return value
        return False

    @property
    def descriptions(self) -> dict:
        fields = KelvinSDKEnvironmentVariables.Config.fields
        fields_keys = list(fields.keys())
        set_items = {key: value for key, value in self.dict().items() if key in fields_keys}
        for k, v in set_items.items():
            fields[k]["current_value"] = v
        return fields

    @property
    def private_fields(self) -> list:
        return ["ksdk_debug"]


class KelvinSDKConfiguration(KSDKSettings):
    last_metadata_refresh: float
    current_url: str
    current_user: str
    ksdk_current_version: str
    ksdk_minimum_version: str
    ksdk_latest_version: str
    configurations: KelvinSDKEnvironmentVariables = KelvinSDKEnvironmentVariables()

    @validator(
        "configurations",
        pre=True,
    )
    def validate_configurations(cls, v: Any) -> KelvinSDKEnvironmentVariables:  # noqa
        return v if v is not None else KelvinSDKEnvironmentVariables()

    @property
    def versions(self) -> dict:
        return {
            "current_version": self.ksdk_current_version,
            "minimum_version": self.ksdk_minimum_version,
            "latest_version": self.ksdk_latest_version,
        }

    def reset(self) -> Any:
        self.current_url = ""
        self.current_user = ""
        return self

    @classmethod
    def from_file(cls, ksdk_config_file_path: KPath) -> Any:
        from kelvin.sdk.cli.version import version

        if ksdk_config_file_path:
            try:
                with FileLock(f"{ksdk_config_file_path}.lock", timeout=LOCK_TIMEOUT):
                    ksdk_config_dict = ksdk_config_file_path.read_yaml(verbose=False)
            except Timeout:
                raise ValueError(f"Configuration file {str(ksdk_config_file_path)!r} is locked")
        else:
            ksdk_config_dict = {}

        ksdk_config_dict.update({"ksdk_current_version": version})

        return cls(**ksdk_config_dict)

    @classmethod
    def from_default_config(cls) -> KelvinSDKConfiguration:
        from kelvin.sdk.cli.version import version

        return cls(
            last_metadata_refresh=0,
            current_url="",
            current_user="",
            ksdk_current_version=version,
            ksdk_minimum_version=version,
            ksdk_latest_version=version,
        )


class KelvinSDKGlobalConfiguration(KSDKSettings):
    ksdk_config_dir_path: KPath = KPath(GeneralConfigs.default_ksdk_configuration_dir).complete_path()
    kelvin_sdk: KelvinSDKConfiguration = KelvinSDKConfiguration.from_default_config()

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.ksdk_config_dir_path = KPath(self.ksdk_config_dir_path).complete_path().create_dir()
        if self.ksdk_config_file_path.exists():
            try:
                self.kelvin_sdk = KelvinSDKConfiguration.from_file(self.ksdk_config_file_path)
            except Exception:  # noqa: any exception, regardless of its type
                self.ksdk_config_file_path.remove()

    @property
    def ksdk_temp_dir_path(self) -> KPath:
        """
        Return the path to the KSDK's temporary directory.
        Usually hosted under `~/.config/kelvin/temp/`

        Returns
        -------
        KPath
            The KPath object to the temporary directory.
        """
        ksdk_temp_dir: str = GeneralConfigs.default_ksdk_temp_dir
        return KPath(self.ksdk_config_dir_path / ksdk_temp_dir).complete_path()

    @property
    def ksdk_schema_dir_path(self) -> KPath:
        """
        Return the path to the app schema hosting directory.
        Usually hosted under `~/.config/kelvin/schemas/`

        Returns
        -------
        KPath
            The KPath object to the app schema directory.
        """
        ksdk_schema_storage_dir: str = GeneralConfigs.default_ksdk_schema_storage_dir
        return KPath(self.ksdk_config_dir_path / ksdk_schema_storage_dir).complete_path()

    @property
    def ksdk_config_file_path(self) -> KPath:
        """
        Return the complete path to the ksdk config file.
        Usually hosted under `~/.config/kelvin/ksdk.yaml`

        Returns
        -------
        KPath
            The KPath object to the ksdk configuration file.
        """
        ksdk_file: str = GeneralConfigs.default_ksdk_configuration_file
        return KPath(self.ksdk_config_dir_path / ksdk_file).complete_path()

    @property
    def ksdk_client_config_file_path(self) -> KPath:
        """
        Return the complete path to the ksdk client config file.
        Usually hosted under `~/.config/kelvin/client.yaml`

        Returns
        -------
        KPath
            The KPath object to the ksdk client configuration file.
        """
        kelvin_client_file: str = GeneralConfigs.default_kelvin_sdk_client_configuration_file
        return KPath(self.ksdk_config_dir_path / kelvin_client_file).complete_path()

    @property
    def ksdk_history_file_path(self) -> KPath:
        """
        Return the complete path to the ksdk history log file.
        Usually hosted under `~/.config/kelvin/ksdk_history.log`

        Returns
        -------
        KPath
            The KPath object to the ksdk history log file.
        """
        history_file: str = GeneralConfigs.default_ksdk_history_file
        return KPath(self.ksdk_config_dir_path / history_file).complete_path()

    def commit_ksdk_configuration(self) -> KelvinSDKGlobalConfiguration:
        try:
            with FileLock(f"{self.ksdk_config_file_path}.lock", timeout=LOCK_TIMEOUT):
                self.kelvin_sdk.to_file(path=self.ksdk_config_file_path)
        except Timeout:
            raise ValueError(f"Configuration file {str(self.ksdk_config_file_path)!r} is locked")
        return self

    def reset_ksdk_configuration(self) -> Any:
        self.kelvin_sdk.reset()
        return self

    def set_configuration(self, configuration: str, value: Any) -> bool:
        if configuration:
            configuration = configuration.lower()
            if not self.kelvin_sdk.configurations:
                self.kelvin_sdk.configurations = KelvinSDKEnvironmentVariables()
            if self.kelvin_sdk.configurations and configuration in self.kelvin_sdk.configurations.dict().keys():
                setattr(self.kelvin_sdk.configurations, configuration, value)
                self.commit_ksdk_configuration()
                return True
            raise ValueError("The configuration you provided is invalid")
        else:
            raise ValueError(f'Provided configuration "{configuration}" does not exist')

    def unset_configuration(self, configuration: str) -> bool:
        if configuration:
            configuration = configuration.lower()
            if not self.kelvin_sdk.configurations:
                self.kelvin_sdk.configurations = KelvinSDKEnvironmentVariables()
            if self.kelvin_sdk.configurations and configuration in self.kelvin_sdk.configurations.dict().keys():
                self.kelvin_sdk.configurations.__setattr__(configuration, None)
                self.commit_ksdk_configuration()
                return True
            raise ValueError("The configuration you provided is invalid")
        else:
            raise ValueError(f'Provided configuration "{configuration}" does not exist')
