"""Common configuration defs"""

import json
import os
from enum import Enum
from getpass import getuser
from .logging_utils import get_logger

logger = get_logger()


class Environment(Enum):
    """Backend environment to communicate with"""

    CI = "ci"
    LOCAL = "local"
    TEST = "test"
    PROD = "prod"


PICTORUS_ENV = Environment(os.environ.get("PICTORUS_ENV", Environment.PROD.value))

API_PREFIX = {
    Environment.CI: "http://127.0.0.1:5000",
    Environment.LOCAL: "http://127.0.0.1:5000",
    Environment.TEST: "https://api.test.pictor.us",
    Environment.PROD: "https://api.pictor.us",
}[PICTORUS_ENV]

# Some linux distros seem to resolve the incorrect path
# as sudo unless the username is explicitly passed in
DEVICE_MGR_DIR = os.path.expanduser(f"~{getuser()}/.pictorus/device_manager")
APP_ASSETS_DIR = os.path.join(DEVICE_MGR_DIR, "apps/")

CONFIG_PATH = os.path.join(DEVICE_MGR_DIR, "config.json")
APP_MANIFEST_PATH = os.path.join(DEVICE_MGR_DIR, "app_manifest.json")
DEFAULT_APP_MANIFEST = {"targets": [], "target_states": {}}


class Config:
    """Device manager configuration"""

    AUTO_UPDATE_KEY = "autoUpdate"
    USE_PRERELEASE_KEY = "usePrerelease"

    _instance = None

    def __init__(self):
        self._config = self._load_config()

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)

        return cls._instance

    def is_empty(self) -> bool:
        return not self._config

    @property
    def client_id(self) -> str:
        return self._config["clientId"]

    @property
    def mqtt_endpoint(self) -> str:
        return self._config["mqttEndpoint"]

    @property
    def credentials(self) -> dict:
        return self._config["credentials"]

    @property
    def auto_update(self) -> bool:
        return self._config.get(self.AUTO_UPDATE_KEY, True)

    @auto_update.setter
    def auto_update(self, value: bool):
        self._update_config(self.AUTO_UPDATE_KEY, value)

    @property
    def use_prerelease(self) -> bool:
        return self._config.get(self.USE_PRERELEASE_KEY, False)

    @use_prerelease.setter
    def use_prerelease(self, value: bool):
        self._update_config(self.USE_PRERELEASE_KEY, value)

    @staticmethod
    def _load_config():
        """Load the config file"""
        if not os.path.exists(CONFIG_PATH):
            return {}

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_config(self):
        os.makedirs(DEVICE_MGR_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._config, f)

    def store_config(self, config: dict):
        """Store config.json file with device info"""
        self._config = config
        self._write_config()

    def _update_config(self, key: str, value):
        """Update and persist a single config value"""
        self._config[key] = value
        self.store_config(self._config)


def load_app_manifest():
    """Load the app manifest file"""
    if not os.path.exists(APP_MANIFEST_PATH):
        return DEFAULT_APP_MANIFEST.copy()

    try:
        with open(APP_MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning("Corrupted app_manifest, deleting")
        try:
            os.remove(APP_MANIFEST_PATH)
        except FileNotFoundError:
            logger.debug("Unable to delete manifest file, not found: %s", APP_MANIFEST_PATH)
        except OSError as exc:
            logger.error("Unable to delete manifest file, OS Error: %s", exc)

    return DEFAULT_APP_MANIFEST.copy()


def store_app_manifest(manifest: dict):
    """Store the app manifest file"""
    os.makedirs(DEVICE_MGR_DIR, exist_ok=True)
    with open(APP_MANIFEST_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest))


def delete_app_manifest():
    """Delete the app manifest file"""
    try:
        os.remove(APP_MANIFEST_PATH)
        logger.info("App manifest deleted")
    except FileNotFoundError:
        logger.debug("Unable to delete manifest file, not found: %s", APP_MANIFEST_PATH)
    except OSError as exc:
        logger.error("Unable to delete manifest file, OS Error: %s", exc)
