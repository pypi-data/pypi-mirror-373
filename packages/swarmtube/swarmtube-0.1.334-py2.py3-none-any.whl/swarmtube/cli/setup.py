import re
import time
import subprocess

import sys

from distutils import command

# import os
import requests

# import yaml

import click

# from pycelium.tools import soft
# from pycelium.tools.cli.inventory import credentials, expand_network
# from pycelium.tools.cli.config import (
#     # config,
#     # banner,
#     RED,
#     RESET,
#     BLUE,
#     PINK,
#     YELLOW,
#     GREEN,
# )
# from swarmtube.helpers import *
from swarmtube.cli.main import main, CONTEXT_SETTINGS
from swarmtube.cli.config import config


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def setup(env):
    """subcommands for managing workspaces for swarmtube"""
    # banner("User", env.__dict__)
    pass


def find_venv():
    for path in sys.path:
        m = re.match(
            r"(?P<virtualenv>.*/(venv|\.venv|env|virtualenv))/lib/python[^/]+/(site-packages)$",
            path,
        )
        if m:
            return m.groupdict()["virtualenv"]


def configure_unit(unit_content, service_name, service_type="service", restart=True):
    # Write the service unit to a file
    _tmp_file = f"/tmp/{service_name}.{service_type}"
    unit_file_path = f"/etc/systemd/system/{service_name}.{service_type}"
    with open(_tmp_file, "w") as unit_file:
        unit_file.write(unit_content)
    subprocess.run(["sudo", "mv", _tmp_file, unit_file_path])

    # Reload systemd to apply changes
    subprocess.run(["sudo", "systemctl", "daemon-reload"])

    # Enable and start the service
    subprocess.run(["sudo", "systemctl", "enable", service_name])
    if restart:
        subprocess.run(["sudo", "systemctl", "restart", service_name])


def _service(env, command):
    """List existing workspaces for swarmtube"""

    # Specify the service name
    service_name = __file__.split("/")[-3]

    # user and group
    user = group = os.getlogin()
    home_dir = os.path.expanduser("~")
    # where is executable
    virtualenv = find_venv()

    if virtualenv is not None:
        exec_start = (
            f"{virtualenv}/bin/python {virtualenv}/bin/{service_name} {command}"
        )
        environment = f"Environment='PATH={virtualenv}/bin'"
    else:
        exec_start = f"{home_dir}/.local/bin/{service_name} {command}"
        environment = ""

    # Define the service unit configuration
    service_unit = f"""
[Unit]
Description=swarmtube Supervisor Service
After=network.target

[Service]
ExecStart={exec_start}
{environment}

ProtectHome=false
WorkingDirectory={home_dir}/workspace/{service_name} 
#Restart=always
Restart=no
#RestartSec=5s
User={user}
Group={group}

[Install]
WantedBy=multi-user.target
"""

    timer_unit = f"""
[Unit]
Description=swarmtube reset

[Timer]
Unit={service_name}.service
#OnCalendar=hourly
#OnCalendar=*:0/30
#OnCalendar=*:0/5

#OnBootSec=10min
#RandomizedDelaySec=15min
#OnActiveSec=15min
#OnCalendar=*-*-* 0/8:00:00
OnCalendar=*-*-* 00:00:00

[Install]
WantedBy=timers.target
"""

    configure_unit(service_unit, service_name, restart=False)
    configure_unit(timer_unit, service_name, service_type="timer")


@setup.command()
@click.option("--command")
@click.pass_obj
def service(env, command):
    """Install a reset service swarmtube"""
    # force config loading
    config.callback()

    _service(env, command)


@setup.command()
@click.pass_obj
def autocomplete(env):
    """Create bash auto-completion script"""
    # force config loading
    config.callback()

    LAST_ACTIVE_WINGDEBUG = os.environ.get("ACTIVE_WINGDEBUG", 0)
    os.environ["ACTIVE_WINGDEBUG"] = False
    subprocess.run(
        ["_SWARMTUBE_COMPLETE=bash_source swarmtube > ~/.swarmtube-complete.bash"],
        shell=True,
    )
    os.environ["ACTIVE_WINGDEBUG"] = LAST_ACTIVE_WINGDEBUG

    print("for activation use:")
    print("source ~/.swarmtube-complete.bash")
