import subprocess
import os
from typing import Union

from pictorus.daemons.daemon import Daemon

LAUNCHD_DIR = os.path.expanduser("~/Library/LaunchAgents/")
LAUNCHCTL_BIN = "launchctl"
PLIST_NAME = "us.pictor.dm.plist"
PLIST_PATH = os.path.join(LAUNCHD_DIR, PLIST_NAME)
SERVICE_LABEL = "pictorus_device_manager"

SERVICE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>{service_label}</string>
        <key>Program</key>
        <string>{bin_path}</string>

        <key>StandardErrorPath</key>
        <string>/tmp/pictorus.err</string>
        <key>StandardOutPath</key>
        <string>/tmp/pictorus.out</string>
    </dict>
</plist>
"""  # noqa: E501 - Trying to format a system file


class Launchd(Daemon):
    def fill_service_template(self, bin_path):
        return SERVICE_TEMPLATE.format(service_label=SERVICE_LABEL, bin_path=bin_path)

    def create_service_file(self, service_name: str, description: str, bin_path: str):
        """Create a launchd service file"""
        service_content = self.fill_service_template(bin_path)
        with open(
            os.path.expanduser(os.path.join(LAUNCHD_DIR, PLIST_PATH)), "w", encoding="utf-8"
        ) as service_file:
            service_file.write(service_content)

    def stop_service(self, service_name: str):
        """Stop a given service"""
        self.run(
            [LAUNCHCTL_BIN, "bootout", f"gui/{os.getuid()}", PLIST_PATH],
            check=False,
            cwd=LAUNCHD_DIR,
        )

    def start_service(self, service_name: str):
        """Start a given service"""
        self.run(
            [LAUNCHCTL_BIN, "bootstrap", f"gui/{os.getuid()}", PLIST_PATH],
            check=False,
            cwd=LAUNCHD_DIR,
        )

    def enable_service(self, service_name: str):
        """Start a given service"""
        # This was obnoxious to figure out. The kickstart command references the "Label"
        # of the plist file and not the name of the file, unlike bootstrap and bootout.
        self.run(
            [LAUNCHCTL_BIN, "kickstart", "-k", f"gui/{os.getuid()}/{SERVICE_LABEL}"],
            check=False,
            cwd=LAUNCHD_DIR,
        )

    def reload_daemon(self, service_name: str):
        """Reload the launchd daemon"""

    def run(self, cmd: list, check=True, cwd=None):
        subprocess.run(cmd, check=check, cwd=cwd)

    def logs(self, service_name: str, number_of_lines: Union[int, None]) -> str:
        """Get the logs for a given service"""
        # Launchd does not have a direct command to fetch logs like systemd.
        # Instead, we can read the log files directly.
        err_log_path = "/tmp/pictorus.err"

        if os.path.exists(err_log_path):
            with open(err_log_path, "r") as err_file:
                err_logs = err_file.read().splitlines()
                if number_of_lines is not None:
                    err_logs = err_logs[-number_of_lines:]  # Get the last N lines
                err_logs = "\n".join(err_logs)  # Convert from list to string
        else:
            err_logs = "No error logs found."

        return f"{err_logs}"
