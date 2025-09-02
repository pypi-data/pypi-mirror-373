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

import os
import re
import uuid
import webbrowser
from contextlib import contextmanager
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple, TypeVar, Union

from pydantic.v1 import ValidationError

from kelvin.sdk.lib.configs.general_configs import GeneralConfigs, GeneralMessages


def guess_delimiter(line: str, delimiters: Iterable[str] = ("\t", "\0", "|", ",")) -> str:
    """Guess delimiter in line.

    Parameters
    ----------
    line: str
        line of delimited text.
    delimiters: Iterable[str]
        delimiters to check.

    Returns
    -------
    str:
        the guessed delimiter string.

    """
    for delimiter in delimiters:
        if delimiter in line:
            return delimiter

    raise ValueError("Unknown delimiter")


def dict_to_yaml(content: dict, comment_header: Optional[Any] = None) -> str:
    """Convert a dictionary to a yaml.

    Parameters
    ----------
    content: dict
        the dictionary content to convert to the yaml format.

    comment_header: Optional[Any]
        the comment header to include in the yaml file. Do not include the '#' character.

    Returns
    -------
    str:
        A string with the yaml format content.

    """
    import io

    import ruamel.yaml as yaml

    yml = yaml.YAML()
    b = io.StringIO()

    if comment_header:
        # manually insert the comment header
        # ruamel.yaml is supposed to support comments but I can't get it to work
        b.write("# ")
        yml.dump(comment_header, b)

    yml.dump(content, b)
    return b.getvalue()


def get_url_encoded_string(original_string: str) -> str:
    """Return the url-encoded version of the provided string.

    Parameters
    ----------
    original_string : str
        the string to url encode

    Returns
    -------
    str:
        a url encoded string

    """
    import urllib.parse

    value = urllib.parse.quote(original_string)
    return str(value)


def standardize_string(value: str) -> str:
    """Given a specific value, replace its spaces and dashes with underscores to be snake-case compliant.

    Parameters
    ----------
    value: str
        the string to be 'standardized'.

    Returns
    -------
    str:
        the new, standardized string.

    """
    return re.sub(r"\s+|-", "_", value) if value else value


def camel_name(name: str) -> str:
    """Create camel-case name from name."""

    return re.sub(r"(^[a-z]|_+[a-zA-Z])", lambda x: x.group(1)[-1].upper(), standardize_string(name))


def open_link_in_browser(link: str) -> bool:
    """Open the specified link on the default web browser.

    Parameters
    ----------
    link: str
        the link to open

    Returns
    -------
    bool:
        a boolean indicating whether the link was successfully opened.
    """
    link_successfully_opened = webbrowser.open(link, new=2, autoraise=True)

    return link_successfully_opened


def get_requirements_from_file(file_path: Optional[Path]) -> List[str]:
    """
    When provided with a path to a requirements file, yield a list of its requirements.

    Parameters
    ----------
    file_path : Path
        the Path to the desired requirements file

    Returns
    -------
    List[str]
        a list containing all requirements in the file

    """
    if file_path and file_path.exists():
        content = file_path.read_text()
        split_lines = content.splitlines() if content else []
        return [entry for entry in split_lines if not entry.startswith("#")]
    return []


T = TypeVar("T", bound=MutableMapping[str, Any])


def merge(x: T, *args: Optional[Mapping[str, Any]], **kwargs: Any) -> T:
    """Merge two dictionaries.

    Parameters
    ----------
    x : dict
        the initial, mutable dictionary.
    args : Mapping[str, Any]
        the arguments to merge into the 'x' dictionary.
    kwargs : Any
        the keyword arguments to merge into the 'x' dictionary.

    Returns
    -------
    dictionary:
        the initial, mutated X dictionary.

    """
    if kwargs:
        args += (kwargs,)

    for arg in args:
        if arg is None:
            continue
        for k, v in arg.items():
            x[k] = merge(x.get(k, {}), v) if isinstance(v, Mapping) else v

    return x


def flatten(x: Mapping[str, Any]) -> Sequence[Tuple[str, Any]]:
    """Flatten nested mappings."""

    return [
        (k if not l else f"{k}.{l}", w)
        for k, v in x.items()
        for l, w in (flatten(v) if isinstance(v, Mapping) else [("", v)])  # noqa
    ]


def inflate(x: Mapping[str, Any], separator: str = ".", result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Inflate flattened keys via separator into nested dictionary."""

    if result is None:
        return inflate(x, separator, {})

    for k, v in x.items():
        if separator not in k:
            result[k] = v
            continue
        head, tail = k.split(separator, 1)
        if head not in result:
            result[head] = {}
        result[head].update(inflate({tail: v}, separator, result[head]))

    return result


def get_bytes_as_human_readable(input_bytes_data: Union[Optional[int], Optional[float]]) -> str:
    """When provided with bytes data, return its 'human-readable' version.

    Parameters
    ----------
    input_bytes_data : Union[Optional[int], Optional[float]]
        the input int that corresponds to the bytes value.

    Returns
    -------
    str:
        a string containing the human-readable version of the input.

    """
    if input_bytes_data:
        import humanize

        value = float(input_bytes_data)
        return humanize.naturalsize(value=value)

    return GeneralMessages.no_data_available


def get_iec_to_si_format_as_human_readable(input_data: str) -> str:
    """When provided with a str in iec format, return its 'human-readable' version. ex: 256Mi

    Parameters
    ----------
    input_data : str
        the input str in iec format. ex: 256Mi

    Returns
    -------
    str:
        a string containing the human-readable version of the input.

    """
    nist_steps = {
        "Bit": 1 / 8.0,
        "Byte": 1,
        "Ki": 1024,
        "Mi": 1048576,
        "Gi": 1073741824,
    }

    import re

    import humanize

    match = re.match(r"([0-9]+)([A-Z]i)", input_data, re.I)
    if match:
        value, unit = match.groups()
        memory_value = int(value) * nist_steps[unit]
        memory = humanize.filesize.naturalsize(memory_value, False, True, "%.0f")
        return memory

    return input_data


def get_datetime_as_human_readable(input_date: Union[float, Optional[datetime]]) -> str:
    """When provided with a datetime, retrieve its human readable form with the base date and its difference.

    Parameters
    ----------
    input_date : Union[float, Optional[datetime]]
        the datetime to display.

    Returns
    -------
    str:
        a string containing both the human readable datetime plus the difference to 'now'

    """
    if input_date:
        try:
            import humanize

            _input_date = input_date if isinstance(input_date, datetime) else datetime.fromtimestamp(float(input_date))
            now = datetime.now()
            diff = now.timestamp() - _input_date.timestamp()
            base_date = _input_date.strftime(GeneralConfigs.default_datetime_visualization_format)
            difference = humanize.naturaltime(timedelta(seconds=diff))
            message = GeneralConfigs.default_datetime_and_elapsed_display
            return message.format(base_date=base_date, now_minus_base_date=difference)
        except Exception:
            return str(input_date)

    return GeneralMessages.no_data_available


def parse_pydantic_errors(validation_error: ValidationError) -> str:
    """Parse the provided ValidationError and break it down to a 'pretty' string message.

    Parameters
    ----------
    validation_error : ValidationError
        the ValidationError to prettify.

    Returns
    -------
    str:
        a 'pretty' string with the parsed errors.

    """
    error_message: str = ""

    for error in validation_error.errors():
        error_message += f"\t{error.get('msg', '')}\n"

    return error_message


def get_files_from_dir(file_type: str, input_dir: str) -> List:
    """Retrieve all files of a given type from the specified directory.

    Parameters
    ----------
    file_type : str
        the file type to search for.
    input_dir : str
        the directory to read the files from.

    Returns
    -------
    List:
        the list of all matching files

    """
    if not file_type or not input_dir:
        raise ValueError(GeneralMessages.invalid_file_or_directory)

    return list(filter(lambda x: x.endswith(file_type), os.listdir(input_dir)))


def unique_items(items: List) -> List:
    """When provided with a list of items, retrieve the same list without duplicates
    and with the same order.

    Parameters
    ----------
    items : List
        the original list.

    Returns
    -------
    List:
        the ordered list.

    """
    found = set([])
    keep = []
    for item in items:
        if item not in found:
            found.add(item)
            keep.append(item)
    return keep


def lower(x: Any) -> Any:
    """Lower representation of data for serialisation."""

    if isinstance(x, (bool, int, float, str)) or x is None:
        return x

    if isinstance(x, Enum):
        return x.name

    if isinstance(x, Mapping):
        return {k: lower(v) for k, v in x.items()}

    if isinstance(x, Sequence):
        return [lower(v) for v in x]

    return x


@contextmanager
def chdir(path: Optional[Path]) -> Any:
    """Change working directory and return to previous on exit."""

    if path is None:
        yield
    else:
        prev_cwd = Path.cwd()
        try:
            os.chdir(path if path.is_dir() else path.parent)
            yield
        finally:
            os.chdir(prev_cwd)


def is_port_open(host: str, port: int) -> bool:
    """Check if a port is being used on a specific ip address"""
    import socket
    from contextlib import closing

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) == 0


def get_system_information(pretty_keys: bool = False) -> dict:
    """Get a dictionary with system-wide information.

    Parameters
    ----------
    pretty_keys: bool
        indicates whether it should yield a dictionary with raw data or a 'prettified' one.

    Returns
    -------
    dict:
        a dictionary containing all system information.
    """
    try:
        import platform
        import sys

        import psutil

        python_version = "Python version" if pretty_keys else "python-version"
        platform_title = "Platform" if pretty_keys else "platform"
        platform_release = "Platform release" if pretty_keys else "platform-release"
        platform_version = "Platform version" if pretty_keys else "platform-version"
        architecture = "Architecture" if pretty_keys else "architecture"
        processor = "Processor" if pretty_keys else "processor"
        ram = "RAM" if pretty_keys else "ram"
        venv = getattr(sys, "prefix", None) or getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None)
        venv_path = "Python (path)" if pretty_keys else "python-path"
        info = {
            python_version: sys.version.replace("\n", ""),
            venv_path: venv if venv else sys.prefix,
            platform_title: platform.system(),
            platform_release: platform.release(),
            platform_version: platform.version(),
            architecture: platform.machine(),
            processor: platform.processor(),
            ram: str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB",
        }
        return info

    except Exception:
        return {"error": "Could not retrieve system information."}


def ansi_escape_string(value: str) -> str:
    """When provided with a string, ansi-escape it.

    Parameters
    ----------
    value : str
        the string to ansi escape

    Returns
    -------
    str:
        The original, clean string.
    """
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", value)


def get_random_hex_string() -> str:
    """Yield a random hex string.

    Returns
    -------
    str:
        a random hex string

    """
    return str(uuid.uuid4())
