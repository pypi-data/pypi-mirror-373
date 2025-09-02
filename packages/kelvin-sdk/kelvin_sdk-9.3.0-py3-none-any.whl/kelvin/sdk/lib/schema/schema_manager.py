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
from json import JSONDecodeError
from typing import Any, Dict, Optional, Tuple

import jsonschema
import requests
from jsonschema import RefResolver
from yaml.parser import ParserError

from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.configs.schema_manager_configs import SchemaManagerConfigs
from kelvin.sdk.lib.exceptions import InvalidApplicationConfiguration, InvalidSchemaVersionException
from kelvin.sdk.lib.models.apps.ksdk_app_configuration import ApplicationFlavour, ProjectType
from kelvin.sdk.lib.models.apps.ksdk_app_setup import ProjectCreationParametersObject
from kelvin.sdk.lib.models.generic import KPath
from kelvin.sdk.lib.models.ksdk_docker import DockerImageName
from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.models.types import VersionStatus
from kelvin.sdk.lib.session.session_manager import session_manager
from kelvin.sdk.lib.utils.logger_utils import logger
from kelvin.sdk.lib.utils.version_utils import assess_version_status

_RESOLVER = RefResolver("https://apps.kelvininc.com/schemas/kelvin/", {})


def generate_base_schema_template(project_creation_parameters_object: ProjectCreationParametersObject) -> dict:
    """
    Generate the base schema template.
    Attempt to retrieve the latest schema version and generate the default from it.

    Parameters
    ----------
    project_creation_parameters_object : ProjectCreationParametersObject
        the app creation parameters object used to generate the default schema.

    Returns
    -------
    dict
        A dict containing the default app creation object.

    """
    latest_schema_version, latest_schema_contents, latest_schema_path = get_latest_app_schema_version()

    app_type_obj: Dict[str, Any] = {"type": project_creation_parameters_object.app_type.app_type_on_config()}

    if project_creation_parameters_object.app_type == ProjectType.kelvin:
        language_block = {"type": project_creation_parameters_object.kelvin_app_lang.value}
        language_block.update(project_creation_parameters_object.get_language_block())
        # 2 - Create the interface block
        app_type_obj.update(
            {
                "kelvin": {
                    "language": language_block,
                    "inputs": [],
                    "outputs": [],
                    "configuration": {},
                    "parameters": [],
                }
            }
        )

    elif project_creation_parameters_object.app_type == ProjectType.bridge:
        language_block = {"type": project_creation_parameters_object.kelvin_app_lang.value}
        language_block.update(project_creation_parameters_object.get_language_block())
        app_type_obj.update(
            {
                "bridge": {
                    "logging_level": "INFO",
                    "language": language_block,
                    "configuration": {},
                    "metrics_map": [],
                }
            }
        )
    else:
        app_type_obj.update(
            {
                "docker": {
                    "dockerfile": "Dockerfile",
                    "context": ".",
                    "args": [],
                }
            }
        )
    creation_object = {
        "spec_version": latest_schema_version,
        "info": {
            "name": project_creation_parameters_object.app_name,
            "title": project_creation_parameters_object.app_name,
            "version": project_creation_parameters_object.app_version,
            "description": project_creation_parameters_object.app_description
            or project_creation_parameters_object.app_name,
        },
        "app": app_type_obj,
    }

    _validate_schema(content=creation_object, schema=latest_schema_contents)

    return creation_object


def build_kelvin_app_block(project_creation_parameters_object: ProjectCreationParametersObject) -> dict:
    """Creates the app configuration for the kelvin apps

    Parameters
    ----------
    project_creation_parameters_object : ProjectCreationParametersObject
        the app creation parameters object used to generate the default schema.

    Returns
    -------
    dict
        The schema app block for kelvin apps

    """
    # 1 - Create the language block
    language_block = {"type": project_creation_parameters_object.kelvin_app_lang.value}
    language_block.update(project_creation_parameters_object.get_language_block())
    # 2 - Create the interface block
    kelvin_block = {"language": language_block}

    # add mqtt config if flavour is pubsub
    if project_creation_parameters_object.app_flavour is ApplicationFlavour.pubsub:
        broker_name = session_manager.get_current_session_metadata().sdk.components.kelvin_broker
        kelvin_broker_container = DockerImageName.parse(name=broker_name)
        kelvin_block.update(
            {
                "outputs": [  # type: ignore
                    {"name": "bar", "data_type": "raw.float32", "targets": [{"asset_names": ["some-asset"]}]}
                ],
                "mqtt": {
                    "ip": kelvin_broker_container.container_name,
                    "port": GeneralConfigs.default_mqtt_port,  # type: ignore
                },
            }
        )

    return {
        "kelvin": kelvin_block,
    }


def validate_app_schema_from_app_config_file(
    app_config: Optional[Dict] = None, app_config_file_path: Optional[KPath] = None
) -> bool:
    """
    When provided with an app configuration file, retrieve the schema for that version and validate it.

    Parameters
    ----------
    app_config : Optional[Dict]
        the alternative app configuration to the app_config_file_path.
    app_config_file_path : Optional[KPath]
        the path to the app configuration.

    Returns
    -------
    bool
        A boolean indicating whether or not the schema complies with the provided spec.
    """
    app_config_content: dict = {}

    if app_config:
        app_config_content = app_config

    if not app_config_content and app_config_file_path:
        app_config_content = app_config_file_path.read_yaml()

    if not app_config_content:
        raise InvalidApplicationConfiguration()

    spec_version: str = ""  # We may need to force an update of the schema.. todo

    # Check if we have a provided schema that has been shipped with KSDK
    latest_schema_contents, _ = _get_shipped_schema()
    if not latest_schema_contents:
        # Retrieve the current spec version, the minimum and latest values
        try:
            spec_version = app_config_content.get("spec_version", "")
            current_session_metadata = session_manager.get_current_session_metadata()
            min_schema_version, latest_schema_version = current_session_metadata.get_min_and_latest_schema_versions()
            version_status = assess_version_status(
                current_version=spec_version, minimum_version=min_schema_version, latest_version=latest_schema_version
            )
            if version_status == VersionStatus.UNSUPPORTED:
                raise InvalidSchemaVersionException(
                    min_version=min_schema_version, current_version=spec_version, latest_version=latest_schema_version
                )
        except InvalidSchemaVersionException:
            raise
        except Exception:
            logger.warning("No spec version defined. Proceeding with the latest schema version")

        latest_schema_contents, _ = _get_and_persist_app_schema(
            schema_url=SchemaManagerConfigs.general_app_schema_url, schema_version=spec_version
        )

    return _validate_schema(content=app_config_content, schema=latest_schema_contents)


def schema_validate(
    file_path: str, schema_file_path: Optional[str], full_schema_errors: bool = True
) -> OperationResponse:
    """
    Validate a file against a schema.

    Parameters
    ----------
    file_path : str
        The path to the file to validate.
    schema_file_path : Optional[str]
        The path to the schema file to validate the file against.
    full_schema_errors : bool
        Indicates whether or not it should log the complete stack trace.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the file schema validation.

    """
    try:
        file_path_object: KPath = KPath(file_path)
        if not file_path_object.exists():
            raise ValueError("The provided file does not exist.")

        schema_file_path_object: Optional[KPath] = KPath(schema_file_path) if schema_file_path else None
        if schema_file_path_object and schema_file_path_object.exists():
            schema_content = schema_file_path_object.read_yaml()
        else:
            _, schema_content, _ = get_latest_app_schema_version()

        file_content = file_path_object.read_yaml()
        validation_result = _validate_schema(content=file_content, schema=schema_content)

        success_message = "The provided file complies with the schema."
        logger.relevant(success_message)

        return OperationResponse(success=validation_result, log=success_message)

    except (jsonschema.exceptions.ValidationError, jsonschema.exceptions.SchemaError) as exc:
        error_message = exc.message
        if full_schema_errors:
            error_message = f"Error validating schema: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)
    except ParserError:
        error_message = "Invalid file format: Cannot parse yaml content"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)
    except Exception as exc:
        error_message = f"Error validating schema: {exc}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def schema_get(schema_file_path: Optional[str] = None) -> OperationResponse:
    """

    Yield the the content of a schema.

    Parameters
    ----------
    schema_file_path : Optional[str]
        The path to the schema file to yield.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the file schema validation.
    """
    try:
        schema_contents: dict = {}

        if schema_file_path:
            path_schema_file_path: KPath = KPath(schema_file_path.strip('"')).complete_path()
            if path_schema_file_path.exists():
                schema_contents = path_schema_file_path.read_yaml()
            else:
                raise InvalidApplicationConfiguration(message="Please provide a valid file")
        else:
            _, schema_contents, _ = get_latest_app_schema_version()
        return OperationResponse(success=True, data=schema_contents)
    except Exception as exc:
        error_message = f"Error retrieving the schema: {exc}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def get_latest_app_schema_version() -> Tuple[str, dict, KPath]:
    """
    Retrieve the latest app schema version and persist it to the configured schema directory.

    Returns
    -------
    A Tuple containing:
        1) latest spec version
        2) the corresponding schema
        3) the path to the persisted schema.

    """

    if session_manager.auth_code:
        logger.info("Retrieving the latest schema version")

        _, latest_schema_version = session_manager.get_current_session_metadata().get_min_and_latest_schema_versions()

        latest_schema_contents, latest_schema_file_path = _get_and_persist_app_schema(
            schema_url=SchemaManagerConfigs.general_app_schema_url, schema_version=latest_schema_version
        )
        return latest_schema_version, latest_schema_contents, latest_schema_file_path

    logger.info("Retrieving the included schema version")
    contents, path = _get_shipped_schema()
    id = contents.get("$id", "")
    if id:
        version = id.split("/")[-3]
        return version, contents, path
    else:
        raise InvalidApplicationConfiguration(message="Failed to identify the release schema")


def _validate_schema(
    content: dict,
    schema: Optional[dict] = None,
    schema_path: Optional[KPath] = None,
    resolver: RefResolver = _RESOLVER,
) -> bool:
    """
    Validate a specific content against a schema.

    Parameters
    ----------
    content : dict
        the content to validate.
    schema : Optional[dict]
        the schema, as a dict, to validate the content against.
    schema_path : Optional[KPath]
        the path to the schema to validate the content against.
    resolver: RefResolver
        optional resolver to override schema component cache

    Returns
    -------
    bool
        A bool indicating whether the provided content is valid.
    """
    schema_content = {}

    if schema:
        schema_content = schema

    if not schema_content and schema_path:
        logger.debug(f'Loading schema from "{schema_path}"')
        schema_content = json.loads(schema_path.read_text())

    if not schema_content:
        raise InvalidApplicationConfiguration(message="Please provide a valid schema")

    jsonschema.validate(instance=content, schema=schema_content, resolver=resolver)

    logger.debug("Provided content successfully validated against the schema")
    return True


def _get_shipped_schema() -> Tuple[dict, KPath]:
    """
    Attempt to retrieve the specified schema/version combination from the included schema.

    Parameters
    ----------
    None

    Returns
    -------
    Tuple[dict, KPath]
        A Tuple containing both the included schema contents and the path to its persisted file.
    """
    schema_contents: dict = {}

    schema_file_path = _get_shipped_schema_file_path()
    try:
        schema_contents = schema_file_path.read_json()
    except JSONDecodeError:
        schema_contents = {}

    return schema_contents, schema_file_path


def _get_and_persist_app_schema(schema_url: str, schema_version: str) -> Tuple[dict, KPath]:
    """
    Attempt to retrieve the specified schema/version combination from the platform.
    Persist said combination in the default directory

    Parameters
    ----------
    schema_url : str
        the url to retrieve the schema from.
    schema_version : str
        the latest schema version.

    Returns
    -------
    Tuple[dict, KPath]
        A Tuple containing both the latest schema contents and the path to its persisted file.
    """
    schema_contents: dict = {}

    schema_file_path = _get_schema_version_file_path(schema_version=schema_version)

    # 1 - If there's already a cached version, use it
    if schema_file_path and schema_file_path.exists():
        logger.info(f"Valid schema available locally. Using cached version ({schema_file_path})")
        try:
            schema_contents = schema_file_path.read_json()
        except JSONDecodeError:
            schema_contents = {}

    # 2 - If not, fetch it and persist it
    if not schema_contents:
        schema_contents = _fetch_app_schema_from_url(schema_url=schema_url, schema_version=schema_version)
        schema_file_path.write_json(content=schema_contents)

    # 3 - Yield both the schema contents
    return schema_contents, schema_file_path


def _fetch_app_schema_from_url(schema_url: str, schema_version: str) -> Dict:
    """
    Fetch the targeted schema version from the provided schema url.

    Parameters
    ----------
    schema_url : str
        the url to retrieve the schema from.
    schema_version : str
        the latest schema version.

    Returns
    -------
    The latest schema contents of the platform.

    """
    specific_app_schema_response = requests.get(
        schema_url.format(version=schema_version), timeout=SchemaManagerConfigs.request_timeout
    )

    if specific_app_schema_response.status_code != 200:
        raise InvalidApplicationConfiguration(message=f'Invalid schema version "{schema_version}"')

    return specific_app_schema_response.json()


def _get_schema_version_file_path(schema_version: str) -> KPath:
    """
    Centralize all calls to get the ksdk schemas directory path.

    Parameters
    ----------
    schema_version : str
        The version corresponding to the generated schema file path.

    Returns
    -------
    KPath
        The KPath of the specific schema file.
    """
    schema_storage_path: KPath = session_manager.get_global_ksdk_configuration().ksdk_schema_dir_path
    return KPath(schema_storage_path / f"{schema_version}.json").complete_path()


def _get_shipped_schema_file_path() -> KPath:
    """
    Centralize all calls to get the ksdk schemas directory path.

    Parameters
    ----------
    None

    Returns
    -------
    KPath
        The KPath of the specific schema file.
    """
    from importlib_resources import files as importlib_resources_files

    res = importlib_resources_files("kelvin.sdk.release_schema").joinpath("release.json")
    return KPath(res)
