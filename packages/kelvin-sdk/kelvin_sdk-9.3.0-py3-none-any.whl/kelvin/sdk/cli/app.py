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

from __future__ import annotations

from typing import Dict, List, Optional

import click
from click import Choice
from colorama import Fore

from kelvin.publisher.main import csv, generator, simulator
from kelvin.sdk.cli.mlflow import mlflow
from kelvin.sdk.lib.configs.general_configs import GeneralConfigs, KSDKHelpMessages
from kelvin.sdk.lib.models.apps.common import ApplicationLanguage
from kelvin.sdk.lib.models.apps.ksdk_app_configuration import ApplicationFlavour, ProjectType
from kelvin.sdk.lib.utils.click_utils import AppNameWithVersionType, KSDKCommand, KSDKGroup
from kelvin.sdk.lib.utils.logger_utils import logger


@click.group(cls=KSDKGroup)
def app() -> None:
    """Create, build and manage applications."""


@app.command(cls=KSDKCommand)
def samples() -> None:
    """Opens Kelvin's code samples GitHub repo."""
    import webbrowser

    logger.info(
        f"""Kelvin code samples are available here:
        {Fore.GREEN}{GeneralConfigs.code_samples_url}{Fore.RESET}
    """
    )
    webbrowser.open_new_tab(GeneralConfigs.code_samples_url)


@app.command(cls=KSDKCommand)
@click.argument("app_name", nargs=1, type=click.STRING, required=False)
@click.option("--description", required=False, default="", type=click.STRING, help=KSDKHelpMessages.app_description)
@click.option(
    "--app-type",
    required=False,
    default=ProjectType.app.value,
    type=Choice(ProjectType.app_types_as_str()),
    help=KSDKHelpMessages.app_type,
)
@click.option(
    "--app-dir",
    type=click.Path(),
    required=False,
    default=".",
    help=KSDKHelpMessages.app_dir,
)
def create(
    app_name: str,
    description: str,
    app_type: Optional[ProjectType],
    app_dir: str,
) -> bool:
    """Create a new application based on the specified parameters."""
    from kelvin.sdk.interface import app_create_from_parameters

    app_type = ProjectType(app_type)
    kelvin_app_lang = ApplicationLanguage.python

    if not app_name:
        app_name = input("Please provide a name for the application: ")

    return app_create_from_parameters(
        app_dir=app_dir or ".",
        app_name=app_name,
        app_description=description,
        app_type=app_type,
        app_flavour=ApplicationFlavour.default,
        kelvin_app_lang=kelvin_app_lang,
    ).success


@app.command(cls=KSDKCommand)
@click.option(
    "--app-dir",
    type=click.Path(exists=True),
    required=False,
    default=".",
    help=KSDKHelpMessages.app_dir,
)
@click.option("--build-arg", type=str, multiple=True, help=KSDKHelpMessages.app_build_args, default=[])
@click.option(
    "--multiarch",
    type=str,
    default="amd64",
    show_default=True,
    help=KSDKHelpMessages.app_build_multiarch,
)
def build(app_dir: str, build_arg: List[str], multiarch: str) -> bool:
    """Build a local application into a packaged image."""
    from kelvin.sdk.interface import app_build

    build_args_dict: Dict[str, str] = dict(x.split("=") for x in build_arg)  # type: ignore

    requested_archs = multiarch.split(",")

    return app_build(app_dir=app_dir, build_args=build_args_dict, archs=requested_archs).success


def split_assets(_, __, value: str) -> List[str]:  # type: ignore
    if value is None:
        return []

    return value.split(",")


@app.command(cls=KSDKCommand)
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
@click.pass_context
def upload(ctx: click.core.Context, app_dir: str, build_arg: List[str], multiarch: str) -> bool:
    """Upload an application to the platform's Application Registry.

    e.g. kelvin app upload --app-dir="."
    """
    from kelvin.sdk.cli.apps import upload as _upload

    return ctx.invoke(_upload, app_dir=app_dir, build_arg=build_arg, multiarch=multiarch)


@app.group(cls=KSDKGroup)
def images() -> None:
    """Management and display of local images on the Local Application Registry."""


@images.command(cls=KSDKCommand)
def list() -> bool:
    """List all locally built applications."""
    from kelvin.sdk.interface import app_images_list

    return app_images_list(should_display=True).success


@images.command(cls=KSDKCommand)
@click.argument("app_name_with_version", nargs=1, type=AppNameWithVersionType(version_required=True))
def remove(app_name_with_version: str) -> bool:
    """Remove an application from the local applications list.\n

    e.g. kelvin app images remove "test-app:1.0.0"
    """
    from kelvin.sdk.interface import app_image_remove

    return app_image_remove(app_name_with_version=app_name_with_version).success


@images.command(cls=KSDKCommand)
@click.argument("app_name_with_version", nargs=1, type=AppNameWithVersionType(version_required=True))
@click.option(
    "--container-dir",
    type=click.Path(),
    required=False,
    default=None,
    help=KSDKHelpMessages.app_images_unpack_container_dir,
)
@click.option(
    "--output-dir",
    type=click.Path(),
    required=True,
    help=KSDKHelpMessages.app_images_unpack_output_dir,
)
def unpack(app_name_with_version: str, container_dir: str, output_dir: str) -> bool:
    """Extract the content of an application from its built image into the specified directory.\n

    e.g. kelvin app images unpack "test-app:1.0.0" --output-dir=my_output_dir

    """
    from kelvin.sdk.interface import app_image_unpack

    return app_image_unpack(
        app_name_with_version=app_name_with_version, container_dir=container_dir, output_dir=output_dir
    ).success


@app.group(cls=KSDKGroup)
def test() -> None:
    """Test local applications."""


test.add_command(simulator)
test.add_command(csv)
test.add_command(generator)

app.add_command(mlflow)
