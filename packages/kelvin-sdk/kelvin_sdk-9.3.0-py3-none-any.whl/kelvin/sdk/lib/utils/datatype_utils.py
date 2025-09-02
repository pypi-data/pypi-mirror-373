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

from pydantic.v1 import ValidationError
from pydantic.v1.tools import parse_obj_as

from kelvin.sdk.lib.configs.general_configs import GeneralMessages
from kelvin.sdk.lib.exceptions import DataTypeException, DataTypeNameIsInvalid
from kelvin.sdk.lib.models.apps.common import DottedIdentifier
from kelvin.sdk.lib.models.datatypes import DottedIdentifierWithOptionalVersion, DottedIdentifierWithVersion
from kelvin.sdk.lib.models.ksdk_docker import DockerImageName
from kelvin.sdk.lib.utils.general_utils import parse_pydantic_errors


def check_if_datatype_name_is_valid(datatype_name: str) -> bool:
    """Verify whether the provided datatype name is valid (or contains a forbidden word combination).

    Raise an exception if the provided datatype name contains a forbidden keyword.

    Parameters
    ----------
    datatype_name : str
        the datatype name to be verified.

    Returns
    -------
    bool:
        a boolean indicating whether the app name is valid.

    """
    try:
        parse_obj_as(DottedIdentifier, datatype_name)
    except ValidationError as exc:
        error_message = parse_pydantic_errors(validation_error=exc)
        raise DataTypeException(GeneralMessages.invalid_name.format(reason=error_message))
    except DataTypeNameIsInvalid as exc:
        raise DataTypeException(GeneralMessages.invalid_name.format(reason=str(exc)))

    return True


def check_if_datatype_name_with_version_is_valid(app_name_with_version: str, version_required: bool = False) -> bool:
    """Verify whether the provided app name is valid (or contains a forbidden word combination).

    Raise an exception if the provided app name contains a forbidden keyword.

    Parameters
    ----------
    app_name_with_version: str
        the app name to be verified. Includes the version
    version_required: bool

    Returns
    -------
    bool:
        a boolean indicating whether the app name is valid.

    """
    try:
        if version_required:
            parse_obj_as(DottedIdentifierWithVersion, app_name_with_version)
        else:
            parse_obj_as(DottedIdentifierWithOptionalVersion, app_name_with_version)
    except ValidationError as exc:
        error_message = parse_pydantic_errors(validation_error=exc)
        raise DataTypeException(GeneralMessages.invalid_name.format(reason=error_message))

    image = DockerImageName.parse(name=app_name_with_version)
    check_if_datatype_name_is_valid(image.name)

    return True
