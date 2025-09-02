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

from typing import Dict, List

import click

from kelvin.sdk.lib.configs.general_configs import KSDKHelpMessages
from kelvin.sdk.lib.utils.click_utils import AppNameWithVersionType, KSDKCommand, KSDKGroup


@click.group(cls=KSDKGroup)
def apps() -> None:
    """Manage platform Applications."""


@apps.command(cls=KSDKCommand)
def list() -> bool:
    """List all the available applications on the platform's Application registry."""
    from kelvin.sdk.interface import apps_list

    return apps_list(should_display=True).success


@apps.command(cls=KSDKCommand)
@click.argument("query", type=click.STRING, nargs=1, required=False)
def search(query: str) -> bool:
    """Search for specific apps on the platform's Application Registry.

    e.g. kelvin apps search "my-app"

    """
    from kelvin.sdk.interface import apps_search

    if query is None:
        query = input("Enter the name of the app you want to search for: ")

    return apps_search(query=query, should_display=True).success


@apps.command(cls=KSDKCommand)
@click.argument("name", type=click.STRING, nargs=1, required=False)
def show(name: str) -> bool:
    """Show the platform details and configurations for a specific application.

    e.g. kelvin apps show "example-app"

    e.g. kelvin apps show "example-app:1.0.0"

    """
    from kelvin.sdk.interface import apps_show

    if name is None:
        name = input("Enter the name of the app you want to show: ")

    return apps_show(app_name=name, should_display=True).success


@apps.command(cls=KSDKCommand)
@click.option(
    "--app-dir",
    type=click.Path(exists=True),
    required=False,
    default=".",
    help=KSDKHelpMessages.app_dir,
)
@click.option("--build-arg", type=str, multiple=True, help="docker build-args", default=[])
@click.option(
    "--multiarch",
    type=str,
    default="amd64",
    show_default=True,
    help=KSDKHelpMessages.app_build_multiarch,
)
def upload(app_dir: str, build_arg: List[str], multiarch: str) -> bool:
    """Upload an application to the platform's Application Registry.

    e.g. kelvin apps upload --app-dir="."
    """
    from kelvin.sdk.interface import apps_upload

    build_args_dict: Dict[str, str] = dict(x.split("=") for x in build_arg)  # type: ignore

    requested_archs = multiarch.split(",")

    return apps_upload(app_dir=app_dir, build_args=build_args_dict, archs=requested_archs).success


@apps.command(cls=KSDKCommand)
@click.argument("app_name_with_version", nargs=1, type=AppNameWithVersionType(version_required=False))
@click.option(
    "--override-local-tag",
    default=False,
    is_flag=True,
    show_default=True,
    help=KSDKHelpMessages.apps_download_override_local_tag,
)
@click.option(
    "--tag-local-name/--no-tag-local-name",
    default=True,
    show_default=True,
    help=KSDKHelpMessages.apps_download_tag_local_name,
)
def download(app_name_with_version: str, override_local_tag: bool, tag_local_name: bool) -> bool:
    """Download an application from the platform and make it available locally.\n

    e.g. kelvin apps download "example-app:1.0.0"
    """
    from kelvin.sdk.interface import apps_download

    return apps_download(
        app_name_with_version=app_name_with_version,
        override_local_tag=override_local_tag,
        tag_local_name=tag_local_name,
    ).success


@apps.command(cls=KSDKCommand)
@click.argument("app_name_with_version", nargs=1, type=AppNameWithVersionType(version_required=False))
@click.option("-y", "--yes", default=False, is_flag=True, show_default=True, help=KSDKHelpMessages.yes)
def delete(app_name_with_version: str, yes: bool) -> bool:
    """Delete an application from the platform's Application Registry.

    e.g. kelvin apps delete "example-app:1.0.0"

    """
    from kelvin.sdk.interface import apps_delete

    return apps_delete(app_name_with_version=app_name_with_version, ignore_destructive_warning=yes).success
