from pictorus.daemons.launchd import Launchd
from pictorus.daemons.sudosystemd import SudoSystemd
from pictorus.daemons.systemd import Systemd


def test_launchd_create_service_file(snapshot):
    launchd = Launchd()
    service = launchd.fill_service_template("some_bin_path")
    assert snapshot == service


def test_systemd_create_service_file(snapshot):
    systemd = Systemd()
    service = systemd.fill_service_template("some_description", "some_bin_path")
    assert snapshot == service


def test_sudosystemd_create_service_file(snapshot):
    systemd = SudoSystemd()
    service = systemd.fill_service_template("some_description", "some_bin_path")
    assert snapshot == service
