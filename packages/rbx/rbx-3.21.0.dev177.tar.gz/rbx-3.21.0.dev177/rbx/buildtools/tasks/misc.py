import subprocess
from os import path

import click


@click.command()
def clean(ctx):
    """Remove all intermediate files from the source tree."""
    subprocess.run("git clean -xdf", shell=True)


@click.command(name="git-next-tag")
def get_next_tag():
    """Generate tag from Git.

    A helper to generate the next tag based on the current git tag.

    To use in Jenkins job:

        >>> export VERSION=`buildtools misc git-next-tag`

    Expects an integer, otherwise will start at 1.
    """
    cmd = "git describe --tags $(git rev-list --tags --max-count=1)"
    process = subprocess.run(cmd, shell=True, capture_output=True)
    try:
        tag = int(process.stdout.strip())
    except ValueError:
        tag = 0
    print(tag + 1)


@click.command(name="git-merge-desc")
def get_merge_desc():
    """Get description from Git.

    A helper to get the description of a merge commit.

    To use in a Jenkins job:

        >>> export DESCRIPTION=`buildtools misc git-merge-desc`

    When merging a PR the subject line will be added to the body of the merge
    commit.
    """
    cmd = "git log -1 --pretty='format:%s'"
    process = subprocess.run(cmd, shell=True, capture_output=True)
    print(process.stdout.decode().strip())


@click.command(name="npm-version")
def get_npm_version():
    """Get version from NPM.

    A helper to get the npm package version from a package.json file.

    To use in Jenkins job:

        >>> export VERSION=`buildtools misc npm-version`

    """
    if path.exists("package.json"):
        cmd = "cat package.json | jq .version -r"
        process = subprocess.run(cmd, shell=True, capture_output=True)
        print(process.stdout.decode().strip())
    else:
        print("unknown")
