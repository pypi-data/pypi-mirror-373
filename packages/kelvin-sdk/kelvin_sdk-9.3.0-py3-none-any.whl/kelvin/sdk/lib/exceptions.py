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

from typing import Optional

from pydantic.v1 import ValidationError


class KSDKException(Exception):
    """
    Base KSDK Exception
    """

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


class AppException(KSDKException):
    """
    Raised when the a generic process fails.

    """


class AppNameIsInvalid(KSDKException):
    """
    Raised when the provided application name is not valid (either a tuple or a different type)
    """

    def __str__(self) -> str:
        return self.message or "The provided application name is not valid."


class KDockerException(KSDKException):
    """
    Raised when there is an issue with Docker.

    """

    def __str__(self) -> str:
        return "Error executing the required docker command." if not self.message else self.message


class DependencyNotRunning(KSDKException):
    """
    Raised when a dependency is not running.

    """

    def __str__(self) -> str:
        return "{dependency} is NOT running. Please start it in order to proceed.".format(dependency=self.message)


class DependencyNotInstalled(KSDKException):
    """
    Raised when a dependency is not installed.

    """

    def __str__(self) -> str:
        return "{dependency} NOT installed. Please install it in order to proceed.".format(dependency=self.message)


class DataTypeException(KSDKException):
    """
    Raised when a process related to Datatype fails.

    """


class DataTypeNameIsInvalid(KSDKException):
    """
    Raised when the provided datatype name is not valid (either a tuple or a different type)
    """

    def __str__(self) -> str:
        return self.message or "The provided datatype name is not valid."


class EmulationException(KSDKException):
    """
    Raised when an Emulation process fails.

    """


class InvalidBaseImageException(KSDKException):
    """
    Raised when the provided docker image is not valid/supported by the current system.

    """

    def __init__(self, registry_url: str, docker_image_name: str):
        self.registry_url = registry_url
        self.docker_image_name = docker_image_name

    def __str__(self) -> str:
        return f"""\n
                    The provided base image is not valid: \"{self.docker_image_name}\". \n
                    Please use an image that is available on the current platform: \"{self.registry_url}\"."""


class InvalidApplicationConfiguration(KSDKException):
    """
    Raised when the provided application configuration is not valid.

    """

    def __str__(self) -> str:
        if self.message:
            return "The provided application configuration is not valid: {message}".format(message=self.message)
        return "Invalid application configuration."


class MandatoryConfigurationsException(KSDKException):
    """
    Raised when a mandatory configuration is missing from the metadata.

    """

    def __init__(self, validation_error: Optional[ValidationError], message: Optional[str] = None):
        self.validation_error = validation_error
        self.message = message if message else ""

    def __str__(self) -> str:
        missing_configs = ""
        if self.message:
            missing_configs = self.message
        elif self.validation_error:
            for error in self.validation_error.errors():
                loc = error.get("loc", "")
                msg = error.get("msg", "")
                missing_configs += "{msg} -> {loc} \n\t".format(loc=loc, msg=msg)
        return """

        Mandatory configurations are missing on the platform you're trying to connect to.
        Please contact Kelvin's support team.
        Stack:

        {reason}

        """.format(
            reason=missing_configs
        )


class InvalidSchemaVersionException(KSDKException):
    """
    Raised when the schema version does not match the pre-established values.

    """

    def __init__(self, min_version: str, current_version: str, latest_version: str):
        self.min_version = min_version
        self.current_version = current_version
        self.latest_version = latest_version

    def __str__(self) -> str:
        return f"""

        The configuration's schema version does not comply with the permitted values:

        > Provided spec version: {self.current_version}

        Minimum spec version >= {self.min_version}
        Latest spec version <= {self.latest_version}
        """  # noqa: E221


class MissingTTYException(KSDKException):
    """
    Raised when tty interaction is not available
    """

    def __str__(self) -> str:
        return "Interactive command is not available. (tty exception)"
