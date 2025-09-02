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

# mypy: ignore-errors
import os
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, Generic, Iterator, List, Mapping, Optional, Tuple, TypeVar

from jinja2 import FileSystemLoader, StrictUndefined, Template
from pydantic.v1 import BaseModel, BaseSettings
from pydantic.v1.env_settings import SettingsSourceCallable

from kelvin.sdk.lib.models.types import DelimiterStyle
from kelvin.sdk.lib.utils.logger_utils import logger

T = TypeVar("T")


class instance_classproperty(Generic[T]):  # noqa
    """Property that works on instances and classes."""

    def __init__(self, fget: Callable[..., T]) -> None:
        """Initialize instance-class property."""

        self.fget = fget

    def __get__(self, owner_self: Any, owner_cls: Any) -> T:
        """Get descriptor."""

        return self.fget(owner_self if owner_self is not None else owner_cls)


class OSInfo:
    is_posix: bool = os.name == "posix"

    @instance_classproperty
    def temp_dir(self_or_cls) -> Optional[str]:  # noqa
        return "/tmp" if self_or_cls.is_posix else None


class Dependency:
    name: str
    version: str

    def __init__(self, dependency: str) -> None:
        self.name, self.version = dependency.split(" ")

    @property
    def is_ksos_core_component(self) -> bool:
        return self.name in ["kelvin-sdk", "kelvin-sdk-client", "kelvin-app"]

    @property
    def pretty_name(self) -> str:
        return f"{self.name}  {self.version}"


# BaseSettings model -> kelvin-sdk-client
class KPath(type(Path())):
    def raise_if_has_files(self):
        """
        Raise an exception if the path contains files.

        Raises:
            ValueError: if the path contains files
        """
        if self.exists() and self.is_dir() and any(self.iterdir()):
            raise ValueError(f"Directory is not empty at {self.absolute()}")

    def delete_dir(self):
        """
        A simple wrapper around the deletion of a directory.


        Returns
        -------
        KPath
            the same KPath object

        """
        if not self.exists():
            return self

        path = self.complete_path()

        # prevent from nuking parent directory of home and current dir
        for parent in [Path.home(), Path.cwd()]:
            try:
                parent.relative_to(path)
            except ValueError:
                pass
            else:
                raise ValueError(f"Can't delete the current or parent directory - {path}")

        shutil.rmtree(str(path), ignore_errors=True)
        logger.debug(f"Directory deleted: {path}")

        return self

    def create_dir(self, parents: bool = True, exist_ok: bool = True, **kwargs):
        """
        Create a directory.

        Args:
            parents (bool, optional): create parents if not exist. Defaults to True.
            exist_ok (bool, optional): raise if exist not ok. Defaults to True.
        """
        if not self.exists():
            logger.debug(f"Directory created (parents included): {self.absolute()}")
        self.mkdir(parents=parents, exist_ok=exist_ok, **kwargs)
        return self

    def read_yaml_all(self, verbose: bool = True) -> Iterator:
        """
        Load the content of the specified yaml_file into a dictionary.

        Parameters
        ----------
        verbose : bool
            indicates whether it should be verbose about the read content

        Returns
        -------
        Generator
            a dictionary containing the yaml data.

        """
        import yaml

        content = self.read_text()

        if verbose:
            logger.debug(f"Content read from: {self.absolute()}")

        return yaml.safe_load_all(content)

    def read_yaml(
        self,
        context: Optional[Mapping[str, Any]] = None,
        delimiter_style: DelimiterStyle = DelimiterStyle.BRACE,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Load the content of the specified yaml_file into a dictionary.

        Parameters
        ----------
        context : Optional[Mapping[str, Any]]
            context variable used to render the template.
        delimiter_style : DelimiterStyle
            the delimiter used to render the template.
        verbose : bool
            Indicates whether it should log the path of the read file.

        Returns
        -------
        Dict[str, Any]
            a dictionary containing the yaml data.
        """
        try:
            import yaml

            content = self.read_text()
            if context:
                content = render_template(content=content, context=context, delimiter_style=delimiter_style)

            if verbose:
                logger.debug(f"Content read from: {self.absolute()}")

            return yaml.safe_load(content)
        except Exception as exc:
            raise ValueError(f"Invalid YAML contents - {exc}")

    def write_yaml(self, yaml_data: dict):
        """
        Write the provided yaml data to a file.

        Parameters
        ----------
        yaml_data : dict
            the yaml data to write into the file

        Returns
        -------

        """
        KPath(self.parent).create_dir()

        if yaml_data:
            from ruamel import yaml

            yaml = yaml.YAML()
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.preserve_quotes = True
            with open(str(self), "w") as file_writer:
                logger.debug(f"YAML File created: {self.absolute()}")
                yaml.dump(yaml_data, file_writer)

        return self

    def complete_path(self) -> KPath:
        return self.expanduser().resolve()

    def read_content(self):
        """
        Read content from the provided file.
        """
        with open(str(self), "r") as file_reader:
            return file_reader.read()

    def write_content(self, content: str):
        """
        Write the provided data to the file.

        Parameters
        ----------
        content : str
            the data to write into the file

        Returns
        -------
        KPath
            the same KPath object

        """
        KPath(self.parent).create_dir()

        if content:
            logger.debug(f"File created: {self.absolute()}")
            try:
                with open(str(self), "w") as file_writer:
                    file_writer.write(content)
            except UnicodeError:
                # prevent in case of Windows encoding issues
                with open(str(self), "w", encoding="utf-8") as file_writer:
                    file_writer.write(content)

        return self

    def read_json(self) -> dict:
        """
        Read json content from the provided file.

        Returns
        -------
        dict
            the file's content as json

        """
        with open(str(self), "r") as file_reader:
            import json

            data = json.load(file_reader)
        return data

    def write_json(self, content: Any):
        """

        Parameters
        ----------
        content : Any
            the json data to write into the file

        Returns
        -------
        KPath
            the same KPath object

        """
        KPath(self.parent).create_dir()

        if content:
            with open(str(self), "w") as file_writer:
                import json

                json.dump(content, file_writer, ensure_ascii=True, indent=4, sort_keys=True)
                file_writer.write("\n")
        return self

    def dir_content(self) -> List[str]:
        """
        Retrieve the list of files contained inside the folder.

        Returns
        -------
        List[str]
            the list of all the files inside the container
        """
        return os.listdir(self)

    def clone_into(self, path: KPath):
        """
        Clones the current file into the newly provided path.

        Parameters
        ----------
        path : KPath
            the path to clone the current file into

        Returns
        -------
        KPath
            the same KPath object

        """
        if os.path.normpath(path) not in os.path.normpath(self):
            shutil.copy(self, path)
        return self

    def clone_dir_into(self, path: KPath):
        """
        Clones the current directory into the newly provided dir path.

        Parameters
        ----------
        path : KPath
            the path to clone the current directory into

        Returns
        -------
        KPath
            the same KPath object

        """
        from distutils.dir_util import copy_tree

        copy_tree(str(self), str(path))
        return self

    def remove(self):
        """
        A simple remove wrapper for KPath

        Returns
        -------
        KPath
            the same KPath object
        """
        if self.exists():
            self.unlink()
        return self


class KSDKModel(BaseModel):
    """
    Extends Pydantic BaseModel with a few additional functionalities.

    """

    def to_file(self, path: KPath, sort_keys: bool = True):
        """
        Auxiliary method to output the contents of the current model into a file

        Parameters
        ----------
        path : KPath
            the path to output the contents to.
        sort_keys : bool
            orders the yaml by key alphabetically.

        Returns
        -------
        KPath
            the same KSDKModel

        """
        KPath(path.parent).create_dir()

        from ruamel import yaml

        yaml = yaml.YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.preserve_quotes = True
        with open(str(path), "w") as file_writer:
            import json

            content = json.loads(self.json(exclude_none=True, sort_keys=sort_keys))
            yaml.dump(content, file_writer)

        return self

    def output_schema(self, output_file_path: KPath) -> bool:
        """
        Output the current model's schema to the specified file.

        Parameters
        ----------
        output_file_path : the file to output the schema into

        Returns
        -------
        bool
            a boolean indicating whether or not the schema was successfully output.
        """
        output_file_path.write_content(content=self.schema_json())
        return True


class KSDKSettings(KSDKModel, BaseSettings):
    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Set the priority of inputs"""
            return env_settings, init_settings, file_secret_settings


class GenericObject(object):
    """
    A simple generic object used to wrap-up dictionaries into a class.
    Uses reflection to set data dynamically.

    """

    def __init__(self, data: Mapping):
        self._set_variables_from_data(data=data)

    def _set_variables_from_data(self, data: Mapping) -> None:
        if data and isinstance(data, Mapping):
            for key, value in data.items():
                setattr(self, key, value)

    def to_dict(self) -> dict:
        return self.__dict__

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()


def render_template(content: str, context: Mapping[str, Any], delimiter_style: DelimiterStyle) -> str:
    """
    Render content with context.

    Parameters
    ----------
    content : str
        the content to render the template
    context : Mapping[str, Any]
        the context to render the content with
    delimiter_style : DelimiterStyle
        the delimiter style of the rendering operation

    Returns
    -------
    str
        the rendered template in a string

    """
    variable_start_string, variable_end_string = delimiter_style.value

    template = Template(content, variable_start_string=variable_start_string, variable_end_string=variable_end_string)
    template.environment.undefined = StrictUndefined
    template.environment.loader = FileSystemLoader(os.curdir)

    return template.render(context)
