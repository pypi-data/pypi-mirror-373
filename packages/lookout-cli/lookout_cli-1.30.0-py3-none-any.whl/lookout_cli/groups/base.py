import os
import subprocess
from pathlib import Path
from typing import List, Optional, cast

import click
from lookout_cli.helpers import (
    call,
    docker_bake,
    docker_compose_path,
    get_installer,
    get_project_root,
    get_version,
    make_dir_set_permission,
)
from lookout_config import get_config_io
from lookout_config.types import (
    Camera,
    CudaVersion,
    GeolocationMode,
    LogLevel,
    LookoutConfig,
    Mode,
    Network,
)
from python_on_whales.components.compose.models import ComposeConfig
from python_on_whales.docker_client import DockerClient
from python_on_whales.exceptions import NoSuchImage
from python_on_whales.utils import ValidPath

# Reusable option decorator for config_dir
config_dir_option = click.option(
    "--config-dir",
    type=str,
    default="~/.config/greenroom",
    help="The directory where the lookout config is stored. Default: ~/.config/greenroom",
)

DOCKER = docker_compose_path("./docker-compose.yaml")
DOCKER_DEV = docker_compose_path("./docker-compose.dev.yaml")
DOCKER_PROD = docker_compose_path("./docker-compose.prod.yaml")
DOCKER_NETWORK_SHARED = docker_compose_path("./docker-compose.network-shared.yaml")
DOCKER_NETWORK_HOST = docker_compose_path("./docker-compose.network-host.yaml")
DOCKER_GPU = docker_compose_path("./docker-compose.gpu.yaml")
DOCKER_PROXY = docker_compose_path("./docker-compose.proxy.yaml")

SERVICES = [
    "lookout_core",
    "lookout_ui",
    "lookout_greenstream",
    "lookout_docs",
]

PYTHON_PACKAGES = ["lookout-config", "lookout-cli"]

DEBIAN_DEPENDENCIES = [
    "docker-ce",
    "docker-ce-cli",
    "containerd.io",
    "docker-buildx-plugin",
    "docker-compose-plugin",
    "python3",
    "python3-pip",
]


def _get_compose_files(
    prod: bool = False, network: Network = Network.HOST, gpu=False
) -> List[ValidPath]:
    compose_files: List[ValidPath] = [DOCKER]

    if prod:
        compose_files.append(DOCKER_PROD)

    if not prod:
        compose_files.append(DOCKER_DEV)

    if network == Network.SHARED:
        compose_files.append(DOCKER_NETWORK_SHARED)

    if network == Network.HOST:
        compose_files.append(DOCKER_NETWORK_HOST)

    if gpu:
        compose_files.append(DOCKER_GPU)

    compose_files.append(DOCKER_PROXY)

    return compose_files


def log_config(config: LookoutConfig):
    click.echo(click.style("[+] Lookout Config:", fg="green"))
    config_io = get_config_io()
    click.echo(click.style(f" ⠿ Path: {config_io.get_path()}", fg="white"))
    for attr, value in config.__dict__.items():
        click.echo(
            click.style(f" ⠿ {attr}: ".ljust(27), fg="white") + click.style(str(value), fg="green")
        )


def set_initial_env(config_dir: str):
    version = get_version()
    os.environ["LOOKOUT_CONFIG_DIR"] = config_dir
    os.environ["LOOKOUT_VERSION"] = version

    if config_dir.startswith("/"):
        click.echo(
            click.style(
                "Warning: Using an absolute path requires the path to be accessible from the host and within the docker container.",
                fg="yellow",
            )
        )


@click.command(name="up")
@click.option(
    "--build",
    type=bool,
    default=False,
    is_flag=True,
    help="Should we rebuild the docker containers? Default: False",
)
@click.option(
    "--pull",
    help="Should we do a docker pull",
    is_flag=True,
)
@config_dir_option
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def up(
    build: bool,
    pull: bool,
    config_dir: str,
    services: List[str],
):
    """Starts lookout"""
    set_initial_env(config_dir)

    config = get_config_io().read()
    log_config(config)

    if config.prod and build:
        raise click.UsageError("Cannot build in production mode. Run `lookout build` instead")

    # Make the log and recordings directories
    log_directory = Path(config.log_directory).expanduser()
    recording_directory = Path(config.recording_directory).expanduser()
    models_directory = Path(config.models_directory).expanduser()
    get_config_io().get_path().chmod(0o777)
    make_dir_set_permission(log_directory)
    make_dir_set_permission(recording_directory)
    make_dir_set_permission(models_directory)

    os.environ["GPU"] = "true" if config.gpu else "false"
    os.environ["ROS_DOMAIN_ID"] = (
        str(config.discovery.ros_domain_id) if config.discovery.type == "simple" else "0"
    )
    os.environ["LOOKOUT_NAMESPACE_VESSEL"] = config.namespace_vessel
    os.environ["LOOKOUT_CONFIG"] = config.model_dump_json()
    os.environ["LOOKOUT_LOG_DIR"] = str(log_directory)
    os.environ["LOOKOUT_RECORDING_DIR"] = str(recording_directory)
    os.environ["LOOKOUT_MODEL_DIR"] = str(models_directory)
    os.environ["CUDA_VERSION"] = str(config.cuda_version)
    os.environ["RMW_IMPLEMENTATION"] = (
        "rmw_zenoh_cpp" if config.discovery.type == "zenoh" else "rmw_fastrtps_cpp"
    )

    if config.prod:
        os.environ["LOOKOUT_CORE_COMMAND"] = "ros2 launch lookout_bringup configure.launch.py"
        os.environ[
            "LOOKOUT_GREENSTREAM_COMMAND"
        ] = "ros2 launch lookout_greenstream_bringup configure.launch.py"
    else:
        os.environ[
            "LOOKOUT_CORE_COMMAND"
        ] = "platform ros launch lookout_bringup configure.launch.py --build --watch"
        os.environ[
            "LOOKOUT_GREENSTREAM_COMMAND"
        ] = "platform ros launch lookout_greenstream_bringup configure.launch.py --build --watch"

    services_list = list(services) if services else None

    docker = DockerClient(
        compose_files=_get_compose_files(prod=config.prod, network=config.network, gpu=config.gpu),
        compose_project_directory=get_project_root(),
    )
    docker.compose.up(
        services_list, detach=True, build=build, pull="always" if pull else "missing"
    )

    click.echo(click.style("UI started: http://localhost:4000", fg="green"))


@click.command(name="down")
@config_dir_option
@click.argument("args", nargs=-1)
def down(config_dir: str, args: List[str]):
    """Stops lookout"""
    set_initial_env(config_dir)

    config = get_config_io().read()

    docker = DockerClient(
        compose_files=_get_compose_files(prod=config.prod, network=config.network, gpu=config.gpu),
        compose_project_directory=get_project_root(),
    )
    docker.compose.down()


@click.command(name="build")
@click.option(
    "--no-cache",
    type=bool,
    default=False,
    is_flag=True,
    help="Should we rebuild without the docker cache?",
)
@click.option(
    "--cuda-version",
    type=click.Choice([v.value for v in CudaVersion]),
    help="CUDA version to use for building",
)
@config_dir_option
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
@click.option("--pull", is_flag=True, help="Pull the latest images")
def build(
    no_cache: bool, cuda_version: str, config_dir: str, services: List[str], pull: bool = False
):
    """Builds the Lookout docker containers"""
    set_initial_env(config_dir)
    config = get_config_io().read()
    os.environ["LOOKOUT_NAMESPACE_VESSEL"] = config.namespace_vessel
    os.environ["GPU"] = "true" if config.gpu else "false"
    os.environ["CUDA_VERSION"] = cuda_version or str(config.cuda_version)

    docker = DockerClient(
        compose_files=_get_compose_files(gpu=config.gpu, prod=False),
        compose_project_directory=get_project_root(),
    )
    services_list = list(services) if services else None

    docker.compose.build(services=services_list, cache=not no_cache, pull=pull)


@click.command(name="bake")
@click.option(
    "--version",
    type=str,
    required=True,
    help="The version to bake. Default: latest",
)
@click.option(
    "--push",
    type=bool,
    default=False,
    is_flag=True,
    help="Should we push the images to the registry? Default: False",
)
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
@click.option(
    "--cuda-version",
    type=click.Choice([v.value for v in CudaVersion]),
    required=True,
    help="CUDA version to use for baking",
)
def bake(version: str, push: bool, services: List[str], cuda_version: str):  # type: ignore
    """Bakes the docker containers"""
    compose_files = _get_compose_files()
    docker_bake(
        version=version,
        services=services,
        push=push,
        compose_files=compose_files,
        cuda_version=cuda_version,
    )


@click.command(name="lint")
def lint():
    """Lints all the things"""
    call("pre-commit run --all")


@click.command(name="generate")
@config_dir_option
def generate(config_dir: str):
    """Generates models, types and schemas"""
    set_initial_env(config_dir)
    config = get_config_io().read()

    os.environ["ROS_DOMAIN_ID"] = (
        str(config.discovery.ros_domain_id) if config.discovery.type == "simple" else "0"
    )
    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )

    click.echo(click.style("Generating models from launch params...", fg="green"))
    nodes = []
    # for node in ["object_tracker", "detector_onnx"]:
    #     nodes.append("-n")
    #     nodes.append(node)

    docker.compose.execute(
        "lookout_core",
        [
            "bash",
            "-l",
            "-c",
            'exec "$@"',
            "--",
            "python3",
            "-m",
            "parameter_persistence.generate_models",
            "-o",
            "/home/ros/lookout_core/src/lookout_config/lookout_config",
            *nodes,
        ],
    )

    click.echo(click.style("Generating schemas for Lookout Config", fg="green"))
    subprocess.run(
        ["python3", "-m", "lookout_config.generate_schemas"],
        check=True,
        text=True,
        capture_output=True,
    )

    click.echo(click.style("Generating ts types...", fg="green"))
    docker.compose.execute("lookout_core", ["npx", "-y", "ros-typescript-generator"])


@click.command(name="upgrade")
@click.option("--version", help="The version to upgrade to.")
def upgrade(version: str):
    """Upgrade Lookout CLI"""
    click.echo(f"Current version: {get_version()}")
    result = click.prompt(
        "Are you sure you want to upgrade?", default="y", type=click.Choice(["y", "n"])
    )
    if result == "n":
        return

    installer = get_installer("lookout-cli")
    if version:
        call(f"{installer} install --upgrade lookout-config=={version}")
        call(f"{installer} install --upgrade lookout-cli=={version}")
    else:
        call(f"{installer} install --upgrade lookout-config")
        call(f"{installer} install --upgrade lookout-cli")

    click.echo(click.style("Upgrade of Lookout CLI complete.", fg="green"))


@click.command(name="authenticate")
@click.option(
    "--username",
    help="The username to use for authentication.",
    required=True,
    prompt=True,
)
@click.option("--token", help="The token to use for authentication.", required=True, prompt=True)
def authenticate(username: str, token: str):
    """
    Authenticate with the package repository so that you can pull images.

    To get a username and token you'll need to contact a Greenroom Robotics employee.
    """
    call(f"echo {token} | docker login ghcr.io -u {username} --password-stdin")


@click.command(name="config")
@config_dir_option
def config(
    config_dir: str,
):
    """Read Config"""
    set_initial_env(config_dir)
    config = get_config_io().read()
    log_config(config)


@click.command(name="configure")
@click.option("--gpu", type=bool, help="Should we use the GPU?", default=True)
@click.option("--default", is_flag=True, help="Use default values")
@config_dir_option
def configure(gpu: bool, default: bool, config_dir: str):
    """Configure Lookout"""
    set_initial_env(config_dir)

    if default:
        config = LookoutConfig(gpu=gpu)
        get_config_io().write(config)
    else:
        # Check if the file exists
        config_io = get_config_io()
        if os.path.exists(config_io.get_path()):
            click.echo(
                click.style(
                    f"Lookout config already exists: {config_io.get_path()}",
                    fg="yellow",
                )
            )
            result = click.prompt(
                "Do you want to overwrite it?", default="y", type=click.Choice(["y", "n"])
            )
            if result == "n":
                return

        try:
            config_current = get_config_io().read()
        except Exception as e:
            print(f"could not read config {e}")
            config_current = LookoutConfig()

        cameras: Optional[List[Camera]] = None
        if not config_current.cameras:
            gen_cameras = click.prompt(
                "No Cameras found, do you want to generate a template?",
                default="y",
                type=click.Choice(["y", "n"]),
            )
            if gen_cameras == "y":
                cameras = [
                    Camera(
                        name="bow",
                        type="color",
                        order=0,
                        ptz=False,
                    )
                ]
        config = LookoutConfig(
            namespace_vessel=click.prompt(
                "Namespace Vessel", default=config_current.namespace_vessel
            ),
            mode=click.prompt(
                "Mode",
                default=str(config_current.mode),
                type=click.Choice([item.value for item in Mode]),
            ),
            gama_vessel=click.prompt(
                "Is this running on a Gama Vessel?",
                default=config_current.gama_vessel,
                type=bool,
            ),
            log_level=click.prompt(
                "Log level",
                default=config_current.log_level,
                type=click.Choice([item.value for item in LogLevel]),
            ),
            gpu=click.prompt(
                "Should we use the GPU?",
                default=config_current.gpu,
                type=bool,
            ),
            cameras=cameras if cameras else config_current.cameras,
            geolocation_mode=GeolocationMode.NONE,
        )
        get_config_io().write(config)


@click.command(name="download")
@click.option(
    "--include-deps",
    help="Should we include the deps",
    is_flag=True,
    default=False,
)
@config_dir_option
@click.argument(
    "output-directory",
    required=False,
    nargs=1,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
)
def download(include_deps: bool, config_dir: str, output_directory: Optional[ValidPath]):
    """
    Saves off the Lookout+ docker images to a tar file and optionally downloads the depependencies.
    Note: This assumes you have a working Lookout+ installation with the images already downloaded.
    It also does not download nvidia drivers - you will need to install those separately if you want to use the GPU.
    """
    set_initial_env(config_dir)

    version = get_version()
    if version == "latest":
        raise click.ClickException(
            "You must install a pinned version of marops-cli to use this command."
        )

    config = get_config_io().read()
    docker_client = DockerClient(
        compose_files=_get_compose_files(prod=config.prod, network=config.network, gpu=config.gpu),
    )
    docker_config = cast(ComposeConfig, docker_client.compose.config())
    docker_services = docker_config.services or {}
    docker_images = [docker_services[service].image for service in docker_services.keys()]
    docker_images = [image for image in docker_images if image]

    if not output_directory:
        output_directory = os.getcwd()

    if include_deps:
        # Download the deps
        click.echo(click.style("Downloading dependencies", fg="green"))

        # Download debian's for the docker install
        os.makedirs(f"{output_directory}/debs", exist_ok=True)

        # Get all the dependencies save to a folder of debs
        # This gross thing parses the output from apt-rdepends so ALL the dependencies are downloaded
        debs = DEBIAN_DEPENDENCIES
        if config.gpu:
            debs.append("nvidia-container-toolkit")

        rdepends_cmd = """
            apt-rdepends {0} | awk '/^[^ ]/ {{print $1}}' | sort -u | while read pkg; do
                if apt-cache policy "$pkg" | grep -q 'Candidate: [^ ]'; then
                    apt download "$pkg"
                else
                    echo "Skipping virtual package: $pkg"
                fi
            done
        """.format(
            " ".join(debs)
        )
        subprocess.call(rdepends_cmd, shell=True, cwd=f"{output_directory}/debs")
        click.echo(click.style(f"Debian's saved to {output_directory}/debs", fg="green"))

        # Download the python deps
        click.echo(click.style("Downloading python deps", fg="green"))

        python_folder = "python_packages"
        os.makedirs(f"{output_directory}/{python_folder}", exist_ok=True)
        python_packages = [f"{package}=={version}" for package in PYTHON_PACKAGES]
        subprocess.call(
            f"pip download --dest={output_directory}/{python_folder}/ "
            + " ".join(python_packages),
            shell=True,
        )
    else:
        click.echo(click.style("Skipping deps download", fg="yellow"))

    click.echo(click.style(f"Found images from docker compose: {docker_images}.", fg="green"))

    docker_download_dir = os.path.join(output_directory, "docker_images")
    # Create the directory if it doesn't exist
    os.makedirs(docker_download_dir, exist_ok=True)

    try:
        click.echo(
            click.style(
                f"Downloading images to {docker_download_dir}. This takes a while...", fg="green"
            )
        )
        docker_client.save(
            docker_images, output=os.path.join(docker_download_dir, "docker_images.tar")
        )
    except NoSuchImage as e:
        click.echo(click.style(f"Image not found: {e}", fg="white"))
        click.echo(
            click.style(
                "At least one image wasn't found locally. Run `lookout up` to download the images.",
                fg="red",
            )
        )
        return

    # Save the images to a tar file
    click.echo(click.style("Images saved to {output_directory}/docker_images.tar", fg="green"))
