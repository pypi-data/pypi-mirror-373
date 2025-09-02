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

from typing import Any, BinaryIO, Optional, Union

from docker.types import CancellableStream

from kelvin.sdk.lib.models.generic import KSDKModel
from kelvin.sdk.lib.utils.logger_utils import logger


class OperationResponse(KSDKModel):
    success: bool = True
    data: Any = None
    log: Union[Any, str] = None
    stream: Optional[Union[BinaryIO, CancellableStream]] = None

    class Config:
        arbitrary_types_allowed = True

    def print(self) -> None:
        if self.success:
            logger.relevant(self.log)
        else:
            logger.error(self.log)
