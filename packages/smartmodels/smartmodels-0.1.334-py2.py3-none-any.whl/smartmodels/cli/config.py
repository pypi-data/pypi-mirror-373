import os

# import yaml

import click

from agptools.helpers import banner
from agptools.helpers import setdefault, load_config, save_config


from ..helpers import *
from .main import main, CONTEXT_SETTINGS


# https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
RED = "\033[31;1;4m"
GREEN = "\033[32;1;4m"
YELLOW = "\033[33;1;4m"
BLUE = "\033[34;1;4m"
PINK = "\033[35;1;4m"

RESET = "\033[0m"


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def config(env):
    """A new group named 'config' nested to 'main' group
    Whenever a 'config' subcommand is called, this code
    will be executed before and load or create a config file
    by default.
    """

    try:
        load_config(env)

    except Exception as why:
        # If load_config fails, then create a clean one.
        print(f"{why}")

        setdefault(
            env,
            "includes",
            {
                r"smartmodels/.*\.yaml$": None,
            },
        )
        setdefault(
            env,
            "excludes",
            {},
        )
        setdefault(
            env,
            "folders",  # Not regexp
            {
                #'~/Documents': None,
                #'~/workspace': None,
                ".": None,
            },
        )
        setdefault(
            env,
            "resource",
            os.path.join(env.home, "resources.yaml"),
        )
        setdefault(
            env,
            "role",
            os.path.join(env.home, "roles.yaml"),
        )
        # if old != env.__dict__:
        # save_config(env)

        save_config(env)
    return env


@config.command()
@click.pass_obj
def list(env):
    banner("Config", env.__dict__)


@config.command()
@click.option("--include", default=None)
@click.option("--exclude", default=None)
@click.option("--folder", default=None)
@click.pass_obj
def view(env, include, exclude, folder):
    if include:
        click.echo(f"add include: {include}")
        s = setdefault(env, "includes", dict())
        s[include] = None
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, "excludes", dict())
        s[exclude] = None
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, "folders", dict())
        s[folder] = None
        save_config(env)
    list.callback()


@config.command()
@click.option("--include", default=None)
@click.option("--exclude", default=None)
@click.option("--folder", default=None)
@click.pass_obj
def add(env, include, exclude, folder):
    if include:
        click.echo(f"add include: {include}")
        s = setdefault(env, "includes", dict())
        s[include] = None
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, "excludes", dict())
        s[exclude] = None
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, "folders", dict())
        s[folder] = None
        save_config(env)
    list.callback()


@config.command()
@click.option("--include", default=None)
@click.option("--exclude", default=None)
@click.option("--folder", default=None)
@click.pass_obj
def delete(env, include, exclude, folder):
    if include:
        click.echo(f"delete include: {include}")
        s = setdefault(env, "includes", dict())
        s.pop(include, None)
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, "excludes", dict())
        s.pop(exclude, None)
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, "folders", dict())
        s.pop(folder, None)
        save_config(env)
    list.callback()
