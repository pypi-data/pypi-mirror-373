"""Module with session for authenticated requests to server."""
import os
import posixpath
import warnings
from contextlib import contextmanager
from http import HTTPStatus
from typing import Generator

import httpx
from httpx import Response
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation
from websocket import WebSocket, create_connection

import ML_management
from ML_management.base_exceptions import MLMClientError
from ML_management.singleton_pattern import Singleton
from ML_management.variables import SERVER_META, get_mlm_credentials, get_server_url


class InvalidCredentialsError(MLMClientError):
    """Exception for invalid login-password pair."""

    pass


class AuthSession(metaclass=Singleton):
    """Extend the standard session functionality with authentication functionality."""

    def __init__(self) -> None:
        self.cookies = {}
        if self._try_set_cookies() or self._try_authenticate_by_credentials():
            self.check_version()

    def check_version(self):
        client_version = ML_management.__version__
        response = httpx.get(posixpath.join(get_server_url(), SERVER_META), cookies=self.cookies)
        try:
            response.raise_for_status()
        except Exception:
            warnings.warn(
                "Can't get ml-management version of the server. "
                f"Server status {response.status_code} with content {response.text}."
            )
            return
        server_version = response.json().get("PLATFORM_VERSION", "unknown")
        if client_version != server_version:
            warnings.warn(
                f"Your ml-management version ({client_version}) does not match the "
                f"version on the server ({server_version})."
            )

    @contextmanager
    def get(self, url: str, stream: bool = False, **kwargs) -> Generator[httpx.Response, None, None]:
        """Proxy get request."""
        with httpx.Client(timeout=None) as client:
            request = client.build_request("GET", url, cookies=self.cookies, **kwargs)
            response = client.send(request=request, stream=stream)
            yield response

        # if token was updated, update our cookie
        self._update_cookies(response, ["kc-access"])

    @contextmanager
    def post(self, url: str, stream: bool = False, **kwargs) -> Generator[httpx.Response, None, None]:
        """Proxy post request."""
        with httpx.Client(timeout=None) as client:
            request = client.build_request("POST", url, cookies=self.cookies, **kwargs)

            # httpx insert content-length even if transfer-encoding was set to 'chunked'
            # so delete content-length header if header transfer-encoding was set
            transfer_encoding_header = request.headers.get("transfer-encoding")
            if transfer_encoding_header == "chunked":
                request.headers.pop("content-length", "")

            response = client.send(request=request, stream=stream)

            yield response

        # if token was updated, update our cookie
        self._update_cookies(response, ["kc-access"])

    # For sdk auth purposes
    def sgqlc_request(self, operation: Operation, timeout=None) -> dict:
        """Make request to /graphql for operation."""
        cookie_header = self._get_cookie_header()
        return HTTPEndpoint(
            posixpath.join(get_server_url(), "graphql"), base_headers={"Cookie": cookie_header}, timeout=timeout
        )(operation)

    def instantiate_websocket_connection(self, url: str) -> WebSocket:
        """Create websocket connection."""
        ws = create_connection(url, cookie=self._get_cookie_header())
        return ws

    def _update_cookies(self, response: Response, cookie_names: list) -> None:
        """Update cookies from cookie_names list."""
        for cookie_name in cookie_names:
            if cookie := response.cookies.get(cookie_name):
                self.cookies[cookie_name] = cookie

    def _get_cookie_header(self) -> str:
        return "; ".join(f"{cookie_name}={cookie_value}" for cookie_name, cookie_value in self.cookies.items())

    def _try_set_cookies(self) -> bool:
        kc_access, kc_state = os.getenv("kc_access"), os.getenv("kc_state")
        if kc_access is not None and kc_state is not None:
            for name, value in zip(["kc-access", "kc-state"], [kc_access, kc_state]):
                self.cookies[name] = value
            return True
        return False

    def _try_authenticate_by_credentials(self) -> bool:
        login, password = get_mlm_credentials()

        try:
            response = httpx.post(
                posixpath.join(get_server_url(), "oauth", "login"), data={"username": login, "password": password}
            )
        except httpx.ConnectError:
            raise RuntimeError("Server is unavailable or server url is incorrect.") from None

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise InvalidCredentialsError(f"User with login {login} and password {password} does not exist.")
        if response.status_code != HTTPStatus.OK:
            if not login or not password:
                raise InvalidCredentialsError("You must provide both login and password credentials.")
            response.raise_for_status()
        self.cookies = {
            "kc-state": response.cookies.get("kc-state"),
            "kc-access": response.cookies.get("kc-access"),
        }
        return True
