"""Test the platform module."""

from unittest.mock import patch

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models import platform

PATH = "regscale.models.platform"


@patch(f"{PATH}.get_regscale_token", return_value=("billy", "zane"))
def test_RegScaleAuth_model_behaves(mock_get_regscale_token):
    """The RegScaleAuth BaseModel class does lots of things, let's test them."""
    api = Api()
    un = "funkenstein"
    pw = "groovin'tothewaveoftheflag"
    domain = "disinfo.org"
    model = platform.RegScaleAuth.authenticate(
        api=api,
        username=un,
        password=pw,
        domain=domain,
    )
    mock_get_regscale_token.assert_called_once()
    assert isinstance(model, platform.RegScaleAuth)
    assert model.token == "Bearer zane"
    assert model.user_id == "billy"
    assert model.username == un
    assert model.password.get_secret_value() == pw
    assert model.domain == domain
