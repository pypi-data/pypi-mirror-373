from copy import copy
from functools import partial
import json
import logging
from urllib.parse import urljoin

import requests
from requests.auth import AuthBase
from requests.exceptions import ConnectionError, Timeout

from ..exceptions import (
    ClientError,
    Forbidden,
    RequestTimeout,
    ServerError,
    TooManyRequests,
    Unauthorized,
)
from ..utils import Singleton

logger = logging.getLogger(__name__)


class HttpAuth(AuthBase):
    """Attaches HTTP AUTH-TOKEN Authentication to the given Request object."""

    def __init__(self, token, key="X-AUTH-TOKEN"):
        self.key = key
        self.token = token

    def __call__(self, r):
        r.headers[self.key] = self.token
        return r

    def __eq__(self, other):
        return all(
            [
                other.key == self.key,
                other.token == self.token,
            ]
        )


class Client(metaclass=Singleton):
    """Base Client offering basic functionality, such as logging in, auto-login on expiry, and
    common error handling.

    The Client is a JSON client, meaning it is to be used with an API that supports JSON format
    in its requests and responses.

    This class must be extended, do not use it directly.
    """

    AUTH_PATH = "auth/login"
    DEFAULT_TIMEOUT = 30
    ENDPOINT = "/"
    TOKEN = "token"

    def __init__(self):
        self.credentials = None
        self.token = None

    @property
    def auth(self):
        """Authentication method.

        Returns None by default, meaning no authentication.
        One can include Digest Authentication using the HttpAuth object, e.g.:

        >>> return HttpAuth(self.token, key='X-AUTH')

        """
        return None

    @property
    def is_authenticated(self):
        return self.token is not None

    def get_message(self, response):
        """Extract the message from the requests response object."""
        return self.get_response(response).get("message")

    def get_response(self, response):
        """Extract the response payload from the requests response object."""
        return response.json()

    def login(self, username, password):
        """Authenticate and set the access token on success."""
        response = self._request(
            "post",
            self.AUTH_PATH,
            data={
                "username": username,
                "password": password,
            },
        )

        self.credentials = {
            "username": username,
            "password": password,
        }
        self.token = response.get(self.TOKEN)
        logger.debug(f"Logged in <Token: {self.token}>")

    def logout(self):
        self.token = None
        if hasattr(self, "csrftoken"):
            self.csrftoken = None

    def refresh_access_token(self):
        raise NotImplementedError

    def _post(self, path, **kwargs):
        """Shortcut for _request('post')."""
        return self._request("post", path, **kwargs)

    def _request(
        self,
        method,
        path,
        content_type="application/json",
        data=None,
        endpoint=None,
        headers=None,
        params=None,
        timeout=None,
    ):
        """Wrap the method call in common error handling."""
        endpoint = endpoint if endpoint is not None else self.ENDPOINT
        url = urljoin(endpoint, path)

        # Default requests parameter (except login).
        args = {"timeout": self.DEFAULT_TIMEOUT if timeout is None else timeout}
        if self.auth:
            args["auth"] = self.auth

        # CSRF Cookies hack required by some vendors (i.e.: Broadsign).
        if hasattr(self, "csrftoken") and self.csrftoken and method in ("post", "put"):
            args.update(
                {
                    "headers": {"X-CSRFToken": self.csrftoken},
                    "cookies": {"csrftoken": self.csrftoken},
                }
            )

        # Add custom headers.
        if headers:
            if "headers" in args:
                args["headers"].update(headers)
            else:
                args["headers"] = headers
        # Add params
        if params is not None:
            args["params"] = params

        # Use the right requests parameter according to the method and data type.
        if data is not None:
            if method == "get":
                args["params"] = args.get("params", {}) | data
            elif type(data) is str:
                args["data"] = data
            else:
                # If the data payload can't be serialized into JSON, then pass it as provided.
                # Otherwise, pass is a as JSON value.
                try:
                    json.dumps(data)
                    args["json"] = data
                except TypeError:
                    args["data"] = data

        try:
            if path == self.AUTH_PATH:
                # Don't use authentication for the token endpoint.
                response = requests.post(url, json=data, timeout=self.DEFAULT_TIMEOUT)
            else:
                response = getattr(requests, method)(url, **args)
        except (ConnectionError, Timeout) as e:
            raise RequestTimeout(message=str(e), url=url)

        # Never include the password field in the log on failure
        payload = copy(data)
        if payload and type(payload) is dict:
            payload.pop("password", None)

        if response.status_code == 500:
            raise ServerError(response.text, details=payload, url=url)

        if response.status_code == 401:
            raise Unauthorized(self.get_message(response), details=payload, url=url)

        if response.status_code == 403:
            raise Forbidden(self.get_message(response), details=payload, url=url)

        if response.status_code == 408:
            raise RequestTimeout(self.get_message(response), details=payload, url=url)

        if response.status_code == 429:
            raise TooManyRequests(self.get_message(response), details=payload, url=url)

        if response.status_code >= 400:
            raise ClientError(
                response.text,
                details=payload,
                status_code=response.status_code,
                url=url,
            )

        # CSRF Cookies hack, continued. Store the first 'csrftoken' value found from the response
        # cookies. The Set-Cookie won't be sent on login, so we have to extract it from the first
        # GET request.
        if (
            hasattr(self, "csrftoken")
            and "csrftoken" in response.cookies
            and method == "get"
        ):
            self.csrftoken = response.cookies["csrftoken"]

        # 204 "No Content" responses return nothing
        if response.status_code == 204:
            return

        if content_type == "text/plain":
            return response.text
        else:
            try:
                return self.get_response(response)
            except ValueError:
                extra = {
                    "request": payload,
                    "response": response.text,
                }
                raise ServerError(
                    "Invalid JSON response", details=extra, status_code=500, url=url
                )

    def request(
        self,
        method,
        path,
        content_type="application/json",
        data=None,
        endpoint=None,
        headers=None,
        params=None,
        timeout=None,
    ):
        """Attempt to re-authenticate when the token has expired.

        Note that the Client must be logged in first for this to work.
        """
        if not self.is_authenticated:
            raise Unauthorized

        api_call = partial(
            self._request,
            method=method,
            path=path,
            content_type=content_type,
            data=data,
            endpoint=endpoint,
            headers=headers,
            params=params,
            timeout=timeout,
        )

        try:
            return api_call()

        except Unauthorized as e:
            # The token has expired. If the client implements the `refresh_access_token` method,
            # then attempt to get a fresh token that way.
            # Otherwise, start fresh.
            logger.debug(f'Access denied: "{e.status_code} - {e.message}"')
            try:
                self.refresh_access_token()
            except (Forbidden, Unauthorized, NotImplementedError):
                self.logout()
                self.login(**self.credentials)

            return api_call()
