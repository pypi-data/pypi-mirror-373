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


class PypiConfigs:
    env_key: str = ":env:"
    global_key: str = "global"
    pypi_index_url_key: str = "index-url"
    pypi_extra_index_url_key: str = "extra-index-url"
    kelvin_pypi_internal_repository: str = "https://nexus.kelvininc.com/repository/pypi-internal/simple"
