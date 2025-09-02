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

from typing import Any, Dict, Optional

from pydantic.v1 import Extra, Field, validator

from kelvin.sdk.lib.models.generic import KPath, KSDKModel

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal  # type: ignore


class WorkloadDeploymentRequest(KSDKModel):
    cluster_name: Optional[str]
    workload_name: Optional[str] = Field(..., max_length=32)
    workload_title: Optional[str] = Field(..., max_length=64)
    app_config: Optional[str]
    runtime: Optional[str]
    quiet: bool = False


class WorkloadUpdateRequest(KSDKModel):
    workload_name: str = Field(..., max_length=32)
    workload_title: Optional[str] = Field(..., max_length=64)
    app_config: str
    runtime: Optional[str]
    quiet: bool = False


class WorkloadTemplateData(KSDKModel):
    class Config:
        extra = Extra.allow

    @validator("app_config", pre=True)
    def validate_app_config(cls, value: str) -> KPath:  # noqa
        path = KPath(value)
        if not path.exists():
            raise ValueError(f"Path does not exist: {value}")
        return path

    @validator("status", "result", pre=True)
    def validate_empty_fields(cls, value: Optional[str]) -> Optional[str]:  # noqa
        if not value:
            return None
        return value

    status: Optional[str] = None
    result: Optional[Literal["success", "failed", "skip"]] = None

    node_name: str
    app_name: str
    app_version: str

    workload_name: str
    workload_title: str

    app_config: KPath

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {**super().dict(*args, **kwargs), "app_config": str(self.app_config)}
