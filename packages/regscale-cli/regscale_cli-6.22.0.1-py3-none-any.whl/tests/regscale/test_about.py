import pytest
from unittest.mock import patch
from click.testing import CliRunner


def test_about_no_variable_fetch():
    """
    Test that the about command runs successfully without fetching any variables
    """
    with patch("regscale.core.app.utils.variables.RsVariablesMeta.fetch_config_value") as mock_fetch:
        # Import after patching to ensure the mock takes effect
        from regscale.regscale import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["about"])

        assert result.exit_code == 0
        assert "RegScale CLI Version:" in result.output
        mock_fetch.assert_not_called()
