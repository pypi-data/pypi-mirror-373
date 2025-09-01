# import re
# import os
# import yaml

import click

# from smartmodels.helpers import *
from smartmodels.cli.main import main, CONTEXT_SETTINGS
from smartmodels.cli.config import config

from smartmodels.definitions import DEFAULT_LANGUAGE, UID_TYPE

# TODO: include any logic from module core
# Examples
# from smartmodels.models import *
# from smartmodels.logic import Tagger
# from syncmodels.storage import Storage

# Import local scripts models
from smartmodels.models.script import SmartmodelsScript as Item
from smartmodels.models.script import SmartmodelsScriptRequest as Request
from smartmodels.models.script import SmartmodelsScriptResponse as Response

# ---------------------------------------------------------
# Dynamic Loading Interface / EP Exposure
# ---------------------------------------------------------
TAG = "Scripts"
DESCRIPTION = "Scripts CLI API"
API_ORDER = 10

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)


# ---------------------------------------------------------
# Script CLI port implementation
# ---------------------------------------------------------
@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def script(env):
    """subcommands for managing scripts for smartmodels"""
    # banner("User", env.__dict__)


submodule = script


@submodule.command()
@click.option("--path", default=None)
@click.pass_obj
def create(env, path):
    """Create a new script for smartmodels"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def read(env):
    """Find and list existing scripts for smartmodels"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def update(env):
    """Update and existing scripts for smartmodels"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def delete(env):
    """Delete an existing scripts for smartmodels"""
    # force config loading
    config.callback()

    # TODO: implement
