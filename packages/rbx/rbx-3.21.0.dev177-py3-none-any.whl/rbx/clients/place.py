import logging
from typing import Dict, Any, Optional

import requests

from requests.auth import AuthBase
from . import Client
from ..exceptions import ClientError, ServerError


logger = logging.getLogger(__name__)


class BearerAuth(AuthBase):
    """Authentication class for Bearer token authorization.

    Adds the Bearer token to the Authorization header of requests.
    """

    def __init__(self, token):
        """Initialize with the token.

        Args:
            token (str): The authentication token
        """
        self.token = token

    def __call__(self, r):
        """Add Authorization header to the request.

        Args:
            r (Request): The request object

        Returns:
            Request: The modified request with Authorization header
        """
        if self.token:
            r.headers["Authorization"] = "Bearer " + self.token
        return r


class PlaceExchangeClient(Client):
    """Client for Place Exchange Creative API.

    Handles authentication and API communication with Place Exchange.
    This client only handles the HTTP requests and authentication,
    not the formatting of data or interpretation of responses.

    API documentation: https://api.placeexchange.com/v3/orgs/{id}/ads
    """

    ENDPOINT = "https://api.placeexchange.com/"
    AUTH_PATH = "v3/token"
    DEFAULT_TIMEOUT = 30
    TOKEN = "access_token"
    MAX_PAGE_SIZE = 4000

    def __init__(self, org_id: str):
        """Initialize the Place Exchange client with authentication credentials.

        Args:
            org_id: Organization ID for Place Exchange API
        """
        super().__init__()
        self.org_id = org_id

    @property
    def auth(self):
        """Get the authentication object for requests.

        Returns:
            BearerAuth: Authentication object with the token
        """
        return BearerAuth(self.token)

    @property
    def is_authenticated(self):
        """Check if the client is authenticated."""
        return self.token is not None

    def refresh_access_token(self):
        """Refresh the access token.

        Place Exchange doesn't support refresh tokens, so we just get a new token.
        """
        self.logout()
        self.login(self.credentials["username"], self.credentials["password"])

    def get_creative(self, creative_id: str):
        """Get a creative by name.

        Args:
            creative_id: The name of the ad to get

        Returns:
            The raw API response data

        Raises:
            ServerError: On server-side errors or invalid responses
            ClientError: On client-side errors
        """
        path = f"v3/orgs/{self.org_id}/ads/{creative_id}"

        try:
            return self.request(
                method="get",
                path=path,
            )
        except ClientError as e:
            if e.status_code == 404:
                return None
            raise

    def submit_creative(self, payload: Dict[str, Any]):
        """Create a new creative.

        Args:
            payload: The creative data to submit

        Returns:
            The raw API response data

        Raises:
            ServerError: On server-side errors or invalid responses
            ClientError: On client-side errors
        """
        path = f"v3/orgs/{self.org_id}/ads"
        headers = {"Content-Type": "application/json"}

        return self.request(
            method="post",
            path=path,
            headers=headers,
            data=payload,
        )

    def update_creative(self, creative_id: str, payload: Dict[str, Any]):
        """Update an existing creative.

        Args:
            creative_id: The name of the creative to update
            payload: The creative data to update

        Returns:
            The raw API response data

        Raises:
            ServerError: On server-side errors or invalid responses
            ClientError: On client-side errors
        """
        path = f"v3/orgs/{self.org_id}/ads/{creative_id}"
        headers = {"Content-Type": "application/json"}

        return self.request(
            method="patch",
            path=path,
            headers=headers,
            data=payload,
        )

    def get_creative_adapprovals(self, creative_id: str):
        """Get approval information for a creative from individual publishers.

        Calls the adapprovals endpoint to retrieve approval status for a creative
        from each publisher. The response contains a list of objects, one per publisher,
        with information about the approval status.

        Args:
            creative_id: The ID of the creative to get approvals for

        Returns:
            The raw API response data containing a list of approval objects.
            Each object contains:
            - owned_by: A string containing the publisher's ID
            - audit: An object with status, feedback, and lastmod fields
              - status: Integer representing approval status (1-5, 500+ for Exchange-specific)
                1 - Pending Audit
                2 - Pre-Approved
                3 - Approved
                4 - Denied
                5 - Changed
              - feedback: Array of strings with explanations for rejection or changes
              - lastmod: Date/time of last modification in ISO 8601 format

        Raises:
            ServerError: On server-side errors or invalid responses
            ClientError: On client-side errors
        """
        path = f"v3/orgs/{self.org_id}/ads/{creative_id}/adapprovals"
        params = {"page": self.MAX_PAGE_SIZE}

        return self.request(
            method="get",
            path=path,
            params=params,
        )

    def get_publishers(self):
        """Get publishers data from Place Exchange sellers.json file.

        Fetches the sellers.json file from Place Exchange website and returns
        the raw JSON response.

        Returns:
            Dict containing the raw JSON response from the sellers.json endpoint

        Raises:
            ServerError: On server-side errors or invalid responses
            ClientError: On client-side errors
        """

        url = "https://www.placeexchange.com/sellers.json"
        headers = {
            # Pretend to be a modern browser to avoid bot/WAF blocks
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
        }

        try:
            response = requests.get(url, timeout=self.DEFAULT_TIMEOUT, headers=headers)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses

            return response.json()

        except requests.HTTPError as e:
            logger.error(f"HTTP error fetching publishers from {url}: {str(e)}")
            raise ServerError(
                message=f"Failed to fetch publishers: {response.text if response is not None else str(e)}",
                url=url,
            )
        except requests.RequestException as e:
            logger.error(f"Error fetching publishers from {url}: {str(e)}")
            raise ServerError(message=f"Failed to fetch publishers: {str(e)}", url=url)
        except ValueError as e:
            logger.error(f"Error parsing JSON from {url}: {str(e)}")
            raise ServerError(
                message=f"Failed to parse publishers data: {str(e)}", url=url
            )

    def get_creatives(
        self,
        lastmod: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ):
        """Get a collection of all ads/creatives for the organization.

        Args:
            lastmod: Date/time filter in ISO format (YYYY-MM-DDTHH:MM:SSZ)
            page: Page number to retrieve
            page_size: Number of entities per page (max 4000)

        Returns:
            API response data with timestamp, count, and ads array

        Raises:
            ServerError: On server-side errors or invalid responses
            ClientError: On client-side errors
        """
        path = f"v3/orgs/{self.org_id}/ads"
        params = {}

        if lastmod is not None:
            params["lastmod"] = lastmod
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size

        return self.request(
            method="get",
            path=path,
            params=params if params else None,
        )
