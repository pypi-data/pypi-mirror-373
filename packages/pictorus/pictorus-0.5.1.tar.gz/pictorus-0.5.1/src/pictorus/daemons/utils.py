import os
import shutil

import psutil

from pictorus.daemons.daemon import Daemon
from pictorus.daemons.launchd import Launchd
from pictorus.daemons.sudosystemd import SudoSystemd
from pictorus.daemons.systemd import Systemd
from pictorus.exceptions import DaemonError
from pictorus.logging_utils import TextFormat, printf

PICTORUS_PROCESS_NAME = "pictorus-device-manager"


def is_other_device_manager_running() -> bool:
    # Pictorus device manager is running as a Python script that is in the 'cmdline' part of the
    # process. psutil.info['cmdline'] is an array that needs to be searched for the script name.
    other_pictorus_device_managers_running = False
    pid = os.getpid()
    ancestor_pids = {p.pid for p in psutil.Process(pid).parents()}
    ancestor_pids.add(pid)

    other_pids = []
    for process in psutil.process_iter(["pid", "cmdline"]):
        info = process.as_dict(attrs=["pid", "cmdline"])
        if info["cmdline"]:
            if not process.is_running():
                continue

            if process.status() in (psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD):
                continue

            if info["pid"] in ancestor_pids:
                # Don't count self or ancestors as other instances
                continue

            if any(PICTORUS_PROCESS_NAME in arg for arg in info["cmdline"]):
                other_pids.append(info["pid"])
                other_pictorus_device_managers_running = True

    # One instance is ok, more than one means another instance is probably running.
    if other_pictorus_device_managers_running:
        printf(
            (
                "Pictorus device manager is already running, either as a service or manually"
                " in another terminal session. "
            ),
            TextFormat.FAIL,
        )
        printf(
            ("Process ID(s) of running pictorus-device-manager instance(s): {}".format(other_pids)),
            TextFormat.FAIL,
        )
        printf(
            (
                'Use "pictorus-cli service --stop" to stop the service if'
                ' you would like to run "pictorus-device-manager" manually from the terminal.'
                ' If you are having issues connecting to the device try "pictorus-cli service'
                ' --restart" to reset the service.'
            ),
            TextFormat.OKCYAN,
        )

    return other_pictorus_device_managers_running


def get_daemon() -> Daemon:
    """Stop the Pictorus device manager service"""
    operating_system = os.uname().sysname
    if operating_system == "Darwin":
        daemon = Launchd()

        if not shutil.which("launchctl"):
            raise DaemonError("Unable to set up device manager: launchctl not found")

    elif operating_system == "Linux":
        if os.getuid() == 0:  # Running as root
            daemon = SudoSystemd()
        else:
            daemon = Systemd()

        if not shutil.which("systemctl"):
            raise DaemonError("Unable to set up device manager: systemctl not found")

    else:
        raise DaemonError("Unsupported operating system")

    return daemon
