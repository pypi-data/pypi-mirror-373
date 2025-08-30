"""
Module to handle API calls to Microsoft Defender for Cloud
"""

from json import JSONDecodeError
from logging import getLogger
from typing import Any, Literal, Optional

from requests import Response

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import error_and_exit
from .defender_constants import APP_JSON

logger = getLogger("regscale")


class DefenderApi:
    """
    Class to handle API calls to Microsoft Defender 365 or Microsoft Defender for Cloud

    :param Literal["cloud", "365"] system: Which system to make API calls to, either cloud or 365
    """

    def __init__(self, system: Literal["cloud", "365"]):
        self.api: Api = Api()
        self.config: dict = self.api.config
        self.system: Literal["cloud", "365"] = system
        self.headers: dict = self.set_headers()
        self.decode_error: str = "JSON Decode error"
        self.skip_token_key: str = "$skipToken"

    def set_headers(self) -> dict:
        """
        Function to set the headers for the API calls
        """
        token = self.check_token()
        return {"Content-Type": APP_JSON, "Authorization": token}

    def get_token(self) -> str:
        """
        Function to get a token from Microsoft Azure and saves it to init.yaml

        :return: JWT from Azure
        :rtype: str
        """
        # set the url and body for request
        if self.system == "365":
            url = f'https://login.windows.net/{self.config["azure365TenantId"]}/oauth2/token'
            client_id = self.config["azure365ClientId"]
            client_secret = self.config["azure365Secret"]
            resource = "https://api.securitycenter.windows.com"
            key = "azure365AccessToken"
        elif self.system == "cloud":
            url = f'https://login.microsoftonline.com/{self.config["azureCloudTenantId"]}/oauth2/token'
            client_id = self.config["azureCloudClientId"]
            client_secret = self.config["azureCloudSecret"]
            resource = "https://management.azure.com"
            key = "azureCloudAccessToken"
        data = {
            "resource": resource,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }
        # get the data
        response = self.api.post(
            url=url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )
        try:
            return self._parse_and_save_token(response, key)
        except KeyError as ex:
            # notify user we weren't able to get a token and exit
            error_and_exit(f"Didn't receive token from Azure.\n{ex}\n{response.text}")
        except JSONDecodeError as ex:
            # notify user we weren't able to get a token and exit
            error_and_exit(f"Unable to authenticate with Azure.\n{ex}\n{response.text}")

    def check_token(self, url: Optional[str] = None) -> str:
        """
        Function to check if current Azure token from init.yaml is valid, if not replace it

        :param str url: The URL to use for authentication, defaults to None
        :return: returns JWT for Microsoft 365 Defender or Microsoft Defender for Cloud depending on system provided
        :rtype: str
        """
        # set up variables for the provided system
        if self.system == "cloud":
            key = "azureCloudAccessToken"
        elif self.system.lower() == "365":
            key = "azure365AccessToken"
        else:
            error_and_exit(
                f"{self.system.title()} is not supported, only Microsoft 365 Defender and Microsoft Defender for Cloud."
            )
        current_token = self.config[key]
        # check the token if it isn't blank
        if current_token and url:
            # set the headers
            header = {"Content-Type": APP_JSON, "Authorization": current_token}
            # test current token by getting recommendations
            token_pass = self.api.get(url=url, headers=header)
            # check the status code
            if getattr(token_pass, "status_code", 0) == 200:
                # token still valid, return it
                token = self.config[key]
                logger.info(
                    "Current token for %s is still valid and will be used for future requests.",
                    self.system.title(),
                )
            elif getattr(token_pass, "status_code", 0) == 403:
                # token doesn't have permissions, notify user and exit
                error_and_exit(
                    "Incorrect permissions set for application. Cannot retrieve recommendations.\n"
                    + f"{token_pass.status_code}: {token_pass.reason}\n{token_pass.text}"
                )
            else:
                # token is no longer valid, get a new one
                token = self.get_token()
        # token is empty, get a new token
        else:
            token = self.get_token()
        return token

    def _parse_and_save_token(self, response: Response, key: str) -> str:
        """
        Function to parse the token from the response and save it to init.yaml

        :param Response response: Response from API call
        :param str key: Key to use for init.yaml token update
        :return: JWT from Azure for the provided system
        :rtype: str
        """
        # try to read the response and parse the token
        res = response.json()
        token = res["access_token"]

        # add the token to init.yaml
        self.config[key] = f"Bearer {token}"

        # write the changes back to file
        self.api.app.save_config(self.api.config)  # type: ignore

        # notify the user we were successful
        logger.info(
            f"Azure {self.system.title()} Login Successful! Init.yaml file was updated with the new access token."
        )
        # return the token string
        return self.config[key]

    def execute_resource_graph_query(
        self, query: str = None, skip_token: Optional[str] = None, record_count: int = 0
    ) -> list[dict]:
        """
        Function to fetch Microsoft Defender resources from Azure

        :param str query: Query to use for the API call
        :param Optional[str] skip_token: Token to skip results, used during pagination, defaults to None
        :param int record_count: Number of records fetched, defaults to 0, used for logging during pagination
        :return: list of Microsoft Defender resources
        :rtype: list[dict]
        """
        url = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2024-04-01"
        if query:
            payload: dict[str, Any] = {"query": query}
        else:
            payload: dict[str, Any] = {
                "query": query,
                "subscriptions": [self.config["azureCloudSubscriptionId"]],
            }
        if skip_token:
            payload["options"] = {self.skip_token_key: skip_token}
            logger.info("Retrieving more Microsoft Defender resources from Azure...")
        else:
            logger.info("Retrieving Microsoft Defender resources from Azure...")
        response = self.api.post(url=url, headers=self.headers, json=payload)
        if response.status_code != 200:
            error_and_exit(
                f"Received unexpected response from Microsoft Defender.\n{response.status_code}:{response.reason}"
                + f"\n{response.text}",
            )
        try:
            response_data = response.json()
            total_records = response_data.get("totalRecords", 0)
            count = response_data.get("count", len(response_data.get("data", [])))
            logger.info(f"Received {count + record_count}/{total_records} items from Microsoft Defender.")
            # try to get the values from the api response
            defender_data = response_data["data"]
        except JSONDecodeError:
            # notify user if there was a json decode error from API response and exit
            error_and_exit(self.decode_error)
        except KeyError:
            # notify user there was no data from API response and exit
            error_and_exit(
                f"Received unexpected response from Microsoft Defender.\n{response.status_code}: {response.reason}\n"
                + f"{response.text}"
            )
        # check if pagination is required to fetch all data from Microsoft Defender
        skip_token = response_data.get(self.skip_token_key)
        if response.status_code == 200 and skip_token:
            # get the rest of the data
            defender_data.extend(
                self.execute_resource_graph_query(query=query, skip_token=skip_token, record_count=count + record_count)
            )
        # return the defender recommendations
        return defender_data

    def get_items_from_azure(self, url: str) -> list:
        """
        Function to get data from Microsoft Defender returns the data as a list while handling pagination

        :param str url: URL to use for the API call
        :return: list of recommendations
        :rtype: list
        """
        # get the data via api call
        response = self.api.get(url=url, headers=self.headers)
        if response.status_code != 200:
            error_and_exit(
                f"Received unexpected response from Microsoft Defender.\n{response.status_code}:{response.reason}"
                + f"\n{response.text}",
            )
        # try to read the response
        try:
            response_data = response.json()
            # try to get the values from the api response
            defender_data = response_data["value"]
        except JSONDecodeError:
            # notify user if there was a json decode error from API response and exit
            error_and_exit(self.decode_error)
        except KeyError:
            # notify user there was no data from API response and exit
            error_and_exit(
                f"Received unexpected response from Microsoft Defender.\n{response.status_code}: {response.text}"
            )
        # check if pagination is required to fetch all data from Microsoft Defender
        if next_link := response_data.get("nextLink"):
            # get the rest of the data
            defender_data.extend(self.get_items_from_azure(url=next_link))
        # return the defender recommendations
        return defender_data

    def fetch_queries_from_azure(self) -> list[dict]:
        """
        Function to fetch queries from Microsoft Defender for Cloud
        """
        url = (
            f"https://management.azure.com/subscriptions/{self.config['azureCloudSubscriptionId']}/"
            "providers/Microsoft.ResourceGraph/queries?api-version=2024-04-01"
        )
        logger.info("Fetching saved queries from Azure Resource Graph...")
        response = self.api.get(url=url, headers=self.headers)
        logger.debug(f"Azure API response status: {response.status_code}")
        if response.raise_for_status():
            error_and_exit(
                f"Received unexpected response from Microsoft Defender.\n{response.status_code}:{response.reason}"
                + f"\n{response.text}",
            )
        logger.debug("Parsing Azure API response...")
        cloud_queries = response.json().get("value", [])
        logger.info(f"Found {len(cloud_queries)} saved queries in Azure Resource Graph.")
        return cloud_queries

    def fetch_and_run_query(self, query: dict) -> list[dict]:
        """
        Function to fetch and run a query from Microsoft Defender for Cloud

        :param dict query: Query to run in Azure Resource Graph
        :return: Results from the query
        :rtype: list[dict]
        """
        url = (
            f"https://management.azure.com/subscriptions/{query['subscriptionId']}/resourceGroups/"
            f"{query['resourceGroup']}/providers/Microsoft.ResourceGraph/queries/{query['name']}"
            "?api-version=2024-04-01"
        )
        response = self.api.get(url=url, headers=self.headers)
        if response.raise_for_status():
            error_and_exit(
                f"Received unexpected response from Microsoft Defender.\n{response.status_code}:{response.reason}"
                + f"\n{response.text}",
            )
        query_string = response.json().get("properties", {}).get("query")
        return self.execute_resource_graph_query(query=query_string)
