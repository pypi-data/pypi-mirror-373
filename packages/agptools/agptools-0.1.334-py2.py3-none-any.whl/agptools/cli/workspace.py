import re
import os
import yaml

import click

from .main import *
from .config import *

@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def workspace(env):
    """subcommands for manae workspaces for agptools"""
    # banner("User", env.__dict__)
    pass


@workspace.command()
@click.option("--path", default=None)
@click.pass_obj
def new(env, path):
    """Create a new workspace for agptools"""
    # force config loading
    config.callback()

    # TODO: add your new workspace configuratoin folder here ...
if not path:
        path = "."

    root = expandpath(path)
    print(f"Creating / updating workspace in {root}")
    os.makedirs(root, exist_ok=True)

    # database for stats
    stats_path = os.path.join(root, 'stats.yaml')
    gitlab_cfg_path = os.path.join(root, '.python-gitlab.cfg')
    db_path = os.path.join(root, 'db')
    if not os.path.exists(stats_path):
        db = {
            'kpi_1': 0.73,
            'kpi_2': 0,
        }
        yaml.dump(db, open(stats_path, 'wt'), Dumper=yaml.Dumper)

    # config file
    config_path = os.path.join(root, 'config.yaml')
    if not os.path.exists(config_path):
        db = {
            'templates': {
                'compiled': {
                    '{root}/{reldir}/compiled/{basename}.json': [
                        r'(?P<dirname>.*)[/\/](?P<basename>(?P<name>.*?)(?P<ext>\.[^\.]+$))'
                    ],
                },
                'error': {
                    '{root}/error/{reldir}/{basename}': [
                        r'(?P<dirname>.*)[/\/](?P<basename>(?P<name>.*?)(?P<ext>\.[^\.]+$))'
                    ],
                },
            },
            'stats': stats_path,
            'db': db_path,
            'folders': {
                'data': f'{root}/data/',
            },
            'gitlab_cfg_path': gitlab_cfg_path,
            'gitlab_instance': 'spec',
            'num_threads': 8,
        }
        yaml.dump(db, open(config_path, 'wt'), Dumper=yaml.Dumper)

    # check folder in config file
    cfg = yaml.load(open(config_path, 'rt'), Loader=yaml.Loader)

    # create working folders
    for name in cfg['folders'].values():
        path = os.path.join(root, name)
        os.makedirs(path, exist_ok=True)

    # check .env file
    env_path = os.path.join(root, '.env')
    if not os.path.exists(env_path):
        content = f"""# ENV variables
PYTHON_GITLAB_CFG={gitlab_cfg_path}
OPENAI_API_KEY=
"""
        open(env_path, 'wt').write(content)

    # check gitlab_cfg_path file
    if not os.path.exists(gitlab_cfg_path):
        content = f"""
[global]
default = spec
ssl_verify = true
timeout = 10

[spec]
url = https://git.spec-cibernos.com
private_token = glpat-ZZ_TDbasg1CsyCsa4ihG
api_version = 4

[elsewhere]
url = http://else.whe.re:8080
private_token = helper: path/to/helper.sh
timeout = 1
"""
        open(gitlab_cfg_path, 'wt').write(content)


@workspace.command()
@click.pass_obj
def list(env):
    """List existing workspaces for agptools"""
    # force config loading
    config.callback()

    # TODO: add your new workspace configuratoin folder here ...


