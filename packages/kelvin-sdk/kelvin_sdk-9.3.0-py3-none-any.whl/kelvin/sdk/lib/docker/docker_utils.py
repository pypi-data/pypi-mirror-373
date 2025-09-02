import json
from time import sleep
from typing import Any, Dict, Generator, List

from kelvin.sdk.lib.configs.docker_configs import DockerConfigs
from kelvin.sdk.lib.exceptions import DependencyNotRunning, KDockerException
from kelvin.sdk.lib.models.ksdk_docker import DockerProgressEntry
from kelvin.sdk.lib.models.types import LogColor
from kelvin.sdk.lib.utils import logger_utils


def display_docker_progress(stream: Generator) -> bool:
    """When provided with a docker stream generator, display the overall progress of all layer involved.

    Parameters
    ----------
    stream: Generator
        a docker stream generator that outputs every entry of the process

    Returns
    -------
    bool
        Return a bool indicating all progress info has been successfully displayed
    """
    from tqdm import tqdm

    # 1 - a dictionary to keep track of all layers
    all_layers: Dict[str, tqdm] = {}
    colour = "WHITE" if logger_utils.LOG_COLOR == LogColor.COLORED else None
    layer_index = 0
    for log_entry in stream:
        entries = process_docker_image_progress_entry(entry=log_entry)
        for item in entries:
            layer_id = item.id
            layer_status = item.status
            layer_progress = item.progress or ""
            if layer_id:
                if layer_id not in all_layers.keys():
                    layer_base_description = DockerConfigs.layer_base_description.format(layer_id=layer_id)
                    all_layers[layer_id] = tqdm(
                        total=100,
                        desc=layer_base_description,
                        position=layer_index,
                        bar_format=DockerConfigs.progress_bar_format,
                        leave=True,
                        dynamic_ncols=True,
                        colour=colour,
                    )
                    layer_index += 1
                else:
                    tracker = all_layers.get(layer_id, None)
                    if tracker:
                        params = {"layer_id": layer_id, "status": layer_status, "progress": layer_progress}
                        description = DockerConfigs.layer_download_success_description.format_map(params)
                        tracker.set_description_str(description)
                        tracker.refresh()
                        sleep(0.01)

    for tracker in all_layers.values():
        tracker.close()
        tracker.clear()

    return True


def process_docker_image_progress_entry(entry: bytes) -> List[DockerProgressEntry]:
    """Print the docker image push progress entry from its rightful dict.

    Parameters
    ----------
    entry: bytes
        A dictionary containing the docker image progress entry.

    Returns
    -------
    List[DockerProgressEntry]
        A list of docker progress entries the result of the processed entry object.

    """
    try:
        split_entry = str(entry, "utf-8").split("\n")
        clean_entries = [json.loads(entry) for entry in split_entry if entry]
        return [DockerProgressEntry(**loaded_entry) for loaded_entry in clean_entries]
    except Exception:
        dockerfile_progress_entry: List[DockerProgressEntry] = []

    return dockerfile_progress_entry


def process_docker_entry(entry: bytes) -> str:
    """Print the datatype compilation entry from its raw string.

    Parameters
    ----------
    entry: bytes
        A byte string containing the datatype compilation entry.

    Returns
    -------
    str
        A string containing the result of the processed entry object.

    """
    try:
        dockerfile_build_entry = entry.decode("utf-8").replace("\n", "")
    except Exception:
        dockerfile_build_entry = ""

    return dockerfile_build_entry


def ensure_docker_is_running(function: Any) -> Any:
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        docker_dependency = DockerConfigs.docker_dependency
        try:
            docker_is_running = self._docker_client.ping()
        except Exception as exc:
            docker_is_running = exc is None

        if not docker_is_running:
            raise DependencyNotRunning(message=docker_dependency)

        return function(self=self, *args, **kwargs)

    return wrapper


def assess_docker_connection_exception(exc: Exception) -> KDockerException:
    """Parse the provided exception and return a 'pretty' docker exception.

    Parameters
    ----------
    exc: Exception
        the exception to verify.

    Returns
    -------
    Exception
        an exception with the adequate result.

    """

    docker_api_not_available: str = f"""\n
        Error accessing the local Docker instance.
        Please ensure Docker is running and its service is accessible.\n
        More information:
            > Using a system installation - https://docs.docker.com/config/daemon/
            > Using Docker Desktop - https://docs.docker.com/docker-for-windows/install/#start-docker-desktop

        Detailed error:
            {str(exc)}

    """
    return KDockerException(docker_api_not_available)
