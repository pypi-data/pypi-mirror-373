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

from typing import Any, Optional

import click

from kelvin.sdk.lib.configs.general_configs import KSDKHelpMessages
from kelvin.sdk.lib.utils.application_utils import check_if_app_name_is_valid
from kelvin.sdk.lib.utils.click_utils import KSDKCommand, KSDKGroup


@click.group(cls=KSDKGroup)
def mlflow() -> None:
    """MLFlow integration commands."""


def click_validate_app_name(_: Any, param: str, value: str) -> str:
    try:
        if value is not None:
            check_if_app_name_is_valid(value)
        return value
    except Exception as e:
        raise click.BadParameter(str(e))


@mlflow.command(cls=KSDKCommand)
@click.option(
    "--registry-uri",
    type=click.STRING,
    help=KSDKHelpMessages.mlflow_registry_uri,
    required=True,
    prompt="MLFlow registry URI",
)
@click.option("--model-name", type=click.STRING, help="Model name")
@click.option("--model-version", type=click.INT, help="Model version")
@click.option("--app-name", type=click.STRING, help=KSDKHelpMessages.mlflow_app_name, callback=click_validate_app_name)
@click.option(
    "--app-dir",
    type=click.Path(),
    required=False,
    default=".",
    help=KSDKHelpMessages.app_dir,
)
@click.option("--prompt/--no-prompt", is_flag=True, default=True, help="Prompt for missing information if needed.")
def create(
    registry_uri: str,
    model_name: Optional[str],
    model_version: Optional[int],
    app_name: Optional[str],
    app_dir: str,
    prompt: bool,
) -> None:
    """Create app based on MLFlow model."""
    from kelvin.sdk.lib.mlflow.mlflow import mlflow_app_create

    ret = mlflow_app_create(
        uri=registry_uri,
        model_name=model_name,
        model_version=model_version,
        app_name=app_name,
        app_dir=app_dir,
        prompt=prompt,
    )
    ret.print()


@mlflow.command(cls=KSDKCommand, name="import")
@click.option(
    "--registry-uri",
    type=click.STRING,
    help=KSDKHelpMessages.mlflow_registry_uri,
    required=True,
    prompt="MLFlow registry URI",
)
@click.option("--model-name", type=click.STRING, help="Model name")
@click.option("--model-version", type=click.INT, help="Model version")
@click.option(
    "--app-dir",
    type=click.Path(),
    required=False,
    default=".",
    help=KSDKHelpMessages.app_dir,
)
@click.option("--prompt/--no-prompt", is_flag=True, default=True, help="Prompt for missing information if needed.")
@click.option(
    "--update-config/--no-update-config", is_flag=True, default=True, help="Update App configuration with model info"
)
def model_import(
    registry_uri: str,
    model_name: Optional[str],
    model_version: Optional[int],
    app_dir: str,
    prompt: bool,
    update_config: bool,
) -> None:
    """Import a MLFlow model into an existing Kelvin App."""
    from kelvin.sdk.lib.mlflow.mlflow import mlflow_model_import

    ret = mlflow_model_import(
        uri=registry_uri,
        model_name=model_name,
        model_version=model_version,
        app_path=app_dir,
        prompt=prompt,
        update_config=update_config,
    )
    ret.print()


@mlflow.command(cls=KSDKCommand)
@click.option("--registry-uri", type=click.STRING, help="MLFlow registry URI.", required=True, prompt=True)
def list(registry_uri: str) -> None:
    """Search MLFlow models.
    Limited to 1000 results. Default filter is model name"""
    from kelvin.sdk.lib.mlflow.mlflow import list_mlflow_models, print_mlflow_model_table

    models = list_mlflow_models(registry_uri=registry_uri)
    print_mlflow_model_table(models)
