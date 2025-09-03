from unittest.mock import patch

import pytest


@pytest.fixture(scope="session", autouse=True)
def mock_config_write(request):
    # Always mock out the config write method, so it doesn't store data on the host
    write_patch = patch("pictorus.config.Config._write_config")
    write_patch.start()

    yield write_patch

    write_patch.stop()
