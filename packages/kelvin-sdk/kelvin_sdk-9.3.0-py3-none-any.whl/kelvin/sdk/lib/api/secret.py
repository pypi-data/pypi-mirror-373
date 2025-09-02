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

from typing import List, Optional, Sequence, cast

from kelvin.api.client.error import APIError
from kelvin.api.client.model.requests import SecretCreate, SecretUpdate
from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.session.session_manager import session_manager
from kelvin.sdk.lib.utils.display_utils import display_data_entries, display_yes_or_no_question
from kelvin.sdk.lib.utils.exception_utils import retrieve_error_message_from_api_exception
from kelvin.sdk.lib.utils.logger_utils import logger


def secret_create(secret_name: str, value: str) -> OperationResponse:
    """
    Create a secret on the platform.

    Parameters
    ----------
    secret_name: str
        The name of the secret to create.
    value: str
        The value corresponding to the secret.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the secrets creation operation.

    """
    try:
        logger.info(f'Creating secret "{secret_name}" on the platform')

        client = session_manager.login_client_on_current_url()

        secret_create_request = SecretCreate(name=secret_name, value=value)

        client.secret.create_secret(data=secret_create_request)

        success_message = f'Secret "{secret_name}" successfully created on the platform'
        logger.relevant(success_message)

        return OperationResponse(success=True, log=success_message)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error creating secret: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error creating secret: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def secret_list(query: Optional[str], should_display: bool = False) -> OperationResponse:
    """
    List all the available secrets on the Platform.

    Parameters
    ----------
    query: Optional[str]
        The query to filter the secrets by.
    should_display: bool
        specifies whether or not the display should output data.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the secrets available on the platform.

    """
    try:
        logger.info("Retrieving platform secrets..")

        client = session_manager.login_client_on_current_url()

        yielded_secrets = cast(List, client.secret.list_secrets(search=query)) or []

        display_data = display_data_entries(
            data=yielded_secrets,
            header_names=["Secret name"],
            attributes=["name"],
            table_title=GeneralConfigs.table_title.format(title="Secrets"),
            should_display=False,
            no_data_message="No secrets available",
        )

        if should_display and display_data:
            logger.info(f"{display_data.tabulated_data}")

        return OperationResponse(success=True, data=display_data.parsed_data)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error retrieving secrets: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error retrieving secrets: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def secret_delete(secret_names: Sequence[str], ignore_destructive_warning: bool = False) -> OperationResponse:
    """
    Delete secrets on the platform.

    Parameters
    ----------
    secret_names: Sequence[str]
        The names of the secrets to delete.
    ignore_destructive_warning: bool
        indicates whether it should ignore the destructive warning.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the secrets deletion operation.

    """
    secrets_description = ", ".join(secret_names)
    logger.info(f'Deleting secret(s) "{secrets_description}" from the platform')

    prompt_question = f'This operation will delete the secret(s) "{secrets_description}" from the platform'
    if not ignore_destructive_warning:
        ignore_destructive_warning = display_yes_or_no_question(question=prompt_question)

    if ignore_destructive_warning:
        client = session_manager.login_client_on_current_url()

        for secret_name in secret_names:
            try:
                client.secret.delete_secret(secret_name=secret_name)
                logger.relevant(f'Secret "{secret_name}" successfully deleted from the platform')

            except APIError as exc:
                api_error = retrieve_error_message_from_api_exception(api_error=exc)
                api_error_message = f"Error deleting secret: {api_error}"
                logger.error(api_error_message)
                return OperationResponse(success=False, log=api_error_message)

            except Exception as exc:
                error_message = f"Error deleting secret: {str(exc)}"
                logger.exception(error_message)
                return OperationResponse(success=False, log=error_message)

    return OperationResponse(success=True, log="Successfully deleted secrets")


def secret_update(secret_name: str, value: str) -> OperationResponse:
    """
    Update an existing secret on the platform.

    Parameters
    ----------
    secret_name: str
        The name of the secret to update.
    value: str
        The new value for the secret.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the secret update operation.
    """
    try:
        logger.info(f'Updating secret "{secret_name}" on the platform')

        client = session_manager.login_client_on_current_url()

        secret_update_request = SecretUpdate(value=value)
        client.secret.update_secret(secret_name=secret_name, data=secret_update_request)

        success_message = f'Secret "{secret_name}" successfully updated on the platform'
        logger.relevant(success_message)
        return OperationResponse(success=True, log=success_message)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error updating secret: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error updating secret: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)
