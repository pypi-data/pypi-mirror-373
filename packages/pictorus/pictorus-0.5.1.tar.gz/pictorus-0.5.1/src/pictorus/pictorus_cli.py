#!/usr/bin/env python3

"""CLI entrypoint for pictorus device manager"""
import argparse
import logging
import platform
import socket
import sys
from urllib.parse import urljoin
import shutil
import json
from typing import Union
import requests

from pictorus.config import API_PREFIX, PICTORUS_ENV, Config, Environment, delete_app_manifest
from pictorus.constants import PICTORUS_SERVICE_NAME
from pictorus import __version__
from pictorus.daemons.utils import get_daemon, is_other_device_manager_running
from pictorus.exceptions import DaemonError
from pictorus.logging_utils import TextFormat, printf, get_logger

logger = get_logger()

config = Config()

DEFAULT_AUTH_ERROR = "Unable to authenticate with pictorus"
DAEMON_NOT_FOUND = (
    "Pictorus device manager was unable to find a Pictorus daemon for this system."
    "Please check that it has been installed."
)


def configure_additional_settings():
    """Configure any additional settings that require user input"""
    # Disabling this prompt for now, if users want to opt out of auto updates they can
    # edit the config file directly. We are still making a lot of breaking changes to the API,
    # so better to keep people up-to-date
    logger.debug("Configuring additional settings")
    config.auto_update = True
    config.use_prerelease = PICTORUS_ENV != Environment.PROD


def configure(args: argparse.Namespace):
    """Configure the device manager"""
    logger.debug("Configuring device manager with args: %s", args)
    configure_device(token=args.token)
    setup_device_manager()
    configure_additional_settings()
    logger.debug("Device manager configuration complete")


def setup_device_manager():
    """Setup and start the device manager service"""
    print("Setting up device manager service")
    bin_path = shutil.which("pictorus-device-manager")
    if not bin_path:
        printf("Unable to set up device manager: executable missing", TextFormat.WARNING)
        return

    logger.debug("Setting up device manager daemon")
    daemon = get_daemon()
    daemon.create_service(
        PICTORUS_SERVICE_NAME,
        "Service to manage Pictorus apps",
        bin_path,
    )
    printf("Configured device manager service", TextFormat.OKGREEN)


def try_device_configuration(
    device_name: str,
    system_data: dict,
    token: str,
) -> bool:
    """Try to configure the device"""
    if not token:
        raise ValueError("Access token must be provided")

    logger.debug("Calling device registration endpoint")
    res = requests.post(
        urljoin(API_PREFIX, "v2/devices"),
        json={
            "name": device_name,
            "system": system_data,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    if not res.ok:
        logger.debug("Failed to register device: %s", res.text)
        try:
            message = res.json().get("message", DEFAULT_AUTH_ERROR)
        except json.JSONDecodeError:
            message = DEFAULT_AUTH_ERROR

        printf(f"Failed to configure device: {message}", TextFormat.FAIL)
        return False

    logger.debug("Device registration successful")
    config.store_config(res.json())
    return True


def configure_device(token: Union[str, None] = None):
    """Configure this device to connect to pictorus"""
    logger.debug("Attempting to configure device")
    if not config.is_empty():
        confirm = input(
            "It looks like this device is already configured."
            " Would you like to overwrite it [y/N]? "
        )
        if confirm.lower() != "y":
            printf("Skipping device registration", TextFormat.OKCYAN)
            return

        # Delete the existing app manifest since a reconfigure should remove
        # any previous targets
        printf("Deleting existing app manifest", TextFormat.OKCYAN)
        delete_app_manifest()

    hostname = socket.gethostname()
    device_name = input(f"Device Name [{hostname}]: ")
    device_name = device_name or hostname
    logger.debug("Using device name: %s", device_name)

    system_data = {
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
    }
    logger.debug("System data for device registration: %s", system_data)

    token = token or input("Enter access token for pictorus: ")
    if not try_device_configuration(device_name, system_data, token):
        raise SystemExit(1)

    printf(f"Successfully configured device: {device_name}", TextFormat.OKGREEN)


def service_manager(args: argparse.Namespace):
    """Manage the Pictorus device manager service"""

    try:
        daemon = get_daemon()
    except DaemonError as e:
        printf(f"Error: {e}", TextFormat.FAIL)
        return

    if args.start:
        if is_other_device_manager_running():
            sys.exit(1)

        if config.is_empty():
            printf(
                "Device is not configured. Please run " "'pictorus configure' first.",
                TextFormat.FAIL,
            )
            return

        printf("Starting Pictorus device manager service", TextFormat.OKCYAN)
        daemon.start_service(PICTORUS_SERVICE_NAME)
        daemon.enable_service(PICTORUS_SERVICE_NAME)
        printf("Pictorus device manager service started", TextFormat.OKGREEN)

    elif args.stop:
        printf("Stopping Pictorus device manager service", TextFormat.OKCYAN)
        daemon.stop_service(PICTORUS_SERVICE_NAME)
        printf("Pictorus device manager service stopped", TextFormat.OKGREEN)

    elif args.restart:
        printf("Restarting Pictorus device manager service", TextFormat.OKCYAN)
        daemon.stop_service(PICTORUS_SERVICE_NAME)

        if is_other_device_manager_running():
            sys.exit(1)

        daemon.start_service(PICTORUS_SERVICE_NAME)
        printf("Pictorus device manager service restarted", TextFormat.OKGREEN)


def log_manager(args: argparse.Namespace):
    """Manage the Pictorus device manager logs"""
    daemon = get_daemon()
    printf("Fetching logs...", TextFormat.OKCYAN)

    logs = daemon.logs(PICTORUS_SERVICE_NAME, args.number)
    print(logs)


def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Pictorus device manager")
    subparsers = parser.add_subparsers()

    parser.add_argument(
        "--version",
        action="version",
        version=f"Running {__version__} of the Pictorus Device Manager and CLI",
        help="Show the version of the Pictorus device manager",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    parser_config = subparsers.add_parser("configure", help="Configure this device")
    parser_config.add_argument(
        "--token",
        help="Authentication token. If not provided, you will be prompted to enter it",
    )
    parser_config.set_defaults(func=configure)

    parser_service = subparsers.add_parser("service", help="Manage Pictorus services")
    parser_service.add_argument(
        "--start",
        action="store_true",
        help="Start the Pictorus device manager service",
    )
    parser_service.add_argument(
        "--stop",
        action="store_true",
        help="Stop the Pictorus device manager service",
    )
    parser_service.add_argument(
        "--restart",
        action="store_true",
        help="Stop the Pictorus device manager service",
    )
    parser_service.set_defaults(func=service_manager)

    parser_logs = subparsers.add_parser(
        "logs", help="Interact with the Pictorus device manager logs"
    )
    parser_logs.add_argument(
        "-n",
        "--number",
        nargs="?",
        metavar="LINES",
        help="Fetch N lines from the Pictorus device manager log, or all if not specified",
        type=positive_int,
    )
    parser_logs.set_defaults(func=log_manager)

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        printf("Debug logging enabled", TextFormat.OKCYAN)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
