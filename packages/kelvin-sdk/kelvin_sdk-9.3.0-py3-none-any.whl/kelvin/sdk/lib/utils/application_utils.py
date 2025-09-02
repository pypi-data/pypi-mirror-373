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
from kelvin.sdk.lib.exceptions import AppException, AppNameIsInvalid
from kelvin.sdk.lib.models.apps.common import NameDNS


def check_if_app_name_is_valid(app_name: str) -> bool:
    """Verify whether the provided app name is valid (or contains a forbidden word combination).

    Raise an exception if the provided app name contains a forbidden keyword.

    Parameters
    ----------
    app_name : str
        the app name to be verified.

    Returns
    -------
    bool:
        a boolean indicating whether the app name is valid.

    """
    try:
        invalid_keywords = ["python", "test", "kelvin"]
        if app_name in invalid_keywords:
            raise AppNameIsInvalid("\tPython-specific keywords are forbidden")
        parse_obj_as(NameDNS, app_name)
    except ValidationError:
        error_message = (
            "Use only lowercase alphanumeric characters (letters and numbers) and dashes ( - )."
            "The entry should start and end with an alphanumeric character. For example: 'my-app'."
        )
        raise AppException(GeneralMessages.invalid_name.format(reason=error_message))
    except AppNameIsInvalid as exc:
        raise AppException(GeneralMessages.invalid_name.format(reason=str(exc)))

    return True
