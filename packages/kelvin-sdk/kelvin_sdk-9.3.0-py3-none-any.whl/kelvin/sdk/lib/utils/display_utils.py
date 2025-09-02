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
from typing import Any, Dict, List, Optional, Union

from colorama import Fore
from tabulate import tabulate

from kelvin.api.client import DataModelBase
from kelvin.sdk.lib.configs.general_configs import GeneralMessages
from kelvin.sdk.lib.exceptions import MissingTTYException
from kelvin.sdk.lib.models.generic import GenericObject, OSInfo
from kelvin.sdk.lib.models.types import LogColor
from kelvin.sdk.lib.utils import logger_utils
from kelvin.sdk.lib.utils.logger_utils import logger


class DisplayObject:
    def __init__(self, raw_data: Any, tabulated_data: str):
        # The raw data associated with the DisplayObject. May be a dictionary, a Model object, etc.
        self.raw_data: Any = raw_data
        # For quick display purposes. A 'pretty' string for cli eye candy
        self.tabulated_data: str = tabulated_data

    @staticmethod
    def parse_entry(entry: Any) -> List:
        return_value = []
        if entry:
            if isinstance(entry, DataModelBase):
                return_value.append(entry.dict())
            elif isinstance(entry, dict):
                return_value.append(entry)
            elif isinstance(entry, DisplayObject):
                return_value.extend(entry.parsed_data)
            elif isinstance(entry, GenericObject):
                return_value.append(entry.to_dict())
        return return_value

    @property
    def parsed_data(self) -> List[dict]:
        """The DisplayObject is usually associated with a model info.
        Treat the 'parsed data' as the dict representation of that model.
        No need to process the data if its already in its dict format.

        Returns
        -------
        List[dict]
            the parsed data in a list of dictionaries.

        """
        return_value = []
        if self.raw_data:
            if isinstance(self.raw_data, List):
                for item in self.raw_data:
                    return_value += self.parse_entry(entry=item)
            else:
                return_value += self.parse_entry(entry=self.raw_data)

        return return_value


# Utils functions
def display_yes_or_no_question(question: str, default: str = "no") -> bool:
    """Ask a yes/no question via raw_input() and return their answer.

    It must be "yes" (the default), "no" or None (meaning an answer is required of the user).

    Parameters
    ----------
    question : str
        is a string that is presented to the user.
    default : str
        is the presumed answer if the user just hits <Enter>.

    Returns
    -------
    bool:
        The "answer" return value is True for "yes" or False for "no".

    """
    valid = {"yes": True, "y": True, "no": False, "n": False}

    if not (sys.__stdout__.isatty() if sys.__stdout__ else False):
        raise MissingTTYException(message="")

    if default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        prompt = " [y/n] "

    if question:
        logger.warning(f"\n{question}")
    sys.stdout.write(GeneralMessages.are_you_sure_question.format(prompt=prompt))
    choice = input().lower()
    sys.stdout.write("\n")
    if default is not None and choice == "":
        return valid[default]
    elif choice in valid:
        return valid[choice]
    else:
        logger.warning(GeneralMessages.provide_a_valid_response)
        return False


def display_data_entries(
    data: List,
    attributes: List[str],
    header_names: List[str],
    table_title: str,
    should_display: bool = True,
    no_data_message: Optional[str] = None,
) -> DisplayObject:
    """Display generic resource data on the screen.

    Will yield the first 10 results (if any is returned) to prevent an overwhelming console output.

    If this is the case, a prompt will ask whether the user wishes to see more outputs.

    Parameters
    ----------
    data: List
        the data to be printed. Usually, a list of dictionaries.
    attributes: List[str]
        the data attributes.
    header_names: List[str]
        the 'pretty' keys to be displayed atop the table.
    table_title: str
        the title to be displayed atop the table.
    should_display: bool
        indicates whether it should print the result.
    no_data_message: str
        the custom message to be displayed on the table if no data is passed.

    Returns
    -------
    DisplayObject:
        a symbolic boolean flag indicating the display of entries was successful.

    """
    data_to_tabulate = [
        [entry.get(attribute) if isinstance(entry, dict) else getattr(entry, attribute) for attribute in attributes]
        for entry in data
    ]
    total_entries = len(data_to_tabulate)
    tabulated_data_as_str = ""
    if total_entries:
        tabulated_data = tabulate(data_to_tabulate, headers=header_names, tablefmt="psql", floatfmt=".2f")
        title = success_colored_message(message=table_title)
        tabulated_data_as_str += f"{title}\n{tabulated_data}\n"
        if should_display:
            logger.info(tabulated_data_as_str)
    else:
        if no_data_message is None:
            no_data_message = GeneralMessages.no_data_yielded
        tabulated_data_as_str += error_colored_message(message=no_data_message)
        if should_display:
            logger.warning(tabulated_data_as_str)

    return DisplayObject(raw_data=data, tabulated_data=tabulated_data_as_str)


def display_data_object(
    data: Union[DataModelBase, Dict], object_title: Optional[str] = None, should_display: bool = True
) -> DisplayObject:
    """Displays the provided data object, be it an app or a node, in a simple, yaml-like format.

    Parameters
    ----------
    data: Union[DataModelBase, Dict]
        the data object to be displayed on screen.
    object_title:  Optional[str]
        the title to display above the object.
    should_display: bool
        indicates whether it should print the result.

    Returns
    -------
    DisplayObject:
        a symbolic boolean flag indicating the display of the object was successful.

    """
    data_as_dict = data.dict() if isinstance(data, DataModelBase) else data

    tabulated_data = ""
    if data_as_dict:
        indented_data = pretty_colored_content(data_as_dict)
        title = success_colored_message(message=f"\n{object_title}\n") if object_title else ""
        tabulated_data += f"{title}{indented_data}\n"
        if should_display:
            logger.info(tabulated_data)
    else:
        tabulated_data += error_colored_message(message=GeneralMessages.no_data_yielded)
        if should_display:
            logger.warning(tabulated_data)

    return DisplayObject(raw_data=data, tabulated_data=tabulated_data)


# Utils
def pretty_colored_content(
    content: dict, initial_indent: int = 1, indent: int = 1, level: int = 0, show_arm: bool = False
) -> str:
    """When provided with a dictionary, return the colorized, 'prettified' yaml-like object.

    Parameters
    ----------
    content: dict
        the content to 'prettify'
    initial_indent: int
        the initial indent dimension to split on.
    indent: int
        the initial indent dimension to split on.
    level: int
        variable to track the level of display.
    show_arm: bool
        indicate whether the 'pretty arm' should be displayed before a key.

    Returns
    -------
    str:
        a 'pretty', indented yaml-like object.

    """
    final_result = ""

    if not OSInfo.is_posix:
        show_arm = False

    for key, value in content.items():
        pretty_key = success_colored_message(message=key)
        total_indent = "  " * initial_indent
        arm_item = "└── " if level > 0 and show_arm else ""
        final_result += f"\n{total_indent}{arm_item}{str(pretty_key)}:"
        value = _safe_load(input=value)
        if isinstance(value, dict):
            final_result += pretty_colored_content(value, initial_indent + indent, indent, level + 1, show_arm)
        elif isinstance(value, List):
            for item in value:
                if isinstance(item, dict):
                    final_result += pretty_colored_content(item, initial_indent + indent, indent, level + 1, show_arm)
                else:
                    final_result += f"\n{total_indent}   - {str(item)}"  # noqa: E221
        else:
            final_result += f" {str(value)}"

    return final_result


def success_colored_message(message: str) -> str:
    """Yield a 'green colored' message.

    Parameters
    ----------
    message : str
        the message to yield in the success format.

    Returns
    -------
    str

    """
    prefix = Fore.GREEN if logger_utils.LOG_COLOR == LogColor.COLORED else ""
    suffix = Fore.RESET if logger_utils.LOG_COLOR == LogColor.COLORED else ""
    return prefix + message + suffix


def warning_colored_message(message: str) -> str:
    """Yield a 'orange colored' message.

    Parameters
    ----------
    message : str
        the message to yield in the warning format.

    Returns
    -------
    str

    """
    prefix = Fore.YELLOW if logger_utils.LOG_COLOR == LogColor.COLORED else ""
    suffix = Fore.RESET if logger_utils.LOG_COLOR == LogColor.COLORED else ""
    return prefix + message + suffix


def error_colored_message(message: str) -> str:
    """Yield a 'red colored' message.

    Parameters
    ----------
    message : str
        the message to yield in the error format.

    Returns
    -------
    str

    """
    prefix = Fore.RED if logger_utils.LOG_COLOR == LogColor.COLORED else ""
    suffix = Fore.RESET if logger_utils.LOG_COLOR == LogColor.COLORED else ""
    return prefix + message + suffix


def _safe_load(input: Any) -> bool:
    try:
        import json

        result = json.loads(input)
        return result
    except Exception:
        return input
