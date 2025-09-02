"""Console script for any click extensible CLI."""

import os
import click

CONTEXT_SETTINGS = dict(default_map={"runserver": {"port": 5000}})


class Env(object):
    def __init__(self, home=None, debug=False):
        home = os.path.expandvars(home)
        home = os.path.expanduser(home)
        home = os.path.abspath(home)

        self.home = os.path.abspath(home)
        self.cwd = os.path.abspath(".")
        if self.cwd != self.home:
            self.config_folders = [self.cwd, self.home]
        else:
            self.config_folders = [self.cwd]

        self.config_files = [
            os.path.join(path, "config.yaml") for path in self.config_folders
        ]

        self.folders = []
        self.debug = debug
        self.autoassign_pattern = r"z.*\d+@"


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--config-folder",
    envvar="SMARTMODELS_HOME",
    default="~/.config/smartmodels",
)
@click.option("--debug/--no-debug", default=False, envvar="REPO_DEBUG")
@click.pass_context
def main(ctx, config_folder, debug):
    ctx.obj = Env(config_folder, debug)


@main.command()
@click.option("--port", default=9080)
@click.pass_obj
def add(env, port):
    click.echo(f"Env: {env}/")
    click.echo(f"Serving on http://127.0.0.1:{port}/")


@main.command()
@click.option("--port", default=9080)
@click.pass_obj
def delete(env, port):
    click.echo(f"Serving on http://127.0.0.1:{port}/")


@main.command()
@click.option("--port", default=9080)
@click.pass_obj
def run(env, port):
    click.echo(f"Serving on http://127.0.0.1:{port}/")
