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

# Import local inventory models
from smartmodels.models.inventory import SmartmodelsItem as Item
from smartmodels.models.inventory import SmartmodelsInventory as Inventory
from smartmodels.models.inventory import SmartmodelsInventoryRequest as Request
from smartmodels.models.inventory import SmartmodelsInventoryResponse as Response

# ---------------------------------------------------------
# Dynamic Loading Interface / EP Exposure
# ---------------------------------------------------------
TAG = "Inventory"
DESCRIPTION = "Inventory CLI API"
API_ORDER = 10

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)


# ---------------------------------------------------------
# Inventory CLI router
# ---------------------------------------------------------
@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def inventory(env):
    """subcommands for managing inventory for smartmodels"""
    # banner("User", env.__dict__)


submodule = inventory


@submodule.command()
@click.option("--path", default=None)
@click.pass_obj
def create(env, path):
    """Create a new inventory item for smartmodels"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def read(env):
    """Find and list existing inventory items for smartmodels"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def update(env):
    """Update and existing inventory item for smartmodels"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def delete(env):
    """Delete an existing inventory item for smartmodels"""
    # force config loading
    config.callback()

    # TODO: implement
