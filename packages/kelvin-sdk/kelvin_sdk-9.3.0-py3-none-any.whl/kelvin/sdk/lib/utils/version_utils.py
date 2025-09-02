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

from packaging import version

from kelvin.sdk.lib.models.types import VersionStatus


def assess_version_status(
    current_version: str, minimum_version: str, latest_version: str, should_warn: bool = True
) -> VersionStatus:
    """Verifies whether the current KSDK version is supported.

    Warn the user, if 'should_warn' is set to True, that the SDK is outdated.
    Raise an exception should it not respect the minimum version.

    Parameters
    ----------
    current_version : str
        the current version to check.
    minimum_version : str
        the minimum accepted version.
    latest_version : str
        the latest version of the SDK.
    should_warn : bool
        if set to true, will warn the user in case the ksdk is out of version.

    Returns
    -------
    VersionStatus:
        the corresponding version status.

    """
    try:
        current_v = version.parse(current_version)
        min_v = version.parse(minimum_version)
        latest_v = version.parse(latest_version)

        if (min_v <= current_v <= latest_v) or check_if_is_pre_release(current_version):
            if current_v < latest_v and should_warn:
                return VersionStatus.OUT_OF_DATE
        else:
            return VersionStatus.UNSUPPORTED
    except TypeError:
        pass
    return VersionStatus.UP_TO_DATE


def check_if_is_pre_release(v: str) -> bool:
    """Check if a given version is a pre-release

    Parameters
    ----------
    version : str
        the version to verify.

    Returns
    -------
    bool:
        a bool indicating whether the version matches the indicated version type.

    """
    try:
        return version.parse(v).is_prerelease
    except Exception:
        return False
