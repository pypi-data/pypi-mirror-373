import click

from lookout_cli.helpers import get_project_root
from pathlib import Path


def write_file(path: str, content: str):
    project_root = get_project_root() or Path()
    click.echo(f"Writing file {project_root / path}")
    with open(project_root / path, "w") as f:
        f.write(content)


@click.group(help="Setup commands")
def setup():
    pass


@click.command(name="secrets")
@click.argument("pat")
def secrets(pat: str):  # type: ignore
    """Setup the .secrets files as docker secrets needs these to build containers"""
    write_file(".secrets/API_TOKEN_GITHUB", pat)

    greenroom_apt_conf = "\n".join(
        [
            "machine raw.githubusercontent.com/Greenroom-Robotics",
            f"login {pat}",
            "password",
        ]
    )
    write_file(".secrets/apt.conf", greenroom_apt_conf)
