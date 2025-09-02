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

import click
from click import Choice

from kelvin.sdk.lib.configs.general_configs import KSDKHelpMessages
from kelvin.sdk.lib.models.types import StatusDataSource
from kelvin.sdk.lib.utils.click_utils import ClickExpandedPath, KSDKCommand, KSDKGroup


@click.group(cls=KSDKGroup)
def workload() -> None:
    """Manage and view application workloads."""


@workload.command(cls=KSDKCommand)
@click.option("--cluster-name", type=click.STRING, required=False, help=KSDKHelpMessages.workload_list_node_name)
@click.option("--app-name", type=click.STRING, required=False, help=KSDKHelpMessages.workload_list_app_name)
@click.option("--source", type=Choice(StatusDataSource.as_list()), help=KSDKHelpMessages.status_source)
def list(cluster_name: str, app_name: str, source: str) -> bool:
    """List the workloads available on the platform."""
    from kelvin.sdk.interface import workload_list

    return workload_list(
        node_name=cluster_name,
        app_name=app_name,
        source=StatusDataSource(source),
        should_display=True,
    ).success


@workload.command(cls=KSDKCommand)
@click.argument("query", type=click.STRING, nargs=1, required=False)
@click.option("--source", type=Choice(StatusDataSource.as_list()), help=KSDKHelpMessages.status_source)
def search(query: str, source: str) -> bool:
    """Search for specific workloads."""
    from kelvin.sdk.interface import workload_search

    if not query:
        query = input("Enter the name of the workload you want to search for: ")

    return workload_search(query=query, source=StatusDataSource(source), should_display=True).success


@workload.command(cls=KSDKCommand)
@click.argument("workload_name", type=click.STRING, nargs=1, required=False)
@click.option("--source", type=Choice(StatusDataSource.as_list()), help=KSDKHelpMessages.status_source)
def show(workload_name: str, source: str) -> bool:
    """Show the details of a specific workload."""
    from kelvin.sdk.interface import workload_show

    if not workload_name:
        workload_name = input("Enter the name of the workload you want to show: ")

    return workload_show(workload_name=workload_name, source=StatusDataSource(source), should_display=True).success


@workload.command(cls=KSDKCommand)
@click.option("--cluster-name", type=click.STRING, required=False, help=KSDKHelpMessages.workload_deploy_node_name)
@click.option("--workload-name", type=click.STRING, required=False, help=KSDKHelpMessages.workload_deploy_workload_name)
@click.option(
    "--workload-title",
    type=click.STRING,
    required=False,
    help=KSDKHelpMessages.workload_deploy_workload_title,
)
@click.option(
    "--app-config",
    type=ClickExpandedPath(exists=True),
    required=False,
    help=KSDKHelpMessages.workload_deploy_app_config,
)
@click.option(
    "--runtime",
    type=ClickExpandedPath(exists=True),
    required=False,
    help=KSDKHelpMessages.workload_deploy_runtime,
)
def deploy(
    cluster_name: Optional[str],
    workload_name: Optional[str],
    workload_title: Optional[str],
    app_config: Optional[str],
    runtime: Optional[str],
) -> bool:
    """Deploy a workload with specified parameters.

    e.g. kelvin apps workload deploy --cluster-name work-cluster --workload-name work-name --runtime runtime.yaml --app-config app.yaml

    """
    from kelvin.sdk.interface import workload_deploy
    from kelvin.sdk.lib.models.workloads.ksdk_workload_deployment import WorkloadDeploymentRequest

    if app_config is None:
        app_config = input("Enter the path to the app config file: ")

    workload_deployment_request = WorkloadDeploymentRequest(
        cluster_name=cluster_name,
        workload_name=workload_name,
        workload_title=workload_title,
        app_config=app_config,
        runtime=runtime,
    )

    return workload_deploy(workload_deployment_request=workload_deployment_request).success


@workload.command(cls=KSDKCommand)
@click.option("--workload-name", type=click.STRING, required=False, help=KSDKHelpMessages.workload_deploy_workload_name)
@click.option(
    "--workload-title",
    type=click.STRING,
    required=False,
    help=KSDKHelpMessages.workload_update_workload_title,
)
@click.option(
    "--app-config",
    type=ClickExpandedPath(exists=True),
    required=True,
    help=KSDKHelpMessages.workload_update_app_config,
)
@click.option(
    "--runtime",
    type=ClickExpandedPath(exists=True),
    required=False,
    help=KSDKHelpMessages.workload_deploy_runtime,
)
def update(
    workload_name: Optional[str],
    workload_title: Optional[str],
    app_config: Optional[str],
    runtime: Optional[str],
) -> bool:
    """Update a specific workload based with new configurations.

    e.g. kelvin apps workload update "my-workload" --app-config app.yaml

    """
    from kelvin.sdk.interface import workload_update
    from kelvin.sdk.lib.models.workloads.ksdk_workload_deployment import WorkloadUpdateRequest

    if workload_name is None:
        workload_name = input("Enter the name of the workload you want to deploy: ")
    if app_config is None:
        app_config = input("Enter the path to the app config file: ")

    update_request = WorkloadUpdateRequest(
        workload_name=workload_name,
        workload_title=workload_title,
        app_config=app_config,
        runtime=runtime,
    )
    return workload_update(update_request).success


@workload.command(cls=KSDKCommand)
@click.argument("workload_name", type=click.STRING, nargs=1, required=False)
@click.option(
    "--tail-lines",
    type=click.INT,
    required=False,
    default=200,
    show_default=True,
    help=KSDKHelpMessages.workload_logs_tail_lines,
)
@click.option("--output-file", type=click.STRING, required=False, help=KSDKHelpMessages.workload_logs_output_file)
@click.option("--follow", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.workload_logs_follow)
def logs(workload_name: str, tail_lines: int, output_file: str, follow: bool) -> bool:
    """Display the logs of a specific workload."""
    from kelvin.sdk.interface import workload_logs

    if not workload_name:
        workload_name = input("Enter the name of the workload you want to follow: ")

    return workload_logs(
        workload_name=workload_name, tail_lines=tail_lines, output_file=output_file, follow=follow
    ).success


@workload.command(cls=KSDKCommand)
@click.argument("workload_name", type=click.STRING, nargs=1, required=False)
@click.option("-y", "--yes", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.yes)
def undeploy(workload_name: str, yes: bool) -> bool:
    """Undeploy and delete a workload."""
    from kelvin.sdk.interface import workload_undeploy

    if not workload_name:
        workload_name = input("Enter the name of the workload you want to undeploy: ")

    return workload_undeploy(workload_name=workload_name, ignore_destructive_warning=yes).success


@workload.command(cls=KSDKCommand)
@click.argument("workload_name", type=click.STRING, nargs=1, required=False)
def start(workload_name: str) -> bool:
    """Start a workload on a node."""
    from kelvin.sdk.interface import workload_start

    if not workload_name:
        workload_name = input("Enter the name of the workload you want to start: ")

    return workload_start(workload_name=workload_name).success


@workload.command(cls=KSDKCommand)
@click.argument("workload_name", type=click.STRING, nargs=1, required=False)
@click.option("-y", "--yes", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.yes)
def stop(workload_name: str, yes: bool) -> bool:
    """Stop a running workload."""
    from kelvin.sdk.interface import workload_stop

    if not workload_name:
        workload_name = input("Enter the name of the workload you want to stop: ")

    return workload_stop(workload_name=workload_name, ignore_destructive_warning=yes).success
