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

import logging
import sys
from json import JSONEncoder
from pathlib import Path
from typing import Any, Optional, Union

import structlog
from colorama import Fore

from kelvin.sdk.lib.models.types import LogColor, LogType

RELEVANT = 25
KSDK_LOGGER_NAME = "kelvin.sdk"
KELVIN_SDK_CLIENT_LOGGER_NAME = "kelvin.api.client"
LOG_COLOR = LogColor.COLORLESS


class BaseLogFormatter(logging.Formatter):
    pass


class KSDKLogFormatter(BaseLogFormatter):
    """
    Logging Formatter to add colors and count warning / errors
    """

    def __init__(self, log_color: Optional[LogColor] = None, debug: bool = False) -> None:
        is_atty: bool = sys.__stdout__.isatty() if sys.__stdout__ else False
        # 1 - if it is not a tty, dont bother setting the color
        if not is_atty or not log_color:
            log_color = LogColor.COLORLESS
        global LOG_COLOR
        LOG_COLOR = log_color
        self.log_color = log_color
        self.debug = debug
        super().__init__()

    # Default format
    message_format = "[%(logger)s][%(asctime)s][%(levelname).1s] %(message)s"

    FORMATS = {
        LogColor.COLORED: {
            logging.DEBUG: Fore.CYAN + message_format + Fore.RESET,
            logging.INFO: Fore.RESET + message_format + Fore.RESET,
            RELEVANT: Fore.GREEN + message_format + Fore.RESET,
            logging.WARNING: Fore.YELLOW + message_format + Fore.RESET,
            logging.ERROR: Fore.RED + message_format + Fore.RESET,
            logging.CRITICAL: Fore.RED + message_format + Fore.RESET,
        },
        LogColor.COLORLESS: {
            logging.DEBUG: message_format,
            logging.INFO: message_format,
            RELEVANT: message_format,
            logging.WARNING: message_format,
            logging.ERROR: message_format,
            logging.CRITICAL: message_format,
        },
    }

    def format(self, record: Any) -> str:
        if not self.debug:
            record.exc_info = None
        if record and (record.name == KSDK_LOGGER_NAME or record.name.startswith(KELVIN_SDK_CLIENT_LOGGER_NAME)):
            log_fmt = self.FORMATS.get(self.log_color, {}).get(record.levelno, "")
            formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
            return formatter.format(record)
        else:
            return super().format(record)


class JSONLogFormatter(BaseLogFormatter):
    def __init__(self, debug: bool = False) -> None:
        super().__init__()
        self.debug = debug

    def format(self, record: Any) -> str:
        if not self.debug:
            record.exc_info = None
        return super().format(record)


def relevant(parent: Any, msg: str, *args: Any, **kwargs: Any) -> None:
    ksdk_level = kwargs.get("extra", {}).get("ksdk_level", RELEVANT)
    return parent.log(ksdk_level, msg or "", *args, **kwargs)


def _filter_kelvin_sdk_client_messages(_logger: Any, _: Any, event_dict: Any) -> dict:
    if _logger and event_dict and _logger.name.startswith(KELVIN_SDK_CLIENT_LOGGER_NAME):
        event_dict["event"] = str(event_dict)
        event_dict["logger"] = KSDK_LOGGER_NAME
    return event_dict


def _json_conversion(obj: Union[Union[dict, list], Any]) -> Union[Union[dict, list], str]:
    if isinstance(obj, dict):
        # Assume dates won't be keys
        return {k: _json_conversion(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_json_conversion(v) for v in obj]
    return str(obj)


def _json_value_to_str_conversion(_: Any, __: Any, event: Any) -> Union[Union[dict, list], str]:
    return _json_conversion(event)


def _setup_logger(
    log_type: LogType = LogType.KSDK,
    log_color: LogColor = LogColor.COLORED,
    debug: bool = False,
    history_file: Optional[Path] = None,
) -> None:
    # Setting the level and adding the relevant level to structlog
    logging.root.handlers.clear()
    logging.addLevelName(RELEVANT, "RELEVANT")
    structlog.stdlib._FixedFindCallerLogger.relevant = relevant  # type: ignore
    structlog.stdlib._NAME_TO_LEVEL["relevant"] = RELEVANT  # type: ignore
    structlog.stdlib.BoundLogger.relevant = relevant  # type: ignore
    structlog.stdlib.RELEVANT = RELEVANT  # type: ignore

    base_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        _filter_kelvin_sdk_client_messages,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
    ]

    log_formatter: BaseLogFormatter
    if log_type == LogType.JSON:
        log_formatter = JSONLogFormatter(debug=debug)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(log_formatter)
        logging.root.addHandler(stream_handler)
        base_processors += [
            _json_value_to_str_conversion,
            structlog.processors.JSONRenderer(cls=JSONEncoder, indent=1, sort_keys=True),
        ]
    else:
        log_formatter = KSDKLogFormatter(log_color=log_color, debug=debug)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(log_formatter)
        logging.root.addHandler(stream_handler)
        base_processors += [
            structlog.processors.TimeStamper(fmt="[%Y-%m-%d %H:%M:%S]", utc=False),
            structlog.stdlib.render_to_log_kwargs,
        ]

    if history_file:
        if history_file.exists() and history_file.stat().st_size >= 1500000:
            history_file.unlink()
        if log_type == LogType.KSDK:  # for the kelvin-sdk specific formatter, make it colorless
            log_formatter = KSDKLogFormatter(log_color=log_color, debug=debug)
        file_handler = logging.FileHandler(filename=history_file)
        file_handler.setFormatter(log_formatter)
        logging.root.addHandler(file_handler)

    # Configure
    structlog.configure(
        processors=base_processors,  # type: ignore
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=False,
    )


def _set_verbose_level(verbose: bool = False) -> Any:
    verbose_level = logging.DEBUG if verbose else logging.INFO
    ksdk_logger = logging.getLogger(KSDK_LOGGER_NAME)
    kelvin_sdk_client_logger = logging.getLogger(KELVIN_SDK_CLIENT_LOGGER_NAME)
    if ksdk_logger.level == logging.NOTSET or verbose_level <= logging.DEBUG:
        kelvin_sdk_client_logger.setLevel(level=verbose_level)
        ksdk_logger.setLevel(level=verbose_level)
        logging.basicConfig(format="", stream=sys.stdout, level=verbose_level)


def setup_logger(
    log_type: LogType = LogType.KSDK,
    log_color: LogColor = LogColor.COLORED,
    verbose: bool = False,
    debug: bool = False,
    history_file: Optional[Path] = None,
) -> Any:
    global logger
    _setup_logger(log_type=log_type, log_color=log_color, debug=debug, history_file=history_file)
    _set_verbose_level(verbose=verbose)
    logger = structlog.get_logger(KSDK_LOGGER_NAME)
    return logger


logger = setup_logger()
