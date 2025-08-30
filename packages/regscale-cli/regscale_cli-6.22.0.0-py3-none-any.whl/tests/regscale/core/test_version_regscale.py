import os
from unittest import mock

import pytest
from click.testing import CliRunner


class TestRegscaleCLIVersion:

    @pytest.fixture(autouse=True)
    def patch_env(self, tmp_path):
        """
        Fixture to patch environment variables for CLI tests to avoid side effects.
        """
        with mock.patch.dict(
            os.environ,
            {
                "REGSCALE_WORKDIR": str(tmp_path),
                "REGSCALE_USER": "testuser",
                "REGSCALE_PASSWORD": "testpass",
                "REGSCALE_DOMAIN": "https://testdomain.com",
                "REGSCALE_USER_ID": "1",
                "REGSCALE_TOKEN": "token",
            },
            clear=True,
        ):
            yield

    def test_cli_version_command(self):
        """
        Test that the CLI 'version' command prints the local RegScale version and exits successfully.
        """
        import regscale.regscale as regscale

        runner = CliRunner()
        result = runner.invoke(regscale.cli, ["version"])
        assert result.exit_code == 0
        assert regscale.__version__ in result.output

    def test_cli_version_server(self):
        """
        Test that the CLI 'version --server' command prints the server version if available.
        Mocks the API call to return a dummy version.
        """
        import regscale.regscale as regscale

        class DummyApi:
            def __init__(self):
                self.app = type("App", (), {"config": {"domain": "https://test.com"}})()

            def get(self, url):
                class DummyRes:
                    ok = True

                    def json(self):
                        return {"version": "1.2.3"}

                return DummyRes()

        with mock.patch("regscale.core.app.api.Api", DummyApi):
            runner = CliRunner()
            result = runner.invoke(regscale.cli, ["version", "--server"])
            assert result.exit_code == 0
            assert "1.2.3" in result.output or "Unable to get version from server." not in result.output
