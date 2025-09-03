"""Provide simple functions for interacting with URLs."""

from os import getenv
from re import match

from regscale.core.static.regex import URL_REGEX


def generate_regscale_domain_url(
    domain: str = getenv("REGSCALE_DOMAIN"),
) -> str:
    """Generate a RegScale domain url

    :param str domain: The domain to use, defaults to getenv("REGSCALE_DOMAIN")
    :raises EnvironmentError: if domain is None
    :return: The domain url
    :rtype: str
    """
    if domain is None:
        raise EnvironmentError("The `REGSCALE_DOMAIN` envar needs set or pass domain arg.")
    if match(URL_REGEX, domain) is not None:
        return domain
    return f"https://{domain}.regscale.io"
