"""Define models used for interacting with the platform."""

from os import getenv
from typing import Optional, Union

from pydantic import BaseModel, SecretStr

from regscale.core.login import get_regscale_token
from regscale.core.utils.urls import generate_regscale_domain_url
from regscale.core.app.api import Api
from regscale.core.app.application import Application


class RegScaleAuth(BaseModel):
    """Define the authorization of a RegScale Authorization of a RegScale auth method for authorizing.
    You can define it specifically:
    >>> rsa = RegScaleAuth(user_id='manic', auth_token='moose')
    or if the proper envars are setup
    >>> rsa = RegScaleAuth.authenticate() # optional arguments, defaults to envars
    """

    domain: Optional[str] = None
    user_id: Optional[str] = None
    auth_token: Optional[SecretStr] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None

    @property
    def token(self):
        """Render the token as a property
        Since this is a property, it can be referred to thusly:
        >>> rsa = RegScaleAuth('macho', 'mosquito')
        >>> print(rsa)
        RegScaleAuth(username='macho', password='**********')
        >>> rsa.token
        'mosquito'
        """
        return "Bearer " + self.auth_token.get_secret_value()

    @classmethod
    def authenticate(
        cls,
        api: Api,
        username: Optional[str] = None,
        password: Optional[Union[str, SecretStr]] = None,
        domain: Optional[str] = None,
        mfa_token: Optional[str] = None,
    ) -> "RegScaleAuth":
        """
        Authenticate with RegScale and return a token and a user_id
        :param Api api: API Object used for authentication
        :param Optional[str] username: Username to log in with, defaults to None
        :param Optional[Union[str, SecretStr]] password: Password to log in with, defaults to None
        :param Optional[str] domain: Domain to log into, defaults to None
        :param Optional[str] mfa_token: mfa_token to verify, defaults to None
        :return: RegScaleAuth object
        :rtype: RegScaleAuth
        """
        # TODO - better implementation and retrieval, but at what stage?
        if username is None:
            # should refactor to `get_username` method to account for other storage methods
            username = getenv("REGSCALE_USER")
        if not username:
            raise ValueError(
                "Username could not be derived from the environment"
                " check upstream scripts for failure to pass to here or "
                "setup the proper environment variables mentioned in the "
                "documentation."
            )
        if password is None:
            # should refactor to `get_password` method to account for other storage methods
            password = getenv("REGSCALE_PASSWORD") or getenv("REGSCALE_PASS")
        if not password:
            raise ValueError(
                "Password could not be found in either environment variable checked and the string was not "
                "passed to this function, check your script logic."
            )
        if domain is None:
            # should refactor to `get_domain` method to account for other storage methods
            domain = generate_regscale_domain_url()
        if isinstance(password, str):
            password = SecretStr(password)
        # now we create this `auth` object
        # FIXME - why does it need oldPassword
        # TODO - HttpBasicAuth at minimum
        uid, auth_token = get_regscale_token(
            api=api,
            username=username,
            password=password.get_secret_value(),
            domain=domain,
            mfa_token=mfa_token,
        )
        return cls(
            user_id=uid,
            auth_token=auth_token,
            domain=domain,
            username=username,
            password=password,
        )

    def refresh(self) -> None:
        """
        Refresh the token

        :rtype: None
        """
        api = Api()
        uid, auth_token = get_regscale_token(api=api, username=self.username, password=self.token, domain=self.domain)
        self.user_id = uid
        self.auth_token = SecretStr(auth_token)
