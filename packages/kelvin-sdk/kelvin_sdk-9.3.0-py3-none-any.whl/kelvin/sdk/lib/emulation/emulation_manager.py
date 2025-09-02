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

from typing import List, Optional, Union

from docker.types import CancellableStream

from kelvin.sdk.lib.configs.docker_configs import DockerConfigs
from kelvin.sdk.lib.configs.emulation_configs import ControlManagerConfigs, EmulationConfigs, StudioConfigs
from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.docker.docker_manager import DockerManager
from kelvin.sdk.lib.exceptions import EmulationException
from kelvin.sdk.lib.models.apps.ksdk_app_setup import ProjectEmulationObject
from kelvin.sdk.lib.models.factories.app_setup_configuration_objects_factory import get_default_app_name
from kelvin.sdk.lib.models.factories.docker_manager_factory import get_docker_manager
from kelvin.sdk.lib.models.generic import GenericObject, KPath
from kelvin.sdk.lib.models.ksdk_docker import DockerContainer, DockerImage, DockerImageName, KSDKDockerVolume
from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.schema.schema_manager import get_latest_app_schema_version, validate_app_schema_from_app_config_file
from kelvin.sdk.lib.session.session_manager import session_manager
from kelvin.sdk.lib.utils.display_utils import display_data_entries
from kelvin.sdk.lib.utils.general_utils import open_link_in_browser
from kelvin.sdk.lib.utils.logger_utils import logger


# 1 - Studio
def studio_start(
    schema_file: Optional[str] = None,
    input_file: Optional[str] = None,
    port: int = StudioConfigs.default_port,
    open_browser: bool = False,
) -> OperationResponse:
    """
    Starts Kelvin Studio to modify the provided input.

    Parameters
    ----------
    schema_file: Optional[str]
        the schema file used to power the Kelvin Studio's interface.
    input_file: Optional[str]
        the input file to modify based on the schema file..
    port: int
        the studio server port.
    open_browser: bool
        Indicates whether Kelvin Studio should be automatically opened on the default browser.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the kelvin studio start.

    """
    try:
        studio_configs = StudioConfigs(port=port)
        if studio_configs.is_port_open():
            raise EmulationException(f"Port {studio_configs.port} already in use")

        # 1 - Load all the input files
        schema_file_path: KPath
        if not schema_file:
            _, _, schema_file_path = get_latest_app_schema_version()
        else:
            schema_file_path = KPath(schema_file)

        schema_file_path = schema_file_path.complete_path().absolute()

        if not schema_file_path.exists():
            raise FileNotFoundError(f"File not found {schema_file_path.absolute()}")

        default_app_yaml: str = GeneralConfigs.default_app_config_file
        input_file_path = KPath(input_file if input_file else default_app_yaml).complete_path().absolute()

        if not input_file_path or (input_file_path and not input_file_path.exists()):
            raise FileNotFoundError("Please provide a valid input file")

        logger.info("Starting Kelvin Studio")

        # 2 - setup the binds, port mapping and arguments
        volumes: List = []
        arguments: List = []
        if schema_file_path:
            studio_schema_file_bind = StudioConfigs.studio_schema_file_bind.format(
                schema_file_path=str(schema_file_path), schema_file_name=schema_file_path.name
            )
            volumes.append(studio_schema_file_bind)
            arguments.append(schema_file_path.name)
        if input_file_path:
            studio_input_file_bind = StudioConfigs.studio_input_file_bind.format(
                input_file_path=str(input_file_path), input_file_name=input_file_path.name
            )
            volumes.append(studio_input_file_bind)
            arguments.append(input_file_path.name)

            if input_file:
                logger.info(f'Configuring "{str(input_file)}"')

        url_metadata = session_manager.get_current_session_metadata()
        studio_app_name = url_metadata.sdk.components.kelvin_studio
        environment_variables = {}
        environment_variables.update({"docker_exposed_port": studio_configs.port})

        # 1 - Jumpstart the application
        docker_manager = get_docker_manager()
        docker_manager.ensure_docker_image_exists(docker_image=studio_app_name)

        project_emulation_object = ProjectEmulationObject(
            app_name=studio_app_name,
            volumes=volumes,
            port_mapping={studio_configs.port: studio_configs.port},
            ports=[(studio_configs.port, "tcp")],
            arguments=arguments,
            environment_variables=environment_variables,
            is_external_app=True,
        )
        successfully_started = emulation_start(project_emulation_object=project_emulation_object)

        if successfully_started.success:
            browser_url = studio_configs.get_url()
            studio_start_success: str = f"""

                    Kelvin Studio successfully started!
                    Use your browser of choice to access it on: \"{browser_url}\"

                    Opening Kelvin Studio...

                """
            logger.relevant(studio_start_success)
            if open_browser:
                import time

                time.sleep(3)
                open_link_in_browser(browser_url)

        return successfully_started
    except Exception as exc:
        error_message = f"Error starting Kelvin Studio: {str(exc)}"
        logger.error(error_message)
        return OperationResponse(success=False, log=error_message)


def studio_stop() -> OperationResponse:
    """
    Stops a Kelvin Studio.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the kelvin studio stop.

    """
    try:
        logger.info("Stopping Kelvin Studio")

        url_metadata = session_manager.get_current_session_metadata()
        studio_app_name = url_metadata.sdk.components.kelvin_studio

        docker_manager = get_docker_manager()
        docker_manager.stop_containers(image_names=[studio_app_name])

        message = "Kelvin Studio successfully stopped"
        logger.relevant(message)
        return OperationResponse(success=True, log=message)

    except Exception as exc:
        error_message = f"Error stopping Kelvin Studio: {str(exc)}"
        logger.error(error_message)
        return OperationResponse(success=False, log=error_message)


# 2 - Server Oriented
def emulation_start_server(
    app_name_with_version: Optional[str] = None, app_config: Optional[str] = None, tail: Optional[int] = None
) -> OperationResponse:
    """
    Start an application on the emulation system.

    Parameters
    ----------
    app_name_with_version: Optional[str]
        the application's name.
    app_config: Optional[str]
        the app configuration file to be used on the emulation.
    tail: Optional[int]
        the application's emulation object.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating whether the app was successfully started.

    """
    try:
        project_emulation_object = load_base_emulation_object(
            app_config=app_config, app_name_with_version=app_name_with_version
        )
        project_emulation_object.tail = tail
        project_emulation_object.should_print = False
        project_emulation_object.follow = False
        project_emulation_object.show_logs = False

        return emulation_start(project_emulation_object=project_emulation_object)
    except Exception as exc:
        error_message = f"Error emulating application: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


# 3 - General Emulation
def emulation_start_simple(
    app_name_with_version: Optional[str] = None,
    app_config: Optional[str] = None,
    show_logs: bool = False,
) -> OperationResponse:
    """
    Start an application on the emulation system.

    Parameters
    ----------
    app_name_with_version: Optional[str]
        the application's name.
    app_config: Optional[str]
        the app configuration file to be used on the emulation.
    show_logs: bool
        if provided, will start displaying logs once the app is emulated.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating whether the app was successfully started.
    """
    try:
        project_emulation_object = load_base_emulation_object(
            app_name_with_version=app_name_with_version, app_config=app_config
        )
        project_emulation_object.show_logs = show_logs
        return emulation_start(project_emulation_object=project_emulation_object)
    except Exception as exc:
        error_message = f"Error emulating application: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def emulation_start(project_emulation_object: ProjectEmulationObject) -> OperationResponse:
    """
    Start an application on the emulation system.

    - Start off by retrieving the current Docker Manager.
    - Setup and start the emulation system
    - Start the application.

    Parameters
    ----------
    project_emulation_object: ProjectEmulationObject
        the application's emulation object.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating whether the app was successfully started.

    """
    try:
        docker_manager = get_docker_manager()

        _start_ksdk_emulation_system(docker_manager=docker_manager)

        return _raw_emulation_start(project_emulation_object=project_emulation_object, docker_manager=docker_manager)

    except Exception as exc:
        error_message = f"Error emulating application: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def _raw_emulation_start(
    project_emulation_object: ProjectEmulationObject, docker_manager: DockerManager
) -> OperationResponse:
    """
    Internal function.
    Assumes both KSDK Network and Broker are already up and running.
    Simply starts the applications

    Parameters
    ----------
    project_emulation_object: ProjectEmulationObject
        the application's emulation object.
    docker_manager : DockerManager
        the object that encapsulates the docker utility instance.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating whether the app was successfully started.

    """
    # 1 - Build the DockerImageName object for the application
    docker_image_name = DockerImageName.parse(name=project_emulation_object.emulation_app_name)

    # 2 - Find the provided application. If it does not exist, attempt to retrieve the registry's counterpart
    if docker_manager.check_if_docker_image_exists(docker_image_name=docker_image_name.raw_name, raise_exception=True):
        project_emulation_object.app_name = docker_image_name.raw_name
        logger.info(f'Loading configuration and starting the application "{project_emulation_object.app_name}"')

    # 3 - If an app configuration is provided, its schema must be validated.
    if project_emulation_object.app_config_path:
        validate_app_schema_from_app_config_file(app_config_file_path=KPath(project_emulation_object.app_config_path))

    # 4 - Run the image with the host config
    image_was_ran = docker_manager.run_app_docker_image(project_emulation_object=project_emulation_object)

    if not image_was_ran:
        raise EmulationException(f'Error starting pre-built application "{project_emulation_object.app_name}"')

    message = f'Application successfully launched: "{project_emulation_object.app_name}"'
    logger.relevant(message)

    if project_emulation_object.show_logs:
        return emulation_logs(
            app_name_with_version=project_emulation_object.app_name,
            tail=project_emulation_object.tail,
            should_print=project_emulation_object.should_print,
            stream=project_emulation_object.stream,
            follow=project_emulation_object.follow,
        )

    return OperationResponse(success=True, log=message)


def emulation_reset() -> OperationResponse:
    """
    Reset the emulation system.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the emulation system reset.

    """
    try:
        logger.relevant("Resetting the Emulation System")
        containers: List[DockerContainer] = get_all_emulation_system_running_containers(should_display=False).data
        docker_manager = get_docker_manager()

        for container in containers:
            emulation_stop(app_name_with_version=container.image_name)

        successfully_reset = _stop_ksdk_network(docker_manager=docker_manager)

        # Last but not least, purge the temporary directory for the emulation
        session_manager.get_global_ksdk_configuration().ksdk_temp_dir_path.delete_dir()
        success_message = "Emulation System successfully reset"
        logger.relevant(success_message)
        return OperationResponse(success=successfully_reset.success, log=success_message)

    except Exception as exc:
        error_message = f"Error resetting the Emulation System: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def emulation_stop(
    app_name_with_version: Optional[str] = None, container_name: Optional[str] = None
) -> OperationResponse:
    """
    Stop a running application on the emulation system.

    Parameters
    ----------
    app_name_with_version: Optional[str]
        the name of the app to stop.
    container_name: Optional[str]
        the name of the container to stop.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating a message indicating whether the application was successfully stopped.

    """
    try:
        # 1 - can either be an application or a container (app_name_with_version)
        if container_name is None:
            # 2.1 - if the app_name_with_version (or container_name) exists, take it
            # 2.2 - if not, attempt to load the current directory's app.yaml
            app_name_with_version = app_name_with_version or get_default_app_name()
            # 2.1.1 - in case its actually a container_name, set the variable "container_name" with it and 'nullify'
            # the "app_name_with_version" to avoid further confusion
            if ".app" in app_name_with_version:
                container_name = app_name_with_version
                app_name_with_version = None
        # 2 - In this case, its a container. The "app_name_with_version" will be 'nullified' to avoid further confusion.
        else:
            app_name_with_version = None

        docker_manager = get_docker_manager()

        # 2 - Round up the container and image names to stop
        image_names_to_stop: Optional[List[str]] = None
        container_names_to_stop: Optional[List[str]] = None

        stopping_message: str = ""
        successfully_stopped_message: str = ""

        if container_name:
            container_names_to_stop = [container_name]
            stopping_message = f'Attempting to stop container "{container_name}"'
            successfully_stopped_message = f'Container "{container_name}" successfully stopped.'
        elif app_name_with_version:
            image_names_to_stop = [app_name_with_version]
            stopping_message = f'Attempting to stop application "{app_name_with_version}"'
            successfully_stopped_message = f'Application "{app_name_with_version}" successfully stopped.'

        logger.info(stopping_message)
        container_stopped = docker_manager.stop_containers(
            image_names=image_names_to_stop, container_names=container_names_to_stop
        )

        # 3 - Report the result
        result_message: str = successfully_stopped_message

        if container_stopped:
            logger.relevant(result_message)
        else:
            result_message = "No running instances of the provided application were found"
            logger.warning(result_message)

        return OperationResponse(success=container_stopped, log=result_message)

    except Exception as exc:
        error_message = f"Error stopping application: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def emulation_logs(
    app_name_with_version: Optional[str],
    tail: Optional[int] = None,
    should_print: bool = True,
    stream: bool = True,
    follow: bool = False,
) -> OperationResponse:
    """
    Display the logs of a running application.

    Parameters
    ----------
    app_name_with_version: Optional[str]
        the name of the application to retrieve the logs from.
    tail: Optional[int]
        indicates whether it should tail the logs and return.
    should_print: bool
        indicates whether the logs should be printed.
    stream: bool
        indicates whether it should return the stream in the response.
    follow: bool
        indicates whether it should follow the logs stream.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object indicating the logs were successfully obtained.

    """
    try:
        app_name_with_version = app_name_with_version or get_default_app_name()

        docker_manager = get_docker_manager()

        if ".app" in app_name_with_version:
            containers = docker_manager.get_docker_containers(container_names=[app_name_with_version])
        else:
            containers = docker_manager.get_docker_containers(image_names=[app_name_with_version])

        successful_logs = docker_manager.get_logs_for_docker_container(
            containers=containers, stream=stream, tail=tail, follow=follow
        )

        if not successful_logs:
            raise EmulationException(message=f'No logs found for the provided application "{app_name_with_version}"')

        if should_print:
            _print_log_stream(log_stream=successful_logs)
            return OperationResponse(success=True)

        if stream:
            return OperationResponse(success=True, stream=successful_logs)
        else:
            return OperationResponse(success=True, data=successful_logs)

    except Exception as exc:
        error_message = f"Error retrieving logs for the provided application: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, log=error_message)


def get_local_appregistry_images(should_display: bool = False) -> OperationResponse:
    """
    Retrieve the list of all application images available on the local registry.

    Parameters
    ----------
    should_display: bool
        specifies whether or not output data should be displayed.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the app images available on the local registry.

    """
    try:
        logger.info("Retrieving applications from the Local Application Registry..")
        ksdk_labels = DockerConfigs.ksdk_base_identification_label

        docker_manager = get_docker_manager()
        existing_ksdk_images: List[DockerImage] = docker_manager.get_docker_images(labels=ksdk_labels)

        filtered_ksdk_images = [
            GenericObject(data={"tag": tag, "readable_created_date": image.readable_created_date})
            for image in existing_ksdk_images
            if any("<none>" not in tag for tag in image.tags)
            for tag in image.tags
        ]

        if should_display:
            display_data_entries(
                data=filtered_ksdk_images,
                header_names=["Applications", "Created"],
                attributes=["tag", "readable_created_date"],
                table_title=GeneralConfigs.table_title.format(title="Existing Apps"),
                no_data_message="No applications available on the Local Application Registry",
            )

        return OperationResponse(success=True, data=existing_ksdk_images)

    except Exception as exc:
        error_message = f"Error retrieving application information: {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, data=[])


def get_emulation_system_native_containers(running: bool = True) -> List[DockerContainer]:
    """

    Return all emulation system native applications in the emulation system.

    Parameters
    ----------
    running : bool
        if set to True, will return only running containers

    Returns
    -------
    List[DockerContainer]
        the list of docker containers that match the criteria.

    """
    docker_manager = get_docker_manager()
    emulation_system_native_containers: List[DockerContainer] = docker_manager.get_docker_containers(
        container_names=[container.container_name for container in _emulation_system_native_services()]
    )
    return [container for container in emulation_system_native_containers if container.running == running]


def get_emulation_system_app_containers(running: bool = True) -> List[DockerContainer]:
    """
    Return kelvin application containers in the emulation system.

    Parameters
    ----------
    running : bool
        if set to True, will return only running containers

    Returns
    -------
    List[DockerContainer]
        the list of docker containers that match the criteria.

    """
    ksdk_labels = DockerConfigs.ksdk_base_identification_label

    docker_manager = get_docker_manager()
    existing_ksdk_containers: List[DockerContainer] = docker_manager.get_docker_containers(labels=ksdk_labels)
    return [container for container in existing_ksdk_containers if container.running == running]


def get_all_emulation_system_running_containers(should_display: bool = False) -> OperationResponse:
    """
    Retrieve the list of all running containers in the Emulation System.

    Parameters
    ----------
    should_display: bool
        specifies whether or not output data should be displayed.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object wrapping the containers running in the Emulation System

    """
    try:
        logger.info("Retrieving applications on the Emulation System..")

        # 1 - emulation system native containers
        emulation_system_native_containers: List[DockerContainer] = get_emulation_system_native_containers()
        # 2 - yield running containers built by kelvin-sdk
        emulation_system_app_containers: List[DockerContainer] = get_emulation_system_app_containers()

        if should_display:
            display_data_entries(
                data=emulation_system_native_containers,
                header_names=["Application", "Container", "Status", "Local IP Address", "Ports (container->host)"],
                attributes=[
                    "image_name",
                    "container_names",
                    "container_status_for_display",
                    "ip_address",
                    "container_ports_for_display",
                ],
                table_title=EmulationConfigs.emulation_system_native_applications_message,
                no_data_message="No Emulation System Native Applications currently running",
            )
            display_data_entries(
                data=emulation_system_app_containers,
                header_names=[
                    "Application",
                    "Container",
                    "Status",
                    "Local IP Address",
                    "Ports (container->host)",
                    "Mounts",
                ],
                attributes=[
                    "image_name",
                    "container_names",
                    "container_status_for_display",
                    "ip_address",
                    "container_ports_for_display",
                    "container_mounts_for_display",
                ],
                table_title=EmulationConfigs.emulation_system_access_local_app_registry,
                no_data_message="No applications running on the Emulation System",
            )

        existing_containers = emulation_system_native_containers + emulation_system_app_containers
        return OperationResponse(success=True, data=existing_containers)

    except Exception as exc:
        error_message = f"Error retrieving application information - {str(exc)}"
        logger.exception(error_message)
        return OperationResponse(success=False, data=[])


def get_emulation_system_native_containers_information() -> dict:
    """
    Yields Emulation System Native Container information for consulting purposes.

    Returns
    -------
    dict
        Returns a dictionary containing general information on the native emulation system containers.

    """
    emulation_system_native_containers: List[DockerContainer] = get_emulation_system_native_containers()
    return_object: dict = {}
    for container in emulation_system_native_containers:
        container_names = container.container_names or []
        container_name: Optional[str] = container_names[0] if len(container_names) > 0 else None
        if container_name:
            ports = [entry for entry in set(tuple(x.items()) for x in [port.dict() for port in container.ports])]
            return_object[container_name] = {
                "container_name": container_name,
                "container_ip_address": container.ip_address,
                "container_internal_ports": ports,
            }
    return return_object


def load_base_emulation_object(
    app_name_with_version: Optional[str] = None, app_config: Optional[str] = None
) -> ProjectEmulationObject:
    """
    Loads the app emulation object from the config file.
    If none is provided, load it from the app name.

    Parameters
    ----------
    app_name_with_version : Optional[str]
        the application's name.
    app_config : Optional[str]
        the app configuration file to be used on the emulation.

    Returns
    -------
    ProjectEmulationObject
        An ProjectEmulationObject ready for consumption.

    """
    project_emulation_object: ProjectEmulationObject
    app_config_file_path: Optional[KPath] = KPath(app_config).complete_path() if app_config else None
    context_app_config_file = app_config or GeneralConfigs.default_app_config_file
    context_app_config_file_path: KPath = KPath(context_app_config_file).complete_path()

    if app_name_with_version:
        logger.relevant(f'Attempting to launch application "{app_name_with_version}" on the emulation system')
        if app_config_file_path and app_config_file_path.exists():
            logger.relevant(f'Emulation configuration loaded from: "{app_config_file_path.absolute()}"')
            project_emulation_object = ProjectEmulationObject.from_app_model(app_config_file_path=app_config_file_path)
            if app_name_with_version != project_emulation_object.app_name:
                different_versions = f"{app_name_with_version} <> {project_emulation_object.app_name}"
                raise ValueError(f"The provided configuration does not match application: {different_versions}")
        else:
            logger.warning(f'Starting "{app_name_with_version}" without configurations')
            project_emulation_object = ProjectEmulationObject(app_name=app_name_with_version)
    elif context_app_config_file_path.exists():
        logger.relevant(f'Emulation configuration loaded from: "{context_app_config_file_path.absolute()}"')
        project_emulation_object = ProjectEmulationObject.from_app_model(
            app_config_file_path=context_app_config_file_path
        )
    else:
        raise EmulationException("Please provide an application name or an application configuration file")

    return project_emulation_object


# Emulation System: Network & Broker
def _emulation_system_native_services() -> List[DockerImageName]:
    """
    Yields the list of all the Emulation System's native services.

    By default:
        - Kelvin MQTT Broker
        - Kelvin Studio

    Returns
    -------
    List[DockerImageName]
        all native services as DockerImageName objects

    """
    url_metadata = session_manager.get_current_session_metadata()
    kelvin_broker_app_name = url_metadata.sdk.components.kelvin_broker
    kelvin_studio_app_name = url_metadata.sdk.components.kelvin_studio
    kelvin_control_manager_app_name = url_metadata.sdk.components.kelvin_control_change_manager
    return [
        DockerImageName.parse(name=kelvin_broker_app_name),
        DockerImageName.parse(name=kelvin_studio_app_name),
        DockerImageName.parse(name=kelvin_control_manager_app_name),
    ]


def _start_ksdk_emulation_system(docker_manager: DockerManager) -> OperationResponse:
    """
    Start the KSDK Emulation System.
    Jumpstart the KSDK network as well as the Kelvin Broker.

    Parameters
    ----------
    docker_manager : DockerManager
        the object that encapsulates the docker utility instance.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of the KSDK Emulation System setup and start.

    """
    try:
        network_started = _start_ksdk_network(docker_manager=docker_manager)

        containers_pruned = docker_manager.prune_docker_containers()

        broker_started = _start_ksdk_broker(docker_manager=docker_manager)

        control_manager_started = _start_control_manager(docker_manager=docker_manager)

        result_message: str = "Kelvin Emulation System is online"
        logger.relevant(result_message)

        success = (
            network_started.success and containers_pruned and broker_started.success and control_manager_started.success
        )

        return OperationResponse(success=success, log=result_message)
    except Exception as exc:
        raise EmulationException(f"Error starting Kelvin Emulation System - {exc}")


def _start_ksdk_network(docker_manager: DockerManager) -> OperationResponse:
    """
    Start the KSDK network of the provided DockerManager.

    Parameters
    ----------
    docker_manager : DockerManager
        the object that encapsulates the docker utility instance.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of whether the ksdk network was successfully started.
    """
    network_id = docker_manager.get_docker_network_id()
    network_already_running = bool(network_id)

    if network_already_running:
        network_already_running_message: str = "Kelvin Network already running"
        logger.debug(network_already_running_message)
        return OperationResponse(success=True, log=network_already_running_message)
    else:
        logger.debug("Starting the Kelvin Network")
        network_successfully_started = docker_manager.create_docker_network()
        success_message = "Kelvin Network successfully started"
        logger.relevant(success_message)
        return OperationResponse(success=network_successfully_started, log=success_message)


def _stop_ksdk_network(docker_manager: DockerManager) -> OperationResponse:
    """
    Stop the KSDK network of the provided DockerManager.

    Parameters
    ----------
    docker_manager : DockerManager
        the object that encapsulates the docker utility instance.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of whether the ksdk network was successfully stopped.
    """
    logger.debug("Stopping the Kelvin Network")

    # Remove the 'ksdk' docker network
    network_removed = docker_manager.remove_docker_network()
    # Remove "dangling" containers
    containers_pruned = docker_manager.prune_docker_containers()
    # Remove "dangling" images
    images_pruned = docker_manager.prune_docker_images()

    network_successfully_stopped = network_removed and containers_pruned and images_pruned
    if network_successfully_stopped:
        result_message: str = "Kelvin Network successfully stopped"
        logger.debug(result_message)
    else:
        result_message = "Error stopping the Kelvin Network"
        logger.error(result_message)

    return OperationResponse(success=True, log=result_message)


def _start_ksdk_broker(docker_manager: DockerManager) -> OperationResponse:
    """
    Start the dedicated Kelvin Broker for application communication.

    Parameters
    ----------
    docker_manager : DockerManager
        the object that encapsulates the docker utility instance.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of whether the kelvin broker was successfully started.

    """
    # 1 - Retrieve the kelvin broker name
    url_metadata = session_manager.get_current_session_metadata()
    broker_app_name = url_metadata.sdk.components.kelvin_broker

    # 2 - Pull to ensure the broker is available
    all_broker_apps = docker_manager.get_docker_containers(image_names=[broker_app_name])
    running_broker_apps = [broker_app for broker_app in all_broker_apps if broker_app.running]

    if running_broker_apps:
        success_message = "Kelvin Broker already running"
        logger.debug(success_message)
        return OperationResponse(success=True, log=success_message)
    else:
        logger.debug("Initializing the Kelvin Broker")
        docker_manager.ensure_docker_image_exists(docker_image=broker_app_name)
        project_emulation_object = ProjectEmulationObject(
            app_name=broker_app_name,
            is_external_app=True,
            file_volumes=[
                KSDKDockerVolume(
                    source_file_path=KPath(GeneralConfigs.default_mqtt_config_file),
                    container_file_path=GeneralConfigs.default_mqtt_config_file,
                    content=GeneralConfigs.default_mqtt_config_content,
                )
            ],
        )
        successfully_started = _raw_emulation_start(
            project_emulation_object=project_emulation_object, docker_manager=docker_manager
        )

        if successfully_started.success:
            result_message = "Kelvin Broker successfully initialized"
            logger.debug(result_message)
        else:
            result_message = "Error initializing the Kelvin Broker"
            logger.exception(result_message)

        return OperationResponse(success=successfully_started.success, log=result_message)


def _start_control_manager(docker_manager: DockerManager) -> OperationResponse:
    """
    Start Kelvin Control Change manager.

    Parameters
    ----------
    docker_manager : DockerManager
        the object that encapsulates the docker utility instance.

    Returns
    -------
    OperationResponse
        an OperationResponse object encapsulating the result of whether the kelvin broker was successfully started.

    """
    # 1 - Retrieve the kelvin broker name
    url_metadata = session_manager.get_current_session_metadata()
    image_name = url_metadata.sdk.components.kelvin_control_change_manager

    # 2 - Pull to ensure the image is available
    image_containers = docker_manager.get_docker_containers(image_names=[image_name])
    running_broker_apps = [app for app in image_containers if app.running]

    if running_broker_apps:
        success_message = "Kelvin Control Manager already running"
        logger.debug(success_message)
        return OperationResponse(success=True, log=success_message)
    else:
        logger.debug("Initializing the Kelvin Control Manager")
        docker_manager.ensure_docker_image_exists(docker_image=image_name)
        project_emulation_object = ProjectEmulationObject(
            app_name=image_name,
            is_external_app=True,
            arguments=[ControlManagerConfigs.control_manager_config_file],
            file_volumes=[
                KSDKDockerVolume(
                    source_file_path=KPath(ControlManagerConfigs.control_manager_config_file),
                    container_file_path=ControlManagerConfigs.control_manager_config_file,
                    content=ControlManagerConfigs.default_control_manager_config_content,
                )
            ],
        )
        successfully_started = _raw_emulation_start(
            project_emulation_object=project_emulation_object, docker_manager=docker_manager
        )

        if successfully_started.success:
            result_message = "Kelvin Control Manager successfully initialized"
            logger.debug(result_message)
        else:
            result_message = "Error initializing theKelvin Control Manager"
            logger.exception(result_message)

        return OperationResponse(success=successfully_started.success, log=result_message)


# Internal utils
def _print_log_stream(log_stream: Union[CancellableStream, str]) -> None:
    """
    Prints a log stream

    Parameters
    ----------
    log_stream : Union[CancellableStream, str]
        stream or a string containing the logs to print

    Returns
    -------
    Nothing

    """
    try:
        if isinstance(log_stream, str):
            logs = log_stream.split("\n")
            for item in logs:
                print(item)  # noqa
        elif isinstance(log_stream, bytes):
            logs = log_stream.decode("utf-8").split("\n")
            for item in logs:
                print(item)  # noqa
        else:
            for item in log_stream:
                print(item.decode("utf-8"), end="")  # type: ignore # noqa
    except Exception as exc:
        logger.error(f'Error processing logs - "{str(exc)}"')
