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

import builtins
import tempfile
from typing import Dict, List, Optional

import inquirer
import mlflow
from mlflow import MlflowException
from mlflow.entities.model_registry import ModelVersion, RegisteredModel
from mlflow.models.signature import ModelSignature
from mlflow.tracking import MlflowClient
from mlflow.types import Schema
from mlflow.types.schema import DataType
from ruamel.yaml import YAML

from kelvin.sdk.lib.apps.local_apps_manager import project_create
from kelvin.sdk.lib.models.apps.common import ApplicationLanguage
from kelvin.sdk.lib.models.apps.ksdk_app_configuration import ApplicationFlavour
from kelvin.sdk.lib.models.apps.ksdk_app_setup import Inout, MLFlowProjectCreationParametersObject, ProjectType
from kelvin.sdk.lib.models.generic import KPath
from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.utils.application_utils import check_if_app_name_is_valid
from kelvin.sdk.lib.utils.display_utils import display_data_entries
from kelvin.sdk.lib.utils.logger_utils import logger


def list_mlflow_models(registry_uri: str, filter_string: Optional[str] = None) -> List[RegisteredModel]:
    cli = MlflowClient(registry_uri=registry_uri)
    models = cli.search_registered_models(filter_string=filter_string, max_results=1000).to_list()
    return models


def print_mlflow_model_table(models: List[RegisteredModel], title: str = "MLFlow Models") -> None:
    def get_latest_model_version(model_versions: List[ModelVersion]) -> ModelVersion:
        latest_version = max(model_versions, key=lambda version: version.creation_timestamp)
        return latest_version

    data = []
    for model in models:
        latest = get_latest_model_version(model.latest_versions) if model.latest_versions else None
        description = (latest.description if latest else model.description) or ""
        data.append(
            {
                "name": model.name,
                "description": description[:50],
                "latest": latest.version if latest else "NA",
            }
        )
    display_data_entries(
        data=data,
        header_names=["Name", "Description", "Latest Version"],
        attributes=["name", "description", "latest"],
        table_title=title,
    )


PT_TYPES_MAP = {
    bool: "boolean",
    int: "number",
    builtins.float: "number",
    str: "string",
}


def prompt_model_name(registry_uri: str) -> str:
    models = list_mlflow_models(registry_uri=registry_uri)
    if not models:
        logger.error("No models found in the registry")
        return ""
    model_names = [model.name for model in models]
    questions = [
        inquirer.List("model", message="Select a model", choices=model_names),
    ]
    answers = inquirer.prompt(questions)
    return answers["model"]


def prompt_model_version(registry_uri: str, model_name: str) -> int:
    client = MlflowClient(registry_uri=registry_uri)
    versions = client.search_model_versions(f"name='{model_name}'")
    if not versions:
        logger.error(f"No versions found for model {model_name}")
        return 0
    version_choices = [version.version for version in versions if version]
    questions = [
        inquirer.List("version", message="Select a version", choices=version_choices),
    ]
    answers = inquirer.prompt(questions)
    return answers["version"]


def download_model_artifacts(artifact_uri: str, model_name: str, model_version: int, path: str) -> bool:
    try:
        mlflow.set_registry_uri(artifact_uri)
        mlflow.artifacts.download_artifacts(artifact_uri=f"models:/{model_name}/{model_version}", dst_path=path)
        return True
    except MlflowException as e:
        logger.error(f"Error downloading model artifacts: {e}")

    return False


def parse_inouts(schema: Schema) -> List[Inout]:
    if schema.is_tensor_spec():
        logger.info("Tensorflow signature not supported yet. Skipping.")
        return []
    out = []
    try:
        for k, v in schema.input_types_dict().items():
            if not isinstance(v, DataType):
                continue

            pt_type = PT_TYPES_MAP.get(v.to_python())
            if pt_type is not None:
                out.append(Inout(name=k, type=pt_type))
    except MlflowException:
        logger.info("No names found in the signature. Skipping setup.")

    return out


def mlflow_app_create(
    uri: str,
    model_name: Optional[str],
    model_version: Optional[int],
    app_name: Optional[str],
    app_dir: Optional[str],
    prompt: bool = True,
) -> OperationResponse:
    if model_name is None:
        if prompt is False:
            return OperationResponse(success=False, log="Model name is required.")

        model_name = prompt_model_name(registry_uri=uri)
        if not model_name:
            return OperationResponse(success=False, log="No model selected.")

    if model_version is None:
        if prompt is False:
            return OperationResponse(success=False, log="Model version is required.")

        model_version = prompt_model_version(registry_uri=uri, model_name=model_name)
        if not model_version:
            return OperationResponse(success=False, log="No version selected.")

    if app_name is None:
        if prompt is False:
            return OperationResponse(success=False, log="App name is required.")
        answers = inquirer.prompt(
            [
                inquirer.Text(
                    "app_name",
                    message="Enter app name",
                    validate=lambda _, x: check_if_app_name_is_valid(x),
                    default=model_name.lower().replace(" ", "-").replace("_", "-"),
                )
            ]
        )
        app_name = answers["app_name"]

    try:
        tmp_dir = tempfile.TemporaryDirectory()
        client = MlflowClient(registry_uri=uri)
        model = client.get_model_version(name=model_name, version=model_version)
        description = model.description or "NA"

        logger.info("Downloading model artifacts")
        if not download_model_artifacts(
            artifact_uri=uri, model_name=model_name, model_version=model_version, path=tmp_dir.name
        ):
            return OperationResponse(success=False, log="Failed to download model artifacts")

        info = mlflow.models.get_model_info(model_uri=tmp_dir.name)
        signature: ModelSignature = info.signature
    except MlflowException as e:
        tmp_dir.cleanup()
        return OperationResponse(success=False, log=f"Error downloading model artifacts: {e}")

    logger.info("Setup app inputs")
    inputs = parse_inouts(signature.inputs)

    logger.info("Setup app outputs")
    outputs = parse_inouts(signature.outputs)

    app_dir = app_dir or "."
    app_final_dir = KPath(app_dir) / app_name
    if prompt and app_final_dir.exists():
        answers = inquirer.prompt(
            [
                inquirer.Confirm("continue", message=f"App directory already exists. Overwrite {app_final_dir}?"),
            ]
        )
        if not answers["continue"]:
            return OperationResponse(success=False, log="MlFlow app create cancelled.")

    project_creation_parameters = MLFlowProjectCreationParametersObject(
        app_dir=app_dir,
        app_name=app_name,
        app_version="1.0.0",
        app_description=description,
        app_type=ProjectType.app,
        app_flavour=ApplicationFlavour.mlflow,
        kelvin_app_lang=ApplicationLanguage.python,
        inputs=inputs,
        outputs=outputs,
    )

    ret = project_create(project_creation_parameters=project_creation_parameters)
    if not ret.success:
        tmp_dir.cleanup()
        return ret

    # copy model artifacts into the app directory
    model_path = KPath(project_creation_parameters.app_dir) / app_name / "model"
    model_path.mkdir(parents=True, exist_ok=True)
    model_tmp = KPath(tmp_dir.name)
    model_tmp.clone_dir_into(model_path)
    tmp_dir.cleanup()

    return OperationResponse(success=True, log="Mlflow App created successfully.")


def merge_app_inouts(inputs: List[Inout], outputs: List[Inout], path_yaml: KPath) -> None:
    yaml = YAML(typ="rt")
    conf: Dict = yaml.load(path_yaml)

    app_inputs = conf.get("data_streams", {}).get("inputs", [])
    app_outputs = conf.get("data_streams", {}).get("outputs", [])

    app_inputs_names = [x["name"] for x in app_inputs]
    app_outputs_names = [x["name"] for x in app_outputs]

    for i in inputs:
        if i.name not in app_inputs_names:
            app_inputs.append({"name": i.name, "data_type": i.type})

    for o in outputs:
        if o.name not in app_outputs_names:
            app_outputs.append({"name": o.name, "data_type": o.type})

    conf["data_streams"]["inputs"] = app_inputs
    conf["data_streams"]["outputs"] = app_outputs

    yaml.dump(conf, path_yaml)


def mlflow_model_import(
    uri: str,
    model_name: Optional[str],
    model_version: Optional[int],
    app_path: Optional[str],
    prompt: bool = True,
    update_config: bool = False,
) -> OperationResponse:
    if model_name is None:
        if prompt is False:
            return OperationResponse(success=False, log="Model name is required.")

        model_name = prompt_model_name(registry_uri=uri)
        if not model_name:
            return OperationResponse(success=False, log="No model selected.")

    if model_version is None:
        if prompt is False:
            return OperationResponse(success=False, log="Model version is required.")

        model_version = prompt_model_version(registry_uri=uri, model_name=model_name)
        if not model_version:
            return OperationResponse(success=False, log="No version selected.")

    if app_path is None:
        if prompt is False:
            return OperationResponse(success=False, log="App dir is required.")
        answers = inquirer.prompt(
            [
                inquirer.Text(
                    "app_dir",
                    message="Enter app dir",
                    validate=lambda _, x: check_if_app_name_is_valid(x),
                    default=model_name.lower().replace(" ", "-").replace("_", "-"),
                )
            ]
        )
        app_path = answers["app_dir"]

    app_dir = KPath(app_path)
    if not app_dir.exists():
        return OperationResponse(success=False, log=f"App directory does not exist: {app_path}")

    tmp_dir = tempfile.TemporaryDirectory()
    logger.info("Downloading model artifacts")
    if not download_model_artifacts(
        artifact_uri=uri, model_name=model_name, model_version=model_version, path=tmp_dir.name
    ):
        return OperationResponse(success=False, log="Failed to download model artifacts")

    model_dir = app_dir / "model"
    if model_dir.exists():
        if prompt:
            questions = [
                inquirer.Confirm("continue", message=f"Overwrite {model_dir}?"),
            ]
            answers = inquirer.prompt(questions)
            if not answers["continue"]:
                return OperationResponse(success=False, log="Model update cancelled.")

    # copy model artifacts into the app directory
    logger.info("Copying model artifacts into app directory")
    model_tmp = KPath(tmp_dir.name)
    model_tmp.clone_dir_into(model_dir)

    if update_config:
        logger.info("Updating app inputs and outputs")
        info = mlflow.models.get_model_info(model_uri=str(model_dir))
        signature: ModelSignature = info.signature
        inputs = parse_inouts(signature.inputs)
        outputs = parse_inouts(signature.outputs)
        merge_app_inouts(inputs, outputs, KPath(app_dir) / "app.yaml")

    return OperationResponse(success=True, log="Model imported successfully.")
