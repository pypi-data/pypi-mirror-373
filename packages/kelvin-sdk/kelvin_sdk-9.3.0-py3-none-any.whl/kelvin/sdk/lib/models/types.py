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

from enum import Enum
from pathlib import Path
from typing import Any, List, Optional


class BaseEnum(Enum):
    @classmethod
    def as_list(cls) -> List[str]:
        return [item.value for item in cls.__members__.values()]

    @classmethod
    def _missing_(cls, value: Any) -> BaseEnum:
        return next(iter(cls.__members__.values()))

    @property
    def value_as_str(self) -> str:
        return str(self.value)


class DelimiterStyle(BaseEnum):
    ANGULAR = "<+", "+>"
    BRACE = "{{", "}}"


class EmbeddedFiles(BaseEnum):
    EMPTY_FILE = "empty_file"
    DOCKERIGNORE = ".dockerignore"
    KELVIN_PYTHON_APP_GITIGNORE = ".gitignore"
    KELVIN_PYTHON_APP_PYPROJECT = "pyproject.toml"
    KELVIN_PYTHON_APP_DOCKERFILE = "kelvin_python_app_dockerfile"
    BRIDGE_PYTHON_APP_DOCKERFILE = "bridge_python_app_dockerfile"
    DEFAULT_DATATYPE_TEMPLATE = "datatype.yml"


class FileType(BaseEnum):
    ROOT = "root"
    APP = "app"
    CONFIGURATION = "configuration"
    BUILD = "build"
    DATA = "data"
    DATATYPE = "datatype"
    DOCS = "docs"
    TESTS = "tests"
    WHEELS = "wheels"
    SCHEMAS = "schemas"


class LogColor(BaseEnum):
    COLORED = "colored"
    COLORLESS = "colorless"


class LogType(BaseEnum):
    KSDK = "KSDK"
    JSON = "JSON"


class StatusDataSource(BaseEnum):
    CACHE = "cache"
    LIVE = "live"


class ShellType(BaseEnum):
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"


class VersionStatus(BaseEnum):
    UNSUPPORTED = 1
    OUT_OF_DATE = 2
    UP_TO_DATE = 3


class WorkloadFileType(BaseEnum):
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"

    @staticmethod
    def parse_file_type(file_type: Optional[str], file: Path) -> WorkloadFileType:
        if file_type:
            if file_type in WorkloadFileType.as_list():
                return WorkloadFileType(file_type)
            raise ValueError("Unknown file-type: {file_type}".format(file_type=file_type))
        else:
            _file_type = file.suffix[1:]
            if _file_type in {"yml", "yaml"}:
                return WorkloadFileType.YAML
            elif _file_type in {"csv", "txt", "tsv", "tab"}:
                return WorkloadFileType.CSV
            elif _file_type in {"json"}:
                return WorkloadFileType.JSON
        raise ValueError("Unknown file-type: {file_type}".format(file_type=_file_type))
