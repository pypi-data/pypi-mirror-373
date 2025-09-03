import subprocess
import os

SYSTEMD_DIR = "/etc/systemd/system/"
SYSTEMCTL_BIN = "systemctl"

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


def _create_service_file(service_name: str, description: str, bin_path: str):
    """Create a systemd service file"""
    service_content = SERVICE_TEMPLATE.format(description=description, bin_path=bin_path)
    with open(
        os.path.join(SYSTEMD_DIR, f"{service_name}.service"), "w", encoding="utf-8"
    ) as service_file:
        service_file.write(service_content)


def _run(cmd: list, check=True):
    subprocess.run(cmd, check=check)


def stop_service(service_name: str):
    """Stop a given service"""
    _run([SYSTEMCTL_BIN, "stop", service_name], check=False)


def start_service(service_name: str):
    """Start a given service"""
    _run([SYSTEMCTL_BIN, "start", service_name])


def enable_service(service_name: str):
    """Start a given service"""
    _run([SYSTEMCTL_BIN, "enable", service_name])


def reload_daemon():
    """Reload the systemd daemon"""
    _run([SYSTEMCTL_BIN, "daemon-reload"])


def create_service(service_name: str, description: str, bin_path: str):
    """Create and start a systemd service"""
    stop_service(service_name)
    _create_service_file(service_name, description, bin_path)
    reload_daemon()
    start_service(service_name)
    enable_service(service_name)
