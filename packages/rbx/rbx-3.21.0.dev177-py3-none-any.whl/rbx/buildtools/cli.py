import click

from .tasks import ec2, image, misc


from rbx import __version__


@click.group(
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
    add_help_option=True,
)
@click.version_option(message=__version__)
def cli():
    """Scoota (a.k.a. RBX) buildtools."""


cli.add_command(ec2.deploy)


@cli.group(name="image")
def image_group():
    """Manage images on Amazon Container Registry."""


image_group.add_command(image.login)
image_group.add_command(image.build)
image_group.add_command(image.upload)


@cli.group(name="misc")
def misc_group():
    """Miscellaneous tools."""


misc_group.add_command(misc.clean)
misc_group.add_command(misc.get_next_tag)
misc_group.add_command(misc.get_merge_desc)
misc_group.add_command(misc.get_npm_version)
