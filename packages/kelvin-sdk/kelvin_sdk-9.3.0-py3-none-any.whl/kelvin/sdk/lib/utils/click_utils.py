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

import sys
from pathlib import Path
from typing import Any, List, Optional, Union

import click
from click import Context, Option, Parameter, UsageError, echo
from click.types import StringParamType
from docker_image.reference import ReferenceInvalidFormat

from kelvin.sdk.lib.configs.general_configs import KSDKHelpMessages
from kelvin.sdk.lib.utils.application_utils import check_if_app_name_is_valid


def _prompt(ctx: Context) -> str:
    """A custom prompt to get the invoked command chain and returns the pretty reversed version of it.

    Parameters
    ----------
    ctx : Context

    Returns
    -------
    str:
        the 'pretty reversed' list of invoked commands.

    """
    command = Path(sys.argv[0]).stem
    result: List[str] = [""]
    root = ctx
    while root.parent:
        result += [root.command.name] if root.command.name else []
        root = root.parent
    result += [command]
    return " > ".join(reversed(result))


class ClickConfigs:
    all_verbose_commands = ["--verbose", "-v"]
    all_help_commands = ["--help", "-h"]


class KSDKGroup(click.Group):
    command_tree: dict = {}

    def add_command(self, cmd: Any, name: Any = None) -> None:
        if self.name not in self.command_tree:
            self.command_tree[self.name] = {}
        clean_description = str(cmd.help).split("\n")[0]
        self.command_tree.setdefault(self.name, {}).update({cmd.name: clean_description})
        super().add_command(cmd, name)

    def add_command_alias(self, cmd: Any, name: str) -> None:
        super().add_command(cmd, name)

    def get_command_tree(self) -> dict:
        commands = self.command_tree.copy()
        commands_to_display = commands.pop("ksdk")
        for key, value in commands_to_display.items():
            if key in commands:
                commands_to_display[key] = commands.pop(key)
        KSDKGroup._look_down_the_tree(tree=commands_to_display, sub_tree=commands)
        return commands_to_display

    @staticmethod
    def _look_down_the_tree(tree: dict, sub_tree: dict) -> dict:
        copy_sub_tree = sub_tree.copy()
        for key in copy_sub_tree.keys():
            if isinstance(tree, dict) and key in tree.keys():
                value_to_set = sub_tree.pop(key)
                tree[key] = value_to_set
            else:
                for value in [value for value in tree.values() if isinstance(value, dict)]:
                    KSDKGroup._look_down_the_tree(value, sub_tree)
        return tree


class KSDKCommand(click.Command):
    version_warning_message: Optional[str] = None

    @staticmethod
    def get_verbose_option(_: Context) -> Option:
        def show_verbose(context: Context, _: Union[Option, Parameter], value: Optional[str]) -> None:
            if value and not context.resilient_parsing:
                echo(context.get_help(), color=context.color)
                context.exit()

        return Option(
            ClickConfigs.all_verbose_commands,
            default=False,
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=show_verbose,
            help=KSDKHelpMessages.verbose,
        )

    def get_params(self, ctx: Context) -> List:
        # Retrieve the params and ensure both '--help' and '--verbose'
        rv = self.params
        help_option = self.get_help_option(ctx)
        verbose_option = self.get_verbose_option(ctx)
        if verbose_option is not None:
            rv = rv + [verbose_option]
        if help_option is not None:
            rv = rv + [help_option]
        return rv

    def parse_args(self, ctx: Any, args: Any) -> list:
        # 1 - Retrieve (and refresh if necessary) the global kelvin-sdk configuration
        if not bool(set(ClickConfigs.all_help_commands) & set(args)):
            from kelvin.sdk.lib.session.session_manager import session_manager

            verbose_flag_specified = any([item for item in ClickConfigs.all_verbose_commands if item in args])

            # 2 - Refresh metadata and setup the logger
            ksdk_configuration = session_manager.refresh_metadata()
            if ksdk_configuration:
                self.version_warning_message = session_manager.assess_kelvin_version()
            session_manager.setup_logger(verbose=verbose_flag_specified)

            # 3 - Drop the verbose option from the args and proceeding
            args = [item for item in args if item not in ClickConfigs.all_verbose_commands]

        return super().parse_args(ctx, args)

    def invoke(self, ctx: Any) -> Any:
        from .logger_utils import logger

        result = None
        try:
            result = super().invoke(ctx)
            if self.version_warning_message:
                logger.info(self.version_warning_message)
        except UsageError:
            raise
        except click.exceptions.Exit:
            pass
        except Exception as e:
            logger.exception(f"Error executing Kelvin command - {e}")
            sys.exit(1)

        if not result:
            sys.exit(1)

        return result


class ClickExpandedPath(click.Path):
    """
    A Click path argument that returns a ``Path``, not a string.
    """

    def convert(  # type: ignore
        self,
        value: str,
        param: Optional[click.core.Parameter] = None,
        ctx: Optional[click.core.Context] = None,
    ) -> Any:
        """
        Return a ``Path`` from the string ``click`` would have created with
        the given options.
        """
        import pathlib

        resolved_path = pathlib.Path(value).expanduser().resolve()
        content = super().convert(value=str(resolved_path), param=param, ctx=ctx)

        return content


class AppNameWithVersionType(StringParamType):
    """Click Custom App name with version validator
    Validates for app name with version "someapp:1.0.0" and/or container name "somecontainer.app"

    Attributes
    ----------
    version_required: bool, optional, default False
        If True, version needs to be present in the string  e.g. "app:1.0.0"
    allow_container: bool, optional, default False
        If True, also the container name is allowed in the following format "somecontainer.app"

    """

    def __init__(self, version_required: bool = False, allow_container: bool = False) -> None:
        super().__init__()
        self.version_required = version_required
        self.allow_container = allow_container

    def convert(self, value: str, param: Optional[Parameter], ctx: Optional[Context]) -> str:
        value = super().convert(value, param, ctx)

        if value:
            if self.allow_container and ".app" in str(value):
                self.validate_container(value, param, ctx)
            else:
                self.validate_app_name_with_version(value, param, ctx)

        return value

    def validate_container(self, value: str, param: Optional[Parameter], ctx: Optional[Context]) -> None:
        try:
            app_name = str(value).split(".")[0]
            check_if_app_name_is_valid(str(app_name))
        except Exception as exp:
            self.fail(f"Invalid app name format: {str(exp)}..", param=param)

    def validate_app_name_with_version(self, value: str, param: Optional[Parameter], ctx: Optional[Context]) -> None:
        from docker_image import reference

        try:
            ref = reference.Reference.parse(value)
            _, name = ref.split_hostname()

            check_if_app_name_is_valid(name)
        except ReferenceInvalidFormat:
            self.fail(message="Invalid app name format..", param=param)
        except Exception as exp:
            self.fail(message=f"Invalid app name with version format: {str(exp)}..", param=param)

        tag = ref.get("tag", None)
        if not tag and self.version_required:
            message = (
                "Missing version. Please use the following "
                'format: "app:1.0.0", "app:latest" or "platform/app:1.0.0."'
            )
            self.fail(message=message, param=param)
