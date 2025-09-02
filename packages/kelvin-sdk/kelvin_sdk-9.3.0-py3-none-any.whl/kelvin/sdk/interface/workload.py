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

from typing import Optional

from typeguard import typechecked

from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.models.types import StatusDataSource
from kelvin.sdk.lib.models.workloads.ksdk_workload_deployment import WorkloadDeploymentRequest, WorkloadUpdateRequest


@typechecked
def workload_list(
    node_name: Optional[str] = None,
    app_name: Optional[str] = None,
    source: StatusDataSource = StatusDataSource.CACHE,
    should_display: bool = False,
) -> OperationResponse:
    """
    Returns the list of workloads filtered any of the arguments.

    Parameters
    ----------
    node_name : Optional[str]
        the name of the node to filter the workloads.
    app_name : Optional[str]
        the name of the app to filter the workloads.
    enabled : bool, Default=None
        indicates whether it should filter workloads by their status.
    source : StatusDataSource, Default=StatusDataSource.CACHE
        the status data source from where to obtain data.
    should_display : bool, Default=False
        specifies whether or not the display should output data.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        An OperationResponse object encapsulating the workloads available on the platform.
    """
    from kelvin.sdk.lib.api.app_workloads import workload_list as _workload_list

    return _workload_list(
        node_name=node_name,
        app_name=app_name,
        source=source,
        should_display=should_display,
    )


@typechecked
def workload_search(
    query: str, source: StatusDataSource = StatusDataSource.CACHE, should_display: bool = False
) -> OperationResponse:
    """
    Search for workloads matching the provided query.

    Parameters
    ----------
    query: str
        the query to search for.
    source: StatusDataSource, Default=StatusDataSource=StatusDataSource.CACHE
        the status data source from where to obtain data.
    should_display: bool, Default=False
        specifies whether or not the display should output data.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the workload search on the platform.

    """
    from kelvin.sdk.lib.api.app_workloads import workload_list as _workload_list

    return _workload_list(query=query, source=source, should_display=should_display)


@typechecked
def workload_show(
    workload_name: str, source: StatusDataSource = StatusDataSource.CACHE, should_display: bool = False
) -> OperationResponse:
    """
    Show the details of the specified workload.

    Parameters
    ----------
    workload_name: str
        the name of the workload.
    source: Default=StatusDataSource=StatusDataSource.CACHE
        the status data source from where to obtain data.
    should_display: bool, Default=False
        specifies whether or not the display should output data.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the yielded workload and its data.

    """
    from kelvin.sdk.lib.api.app_workloads import workload_show as _workload_show

    return _workload_show(workload_name=workload_name, source=source, should_display=should_display)


@typechecked
def workload_deploy(workload_deployment_request: WorkloadDeploymentRequest) -> OperationResponse:
    """
    Deploy a workload from the specified deploy request.

    Parameters
    ----------
    workload_deployment_request: WorkloadDeploymentRequest
        the deployment object that encapsulates all the necessary parameters for deploy.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the workload deploy operation.

    """
    from kelvin.sdk.lib.api.app_workloads import workload_deploy as _workload_deploy

    return _workload_deploy(deployment=workload_deployment_request)


@typechecked
def workload_update(update_request: WorkloadUpdateRequest) -> OperationResponse:
    """
    Update an existing workload with the new parameters.

    Parameters
    ----------
    workload_name: str
        the name for the workload to update.
    workload_title: Optional[str]
        the title for the  workload.
    app_config: str
        the path to the app configuration file.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the workload update operation.

    """
    from kelvin.sdk.lib.api.app_workloads import workload_update as _workload_update

    return _workload_update(update_request)


@typechecked
def workload_logs(workload_name: str, tail_lines: int, output_file: Optional[str], follow: bool) -> OperationResponse:
    """
    Show the logs of a deployed workload.

    Parameters
    ----------
    workload_name: str
        the name of the workload.
    tail_lines: int
        the number of lines to retrieve on the logs request.
    output_file: Optional[str]
        the file to output the logs into.
    follow: bool
        a flag that indicates whether it should trail the logs, constantly requesting for more logs.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the logs of the workload.

    """
    from kelvin.sdk.lib.api.app_workloads import workload_logs as _workload_logs

    return _workload_logs(workload_name=workload_name, tail_lines=tail_lines, output_file=output_file, follow=follow)


@typechecked
def workload_undeploy(workload_name: str, ignore_destructive_warning: bool) -> OperationResponse:
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
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the workload undeploy operation.

    """
    from kelvin.sdk.lib.api.app_workloads import workload_undeploy as _workload_undeploy

    return _workload_undeploy(workload_name=workload_name, ignore_destructive_warning=ignore_destructive_warning)


@typechecked
def workload_start(workload_name: str) -> OperationResponse:
    """
    Start the provided workload.

    Parameters
    ----------
    workload_name: str
        the workload to start on the platform.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the workload start operation.

    """
    from kelvin.sdk.lib.api.app_workloads import workload_start as _workload_start

    return _workload_start(workload_name=workload_name)


@typechecked
def workload_stop(workload_name: str, ignore_destructive_warning: bool) -> OperationResponse:
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
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the workload stop operation.

    """
    from kelvin.sdk.lib.api.app_workloads import workload_stop as _workload_stop

    return _workload_stop(workload_name=workload_name, ignore_destructive_warning=ignore_destructive_warning)
