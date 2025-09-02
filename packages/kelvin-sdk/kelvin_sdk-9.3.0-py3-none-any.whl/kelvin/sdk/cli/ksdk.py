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

from typing import Any, Optional, Union

import click
from click import Context, Option, Parameter

from kelvin.sdk.cli.app import app
from kelvin.sdk.cli.appregistry import appregistry
from kelvin.sdk.cli.apps import apps
from kelvin.sdk.cli.authentication import auth
from kelvin.sdk.cli.configuration import configuration, reset
from kelvin.sdk.cli.secret import secret
from kelvin.sdk.cli.system_report import info
from kelvin.sdk.cli.version import version
from kelvin.sdk.cli.workload import workload
from kelvin.sdk.lib.configs.general_configs import GeneralConfigs, KSDKHelpMessages
from kelvin.sdk.lib.utils.click_utils import KSDKGroup


def display_ksdk_version(ctx: Context, param: Union[Option, Parameter], value: Optional[str]) -> Any:
    if not value or ctx.resilient_parsing:
        return param or True
    ksos_version = ""
    try:
        import pkg_resources

        from kelvin.sdk.lib.models.generic import Dependency

        all_dependencies = [Dependency(str(d)) for d in pkg_resources.working_set]
        ksos_dependency_list = [dependency for dependency in all_dependencies if dependency.name.startswith("ksos")]
        if ksos_dependency_list:
            ksos_version = f" (KSOS {ksos_dependency_list[0].version})"
    except Exception:
        pass

    display_message = f"Kelvin SDK {version}{ksos_version}"

    click.echo(display_message)
    ctx.exit()
    return True


def display_ksdk_documentation_link(ctx: Context, param: Union[Option, Parameter], value: Optional[str]) -> Any:
    if not value or ctx.resilient_parsing:
        return param or True

    from kelvin.sdk.lib.session.session_manager import session_manager
    from kelvin.sdk.lib.utils.general_utils import open_link_in_browser

    docs_url: str = session_manager.get_documentation_link_for_current_url() or GeneralConfigs.docs_url

    open_link_in_browser(docs_url)

    ctx.exit()
    return True


def display_command_tree(ctx: Context, param: Union[Option, Parameter], value: Optional[str]) -> Any:
    if not value or ctx.resilient_parsing:
        return param or True
    from kelvin.sdk.lib.utils.display_utils import pretty_colored_content, success_colored_message

    commands_to_display = KSDKGroup().get_command_tree()
    colored_title = success_colored_message(KSDKHelpMessages.tree_title)
    colored_content = pretty_colored_content(content=commands_to_display, initial_indent=2, indent=2, show_arm=True)
    click.echo(f"{colored_title}")
    click.echo(f"{colored_content}")
    return ctx.exit()


@click.group(cls=KSDKGroup)
@click.option(
    "--version",
    is_flag=True,
    help=version,
    callback=display_ksdk_version,
    expose_value=False,
    is_eager=True,
)
@click.option(
    "--docs",
    is_flag=True,
    help=KSDKHelpMessages.docs,
    callback=display_ksdk_documentation_link,
    expose_value=False,
    is_eager=True,
)
@click.option(
    "--tree",
    is_flag=True,
    help=KSDKHelpMessages.tree_help,
    callback=display_command_tree,
    expose_value=False,
    is_eager=True,
)
def ksdk() -> None:
    """Kelvin SDK

    \b
    The complete tool to interact with the Kelvin Ecosystem.

    """


ksdk.add_command(app)
ksdk.add_command(apps)
ksdk.add_command(appregistry)
ksdk.add_command(auth)
ksdk.add_command(configuration)
ksdk.add_command(reset)
ksdk.add_command(secret)
ksdk.add_command(workload)
ksdk.add_command(info)
