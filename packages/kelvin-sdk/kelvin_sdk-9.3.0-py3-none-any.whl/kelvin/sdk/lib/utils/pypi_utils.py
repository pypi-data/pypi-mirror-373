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

import warnings
from typing import Dict

from kelvin.sdk.lib.configs.pypi_configs import PypiConfigs
from kelvin.sdk.lib.utils.logger_utils import logger

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message="Setuptools is replacing distutils.")

    from pip._internal.configuration import Configuration as PipConfiguration
    from pip._internal.configuration import ConfigurationError as PipConfigurationError
    from pip._internal.utils.compat import WINDOWS


def get_pypi_credentials() -> dict:
    """
    When provided with Kelvin SDK global configuration, retrieve the pypi credentials
    to install external dependencies required by the application.

    Returns
    -------
    dict:
        a dictionary containing the required pypi credentials for external dependencies.

    """
    try:
        # pip configuration
        pip_config = PipConfiguration(isolated=False)
        pip_config.load()

        pypi_index_url_key = PypiConfigs.pypi_index_url_key
        pypi_extra_index_url_key = PypiConfigs.pypi_extra_index_url_key

        pypi_urls: Dict[str, Dict] = {}

        # collect PyPI urls from environment (priority) and pip config
        for key in [pypi_index_url_key, pypi_extra_index_url_key]:
            for section in [PypiConfigs.global_key, PypiConfigs.env_key]:
                try:
                    value = pip_config.get_value(f"{section}.{key}")
                    pypi_urls[key] = {"section": section, "key": key, "url": value}
                    logger.relevant(get_pretty_source_from_section(section=section, pypi_url=value))
                except PipConfigurationError:
                    continue

        result = {f"PIP_{key.upper().replace('-', '_')}": values.get("url", "") for key, values in pypi_urls.items()}
        if not result:
            logger.info("No PyPi credentials retrieved from the system.")
        return result

    except Exception as exc:
        logger.error(f"Unable to access any repositories - {exc}")
        return {}


def get_pretty_source_from_section(section: str, pypi_url: str) -> str:
    """Return the pretty log entry for a given section & pypi url.

    Parameters
    ----------
    section :str
        the section (env/pip) corresponding to the pip credential source.
    pypi_url :str
        the pypi url associated to the section.

    Returns
    -------
    str:
        the redacted version of the original url.
    """
    redacted_pypi_url = " ".join(redact_pip_url(pip_url=x) for x in pypi_url.strip().split("\n"))
    if section == PypiConfigs.global_key:
        config_file = "pip.ini" if WINDOWS else "pip.conf"
        return f'Loading PyPi credentials from file "{config_file}": "{redacted_pypi_url}"'
    if section == PypiConfigs.env_key:
        return f'Loaded PyPi credentials from Environment Variable ("PIP_EXTRA_INDEX_URL"): "{redacted_pypi_url}"'
    return ""


def redact_pip_url(pip_url: str) -> str:
    """Hide sensitive data (password) from a valid PyPi credential.

    Parameters
    ----------
    pip_url :str
        the pip url to redact to obfuscate.

    Returns
    -------
    str:
        the original, redacted pip url
    """
    from urllib.parse import urlparse

    parsed = urlparse(pip_url.strip())
    if parsed.username:
        replaced = parsed._replace(netloc="{}:{}@{}".format(parsed.username, "******", parsed.hostname))
        return replaced.geturl()
    return pip_url
