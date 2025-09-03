"""Create the AppConfig objects."""

from typing import Optional
from inspect import getmembers, currentframe, isclass
from pydantic import BaseModel, create_model, SecretStr
from regscale.models.platform import RegScaleAuth


class Provider(BaseModel):
    """A provider class"""

    provider: str

    def __getitem__(self, item):
        """Override the default getitem to modify the config dict object."""
        self.__dict__.get(item)

    def __setitem__(self, key, value):
        """Override the default setitem to modify the config dict object."""
        self.__dict__[key] = value

    def refresh(self):
        """Refresh this providers data"""
        # TODO - implement the refresh method
        raise NotImplementedError("coming soon!")


providers = {
    "AdProvider": {
        "adAccessToken": (str, ...),
        "adAuthUrl": (str, ...),
        "adClientSecret": (SecretStr, ...),
        "adClientId": (SecretStr, ...),
        "adGraphURL": (str, ...),
    },
    "Azure365Provider": {
        "azure365AccessToken": (str, ...),
        "azure365ClientId": (SecretStr, ...),
        "azure365TenantId": (str, ...),
    },
    "AzureCloudProvider": {
        "azureCloudAccessToken": (SecretStr, ...),
        "azureCloudClientId": (str, ...),
        "azureCloudTenantId": (str, ...),
        "azureCloudSubscriptionId": (SecretStr, ...),
    },
    "CisaProvider": {
        "cisaKev": (
            str,
            "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        ),
        "cisa_alerts": (str, "https://www.cisa.gov/uscert/ncas/alerts/"),
        "cisa_kev": (
            str,
            "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        ),
    },
    "DependabotProvider": {
        "dependabotId": (SecretStr, ...),
        "dependabotOwner": (str, ...),
        "dependabotRepo": (str, ...),
        "dependabotToken": (SecretStr, ...),
    },
    "JiraProvider": {
        "jiraApiToken": (SecretStr, ...),
        "jiraUrl": (str, ...),
        "jirUserName": (str, ...),
    },
    "OktaProvider": {
        "oktaApiToken": (SecretStr, ...),
        "oktaClientId": (str, ...),
        "oktaUrl": (str, ...),
    },
    "QualysProvider": {
        "qualysURL": (str, ...),
        "qualysUserName": (str, ...),
        "qualysPassword": (SecretStr, ...),
    },
    "SnowProvider": {
        "snowPassword": (SecretStr, ...),
        "snowUserName": (str, ...),
        "snowUrl": (str, ...),
    },
    "SonarProvider": {
        "sonarToken": (SecretStr, ...),
    },
    "TenableProvider": {
        # FIXME - [sic] in mistake below, key is lowercase
        "tenableAccesskey": (SecretStr, ...),
        "tenableSecretkey": (SecretStr, ...),
        "tenableUrl": (str, "https://sc.tenable.online"),
    },
    "WizProvider": {
        "wizAccessToken": (SecretStr, ...),
        "wizAuthUrl": (str, "https://auth.wiz.io/oauth/token"),
        "wizExcludes": (str, ""),
        "wizReportAge": (int, 15),
    },
}

# the above dict is itemized, and the key for each dict is assigned
# a new class with the sub-dict as kwargs to the Provider class
# the tuple of each sub-dict key defines the type and the default
# if ... is supplied, there is no default and it is required
for provider_name, fields in providers.items():
    # Add or override fields in the provider's dictionary
    updated_fields = {}
    for field_name, (field_type, default_value) in fields.items():
        # Use the field_type and default_value from the tuple
        if default_value is ...:  # Checking if the field is required
            updated_fields[field_name] = (field_type, ...)
        else:
            updated_fields[field_name] = (field_type, default_value)

    # Add the 'provider' field with its type and value
    provider_key = provider_name.split("Provider")[0].lower()
    updated_fields["provider"] = (str, provider_key)

    # Create the model with the updated fields
    globals()[provider_name] = create_model(provider_name, **updated_fields, __base__=Provider)


class Providers(BaseModel):
    pass


# generate a hidden dict of classes for all classes currently defined
_all_classes = {name: obj for name, obj in getmembers(currentframe().f_globals) if isclass(obj)}
# iterate over the provider keys, and add an Optional dynamically created provider class
for provider in providers.keys():
    if provider in _all_classes:
        Providers.__annotations__[provider.split("Provider")[0].lower()] = Optional[_all_classes[provider]]
# now any provider class is a parameter to Providers, so
# providers = Providers(wiz=WizProvider(...), ad=AdProvider(...))
# providers.wiz.wizAccessToken will access the access token in the providers class


class AppConfig(BaseModel):
    """The AppConfig object will be used to generate the config for platform interaction"""

    auth: RegScaleAuth
    config: Optional[dict] = None  # TODO - Spec this as a BaseModel too
    providers: Optional[Providers] = None  # TODO - spec providers and implement
    # with the providers we can access values like AppConfig.providers.wiz.wizAccessToken

    @property
    def token(self):
        return self.auth.token

    @classmethod
    def populate(cls):
        """Class method to populate the AppConfig class"""
        # TODO implement method for retrieving config from platform
        return cls()
