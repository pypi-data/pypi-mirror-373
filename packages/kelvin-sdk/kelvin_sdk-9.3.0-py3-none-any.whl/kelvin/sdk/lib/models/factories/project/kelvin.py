from dataclasses import dataclass
from typing import Any, Dict, List

from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.models.apps.ksdk_app_configuration import ApplicationFlavour
from kelvin.sdk.lib.models.apps.ksdk_app_setup import Directory, MLFlowProjectCreationParametersObject
from kelvin.sdk.lib.models.factories.project.project import ProjectBase, ProjectFileTree
from kelvin.sdk.lib.models.generic import KPath
from kelvin.sdk.lib.models.types import FileType


class ProjectDockerDefaultFileTree(ProjectFileTree):
    schemas: Directory

    @staticmethod
    def get_tree_dict(app_root: KPath, **kwargs: Any) -> Dict:
        return {
            FileType.ROOT.value: {"file_type": FileType.APP, "directory": app_root},
            "schemas": {"file_type": FileType.SCHEMAS, "directory": app_root / "ui_schemas"},
        }

    def fundamental_dirs(self) -> List[Directory]:
        return [self.root]

    def optional_dirs(self) -> List[Directory]:
        return [self.schemas]


@dataclass
class KelvinProject(ProjectBase):
    flavour_registry = {
        ApplicationFlavour.default: ProjectDockerDefaultFileTree,
        ApplicationFlavour.mlflow: ProjectDockerDefaultFileTree,
    }

    def get_template_parameters(self) -> Dict:
        jinja_params = {
            "app_root": KPath(self.creation_parameters.app_dir) / self.creation_parameters.app_name,
            "app_name": self.creation_parameters.app_name,
            "app_description": self.creation_parameters.app_description or self.creation_parameters.app_name,
            "app_version": self.creation_parameters.app_version,
            "app_config_file": GeneralConfigs.default_app_config_file,
            "title": self.creation_parameters.app_name.title(),
            "app_type": self.creation_parameters.app_type.app_type_on_config(),
            "spec_version": "5.0.0",  # TODO: infer this
        }

        if isinstance(self.creation_parameters, MLFlowProjectCreationParametersObject):
            jinja_params["inputs"] = [{"name": i.name, "data_type": i.type} for i in self.creation_parameters.inputs]
            jinja_params["outputs"] = [{"name": o.name, "data_type": o.type} for o in self.creation_parameters.outputs]

        return jinja_params

    def _build_file_tree(self) -> ProjectFileTree:
        # 1 - Configuration files, app dir and files
        parameters: dict = self.get_template_parameters()
        app_root_dir_path = parameters.get("app_root", "")

        project_file_tree_class = self.get_flavour_class()
        parameters.update(**project_file_tree_class.get_extra_template_parameters())

        # directory file tree required for a docker project
        project_type = self.creation_parameters.app_type
        kelvin_app_flavour = self.creation_parameters.app_flavour
        file_tree: ProjectFileTree = project_file_tree_class.from_tree(
            app_root=app_root_dir_path,
            template_parameters=parameters,
            project_type=project_type,
            kelvin_app_flavour=kelvin_app_flavour,
        )

        return file_tree
