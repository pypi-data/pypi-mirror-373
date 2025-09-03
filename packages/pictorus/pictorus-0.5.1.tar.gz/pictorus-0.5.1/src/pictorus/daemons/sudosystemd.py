from subprocess import run, CalledProcessError
import os
from typing import Union
from pictorus.constants import JOURNALCTL_BIN, SYSTEMCTL_BIN
from pictorus.daemons.daemon import Daemon

SYSTEMD_DIR = os.path.expanduser("/etc/systemd/system/")

SERVICE_TEMPLATE = """
[Unit]
Description={description}

[Service]
ExecStart={bin_path}
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
"""


class SudoSystemd(Daemon):
    def fill_service_template(self, description, bin_path):
        return SERVICE_TEMPLATE.format(description=description, bin_path=bin_path)

    def create_service_file(self, service_name: str, description: str, bin_path: str):
        """Create a systemd service file"""

        # Create the directory if it doesn't exist
        if not os.path.exists(SYSTEMD_DIR):
            os.makedirs(SYSTEMD_DIR)

        service_content = self.fill_service_template(description, bin_path)
        with open(
            os.path.join(SYSTEMD_DIR, f"{service_name}.service"), "w", encoding="utf-8"
        ) as service_file:
            service_file.write(service_content)

    def run(self, cmd: list, check=True, cwd=None):
        run(cmd, check=check, cwd=cwd)

    def stop_service(self, service_name: str):
        """Stop a given service"""
        self.run([SYSTEMCTL_BIN, "stop", service_name], check=False)

    def start_service(self, service_name: str):
        """Start a given service"""
        self.run([SYSTEMCTL_BIN, "start", service_name])

    def enable_service(self, service_name: str):
        """Start a given service"""
        self.run([SYSTEMCTL_BIN, "enable", service_name])

    def reload_daemon(self, service_name: str = ""):
        """Reload the systemd daemon"""
        self.run([SYSTEMCTL_BIN, "daemon-reload"])

    def logs(self, service_name: str, number_of_lines: Union[int, None]) -> str:
        """Get the logs for a given service"""
        try:
            command = [JOURNALCTL_BIN, "-u", service_name, "--no-pager"]
            if number_of_lines is not None:
                command.extend(["-n", str(number_of_lines)])
            result = run(command, check=True, capture_output=True, text=True)
            return result.stdout
        except CalledProcessError as e:
            return f"Error getting logs: {e.stderr}"
