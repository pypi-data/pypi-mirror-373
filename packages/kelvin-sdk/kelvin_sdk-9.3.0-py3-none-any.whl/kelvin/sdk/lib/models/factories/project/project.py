import abc
from dataclasses import dataclass
from typing import Dict, List, Optional, Type

from kelvin.sdk.lib.exceptions import AppException
from kelvin.sdk.lib.models.apps.common import ApplicationLanguage
from kelvin.sdk.lib.models.apps.ksdk_app_configuration import ApplicationFlavour, ProjectType
from kelvin.sdk.lib.models.apps.ksdk_app_setup import Directory, File, ProjectCreationParametersObject, TemplateFile
from kelvin.sdk.lib.models.generic import KPath, KSDKModel
from kelvin.sdk.lib.schema.schema_manager import generate_base_schema_template
from kelvin.sdk.lib.templates.templates_manager import get_file_templates, get_files_from_templates
from kelvin.sdk.lib.utils.general_utils import dict_to_yaml


class ProjectFileTree(KSDKModel, abc.ABC):
    root: Directory

    @classmethod
    def from_tree(
        cls,
        app_root: KPath,
        project_type: ProjectType,
        kelvin_app_flavour: ApplicationFlavour,
        template_parameters: Dict,
        kelvin_app_lang: Optional[ApplicationLanguage] = None,
        **kwargs: Dict,
    ) -> "ProjectFileTree":
        """Class method that must fill the Tree directories and respective files

        Parameters
        ----------
        app_root: KPath
            Application path root directory path
        template_parameters:
            Dictionary to fill the templates
        project_type: ProjectType
        kelvin_app_flavour: ApplicationFlavour
        kelvin_app_lang: ApplicationLanguage, optional

        Returns
        -------

        """

        tree_dict = cls.get_tree_dict(app_root=app_root, **kwargs)

        # iterate over directories and prepare the files based on the templates
        creation_dict = {
            key: cls._build_directory(
                directory=item["directory"],
                parameters=template_parameters,
                files_templates=get_file_templates(
                    file_type=item["file_type"],
                    project_type=project_type,
                    app_flavour=kelvin_app_flavour,
                    kelvin_app_lang=kelvin_app_lang,
                ),
            )
            for key, item in tree_dict.items()
        }

        return cls(**creation_dict)

    @staticmethod
    @abc.abstractmethod
    def get_tree_dict(app_root: KPath, **kwargs: Dict) -> Dict:
        """Returns a dictionary with the file tree associated with the class attributes"""

    @abc.abstractmethod
    def fundamental_dirs(self) -> List[Directory]:
        """A list of project's main directories

        Returns
        -------
        List[Directory]
        """

    @abc.abstractmethod
    def optional_dirs(self) -> List[Directory]:
        """A list of project's optional directories

        Returns
        -------
        List[Directory]
        """

    @staticmethod
    def _build_directory(
        directory: KPath, parameters: dict, files_templates: Optional[List[TemplateFile]] = None
    ) -> Directory:
        """Create a directory instance with the associated list of files

        Parameters
        ----------
        directory: KPath
            The directory path
        parameters: Dict
            The list of parameters required to fill the file templates
        files_templates: List[TemplateFile], optional
            The file templates list associated with the directory

        Returns
        -------
        Directory
            A directory instance that contains the path and a list of files

        """
        directory_object = Directory(directory=directory)
        if files_templates:
            files = get_files_from_templates(directory=directory, templates=files_templates, render_params=parameters)
            directory_object.files = files

        return directory_object

    @staticmethod
    def get_extra_template_parameters() -> Dict:
        return {}


@dataclass
class ProjectMixin:
    """Workaround due to mypy and dataclasses issue
    https://github.com/python/mypy/issues/5374
    """

    creation_parameters: ProjectCreationParametersObject


class ProjectBase(ProjectMixin, abc.ABC):
    """Project representation
    Contains the structure to create the app file tree and templates based on the AppType and AppFlavour
    """

    creation_parameters: ProjectCreationParametersObject
    file_tree: Optional[ProjectFileTree] = None
    flavour_registry: Dict = {}

    def __post_init__(self) -> None:
        self.file_tree = self._build_file_tree()

    def get_flavour(self) -> ApplicationFlavour:
        return self.creation_parameters.app_flavour

    def get_flavour_class(self) -> Type[ProjectFileTree]:
        project_flavour = self.creation_parameters.app_flavour
        project_class_flavour = self.flavour_registry.get(project_flavour, None)

        if not project_class_flavour:
            raise AppException(f'The provided application type does not support the "{project_flavour.name}" flavour.')

        return project_class_flavour

    def _build_app_config_file(self, app_config_file_path: KPath) -> File:
        """Build the app yaml File based on the current schema

        Returns
        -------
        File
            The app yaml config file based on the current schema
        """
        # get app config file
        app_configuration = generate_base_schema_template(project_creation_parameters_object=self.creation_parameters)
        app_configuration_yaml: str = dict_to_yaml(content=app_configuration)
        file = File(file=app_config_file_path, content=app_configuration_yaml)

        return file

    def create_dirs_and_files(self) -> None:
        """Creates the directory tree and the files for each one"""
        if self.file_tree:
            fundamental_dirs = self.file_tree.fundamental_dirs()
            optional_dirs = self.file_tree.optional_dirs()

            for directory in fundamental_dirs + optional_dirs:
                if directory.exists():
                    raise AppException(f"Directory {directory.path()} already exists.")
                directory.create()
                for file in directory.files:
                    file.create()

    @abc.abstractmethod
    def _build_file_tree(self) -> ProjectFileTree:
        """Build the project file tree using the creation parameters"""

    @abc.abstractmethod
    def get_template_parameters(self) -> Dict:
        """Dict used to fill the templates

        Returns
        -------
        Dict
            A dictionary containing the required parameters to fill the project templates
        """
