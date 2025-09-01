# from datetime import timedelta
import shutil
import re
import os

# import time
# import traceback
# import string
# from urllib import parse
import yaml

# from dateutil import parser
# from glom import glom, assign


# ---------------------------------------------------------
# General Helpers
# ---------------------------------------------------------

from agptools.helpers import (
    # path
    expandpath,
    # config
    # load_config,
    # save_config,
    # uri
    # parse_uri,
    # build_uri,
    # base codification
    # convert_base,
    # from_base,
    # new_uid,
    # jinja2
    # escape,
    # fmt,
    # setdefault,
    # converters
    # I,
    # INT,
    # FLOAT,
    # BOOL,
    # DATE,
    # DURATION,
    # COLOR,
    # PRIORITY,
    # console
    # banner,
)


# ---------------------------------------------------------
# Local imports
# ---------------------------------------------------------
from ..definitions import DEFAULT_LANGUAGE, MAPPING

from .loaders import ModuleLoader

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)

# subloger = logger(f'{__name__}.subloger')
# import jmespath


# ----------------------------------------------------------
# Progress
# ----------------------------------------------------------
from agptools.progress import Progress


# ----------------------------------------------------------
# Workspace helpers
# ----------------------------------------------------------
def find_folder(top, pattern):
    for root, folders, files in os.walk(top):
        for src in folders:
            src = os.path.join(root, src)
            if re.search(pattern, src):
                return src

        for src in files:
            src = os.path.join(root, src)
            if re.search(pattern, src):
                return src


def merge_folder(source, target, pattern="."):
    os.makedirs(target, exist_ok=True)

    for root, folders, files in os.walk(source):
        for src in folders:
            src = os.path.join(root, src)
            if not re.search(pattern, src):
                continue
            relpath = src.split(source)[-1][1:]
            dst = os.path.join(target, relpath)
            if not os.path.exists(dst):
                os.makedirs(dst)

        for src in files:
            src = os.path.join(root, src)
            if not re.search(pattern, src):
                continue
            relpath = src.split(source)[-1][1:]
            dst = os.path.join(target, relpath)
            if not os.path.exists(dst):
                shutil.copyfile(src, dst)


def build_workspace(path=None, interactive=True, package_folder=None):
    if not path:
        path = "."

    if not package_folder:
        loader = ModuleLoader(__file__)
        root = package_folder = loader.get_project_root()

    root = expandpath(path)
    if interactive:
        log.info("Creating / updating workspace in %s", root)
    os.makedirs(root, exist_ok=True)

    mapping_path = os.path.join(root, "mapping.yaml")
    if not os.path.exists(mapping_path):
        yaml.dump(
            MAPPING, open(mapping_path, "wt", encoding="utf-8"), Dumper=yaml.Dumper
        )

    # # Interests
    # mapping = yaml.load(open(mapping_path), Loader=yaml.Loader)
    # LANG_UX_CONFIG["interest"][-1] = mapping["default"]

    # for table, (klass, default_names, default_mapping) in LANG_UX_CONFIG.items():
    #     default_names = default_names or {k: k for k in [e.value for e in klass]}
    #     names = {DEFAULT_LANGUAGE: default_names}
    #     build_configuration_ui_config(root, table, names, klass, default_mapping)

    # # markov chains
    # markov = build_markov_configuration(root)

    # Stats / KPI
    stats_path = os.path.join(root, "stats.yaml")
    db_path = expandpath(os.path.join(root, "db"))

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
            "active_ports": [".*"],
            "app_url": "https://domain:9080",
            "app_url_dev": "https://smartmodels.spec-cibernos.com",
            "app_dev": True,
            # "mapping_url": mapping_path,
            # "markov": markov,
            # "interest_url": interests_path,
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
            "db_url": db_path,
            "folders": {
                "data": f"{root}/data/",
            },
            "num_threads": 8,
            "surreal_url": "http://localhost:9080",
        }

        # initial active ports found
        from ..api import ports

        # show found active ports
        # add '.*' regexp pattern to include any other port created later
        # later by default, so it must be visible until user manually will change
        # which ports wants to be exposed or not
        loader = ModuleLoader(ports)

        db[loader.ACTIVE_PORT_KEY] = loader.available_modules() + [".*"]

        # lang specific configuration
        # lang = DEFAULT_LANGUAGE
        # for table, (klass, default_names, default_mapping) in LANG_UX_CONFIG.items():
        #     _path = os.path.join(root, f"{table}" + ".{lang}.yaml")
        #     db[f"{table}_url"] = _path

        yaml.dump(db, open(config_path, "wt", encoding="utf-8"), Dumper=yaml.Dumper)

    # check folder in config file
    cfg = yaml.load(open(config_path, "rt", encoding="utf-8"), Loader=yaml.Loader)

    # create working folders
    for name in cfg["folders"].values():
        path = os.path.join(root, name)
        os.makedirs(path, exist_ok=True)

    # coping deployments files
    deploy = find_folder(package_folder, "deploy")
    if deploy:
        source = os.path.join(deploy, "static")
        target = os.path.join(root, "static")
        merge_folder(source, target)
    else:
        print("Warning: unable to find 'deploy'")

    # copy some files
    for path in ["logging.yaml"]:
        src = os.path.join(package_folder, path)
        dst = os.path.join(root, path)
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)

    # check .env file
    env_path = os.path.join(root, ".env")
    if not os.path.exists(env_path):
        content = f"""# ENV variables
OPENAI_API_KEY=
"""
        open(env_path, "wt").write(content)

    # check gitlab_cfg_path file
    # if not os.path.exists(gitlab_cfg_path):
    # content = f"""


# [global]
# default = spec
# ssl_verify = true
# timeout = 10

# [spec]
# url = https://git.spec-cibernos.com
# private_token = glpat-ZZ_xxxx
# api_version = 4

# [elsewhere]
# url = http://else.whe.re:8080
# private_token = helper: path/to/helper.sh
# timeout = 1
# """
# open(gitlab_cfg_path, "wt").write(content)
