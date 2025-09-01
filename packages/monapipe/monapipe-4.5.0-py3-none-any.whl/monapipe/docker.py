# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import shutil
import subprocess
import time

import docker
import requests

from monapipe.config import LOCAL_PATHS


def provide_docker_container(
    dockerfile_dir: str,
    dockerfile: str = "Dockerfile",
    container_port: int = 80,
    host_port: int = 16000,
    data_path_host: str = LOCAL_PATHS["data_path"],
    data_path_container: str = LOCAL_PATHS["data_path_container"],
    debug_mode: bool = False,
):
    """Function that builds image and container for MONAPipe API components.

    Args:
        dockerfile_dir: Dir name of Dockerfile.
        dockerfile: Name of the Dockerfile.
        container_port: Port to run the API inside the container.
        host_port: Port to expose the API to the host system.
        data_path_host: Path to the data directory for the data at host system.
        data_path_container: Path to the data directory for the data at container.
        debug_mode: Flag to enable debug mode.

    """
    # Check if Docker is installed and running
    check_docker_installation()
    check_docker_running()

    client = docker.from_env()

    # Check if `config.py` and `resource_handler.py` are copied to the Dockerfile directory
    base_path = os.path.join(dockerfile_dir, "app")
    for file_name in ["config.py", "resource_handler.py"]:
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        shutil.copy(
            os.path.join(os.path.dirname(__file__), file_name),
            base_path,
        )

    # Generate the tag for the Docker image
    tag = dockerfile_dir.split("/")[-1]

    # Check if the image already exists
    image_exists = False
    try:
        client.images.get(tag)
        image_exists = True
        print(f"Image {tag} already exists. Skipping build.")
    except docker.errors.ImageNotFound:
        print(f"Image {tag} not found. Building Docker image for {tag}...")

    # build the Docker image
    if not image_exists:
        image, build_logs = client.images.build(
            path=dockerfile_dir,
            dockerfile=dockerfile,
            tag=tag,
            buildargs={"PORT": str(container_port)},
        )

        if debug_mode:
            # print build logs
            for log in build_logs:
                print(log.get("stream", ""))

    container_name = tag + "_monapipe_container"
    try:
        # check if container already exists
        container = client.containers.get(container_name)

        if container.status == "running":
            print(f"Container {container.name} already exists and is running.")
        # if container is not running, start container
        elif container.status != "running":
            container.start()
            print(f"Container {container.name} already exists and is starting now.")

    except docker.errors.NotFound:
        # start container from image if not exists

        volumes = {}

        # Add data path to volumes
        data_path_host_container_mapping = {
            data_path_host: {"bind": data_path_container, "mode": "rw"}
        }
        volumes.update(data_path_host_container_mapping)

        container = client.containers.run(
            tag,
            detach=True,
            name=container_name,
            ports={f"{container_port}/tcp": host_port},
            network_mode="bridge",
            volumes=volumes,
        )

        api_url = f"http://localhost:{host_port}/"
        print(f"Starting Docker container... @ {api_url}")

        # Check container status
        # container.reload()
        print(f"Container status: {container.status}")

        # Wait until API is ready
        if not wait_for_api(api_url):
            raise RuntimeError("API did not become ready in time.")

        print(f"Container {container.name} started and running.")


def wait_for_api(url, timeout=300):
    """Waits until the API is available at the specified URL."""
    start_time = time.time()
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("API is ready.")
                return True
        except requests.exceptions.ConnectionError:
            pass

        if time.time() - start_time > timeout:
            print("API did not become ready in time.")
            return False

        # print("Waiting for API to be ready...")
        time.sleep(2)


def stop_docker_container(name="all", remove=False):
    """Method to stop all running MONAPipe containers."""
    client = docker.from_env()
    if name == "all":
        for container in client.containers.list():
            if container.name.endswith("_monapipe_container"):
                if container.name == name or name == "all":
                    container.stop()
                    if remove:
                        container.remove()


def delete_docker_container(name="all"):
    """Method to delete all running MONAPipe containers."""
    stop_docker_container(name=name, remove=True)


def check_docker_installation():
    """
    Checks if Docker is installed by attempting to run the command `docker --version`.

    :Raises:
        EnvironmentError: If Docker is not installed (FileNotFoundError), if Docker
                          is installed but the service might not be active, or if
                          an unknown OS error occurs (OSError).
    """
    try:
        # Check if Docker is installed
        subprocess.run(
            ["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except FileNotFoundError as e:
        raise EnvironmentError(
            "This MONAPipe implementation needs Docker. Docker is not installed. Please install Docker and try again."
        ) from e
    except subprocess.CalledProcessError as e:
        raise EnvironmentError(
            "This MONAPipe implementation needs Docker. Docker is installed, but the Docker service might not be active."
        ) from e
    except OSError as e:
        raise EnvironmentError(
            "This MONAPipe implementation needs Docker. An OS error occurred while trying to check Docker installation."
        ) from e


def check_docker_running():
    """
    Checks if the Docker daemon is running by executing the command `docker info`.

    :Raises:
        EnvironmentError: If Docker is installed but the daemon is not running (CalledProcessError),
                          if an unknown OS error occurs (OSError), or if any other unexpected error occurs.
    """
    try:
        # Check if Docker daemon is running
        subprocess.run(
            ["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        raise EnvironmentError(
            "This MONAPipe implementation needs Docker. Docker is installed, but the Docker daemon is not running. Please start the Docker service."
        ) from e
    except OSError as e:
        raise EnvironmentError(
            "This MONAPipe implementation needs Docker. An OS error occurred while trying to check Docker daemon status."
        ) from e
    except Exception as e:
        raise EnvironmentError(f"An unknown error occurred: {e}") from e
