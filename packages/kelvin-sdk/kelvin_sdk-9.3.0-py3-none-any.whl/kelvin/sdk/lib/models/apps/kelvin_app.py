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
    DataType,
    Images,
    Language,
    LoggingLevel,
    Mqtt,
    Name,
    NameDNS,
    NonEmptyString,
    Storage,
)
from kelvin.sdk.lib.models.generic import KSDKModel
from kelvin.sdk.lib.models.types import BaseEnum


class DeviceTypeName(BaseEnum):
    asset = "asset"
    component = "component"
    part = "part"
    sensor = "sensor"
    enterprise = "enterprise"
    site = "site"
    area = "area"
    productionline = "production-line"
    processcell = "process-cell"
    productionunit = "production-unit"
    storageunit = "storage-unit"


class AssetsEntry(KSDKModel):
    name: Optional[NonEmptyString] = Field(None, description="Name.", title="Name")
    properties: Optional[Any] = Field(None, description="Asset Properties.", title="Asset Properties")
    parameters: Optional[Any] = Field(None, description="Asset Parameters.", title="Asset Parameters")
    metrics: Optional[Any] = Field(None, description="Asset Metrics.", title="Asset Metrics")


class MetricInfo(KSDKModel):
    node_names: Optional[List[NameDNS]] = Field(None, description="List of Node names.", title="Node Names")
    workload_names: Optional[List[NameDNS]] = Field(None, description="List of Workload names.", title="Workload Names")
    asset_names: Optional[List[Name]] = Field(None, description="List of asset names.", title="Asset Names")
    names: Optional[List[Name]] = Field(None, description="List of external metric names.", title="Names")


class Metric(KSDKModel):
    name: Name = Field(..., description="Name.", title="Name")
    data_type: str = Field(..., description="Data type.", title="Data Type")


class MetricInput(Metric):
    sources: Optional[List[MetricInfo]] = None


class MetricOutput(Metric):
    targets: Optional[List[MetricInfo]] = None
    storage: Optional[Storage] = Field(None, description="Metric Storage.", title="Storage")
    retain: Optional[bool] = None
    control_change: Optional[bool] = None


class KelvinAppType(KSDKModel):
    logging_level: Optional[LoggingLevel] = Field("INFO", description="Core Logging Level", title="Logging Level")
    images: Optional[Images] = Field(
        None, description="Image configuration for building a Kelvin application.", title="Kelvin Application Images"
    )
    assets: Optional[List[AssetsEntry]] = Field(None, description="Assets Parameters.", title="Assets Parameters")
    global_: Optional[MetricInfo] = Field(None, alias="global", description="Global source/targets", title="Global")
    system_packages: Optional[List[str]] = Field(
        None, description="Packages to install into image.", title="System Packages"
    )
    mqtt: Optional[Mqtt] = None
    language: Language
    data_types: Optional[List[DataType]] = []
    inputs: Optional[List[MetricInput]] = Field(None, description="Inputs.", title="Inputs")
    outputs: Optional[List[MetricOutput]] = Field(None, description="Outputs.", title="Outputs")
    configuration: Optional[Any] = Field(None, description="Configuration.", title="Configuration")
