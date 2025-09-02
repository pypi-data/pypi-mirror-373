import subprocess
from os import getcwd, path

import click

from .. import REGISTRY

BASEPATH = path.basename(getcwd())


@click.command()
def login():
    """Login to the Amazon Container Registry."""
    subprocess.run(
        "aws ecr get-login-password | docker login"
        f" --username AWS --password-stdin {REGISTRY}",
        shell=True,
    )


@click.command()
@click.option("--build-arg", multiple=True)
@click.option("--cache/--no-cache", default=True)
@click.option("--name", default=BASEPATH)
@click.option("--version", default="develop")
@click.option("--target")
@click.option("--test/--no-test", default=False)
def build(build_arg, cache, name, version, target, test):
    """Build the docker image.

    Note that parameters always take precedence over environment variables.
    """
    command = ["docker build"]

    if target:
        command.append("--target {}".format(target))

    if test:
        command.append("--build-arg INSTALL_TEST_DEPENDENCIES=yes")

    for arg in build_arg:
        command.append("--build-arg {}".format(arg))

    if not cache:
        command.append("--no-cache")

    command.append(f"-t {REGISTRY}/{name}:{version} .")
    command = " ".join(command)
    subprocess.run(command, shell=True)


@click.command()
@click.option("--name", default=BASEPATH)
@click.option("--version", default="develop")
def upload(name, version):
    """Upload the docker image to Amazon Container Registry.

    Needless to say, this image must have been already built.

    Note that parameters always take precedence over environment variables.
    """
    subprocess.run(f"docker push {REGISTRY}/{name}:{version}", shell=True)
