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

import time
from datetime import datetime
from typing import List, Optional, cast

import yaml

from kelvin.api.client import Client
from kelvin.api.client.error import APIError
from kelvin.api.client.model.requests import (
    LegacyWorkloadDeploy,
    WorkloadCreate,
    WorkloadsDelete,
    WorkloadsStart,
    WorkloadsStop,
    WorkloadUpdate,
)
from kelvin.api.client.model.responses import WorkloadLogsGet as WorkloadLogs
from kelvin.api.client.model.type import Workload, WorkloadStatus
from kelvin.config.parser import AppConfigObj, parse_config_file
from kelvin.sdk.lib.configs.general_configs import GeneralConfigs, GeneralMessages
from kelvin.sdk.lib.exceptions import AppException
from kelvin.sdk.lib.models.generic import KPath
from kelvin.sdk.lib.models.ksdk_docker import DockerImageName
from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.models.types import StatusDataSource
from kelvin.sdk.lib.models.workloads.ksdk_workload_deployment import WorkloadDeploymentRequest, WorkloadUpdateRequest
from kelvin.sdk.lib.schema.schema_manager import validate_app_schema_from_app_config_file
from kelvin.sdk.lib.session.session_manager import session_manager
from kelvin.sdk.lib.utils.display_utils import (
    DisplayObject,
    display_data_entries,
    display_data_object,
    display_yes_or_no_question,
    error_colored_message,
    success_colored_message,
    warning_colored_message,
)
from kelvin.sdk.lib.utils.exception_utils import retrieve_error_message_from_api_exception
from kelvin.sdk.lib.utils.general_utils import get_datetime_as_human_readable
from kelvin.sdk.lib.utils.logger_utils import logger


def workload_list(
    query: Optional[str] = None,
    node_name: Optional[str] = None,
    app_name: Optional[str] = None,
    source: StatusDataSource = StatusDataSource.CACHE,
    should_display: bool = False,
) -> OperationResponse:
    """
    Returns the list of workloads filtered any of the arguments.

    Parameters
    ----------
    query: Optional[str]
        the query to search for.
    node_name : Optional[str]
        the name of the node to filter the workloads.
    app_name : Optional[str]
        the name of the app to filter the workloads.
    source : StatusDataSource
        the status data source from where to obtain data.
    should_display : bool
        specifies whether or not the display should output data.

    Returns
    -------
    OperationResponse
        An OperationResponse object encapsulating the workloads available on the platform.
    """
    try:
        workload_list_step_1 = "Retrieving workloads.."
        if query:
            workload_list_step_1 = f'Searching workloads that match "{query}"'

        logger.info(workload_list_step_1)

        if app_name:
            app_name_with_version = DockerImageName.parse(name=app_name)
            app_name = app_name_with_version.name
            app_version = app_name_with_version.version
        else:
            app_name = None
            app_version = None

        display_obj = retrieve_workload_and_workload_status_data(
            query=query,
            app_name=app_name,
            app_version=app_version,
            node_name=node_name,
            source=source,
            should_display=should_display,
        )

        return OperationResponse(success=True, data=display_obj.parsed_data)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error retrieving workloads: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error retrieving workloads: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def workload_show(workload_name: str, source: StatusDataSource, should_display: bool = False) -> OperationResponse:
    """
    Show the details of the specified workload.

    Parameters
    ----------
    workload_name: str
        the name of the workload.
    source: StatusDataSource
        the status data source from where to obtain data.
    should_display: bool
        specifies whether or not the display should output data.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the yielded workload and its data.

    """
    try:
        workload_show_step_1 = f'Retrieving workload details for "{workload_name}"'
        base_table_title = GeneralConfigs.table_title.format(title="Workload Info")
        status_table_title = GeneralConfigs.table_title.format(title="Workload Status")

        logger.info(workload_show_step_1)

        client = session_manager.login_client_on_current_url()

        workload = client.app_workloads.get_workload(workload_name=workload_name)
        workload_status = {
            "name": workload.name,
            "status": workload.status.dict() if workload.status else GeneralMessages.no_data_available,
        }

        workload_display = display_data_object(data=workload, should_display=False, object_title=base_table_title)
        workload_status_display = display_data_object(
            data=workload_status, should_display=False, object_title=status_table_title
        )

        if should_display:
            logger.info(f"{workload_display.tabulated_data}\n{workload_status_display.tabulated_data}")

        complete_workload_info = {}
        if workload_display:
            complete_workload_info["workload"] = workload_display.parsed_data
        if workload_status_display:
            complete_workload_info["workload_status"] = workload_status_display.parsed_data

        return OperationResponse(success=True, data=complete_workload_info)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error showing workload: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error showing workload: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def workload_deploy(deployment: WorkloadDeploymentRequest) -> OperationResponse:
    """
    Deploy a workload from the specified deploy request.

    Parameters
    ----------
    deployment: WorkloadDeploymentRequest
        the deployment object that encapsulates all the necessary parameters for deploy.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the workload deploy operation.

    """
    try:
        logger.info("Creating workload..")

        app_config: AppConfigObj = parse_config_file(deployment.app_config)
        client = session_manager.login_client_on_current_url()

        if app_config.is_legacy():
            logger.warning(
                """Deprecation warning: using old app.yaml configuration to deploy workloads.
            Please consider updating your application."""
                f"See: {session_manager.get_documentation_link_for_current_url()}"
            )

            if not deployment.cluster_name or not deployment.workload_name:
                raise AppException("Cluster name and workload name are required")

            app_config_file_path: KPath = KPath(deployment.app_config)
            loaded_app_config_object = app_config_file_path.read_yaml()
            validate_app_schema_from_app_config_file(app_config=loaded_app_config_object)

            if not deployment.quiet and loaded_app_config_object:
                logger.info("Application configuration successfully loaded")

            payload = LegacyWorkloadDeploy(
                app_name=app_config.name,
                app_version=app_config.version,
                cluster_name=deployment.cluster_name,
                name=deployment.workload_name,
                title=deployment.workload_title,
                payload=loaded_app_config_object,
            )
            result = client.deprecated_workload.deploy_legacy_workload(data=payload)
        else:
            if not deployment.runtime:
                raise AppException("Runtime config file is required")

            runtime = {}
            with open(deployment.runtime, "r", encoding="utf-8") as file:
                runtime = dict(yaml.safe_load(file))

            # setting app name/version if not set in runtime config
            runtime.setdefault("app_name", app_config.name)
            runtime.setdefault("app_version", app_config.version)

            # overriding options if set by cli
            if deployment.cluster_name:
                runtime.setdefault("cluster_name", deployment.cluster_name)
            if deployment.workload_name:
                runtime.setdefault("name", deployment.workload_name)
            if deployment.workload_title:
                runtime.setdefault("title", deployment.workload_title)

            payload = WorkloadCreate.parse_obj(runtime)  # type: ignore
            result = client.app_workloads.create_workload(data=payload)  # type: ignore

        success_message = ""
        if not deployment.quiet:
            success_message = f"""\n
                Workload "{result.name}" successfully deployed.
            """
            logger.relevant(success_message)

        return OperationResponse(success=True, log=success_message)
    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"API Error creating workload: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Unexpected error creating workload: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def workload_update(update_request: WorkloadUpdateRequest) -> OperationResponse:
    """
    Update an existing workload with the new parameters.

    Parameters
    ----------
    update: WorkloadDeploymentRequest
        the update object that encapsulates all the necessary parameters for deploy.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the workload update operation.

    """
    try:
        logger.info("Updating workload")
        app_config: AppConfigObj = parse_config_file(update_request.app_config)
        client = session_manager.login_client_on_current_url()

        # 1 - fetch the specified workload
        client = session_manager.login_client_on_current_url()
        workload = client.app_workloads.get_workload(workload_name=update_request.workload_name)

        if app_config.is_legacy():
            logger.warning(
                """Deprecation warning: using old app.yaml configuration to deploy workloads.
            Please consider updating your application."""
                f"See: {session_manager.get_documentation_link_for_current_url()}"
            )

            app_config_file_path: KPath = KPath(update_request.app_config)
            loaded_app_config_object = app_config_file_path.read_yaml()
            validate_app_schema_from_app_config_file(app_config=loaded_app_config_object)

            if not update_request.quiet and loaded_app_config_object:
                logger.info("Application configuration successfully loaded")

            payload = LegacyWorkloadDeploy(
                app_name=app_config.name,
                app_version=app_config.version,
                cluster_name=workload.cluster_name,
                name=update_request.workload_name,
                title=update_request.workload_title,
                payload=loaded_app_config_object,
            )
            client.deprecated_workload.deploy_legacy_workload(data=payload)
        else:
            if not update_request.runtime:
                raise AppException("Runtime config file is required")

            runtime = {}
            with open(update_request.runtime, "r", encoding="utf-8") as file:
                runtime = yaml.safe_load(file)

            payload = WorkloadUpdate.parse_obj(runtime)  # type: ignore
            payload.app_version = app_config.version
            payload.title = update_request.workload_title

            client.app_workloads.update_workload(workload_name=update_request.workload_name, data=payload)

        if not update_request.quiet:
            success_message = f"""\n
                Workload "{update_request.workload_name}" updated.
            """
            logger.relevant(success_message)
            return OperationResponse(success=True, log=success_message)
        else:
            return OperationResponse(success=False, log="Error updating workload")

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error updating workload: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error updating workload: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def workload_logs(
    workload_name: str, tail_lines: Optional[int], follow: bool, output_file: Optional[str] = None
) -> OperationResponse:
    """
    Show the logs of a deployed workload.

    Parameters
    ----------
    workload_name: str
        the name of the workload.
    tail_lines: str
        the number of lines to retrieve on the logs request.
    output_file: bool
        the file to output the logs into.
    follow: Optional[str]
        a flag that indicates whether it should trail the logs, constantly requesting for more logs.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the logs of the workload.

    """
    try:
        logger.info(f'Retrieving workload logs for "{workload_name}"')

        client = session_manager.login_client_on_current_url()

        _retrieve_workload_logs(
            client=client,
            workload_name=workload_name,
            since_time=None,
            tail_lines=tail_lines,
            output_file=output_file,
            follow=follow,
        )

        return OperationResponse(success=True)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error retrieving logs for workload: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error retrieving logs for workload: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def workload_undeploy(workload_name: str, ignore_destructive_warning: bool = False) -> OperationResponse:
    """
    Stop and delete a workload on the platform.

    Parameters
    ----------
    workload_name: str
        the name of the workload to be stopped and deleted.
    ignore_destructive_warning: bool
        indicates whether it should ignore the destructive warning.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the workload undeploy operation.

    """
    try:
        if not ignore_destructive_warning:
            workload_undeploy_confirmation: str = """
                This operation will remove the workload from the node.
                All workload local data will be lost.
            """
            ignore_destructive_warning = display_yes_or_no_question(workload_undeploy_confirmation)

        success_message = ""
        if ignore_destructive_warning:
            logger.info(f'Undeploying workload "{workload_name}"')

            client = session_manager.login_client_on_current_url()
            client.app_workloads.delete_workloads(data=WorkloadsDelete(workload_names=[workload_name]))

            success_message = f'Workload "{workload_name}" successfully undeployed'
            logger.relevant(success_message)

        return OperationResponse(success=True, log=success_message)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error undeploying workload: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error undeploying workload: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def workload_start(workload_name: str) -> OperationResponse:
    """
    Start the provided workload.

    Parameters
    ----------
    workload_name: str
        the workload to start on the platform.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the workload start operation.

    """
    try:
        logger.info(f'Starting workload "{workload_name}"')

        client = session_manager.login_client_on_current_url()
        client.app_workloads.start_workloads(WorkloadsStart(workload_names=[workload_name]))

        success_message = f'Workload "{workload_name}" successfully started'
        logger.relevant(success_message)

        return OperationResponse(success=True, log=success_message)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error starting workload: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error starting workload: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def workload_stop(workload_name: str, ignore_destructive_warning: bool = False) -> OperationResponse:
    """
    Stop the provided workload.

    Parameters
    ----------
    workload_name: str
        the workload to stop on the platform.
    ignore_destructive_warning: bool
        indicates whether it should ignore the destructive warning.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the workload stop operation.

    """
    try:
        if not ignore_destructive_warning:
            workload_stop_confirmation: str = """
                This operation will stop the workload from running in the node.
                Persistent data will be kept intact.
            """
            ignore_destructive_warning = display_yes_or_no_question(workload_stop_confirmation)

        success_message: str = ""
        if ignore_destructive_warning:
            logger.info(f'Stopping workload "{workload_name}"')

            client = session_manager.login_client_on_current_url()
            client.app_workloads.stop_workloads(WorkloadsStop(workload_names=[workload_name]))

            success_message = f'Workload "{workload_name}" successfully stopped'
            logger.relevant(success_message)

        return OperationResponse(success=True, log=success_message)

    except APIError as exc:
        api_error = retrieve_error_message_from_api_exception(api_error=exc)
        api_error_message = f"Error stopping workload: {api_error}"
        logger.error(api_error_message)
        return OperationResponse(success=False, log=api_error_message)

    except Exception as exc:
        error_message = f"Error stopping workload: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def retrieve_workload_and_workload_status_data(
    query: Optional[str] = None,
    app_name: Optional[str] = None,
    app_version: Optional[str] = None,
    node_name: Optional[str] = None,
    source: StatusDataSource = StatusDataSource.CACHE,
    should_display: bool = True,
) -> DisplayObject:
    """
    Centralize all calls to workloads.
    First, retrieve all workloads that match the provided criteria.
    Second, retrieve all workload status.
    Last, merge both results and yield the result.

    Parameters
    ----------
    node_name: Optional[str]
        the name of the node to filter the workloads.
    app_name: Optional[str]
        the name of the app to filter the workloads.
    app_version: Optional[str]
        the version of the app to filter the workloads.
    query: Optional[str]
        the query to query specific workloads.
    source: StatusDataSource
        the status data source from where to obtain data.
    should_display: bool
        if specified, will display the results of this retrieve operation.

    Returns
    -------
    DisplayObject
        a DisplayObject containing the workload and respective status data.

    """
    client = session_manager.login_client_on_current_url()

    app_names: Optional[List[str]] = [app_name] if app_name else None
    app_versions: Optional[List[str]] = [app_version] if app_version else None
    node_names: Optional[List[str]] = [node_name] if node_name else None
    search: Optional[List[str]] = [query] if query else None

    yielded_workloads = (
        cast(
            List,
            client.app_workloads.list_workloads(
                app_names=app_names,
                app_versions=app_versions,
                node_names=node_names,
                search=search,
            ),  # camouflaged
        )
        or []
    )

    data_to_display = _filter_workload_status_data(workloads=yielded_workloads)

    return display_data_entries(
        data=data_to_display,
        header_names=[
            "Name",
            "Title",
            "Cluster Name",
            "App Name",
            "App Version",
            "Workload Status",
            "Last Seen",
        ],
        attributes=[
            "name",
            "title",
            "cluster_name",
            "app_name",
            "app_version",
            "workload_status",
            "last_seen",
        ],
        table_title=GeneralConfigs.table_title.format(title="Workloads"),
        should_display=should_display,
        no_data_message="No workloads available",
    )


def _filter_workload_status_data(workloads: List[Workload]) -> List:
    """
    When provided with a list of workloads, filter the status to just include state and last_seen.

    Parameters
    ----------
    workloads: List[Workload]
        the list of workloads to combine.

    Returns
    -------
    List[]
    """
    return [
        {
            **workload,
            "workload_status": _get_parsed_workload_status(workload.status),
            "last_seen": (
                get_datetime_as_human_readable(workload.status.last_seen)
                if workload.status
                else GeneralMessages.no_data_available
            ),
        }
        for workload in workloads
    ]


def _retrieve_workload_logs(
    client: Client,
    workload_name: str,
    since_time: Optional[datetime],
    tail_lines: Optional[int],
    output_file: Optional[str],
    follow: bool = False,
) -> bool:
    """

    Parameters
    ----------
    client: Client
        the Kelvin SDK Client object used to retrieve data.
    workload_name: str
        the name of the workload.
    tail_lines: Optional[str]
        the number of lines to retrieve on the logs request.
    output_file: Optional[str]
        the file to output the logs into.
    follow: bool
        a flag that indicates whether it should trail the logs, constantly requesting for more logs.

    Returns
    -------
    bool
        a boolean indicating the end of the internal workload logs retrieval operation.

    """
    logs_for_workload: WorkloadLogs = client.app_workloads.get_workload_logs(
        workload_name=workload_name, since_time=since_time, tail_lines=tail_lines
    )

    file_path = KPath(output_file) if output_file else None

    if logs_for_workload.logs:
        for key, value in logs_for_workload.logs.items():
            log_strings = [entry for entry in value if entry]
            last_date = _extract_last_date_from_log_entries(entry=log_strings)
            entry_logs = "\n".join(log_strings)
            logger.info(entry_logs)
            # output to file
            if file_path:
                file_path.write_text(entry_logs)
            # if it should follow, return the recursive call
            if follow:
                time.sleep(10)
                return _retrieve_workload_logs(
                    client=client,
                    workload_name=workload_name,
                    since_time=last_date,
                    tail_lines=tail_lines,
                    output_file=output_file,
                    follow=follow,
                )
            # finish with success
            elif not follow and file_path:
                logger.info(f'Workload logs successfully written to "{str(file_path)}"')
    else:
        logger.warning(f'No workload logs available for "{workload_name}"')
    return True


def _extract_last_date_from_log_entries(entry: List) -> Optional[datetime]:
    """
    Retrieves the latest date from the provided list of logs.

    Parameters
    ----------
    entry: List
        the log entries to retrieve the data from.

    Returns
    -------
    Optional[str]
        a string containing the parsed datetime.

    """
    if entry:
        import re

        last_entry = entry[-1]
        match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d\+Z", last_entry)
        last_date = datetime.strptime(match.group(), "%Y-%m-%dT%H:%M:%S.%fZ") if match else None
        return last_date
    return None


def _get_parsed_workload_status(workload_status: Optional[WorkloadStatus] = None) -> str:
    """
    When provided with a WorkloadStatus, yield the message the message with the provided color schema and format.

    Parameters
    ----------
    workload_status_item: Optional[WorkloadStatus]
        the Workload status item containing all necessary information.

    Returns
    -------
    str
        a formatted string with the correct color schema.

    """
    message = GeneralMessages.no_data_available
    state = GeneralMessages.no_data_available

    if workload_status:
        message = workload_status.message or message
        state = str(workload_status.state or state)

    formatter_structure = {
        "running": success_colored_message,
        "deploying": warning_colored_message,
        "stopped": warning_colored_message,
        "pending_deploy": warning_colored_message,
        "pending_start": warning_colored_message,
        "failed": error_colored_message,
        "offline": error_colored_message,
    }
    formatter = formatter_structure.get(state)

    return formatter(message=message) if formatter else message
