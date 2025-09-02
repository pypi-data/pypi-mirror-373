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

import json
import re
import sys
import time
import webbrowser
from getpass import getpass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse

from keycloak.exceptions import KeycloakError
from pydantic.v1 import ValidationError

from kelvin.api.client import Client
from kelvin.api.client.config import ConfigError
from kelvin.sdk.lib.configs.auth_manager_configs import AuthManagerConfigs
from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.exceptions import KSDKException, MandatoryConfigurationsException
from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.utils.display_utils import (
    display_data_entries,
    display_yes_or_no_question,
    pretty_colored_content,
    success_colored_message,
)
from kelvin.sdk.lib.utils.logger_utils import logger, setup_logger

from ..configs.click_configs import color_formats
from ..configs.general_configs import KSDKHelpMessages
from ..models.generic import KPath
from ..models.ksdk_docker import KSDKDockerAuthentication
from ..models.ksdk_global_configuration import CompanyMetadata, KelvinSDKGlobalConfiguration
from ..models.types import LogColor, VersionStatus
from ..utils.exception_utils import retrieve_error_message_from_keycloak_exception
from ..utils.general_utils import get_system_information
from ..utils.version_utils import check_if_is_pre_release


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Server(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        query = urlparse(self.path).query
        parsed_query = parse_qs(query)
        if "code" in parsed_query:
            logger.relevant("A request was received with an authorization code.")
            code = parsed_query["code"][0]
            self.wfile.write(bytes('<script>window.alert("Kelvin SDK connected."); window.close();</script>', "UTF-8"))
            SessionManager.auth_code = code


class SessionManager(metaclass=Singleton):
    # 1 - Central piece
    _global_ksdk_configuration: Optional[KelvinSDKGlobalConfiguration] = None
    # 2 - Cached blocks
    _docker_credentials: Optional[KSDKDockerAuthentication] = None
    _current_site_metadata: Optional[CompanyMetadata] = None
    _current_client: Optional[Client] = None

    auth_code: Optional[str] = None

    # 1 - Global Session Manager
    def reset_session(self, full_reset: bool = False, ignore_destructive_warning: bool = False) -> OperationResponse:
        """Logs off the client all currently stored sessions.

        Parameters
        ----------
        full_reset: bool, default=False
            Indicates whether it should proceed with a full reset.
        ignore_destructive_warning: bool, default=False
            Ignore_destructive_warning: indicates whether it should ignore the destructive warning.

        Returns
        -------
        OperationResponse
            An OperationResponse object encapsulating the result of the logout request.

        """
        try:
            # 1 - Logout from all sessions
            if not ignore_destructive_warning:
                ignore_destructive_warning = display_yes_or_no_question("")

            if ignore_destructive_warning:
                if self._current_client:
                    self._current_client.logout()
                    self._current_client = None
                    self._current_site_metadata = None

                self.get_global_ksdk_configuration().reset_ksdk_configuration().commit_ksdk_configuration()

            ksdk_configuration = self.get_global_ksdk_configuration()

            # 2 - If it is a full reset, purge all the configuration files
            if full_reset:
                logger.info("Resetting KSDK configurations..")
                self._reset_configuration_files(ksdk_configuration=ksdk_configuration)

            success_message = "Session successfully reset."
            logger.relevant(success_message)
            return OperationResponse(success=True, log=success_message)
        except Exception as exc:
            error_message = f"Error resetting session: {str(exc)}"
            logger.exception(error_message)
            return OperationResponse(success=False, log=error_message)

    def full_reset(self, ignore_destructive_warning: bool = False) -> OperationResponse:
        """
        Reset all configurations & cache used by Kelvin SDK.

        Parameters
        ----------
        ignore_destructive_warning : bool
            indicates whether or not the command should bypass the destructive prompt warning.

        Returns
        -------
        OperationResponse
            an OperationResponse encapsulating the result of the reset operation.

        """
        try:
            if not ignore_destructive_warning:
                question: str = "\tThis operation will reset all configurations"
                ignore_destructive_warning = display_yes_or_no_question(question=question)

            result_message: str = "Reset operation cancelled"
            if ignore_destructive_warning:
                ksdk_config_dir_path: KPath = self.get_global_ksdk_configuration().ksdk_config_dir_path
                if ksdk_config_dir_path and ksdk_config_dir_path.exists():
                    logger.info(f'Resetting configurations under "{ksdk_config_dir_path.expanduser().absolute()}".')
                    ksdk_config_dir_path.delete_dir()
                    result_message = "Configurations successfully reset"
                    logger.relevant(result_message)
            else:
                logger.warning(result_message)

            return OperationResponse(success=True, log=result_message)

        except Exception as exc:
            error_message: str = str(exc)
            logger.error(f'Error resetting configurations: "{error_message}"')
            return OperationResponse(success=False, log=error_message)

    # 2 - Internal functions
    @staticmethod
    def _reset_configuration_files(ksdk_configuration: KelvinSDKGlobalConfiguration) -> None:
        """Clear all configuration files and folders

        Parameters
        ----------
        ksdk_configuration: KelvinSDKGlobalConfiguration
            A KSDK global configuration instance
        """
        # 1 - get the variables
        files_to_reset: List[KPath] = [
            ksdk_configuration.ksdk_history_file_path,
            ksdk_configuration.ksdk_client_config_file_path,
            ksdk_configuration.ksdk_config_file_path,
            ksdk_configuration.ksdk_temp_dir_path,
            ksdk_configuration.ksdk_schema_dir_path,
        ]
        # 2 - delete all files
        for item in files_to_reset:
            if item.exists():
                if item.is_dir():
                    item.delete_dir()
                else:
                    item.unlink()

    def _fresh_client_login_for_url(
        self,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_code: Optional[str] = None,
        totp: Optional[str] = None,
    ) -> Client:
        """Setup a fresh login, writing the required configurations to target ksdk configuration file path.

        Sets up the kelvin API client configuration to allow api interaction.
        Sets up the kelvin sdk configuration to allow the storage of specific ksdk variables.

        Parameters
        ----------
        url: str
            The url to login to.
        username: str
            The username of the client site.
        password: str
            The password corresponding to the username.
        totp: str, optional
            The TOTP corresponding to the username.
        Returns
        -------
        Client
            A ready-to-use KelvinClient object.
        """

        ksdk_configuration: KelvinSDKGlobalConfiguration = self.get_global_ksdk_configuration()
        try:
            # Prepare metadata retrieval
            logger.info(f'Attempting to log on "{url}"')

            self._current_client = Client.from_file(
                ksdk_configuration.ksdk_client_config_file_path,
                site=url,
                username=username,
                create=True,
                verbose=True,
                timeout=AuthManagerConfigs.kelvin_client_timeout_thresholds,
            )
            self._current_client.login(
                password=password,
                auth_code=auth_code,
                redirect_uri=AuthManagerConfigs.browser_auth_redirect_uri,
                totp=totp,
                force=True,
            )

            # Retrieve the versions and set them once the client access is done
            url_metadata = self._set_metadata_for_current_url()

            ksdk_configuration.kelvin_sdk.last_metadata_refresh = time.time()
            ksdk_configuration.kelvin_sdk.current_url = url
            ksdk_configuration.kelvin_sdk.current_user = self._current_client.user_info["preferred_username"]
            ksdk_configuration.kelvin_sdk.ksdk_minimum_version = url_metadata.sdk.ksdk_minimum_version
            ksdk_configuration.kelvin_sdk.ksdk_latest_version = url_metadata.sdk.ksdk_latest_version
            ksdk_configuration.commit_ksdk_configuration()

            return self._current_client
        except Exception as inner_exception:
            try:
                ksdk_configuration.reset_ksdk_configuration().commit_ksdk_configuration()
            except Exception:
                raise inner_exception
            raise inner_exception

    def _set_metadata_for_current_url(self) -> CompanyMetadata:
        """Retrieve the metadata from the specified url.

        Returns
        -------
        CompanyMetadata
            The CompanyMetadata object that encapsulates all the metadata.
        """

        try:
            if not self._current_client:
                self._current_client = self.login_client_on_current_url()
            if self._current_client and self._current_client.config.metadata:
                self._current_site_metadata = CompanyMetadata(**self._current_client.config.metadata)
                return self._current_site_metadata
            raise
        except ValidationError as exc:
            raise MandatoryConfigurationsException(exc)
        except Exception:
            raise ValueError(AuthManagerConfigs.invalid_session_message)

    def browser_login(self, url: str) -> Optional[str]:
        if not re.match(r"\w+://", url):
            url = f"https://{url}"
        if "." not in url:
            url = f"{url}.kelvininc.com"

        path = "auth/realms/kelvin/protocol/openid-connect/auth"
        params = {
            "client_id": AuthManagerConfigs.browser_auth_client_id,
            "redirect_uri": AuthManagerConfigs.browser_auth_redirect_uri,
            "response_type": "code",
        }
        page = f"{url}/{path}?{urlencode(params)}"

        httpd = HTTPServer(server_address=("", AuthManagerConfigs.browser_auth_port), RequestHandlerClass=Server)
        httpd.timeout = AuthManagerConfigs.browser_auth_timeout

        logger.info("Opening browser to authenticate")
        webbrowser.open_new_tab(page)

        logger.info("Waiting for authorization code.")
        httpd.handle_request()

        return SessionManager.auth_code

    # 2 - Client access and instantiation
    def login_on_url(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        browser: bool = False,
        reset: bool = False,
    ) -> OperationResponse:
        """Logs the user into the provided url.

        Parameters
        ----------
        url: str, optional
            The url to log on.
        username: str, optional
            The username of the client site.
        password: str, optional
            The password corresponding to the username.
        totp: str, optional
            The current TOTP corresponding to the username.
        browser: bool, default=False
            If set, opens a browser window to proceed with the authentication.
        reset: bool, default=False
            If set to True, will clear the existing configuration prior to the new session.

        Returns
        -------
        OperationResponse
            An OperationResponse object encapsulating the result of the authentication request.

        """
        try:
            if reset:
                self.reset_session(full_reset=reset, ignore_destructive_warning=True)

            url = url or input("Platform: ")
            username_missing = username is None and password is not None
            password_missing = username is not None and password is None
            empty_credentials = username is None and password is None

            auth_code = None
            if browser:
                auth_code = self.browser_login(url=url)
                username = username or ""

            if not browser and (username_missing or password_missing):
                ksdk_auth_incomplete_credentials: str = """Incomplete credentials. \n
                    Either provide both credentials or follow the prompt."""
                raise KSDKException(ksdk_auth_incomplete_credentials)

            if not browser and empty_credentials:
                username = input("Enter your username: ")
                password = getpass(prompt="Enter your password: ")
                totp_prompt: str = "Enter 2 Factor Authentication (2FA) one-time password (blank if not required): "
                totp = getpass(totp_prompt) or None

            if auth_code is None and (not username or not password):
                raise KSDKException(message="Please provide a valid set of credentials")

            # 1 - Ensure the ksdk configuration file exists before proceeding
            if not url:
                raise KSDKException(message="No session currently available. Please provide a valid url argument")

            # 2 - Save the client configuration to the client configuration
            self._current_client = self._fresh_client_login_for_url(
                url=url, username=username, password=password, auth_code=auth_code, totp=totp
            )
            success_message = f'Successfully logged on "{self._current_client.config.url}" as "{self._current_client.user_info["preferred_username"]}"'
            logger.relevant(success_message)
            return OperationResponse(success=True, log=success_message)
        except KeycloakError as exc:
            error_message = retrieve_error_message_from_keycloak_exception(keycloak_exception=exc)
            keycloak_auth_failure: str = f"""Error authenticating: {error_message}. \n
                Contact Kelvin's support team.
            """
            logger.exception(keycloak_auth_failure)
            return OperationResponse(success=False, log=keycloak_auth_failure)
        except Exception as exc:
            api_auth_failure: str = f"""Error authenticating: {str(exc)}. \n
                Consider invalidating authentication cache with `kelvin auth login --reset`.
            """
            logger.error(api_auth_failure)
            return OperationResponse(success=False, log=api_auth_failure)

    def login_client_on_current_url(
        self, login: bool = True, verbose: bool = True, force_metadata: bool = False
    ) -> Client:
        """Performs a fresh login on the current url, retrieving the instantiated KelvinClient object.

        Parameters
        ----------
        login: bool, default=True
            Hints the Kelvin SDK Client object it should perform a login.
        verbose: bool, default=True
            Indicates whether the Kelvin SDK Client object should display all verbose logs.
        force_metadata: bool, default=True
            Indicates whether the Kelvin SDK Client object should force fetch metadata.

        Returns
        -------
        Client
            A ready-to-use KelvinClient object.

        """

        try:
            return self._get_current_client(login=login, verbose=verbose, force_metadata=force_metadata)
        except ConfigError:
            logger.error("Unable to load configuration file. Retrying...")
            time.sleep(2)
            return self._get_current_client(login=login, verbose=verbose, force_metadata=force_metadata)
        except Exception:
            raise ConnectionError(AuthManagerConfigs.invalid_session_message)

    def _get_current_client(self, login: bool = True, verbose: bool = True, force_metadata: bool = False) -> Client:
        ksdk_configuration = self.get_global_ksdk_configuration()
        current_url = ksdk_configuration.kelvin_sdk.current_url
        current_user = ksdk_configuration.kelvin_sdk.current_user
        kwargs = {"metadata": None} if force_metadata else {}

        self._current_client = Client.from_file(
            ksdk_configuration.ksdk_client_config_file_path,
            site=current_url,
            url=current_url,
            username=current_user,
            login=login,
            verbose=verbose,
            timeout=AuthManagerConfigs.kelvin_client_timeout_thresholds,
            **kwargs,  # type: ignore
        )
        if not self._current_site_metadata:
            self._set_metadata_for_current_url()
        return self._current_client

    def authentication_token(self, full: bool, margin: float = 10.0) -> OperationResponse:
        """Obtain an authentication authentication_token from the API.

        Parameters
        ----------
        full: bool
            Return the full authentication_token.
        margin: float, default=10.0
            Minimum time to expiry.
        Returns
        -------
        OperationResponse
            OperationResponse object encapsulating the authentication token.
        """

        margin = max(margin, 0.0)
        force = margin <= 0.0

        try:
            client = self.login_client_on_current_url(login=False, verbose=False)
            client.login(force=force, margin=margin)
        except Exception as exc:
            logger.error(str(exc))
            return OperationResponse(success=False, log=str(exc))

        if full:
            json.dump(client.token, sys.stdout, indent=2)
        else:
            sys.stdout.write(client.token["access_token"])

        return OperationResponse(success=True, log=str(client.token))

    def get_global_ksdk_configuration(self) -> KelvinSDKGlobalConfiguration:
        """Attempt to retrieve the KelvinSDKGlobalConfiguration from specified file path.

        Returns
        -------
        KelvinSDKGlobalConfiguration
            A KelvinSDKGlobalConfiguration object corresponding to the current configuration.
        """

        if self._global_ksdk_configuration:
            return self._global_ksdk_configuration

        self._global_ksdk_configuration = KelvinSDKGlobalConfiguration()
        return self._global_ksdk_configuration.commit_ksdk_configuration()

    def get_documentation_link_for_current_url(self) -> Optional[str]:
        """
        Retrieve, if existent, the complete url to the documentation page.

        Returns
        -------
        Optional[str]
            a string containing a link to the documentation page.
        """
        try:
            return self.get_current_session_metadata().documentation.url
        except Exception:
            return None

    def get_kelvin_system_information_for_display(self) -> str:
        """Display system information as well as, if existent, the current session's url.

        Returns
        -------
        str
            a string containing the system's information.
        """

        try:
            system_information = get_system_information(pretty_keys=True)
            ksdk_configuration = self.get_global_ksdk_configuration()
            current_url = ksdk_configuration.kelvin_sdk.current_url or KSDKHelpMessages.current_session_login
            # display utils
            pretty_current_url = success_colored_message(message=current_url)
            pretty_system_info = pretty_colored_content(content=system_information, indent=2, initial_indent=2)
            return f"\nCurrent session: {pretty_current_url}\nSystem Information: {pretty_system_info}"
        except Exception:
            return KSDKHelpMessages.current_session_login

    def get_kelvin_system_information(self) -> dict:
        """
        Report the entire configuration set currently in use by Kelvin SDK.

        Returns
        -------
        dict
            a dictionary containing the entire Kelvin System Information

        """
        system_information = get_system_information(pretty_keys=False)
        current_session_metadata = self.get_current_session_metadata().dict(exclude_none=True, exclude_unset=True)
        from ..emulation.emulation_manager import get_emulation_system_native_containers_information

        current_emulation_system_information = get_emulation_system_native_containers_information()
        current_url = (
            self.get_global_ksdk_configuration().kelvin_sdk.current_url or KSDKHelpMessages.current_session_login
        )
        return {
            "current_url": current_url,
            "system_information": system_information,
            "metadata": current_session_metadata,
            "emulation_system": current_emulation_system_information,
        }

    def get_docker_credentials_for_current_url(self) -> KSDKDockerAuthentication:
        """Returns the current credentials for the specified url.

        Returns
        -------
        KSDKDockerAuthentication
            An KSDKDockerAuthentication instance containing the Kelvin API Client credentials for the specified url.
        """
        try:
            if self._docker_credentials:
                return self._docker_credentials

            ksdk_configuration = self.get_global_ksdk_configuration()
            current_client = self.login_client_on_current_url()
            current_site_metadata = self.get_current_session_metadata()

            self._docker_credentials = KSDKDockerAuthentication(
                **{
                    "registry_url": str(current_site_metadata.docker.url or ""),
                    "registry_port": str(current_site_metadata.docker.port or ""),
                    "username": ksdk_configuration.kelvin_sdk.current_user,
                    "password": str(current_client.password or ""),
                }
            )
            return self._docker_credentials
        except Exception:
            raise ConnectionError(AuthManagerConfigs.invalid_session_message)

    def get_current_session_metadata(self) -> CompanyMetadata:
        """Returns the current session company metadata

        Returns
        -------
        CompanyMetadata
            An object containing the company metadata
        """

        if self._current_site_metadata:
            return self._current_site_metadata

        return self._set_metadata_for_current_url()

    def refresh_metadata(self) -> Optional[KelvinSDKGlobalConfiguration]:
        """A simple wrapper method to refresh metadata on request.

        Returns
        -------
        KelvinSDKGlobalConfiguration, optional
            A boolean indicating whether or not the metadata was successfully refreshed.
        """
        try:
            # 1 - Get the current configuration
            ksdk_configuration = self.get_global_ksdk_configuration()

            # 2 - Assess the last timestamp
            try:
                last_metadata_retrieval = int(ksdk_configuration.kelvin_sdk.last_metadata_refresh)
            except TypeError:
                last_metadata_retrieval = 0
            # 3 - check the difference
            time_difference = time.time() - last_metadata_retrieval
            twelve_hours_cap_is_crossed = time_difference >= 12 * 3600
            # 4 - If it crosses the 12h threshold, force refresh
            if twelve_hours_cap_is_crossed:
                logger.info("Refreshing metadata..")
                self.login_client_on_current_url(force_metadata=True)
                url_metadata = self.get_current_session_metadata()

                ksdk_configuration.ksdk_schema_dir_path.delete_dir()
                ksdk_configuration.kelvin_sdk.last_metadata_refresh = time.time()
                ksdk_configuration.kelvin_sdk.ksdk_minimum_version = url_metadata.sdk.ksdk_minimum_version
                ksdk_configuration.kelvin_sdk.ksdk_latest_version = url_metadata.sdk.ksdk_latest_version
                self._global_ksdk_configuration = ksdk_configuration.commit_ksdk_configuration()
                return self._global_ksdk_configuration
        except ConnectionError:
            logger.debug("Could not retrieve metadata. Proceeding regardless..")
        return None

    def assess_kelvin_version(self) -> Optional[str]:
        """
        Assess the current kelvin-sdk version.
        Display the necessary warning if that is the case

        Returns
        -------
        str
            The string containing the appropriate message warning.

        """
        ksdk_configuration = self.get_global_ksdk_configuration()
        should_warn = ksdk_configuration.kelvin_sdk.configurations.ksdk_version_warning

        if not should_warn:
            return None
        else:
            from kelvin.sdk.lib.utils.version_utils import assess_version_status

            version_status = assess_version_status(
                current_version=ksdk_configuration.kelvin_sdk.ksdk_current_version,
                minimum_version=ksdk_configuration.kelvin_sdk.ksdk_minimum_version,
                latest_version=ksdk_configuration.kelvin_sdk.ksdk_latest_version,
                should_warn=should_warn,
            )

            if not version_status == VersionStatus.UP_TO_DATE:
                from kelvin.sdk.lib.configs.pypi_configs import PypiConfigs

                repository = ""
                if check_if_is_pre_release(ksdk_configuration.kelvin_sdk.ksdk_latest_version):
                    repository = f"--extra-index-url {PypiConfigs.kelvin_pypi_internal_repository} "

                ksdk_version_warning: str = """\n
                        The current SDK version is not the recommended for the environment you are currently using.
                        Current: {red}{current_version}{reset} Recommended: {green}{latest_version}{reset} \n
                        You can install the recommended version with:
                        {green}pip3 install {repository}kelvin-sdk=={latest_version} {reset}\n
                        And log in again with {green}kelvin auth login <url>{reset}.
                """
                return ksdk_version_warning.format_map(
                    {
                        **color_formats,
                        **ksdk_configuration.kelvin_sdk.versions,
                        "repository": repository,
                    }
                )
            return None

    def setup_logger(self, verbose: bool = False, colored_logs: bool = True) -> Any:
        """
        Sets up the logger based on the verbose flag.

        Parameters
        ----------
        verbose : bool
            the flag indicating whether it should setup the logger in verbose mode.
        colored_logs: bool, Default=False
            Indicates whether all logs should be colored and 'pretty' formatted.

        Returns
        -------
        Any
            the setup logger.

        """
        global_configuration: KelvinSDKGlobalConfiguration = self.get_global_ksdk_configuration()
        log_color: LogColor = LogColor.COLORED
        if (
            not (sys.__stdout__.isatty() if sys.__stdout__ else False)
            or not global_configuration.kelvin_sdk.configurations.ksdk_colored_logs
            or not colored_logs
        ):
            log_color = LogColor.COLORLESS
        ksdk_history_file_path: KPath = global_configuration.ksdk_history_file_path
        debug: bool = global_configuration.kelvin_sdk.configurations.ksdk_debug

        return setup_logger(
            log_color=log_color,
            verbose=verbose,
            debug=debug,
            history_file=ksdk_history_file_path,
        )

    # Global KSDK Configurations
    def global_configuration_list(self, should_display: bool = False) -> OperationResponse:
        """
        List all available configurations for the Kelvin-SDK

        Parameters
        ----------
        should_display: bool, default=True
            specifies whether or not the display should output data.

        Returns
        -------
        OperationResponse
            An OperationResponse object encapsulating the yielded Kelvin tool configurations.
        """

        try:
            global_ksdk_configuration = self.get_global_ksdk_configuration()
            descriptions = global_ksdk_configuration.kelvin_sdk.configurations.descriptions
            private_fields = global_ksdk_configuration.kelvin_sdk.configurations.private_fields

            data = [v for k, v in descriptions.items() if k not in private_fields]

            display_obj = display_data_entries(
                data=data,
                header_names=["Variable", "Description", "Current Value"],
                attributes=["env", "description", "current_value"],
                table_title=GeneralConfigs.table_title.format(title="Environment Variables"),
                should_display=should_display,
            )
            set_unset_command = success_colored_message("kelvin configuration set/unset")
            logger.info(f"See {set_unset_command} for more details on how to configure this tool.")
            return OperationResponse(success=True, data=display_obj.parsed_data)

        except Exception as exc:
            error_message = f"Error retrieving environment variable configurations: {str(exc)}"
            logger.exception(error_message)
            return OperationResponse(success=False, log=error_message)

    def global_configuration_set(self, configuration: str, value: str) -> OperationResponse:
        """Set the specified configuration on the platform system.

        Parameters
        ----------
        configuration: str
            the configuration to change.
        value: str
            the value that corresponds to the provided configuration.
        Returns
        -------
        OperationResponse
            An OperationResponse object encapsulating the result the configuration set operation.
        """
        try:
            global_ksdk_configuration = self.get_global_ksdk_configuration()
            global_ksdk_configuration.set_configuration(configuration=configuration, value=value)
            success_message = f'Successfully set "{configuration}" to "{value}"'
            logger.relevant(success_message)
            return OperationResponse(success=True, log=success_message)
        except Exception as exc:
            error_message = f"Error setting configuration variable: {str(exc)}"
            logger.exception(error_message)
            return OperationResponse(success=False, log=error_message)

    def global_configuration_unset(self, configuration: str) -> OperationResponse:
        """Unset the specified configuration from the platform system

        Parameters
        ----------
        configuration: str
            the configuration to unset.

        Returns
        -------
        OperationResponse
            an OperationResponse object encapsulating the result the configuration unset operation.
        """
        try:
            global_ksdk_configuration = self.get_global_ksdk_configuration()
            global_ksdk_configuration.unset_configuration(configuration=configuration)
            success_message = f'Successfully unset "{configuration.lower()}"'
            logger.relevant(success_message)
            return OperationResponse(success=True, log=success_message)
        except Exception as exc:
            error_message = f"Error un-setting configuration variable: {str(exc)}"
            logger.exception(error_message)
            return OperationResponse(success=False, log=error_message)


session_manager: SessionManager = SessionManager()
