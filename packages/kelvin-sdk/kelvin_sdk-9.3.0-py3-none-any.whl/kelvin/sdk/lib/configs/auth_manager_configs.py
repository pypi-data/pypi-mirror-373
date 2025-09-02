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


class AuthManagerConfigs:
    kelvin_client_timeout_thresholds = (10.0, 30.0)
    invalid_session_message: str = "No valid session found. Please login."
    browser_auth_port: int = 38638
    browser_auth_redirect_uri = f"http://localhost:{browser_auth_port}"
    browser_auth_client_id: str = "kelvin-client"
    browser_auth_timeout: int = 30
