import json

from keycloak.exceptions import KeycloakError

from kelvin.api.client.error import APIError


def retrieve_error_message_from_api_exception(api_error: APIError) -> str:
    """Returns the 'pretty' error message from the APIError.

    Parameters
    ----------
    api_error : APIError
         The exception yielded by the service call.

    Returns
    -------
    str:
        a string containing the error message of the APIError.

    """
    try:
        if api_error.response.status_code == 403:
            return "You don’t have the required permissions to execute this command. Please contact your system administrator."

        return f"(API error {api_error.response.status_code})\n{api_error}"
    except Exception as exc:
        return f"Error retrieving APIError - {str(exc)}"


def retrieve_error_message_from_keycloak_exception(keycloak_exception: KeycloakError) -> str:
    """Returns the 'pretty' error message from the KeycloakError.

    Parameters
    ----------
    keycloak_exception : KeycloakError
        The exception yielded by the service call.

    Returns
    -------
    str:
        a string containing the error message of the KeycloakError.

    """
    try:
        try:
            message = json.loads(keycloak_exception.error_message)
        except (UnicodeDecodeError, AttributeError):
            message = {"error_description": "Error retrieving KeyCloak exception"}

        return f"(Authentication API error) {message.get('error_description')}"

    except Exception as exc:
        return f"Error handling KeycloakError exception - {str(exc)}"
