#!/usr/bin/env python3

"""Daemon process for handling IoT interactions"""
import sys
import os
from pictorus.config import Config
from pictorus.daemons.utils import is_other_device_manager_running
from pictorus.logging_utils import get_logger
from pictorus.device_manager import DeviceManager
from pictorus.updates_manager import UpdatesManager

logger = get_logger()
config = Config()


def main():
    """Main run function"""
    if is_other_device_manager_running():
        sys.exit(1)

    log_level = os.environ.get("LOG_LEVEL", default="INFO").upper()
    logger.setLevel(log_level)
    logger.info("Starting device manager for device: %s", config.client_id)

    with UpdatesManager() as version_mgr, DeviceManager(version_mgr) as app_mgr:
        app_mgr.complete.wait()


if __name__ == "__main__":
    sys.exit(main())
