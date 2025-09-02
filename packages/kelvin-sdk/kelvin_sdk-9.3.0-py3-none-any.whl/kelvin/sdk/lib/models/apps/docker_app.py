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

from typing import List, Optional

from pydantic.v1 import Field

from kelvin.sdk.lib.models.generic import KSDKModel


class DockerAppType(KSDKModel):
    dockerfile: str = Field(..., description="Docker file.", title="Docker File")
    context: str = Field(..., description="Build context directory.", title="Build context.")
    args: Optional[List[str]] = None
