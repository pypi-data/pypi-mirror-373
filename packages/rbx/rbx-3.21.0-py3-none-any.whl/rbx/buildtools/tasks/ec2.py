import click
from fabric import Connection

from .. import CONFIGURATIONS, REGISTRY


@click.command()
@click.argument("host")
@click.argument("user")
@click.argument("key_filename")
@click.argument("service")
@click.argument("environment")
@click.option("--sandboxed/--no-sandboxed", default=True)
@click.option("-v", "--version", default="latest")
def deploy(host, user, key_filename, service, environment, sandboxed, version):
    """Deploy to EC2.

    Download a Docker image and start the container on a Remote Server.
    """
    connection = Connection(
        host=host, user=user, connect_kwargs={"key_filename": key_filename}
    )

    # Login to Scoota Docker Registry
    connection.run(
        "aws ecr get-login-password | docker login"
        f" --username AWS --password-stdin {REGISTRY}",
        echo=True,
    )

    # Get the latest configuration for the Server we are deploying to.
    # Valid configurations are located at '/<Service>/<Env>/'
    connection.run(
        "aws s3 sync {config}/{service}/{env} {service}".format(
            config=CONFIGURATIONS, env=environment, service=service
        ),
        echo=True,
    )

    # Restart the Docker container forcing recreate so that new version is used.
    # Using `force-recreate` alone doesn't seem to be enough to use the latest version. So we
    # do `down` and then `up`.
    connection.run(
        "docker-compose -p {service}{env} -f {service}/docker-compose.yml down"
        " --volumes --remove-orphans".format(service=service, env=environment),
        echo=True,
        env={
            "SANDBOXED": sandboxed,
            "VERSION": version,
        },
        warn=True,
    )
    connection.run(
        "docker-compose -p {service}{env} -f {service}/docker-compose.yml up -d".format(
            service=service, env=environment
        ),
        echo=True,
        env={
            "SANDBOXED": sandboxed,
            "VERSION": version,
        },
    )

    # Remove all unused Docker Images
    connection.run("docker rmi `docker images -q` || true", echo=True)
    connection.run("docker rm `docker ps -a -q` || true", echo=True)
