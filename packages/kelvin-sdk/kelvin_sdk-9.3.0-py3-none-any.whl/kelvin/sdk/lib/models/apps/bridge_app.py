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

from typing import Any, List, Optional

from pydantic.v1 import Field

from kelvin.sdk.lib.models.apps.common import (
    Access,
    DataType,
    Images,
    Language,
    LoggingLevel,
    Mqtt,
    Name,
    NonEmptyString,
    Protocol,
    Storage,
)
from kelvin.sdk.lib.models.generic import KSDKModel


class MetricsMapEntry(KSDKModel):
    name: Name = Field(..., description="Name.", title="Name")
    asset_name: NonEmptyString = Field(..., description="Asset Name.", title="Asset Name")
    data_type: str = Field(..., description="Data Type.", title="Data Type")
    access: Optional[Access] = Field(Access.RO, description="Metric Access.", title="Access")
    storage: Optional[Storage] = Field(Storage.node_and_cloud, description="Metric Storage.", title="Storage")
    configuration: Optional[Any] = Field(None, description="Configuration.", title="Configuration")
    retain: Optional[bool] = True


class BridgeAppType(KSDKModel):
    protocol: Optional[Protocol] = Field(None, description="Bridge Protocol", title="Protocol")
    logging_level: Optional[LoggingLevel] = Field("INFO", description="Core Logging Level", title="Logging Level")
    images: Optional[Images] = Field(
        None, description="Image configuration for building a Kelvin application.", title="Kelvin Application Images"
    )
    system_packages: Optional[List[str]] = Field(
        None, description="Packages to install into image.", title="System Packages"
    )
    mqtt: Optional[Mqtt] = None
    language: Language
    data_types: Optional[List[DataType]] = None
    metrics_map: List[MetricsMapEntry] = Field(..., description="Metrics Map.", title="Metrics Map")
    configuration: Any = Field(..., description="Configuration.", title="Configuration")
