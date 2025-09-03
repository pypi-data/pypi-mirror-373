import sys
from unittest import TestCase, mock
import responses
from subprocess import CalledProcessError

from semver import VersionInfo

import pictorus as pictorus
from pictorus.updates_manager import UpdatesManager
from pictorus.config import Config

config = Config()


class TestUpdatesManager(TestCase):
    def setUp(self):
        config.use_prerelease = False
        self.um = UpdatesManager()
        self.version = VersionInfo.parse(pictorus.__version__)

    @responses.activate
    def test_check_for_newer_version_has_new_version(self):
        new_version = self.version.bump_patch()
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"info": {"version": str(new_version)}},
        )
        assert self.um.check_for_newer_version() == str(new_version)

    @responses.activate
    def test_check_for_newer_version_prerelease(self):
        rc_version = self.version.bump_minor().bump_prerelease("rc")
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"releases": {str(rc_version): []}},
        )
        config.use_prerelease = True
        assert self.um.check_for_newer_version() == str(rc_version)

    @responses.activate
    def test_check_for_newer_version_no_update(self):
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"info": {"version": pictorus.__version__}},
        )
        assert self.um.check_for_newer_version() is None

    @responses.activate
    def test_check_for_newer_version_request_failure(self):
        responses.add(responses.GET, "https://pypi.org/pypi/pictorus/json", status=500)
        assert self.um.check_for_newer_version() is None
        assert self.um._transient_check_fail is True

    @responses.activate
    def test_check_for_newer_version_uses_cached_version_from_last_update(self):
        new_version = self.version.bump_patch()
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"info": {"version": str(new_version)}},
        )
        self.um._last_installed = str(new_version)
        assert self.um.check_for_newer_version() is None

    @mock.patch("pictorus.updates_manager.sp.check_call")
    def test_install_version_success(self, m_check_call):
        version = "1.2.3"
        self.um.install_version(version)
        m_check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", f"pictorus=={version}"]
        )

    @responses.activate
    def test_check_update_from_rc_to_rc(self):
        self.um._last_installed = "1.2.3rc4"
        new_version = "1.2.3rc5"
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"releases": {str(new_version): []}},
        )
        config.use_prerelease = True
        assert self.um.check_for_newer_version() == new_version

    @responses.activate
    def test_check_update_from_rc_to_stable(self):
        self.um._last_installed = "1.2.3rc4"
        new_version = "1.2.3"
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"info": {"version": str(new_version)}},
        )
        config.use_prerelease = False
        assert self.um.check_for_newer_version() == new_version

    @responses.activate
    def test_check_dont_update_to_newer_rc_if_use_prerelease_false(self):
        self.um._last_installed = "1.2.3rc4"
        new_rc_version = "1.2.3rc5"
        new_stable_version = "1.2.2"
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={
                "info": {"version": str(new_stable_version)},
                "releases": {str(new_rc_version): []},
            },
        )
        config.use_prerelease = False
        assert self.um.check_for_newer_version() is None

    @mock.patch("pictorus.updates_manager.sp.check_call")
    def test_install_version_fails(self, m_check_call):
        m_check_call.side_effect = CalledProcessError(99, "pip install")
        version = "2.3.4"
        with self.assertRaises(CalledProcessError):
            self.um.install_version(version)

        m_check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", f"pictorus=={version}"]
        )

    @mock.patch("pictorus.updates_manager.cp.Cache")
    @mock.patch("pictorus.updates_manager.time.sleep")
    def test_update_ocd_cache_retries_on_failure(self, _, m_cache):
        def set_cache_index():
            cache.index = {"foo": "bar"}

        cache_values = [mock.Mock(), mock.Mock(), mock.Mock()]
        for cache in cache_values:
            cache.index = None
            cache.cache_descriptors.return_value = None

        cache_values[2].cache_descriptors.side_effect = set_cache_index

        m_cache.side_effect = cache_values

        with mock.patch.object(self.um, "TRANSIENT_FAIL_CHECK_FREQUENCY_S", 0):
            self.um.update_ocd_cache()

        assert m_cache.call_count == 3

    @mock.patch("pictorus.updates_manager.cp.Cache")
    def test_update_ocd_cache_returns_on_success(self, m_cache):
        def set_cache_index():
            cache.index = {"foo": "bar"}

        cache = mock.Mock()
        cache.index = None
        cache.cache_descriptors.side_effect = set_cache_index

        m_cache.return_value = cache
        self.um.update_ocd_cache()
        assert m_cache.call_count == 1

    @mock.patch("pictorus.updates_manager.cp.Cache")
    def test_update_ocd_cache_skips_if_already_cached(self, m_cache):
        cache = mock.Mock()
        cache.index = {"foo": "bar"}

        self.um.update_ocd_cache()

        assert cache.cache_descriptors.call_count == 0
        assert m_cache.call_count == 1
