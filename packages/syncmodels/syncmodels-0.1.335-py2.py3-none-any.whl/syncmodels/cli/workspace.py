import re
import os
import yaml

import click

from .main import *
from .config import *


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def workspace(env):
    """subcommands for manae workspaces for syncmodels"""
    # banner("User", env.__dict__)
    pass


@workspace.command()
@click.option("--path", default=None)
@click.pass_obj
def new(env, path):
    """Create a new workspace for syncmodels"""
    # force config loading
    config.callback()

    if not path:
        path = "."

    root = expandpath(path)
    print(f"Creating / updating workspace in {root}")
    os.makedirs(root, exist_ok=True)

    # database for stats
    stats_path = os.path.join(root, "stats.yaml")
    db_path = os.path.join(root, "db")
    if not os.path.exists(stats_path):
        db = {
            "kpi_1": 0.73,
            "kpi_2": 0,
        }
        yaml.dump(db, open(stats_path, "wt"), Dumper=yaml.Dumper)

    # config file
    config_path = os.path.join(root, "config.yaml")
    if not os.path.exists(config_path):
        db = {
            "templates": {
                "compiled": {
                    "{root}/{reldir}/compiled/{basename}.json": [
                        r"(?P<dirname>.*)[/\/](?P<basename>(?P<name>.*?)(?P<ext>\.[^\.]+$))"
                    ],
                },
                "error": {
                    "{root}/error/{reldir}/{basename}": [
                        r"(?P<dirname>.*)[/\/](?P<basename>(?P<name>.*?)(?P<ext>\.[^\.]+$))"
                    ],
                },
            },
            "stats": stats_path,
            "db": db_path,
            "folders": {
                "data": f"{root}/data/",
            },
            "token": None,
        }
        yaml.dump(db, open(config_path, "wt"), Dumper=yaml.Dumper)

    # check folder in config file
    cfg = yaml.load(open(config_path, "rt"), Loader=yaml.Loader)

    # create working folders
    for name in cfg["folders"].values():
        path = os.path.join(root, name)
        os.makedirs(path, exist_ok=True)

    # check .env file
    env_path = os.path.join(root, ".env")
    if not os.path.exists(env_path):
        content = """# ENV variables
OPENAI_API_KEY=
"""
        open(env_path, "wt").write(content)


@workspace.command()
@click.pass_obj
def list(env):
    """List existing workspaces for syncmodels"""
    # force config loading
    config.callback()

    # TODO: add your new workspace configuratoin folder here ...
