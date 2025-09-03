import sys
import time
import subprocess as sp
from threading import Thread
from typing import Union, Tuple
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

import requests
import cmsis_pack_manager as cp
from semver import VersionInfo

import pictorus
from pictorus.logging_utils import get_logger
from pictorus.config import Config

logger = get_logger()
config = Config()


def run_until_cancelled(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        next_cb_time = 0
        while self._run:
            should_run_cb = time.time() > next_cb_time
            if should_run_cb:
                next_sleep_duration = method(self, *args, **kwargs)
                if next_sleep_duration is None:
                    break

                next_cb_time = time.time() + next_sleep_duration
            else:
                time.sleep(1)

    return wrapper


class UpdatesManager:
    """Manage any necessary updates"""

    # Check for new version every 30 minutes
    CHECK_FREQUENCY_S = 60 * 30
    # If the check fails due to a transient error, try again after 1 minute
    TRANSIENT_FAIL_CHECK_FREQUENCY_S = 60

    def __init__(self):
        self._last_installed: Union[str, None] = None
        self._transient_check_fail = False
        self._run = True
        self._run_thread: Union[Thread, None] = None

    def __enter__(self):
        executor = ThreadPoolExecutor()
        self.ocd_update_future = executor.submit(self.update_ocd_cache)

        if not config.auto_update:
            return self

        # Start run_continuously in a separate thread
        self._run = True
        self._run_thread = Thread(target=self._check_pictorus_updates)
        self._run_thread.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._run = False
        if self._run_thread:
            self._run_thread.join()

        if not self.ocd_update_future.done():
            self.ocd_update_future.cancel()

    @property
    def last_installed(self) -> Union[str, None]:
        return self._last_installed

    def _parse_pre_release(self, version: str) -> Tuple[str, VersionInfo]:
        try:
            return (
                version,
                VersionInfo.parse(
                    version.replace("a", "-a").replace("b", "-b").replace("rc", "-rc")
                ),
            )
        except ValueError:
            return (version, VersionInfo.parse("0.0.0"))

    def check_for_newer_version(self):
        """Check if there is a new version available on pip"""
        try:
            response = requests.get("https://pypi.org/pypi/pictorus/json")
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.debug("Could not check if there is a new version of pip available.")
            self._transient_check_fail = True
            return None

        self._transient_check_fail = False

        data = response.json()
        if config.use_prerelease:
            versions = data["releases"].keys()
            all_versions = [self._parse_pre_release(v) for v in versions]
            latest_version = max(all_versions, key=lambda x: x[1])
        else:
            version: str = data["info"]["version"]
            latest_version = (version, VersionInfo.parse(version))

        current_version = self._last_installed or pictorus.__version__
        # If there is a value error, try with `_parse_pre_release`
        try:
            current_version = VersionInfo.parse(current_version)
        except ValueError:
            _, current_version = self._parse_pre_release(current_version)

        if current_version < latest_version[1]:
            return latest_version[0]

        return None

    def install_version(self, version: str):
        """Attempt to install latest version of pictorus package"""
        sp.check_call([sys.executable, "-m", "pip", "install", f"pictorus=={version}"])
        self._last_installed = version

    def _try_update_version(self):
        """Update to the latest version if a newer one is available"""
        new_version = self.check_for_newer_version()
        if not new_version:
            logger.debug("No new version of pictorus is available.")
            return

        logger.info("A new version of pictorus is available. Attempting to update...")
        try:
            self.install_version(new_version)
        except sp.CalledProcessError:
            logger.error("Could not update pictorus. Please update manually.", exc_info=True)
        else:
            logger.info("Update complete. Please restart pictorus to apply.")

    @run_until_cancelled
    def update_ocd_cache(self):
        cache = cp.Cache(True, False)
        # If the cache is already populated, no need to update
        if cache.index:
            return None

        logger.info("Attempting to update OCD cache")
        cache.cache_descriptors()
        if cache.index:
            logger.info("OCD cache updated successfully")
            return None

        # If the cache is still empty, try again after 1 minute
        logger.warning("Failed to update OCD cache. Will try again later.")
        return self.TRANSIENT_FAIL_CHECK_FREQUENCY_S

    @run_until_cancelled
    def _check_pictorus_updates(self):
        """Continuously check for updates to pictorus package"""
        self._try_update_version()

        return (
            self.TRANSIENT_FAIL_CHECK_FREQUENCY_S
            if self._transient_check_fail
            else self.CHECK_FREQUENCY_S
        )
