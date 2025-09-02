from __future__ import annotations

import asyncio
import json
import os
import ssl
import warnings
from abc import ABC, abstractmethod
from functools import wraps
from http import HTTPStatus
from typing import Optional, Union
from urllib.parse import urlparse

import aiohttp
import nest_asyncio
import requests
from pydantic import BaseModel
from websockets import InvalidStatus
from websockets.sync.client import connect

from bigdata_client.clerk.constants import ClerkInstanceType
from bigdata_client.clerk.exceptions import (
    ClerkAuthError,
    ClerkAuthUnsupportedError,
    ClerkInvalidCredentialsError,
    ClerkTooManySignInAttemptsError,
    ClerkUnexpectedSignInParametersError,
)
from bigdata_client.clerk.models import SignInStrategyType
from bigdata_client.clerk.token_manager import (
    ClerkTokenManager,
    TokenManagerWithConcurrency,
)
from bigdata_client.clerk.token_manager_factory import token_manager_factory
from bigdata_client.constants import DEPRECATED_WARNING_AUTOSUGGEST, THREAD_WAIT_TIMEOUT
from bigdata_client.exceptions import (
    BigdataClientAuthFlowError,
    BigdataClientError,
    BigdataClientTooManySignInAttemptsError,
)
from bigdata_client.settings import settings
from bigdata_client.user_agent import get_user_agent

ALL_PROTOCOLS = ("http", "https", "wss")
ALL_PROTOCOLS_KEYWORD = "all"
MAX_RETRIES = 3
TIMEOUT_SECONDS = 5


class AsyncRequestContext(BaseModel):
    """
    Context used to pass information to auth module for making async requests.
    Async requests are made in parallel, so each request is associated with an id to
    retrieve it from a list of responses.
    """

    id: str
    url: str
    params: dict


class AsyncResponseContext(BaseModel):
    """
    Structure used to return the response of an async request.
    Async requests are made in parallel, so each response is associated with the id it was
    used to make the request.
    """

    id: str
    response: dict


class Proxy(BaseModel):
    protocol: str = "https"
    url: str


def handle_clerk_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClerkAuthUnsupportedError as e:
            raise BigdataClientAuthFlowError(e)
        except ClerkUnexpectedSignInParametersError as e:
            raise BigdataClientAuthFlowError(e)
        except ClerkInvalidCredentialsError as e:
            raise BigdataClientAuthFlowError(e)
        except ClerkTooManySignInAttemptsError as e:
            raise BigdataClientTooManySignInAttemptsError(e)
        except ClerkAuthError as e:
            raise BigdataClientError(e)

    return wrapper


def retry_websocket_connection(max_retries: int = MAX_RETRIES):
    """
    Decorator to handle retry logic for WebSocket connections.

    Args:
        max_retries: Maximum number of retry attempts
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except TimeoutError as e:
                    if attempt == max_retries - 1:
                        # Last attempt failed, re-raise the exception
                        raise TimeoutError(
                            f"Failed to establish WebSocket connection after {max_retries} attempts. Error: {e}"
                        )
                    continue

        return wrapper

    return decorator


class BaseAuth(ABC):
    """
    Base class that performs the authentication logic. It wraps all the http calls
    so that it can handle the token autorefresh when needed.
    """

    def __init__(
        self,
        pool_maxsize: int,
        verify: Union[bool, str],
        proxies: Optional[dict],
    ):
        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize)  # type: ignore
        self._session.mount("https://", adapter)
        if proxies:
            self._session.proxies.update(proxies)
        self.verify = verify
        self.proxies = proxies
        self._session.verify = verify

    @staticmethod
    def get_common_headers_jwt_and_api_key(url: str) -> dict:
        # 'https://api.bigdata.com/cqs/query-chunks' -> 'https://api.bigdata.com'
        parsed_url = urlparse(url)
        url_no_path = f"{parsed_url.scheme}://{parsed_url.netloc}"

        return {
            "origin": url_no_path,
            "referer": url_no_path,
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": get_user_agent(settings.PACKAGE_NAME),
        }

    @abstractmethod
    def get_headers(self, *args, **kwargs) -> dict:
        """Get headers for the request"""
        pass

    @abstractmethod
    def request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        stream: Optional[bool] = None,
    ):
        """Make an HTTP request"""

    @abstractmethod
    def async_requests(
        self, method: str, request_contexts: list[AsyncRequestContext]
    ) -> list[AsyncResponseContext]:
        """Make async HTTP requests"""

    def get_ws_auth(
        self, ws_url: str, verify: bool, proxy: Optional[Proxy]
    ) -> "WSAuth":
        """Return WSAuth"""


class JWTAuth(BaseAuth):
    def __init__(
        self,
        token_manager: ClerkTokenManager,
        pool_maxsize: int,
        verify: Union[bool, str],
        proxies: Optional[dict] = None,
    ):
        super().__init__(pool_maxsize=pool_maxsize, verify=verify, proxies=proxies)
        self._token_manager = TokenManagerWithConcurrency(token_manager)

    @classmethod
    @handle_clerk_exceptions
    def from_username_and_password(
        cls,
        username: str,
        password: str,
        clerk_frontend_url: str,
        clerk_instance_type: ClerkInstanceType,
        pool_maxsize: int,
        proxy: Optional[Proxy],
        verify: Union[bool, str],
    ) -> "JWTAuth":

        if proxy and proxy.protocol == ALL_PROTOCOLS_KEYWORD:
            proxies = {protocol: proxy.url for protocol in ALL_PROTOCOLS}
        else:
            proxies = {proxy.protocol: proxy.url} if proxy else None
        # A token manager handles the authentication flow and stores a jwt. It contains methods for refreshing it.
        token_manager = token_manager_factory(
            instance_type=clerk_instance_type,
            sign_in_strategy=SignInStrategyType.PASSWORD,
            clerk_frontend_url=clerk_frontend_url,
            email=username,
            password=password,
            pool_maxsize=pool_maxsize,
            proxies=proxies,
            verify=verify,
        )
        token_manager.refresh_session_token()
        return cls(
            token_manager=token_manager,
            pool_maxsize=pool_maxsize,
            proxies=proxies,
            verify=verify,
        )

    @classmethod
    def get_headers(
        cls, url: str, jwt: str, extra_headers: Optional[dict] = None
    ) -> dict:
        common_headers = cls.get_common_headers_jwt_and_api_key(url)

        return {
            **common_headers,
            "Authorization": f"Bearer {jwt}",
            **(extra_headers or {}),
        }

    @handle_clerk_exceptions
    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        json=None,
        stream=None,
    ):
        """Makes an HTTP request, handling the token refresh if needed"""
        # Wait until token is valid - do not make requests if token was marked as invalid/expired.
        self._token_manager.wait(timeout=THREAD_WAIT_TIMEOUT)
        token_used = self._token_manager.get_session_token()

        headers = self.get_headers(url=url, jwt=token_used, extra_headers=headers)

        # The request method has other arguments but we are not using them currently
        response = self._session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            json=json,
            stream=stream,
        )
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            self._token_manager.refresh_jwt(token_used)

            # This headers.copy() is needed for testing. Mock lib does not make a copy, instead it points to
            # the original headers, so asserting that the headers changed fails.
            headers = headers.copy()
            headers["Authorization"] = (
                f"Bearer {self._token_manager.get_session_token()}"
            )

            # Retry the request
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                json=json,
                stream=stream,
            )

        return response

    @handle_clerk_exceptions
    def async_requests(
        self, method: str, request_contexts: list[AsyncRequestContext]
    ) -> list[AsyncResponseContext]:
        """Makes an async HTTP request, handling the token refresh if needed"""
        # 'https://api.bigdata.com/cqs/query-chunks' -> 'https://api.bigdata.com'
        if any(
            request_context.url != request_contexts[0].url
            for request_context in request_contexts
        ):
            raise ValueError(
                "All requests must have the same URL sice with the current logic origin/referer are "
                "shared across all requests."
            )
        parsed_url = urlparse(request_contexts[0].url)
        url_no_path = f"{parsed_url.scheme}://{parsed_url.netloc}"
        token_used = self._token_manager.get_session_token()
        headers = {
            "origin": url_no_path,
            "referer": url_no_path,
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": get_user_agent(settings.PACKAGE_NAME),
            "Authorization": f"Bearer {token_used}",
        }
        nest_asyncio.apply()  # Required for running asyncio in notebooks

        try:
            return asyncio.run(
                self._create_and_resolve_tasks(method, headers, request_contexts)
            )
        # If any request raises HTTPStatus.UNAUTHORIZED refresh the token and use it again for all of the requests
        except aiohttp.client_exceptions.ClientResponseError as err:
            if err.status != HTTPStatus.UNAUTHORIZED:
                raise

            # This headers.copy() is needed for testing. Mock lib does not make a copy, instead it points to
            # the original headers, so asserting that the headers changed fails.
            self._token_manager.refresh_jwt(token_used)
            headers = headers.copy()
            headers["Authorization"] = (
                f"Bearer {self._token_manager.get_session_token()}"
            )

            try:
                return asyncio.run(
                    self._create_and_resolve_tasks(method, headers, request_contexts)
                )
            except aiohttp.client_exceptions.ClientResponseError as err:
                if err.status == HTTPStatus.UNAUTHORIZED:
                    warnings.warn(DEPRECATED_WARNING_AUTOSUGGEST)
                raise

    async def _create_and_resolve_tasks(
        self, method: str, headers: dict, requests_contexts: list[AsyncRequestContext]
    ) -> list[AsyncResponseContext]:
        ssl_verification = self.verify
        if isinstance(self.verify, str):
            ssl_context = ssl.create_default_context()
            ssl_context.load_cert_chain(
                certfile=self.verify, keyfile=None, password=None
            )
            ssl_verification = ssl_context
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.ensure_future(
                    self._make_async_request(
                        method,
                        headers,
                        session,
                        request_context,
                        ssl_verification=ssl_verification,
                    )
                )
                for request_context in requests_contexts
            ]
            return await asyncio.gather(*tasks)

    async def _make_async_request(
        self,
        method: str,
        headers: dict,
        session: aiohttp.ClientSession,
        request_context: AsyncRequestContext,
        ssl_verification: Union[bool, ssl.SSLContext],
    ) -> AsyncResponseContext:

        target_scheme = urlparse(request_context.url).scheme

        proxy = (
            os.environ.get("ALL_PROXY")
            or os.environ.get(f"{target_scheme.upper()}_PROXY")
            or self._session.proxies.get(target_scheme)
        )

        async with session.request(
            method=method,
            headers=headers,
            params=request_context.params,
            url=request_context.url,
            raise_for_status=True,
            proxy=proxy,
            ssl=ssl_verification,
        ) as response:
            response = await response.json()

        return AsyncResponseContext(id=request_context.id, response=response)

    def get_ws_auth(
        self, ws_url: str, verify: bool, proxy: Optional[Proxy]
    ) -> "WSAuth":
        return WSAuth(
            auth_manager=WSContextManagerWithJwt(
                url=ws_url,
                token_manager=self._token_manager,
                verify=verify,
                proxy=proxy,
            )
        )


class ApiKeyAuth(BaseAuth):
    def __init__(
        self,
        api_key: str,
        pool_maxsize: int,
        verify: Union[bool, str],
        proxies: Optional[dict] = None,
    ):
        super().__init__(pool_maxsize, verify, proxies)
        self.api_key = api_key

    @classmethod
    def from_api_key(
        cls,
        api_key: str,
        pool_maxsize: int,
        proxy: Optional[Proxy],
        verify: Union[bool, str],
    ) -> "ApiKeyAuth":
        """Create an API key authentication instance"""
        if proxy and proxy.protocol == ALL_PROTOCOLS_KEYWORD:
            proxies = {protocol: proxy.url for protocol in ALL_PROTOCOLS}
        else:
            proxies = {proxy.protocol: proxy.url} if proxy else None

        return cls(
            api_key=api_key,
            pool_maxsize=pool_maxsize,
            proxies=proxies,
            verify=verify,
        )

    def get_headers(self, url: str, extra_headers: Optional[dict] = None) -> dict:
        common_headers = self.get_common_headers_jwt_and_api_key(url)
        return {**common_headers, "x-api-key": self.api_key, **(extra_headers or {})}

    def request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        stream: Optional[bool] = None,
    ):
        headers = self.get_headers(url=url, extra_headers=headers)
        return self._session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            json=json,
            stream=stream,
        )

    def async_requests(
        self, method: str, request_contexts: list[AsyncRequestContext]
    ) -> list[AsyncResponseContext]:
        """Make async HTTP requests"""
        raise NotImplementedError("Deprecated methods are not supported with API Keys")

    def get_ws_auth(
        self, ws_url: str, verify: bool, proxy: Optional[Proxy]
    ) -> "WSAuth":
        return WSAuth(
            auth_manager=WSContextManagerWithApiKey(
                url=ws_url, api_key=self.api_key, proxy=proxy, verify=verify
            )
        )


class WSContextManagerBase(ABC):
    @abstractmethod
    def send(self, msg: str):
        pass

    @abstractmethod
    def recv(self):
        pass

    @staticmethod
    def _get_ssl_context(verify: bool):
        context = ssl.create_default_context()
        if not verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        return context


class WSContextManagerWithJwt(WSContextManagerBase):
    """Context manager for JWT based authentication"""

    def __init__(
        self,
        url: str,
        token_manager: TokenManagerWithConcurrency,
        proxy: Optional[Proxy],
        verify: bool,
    ):
        super().__init__()
        self.url = url
        self.token_manager = token_manager
        self.proxy = proxy
        self.verify = verify

    def send(self, msg: dict):
        self.ws.send(message=json.dumps(msg))

    def recv(self, timeout: Optional[float] = None) -> dict:
        response = self.ws.recv(timeout=timeout)
        return json.loads(response)

    @retry_websocket_connection(max_retries=MAX_RETRIES)
    def __enter__(self):
        token_used = self.token_manager.get_session_token()
        url_with_jwt = f"{self.url}?jwt_token={token_used}"
        proxy = (
            self.proxy.url if self.proxy else True
        )  # True is the default value to use proxy from env variables

        try:
            self.ws = connect(
                url_with_jwt,
                ssl=self._get_ssl_context(self.verify),
                proxy=proxy,
                open_timeout=TIMEOUT_SECONDS,
            ).__enter__()
        except InvalidStatus as e:
            if e.response.status_code == HTTPStatus.UNAUTHORIZED:
                self.token_manager.refresh_jwt(token_used)
                url_with_jwt = (
                    f"{self.url}?jwt_token={self.token_manager.get_session_token()}"
                )
                self.ws = connect(
                    url_with_jwt,
                    ssl=self._get_ssl_context(self.verify),
                    proxy=proxy,
                ).__enter__()
            else:
                raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ws.__exit__(exc_type, exc_val, exc_tb)


class WSContextManagerWithApiKey(WSContextManagerBase):
    """Context manager for Api Key based authentication"""

    def __init__(self, url: str, api_key: str, proxy: Optional[Proxy], verify: bool):
        super().__init__()
        self.url = url
        self.api_key = api_key
        self.proxy = proxy
        self.verify = verify

    def send(self, msg: dict):
        self.ws.send(message=json.dumps(msg))

    def recv(self, timeout: Optional[float] = None) -> dict:
        response = self.ws.recv(timeout=timeout)
        return json.loads(response)

    @retry_websocket_connection(max_retries=MAX_RETRIES)
    def __enter__(self):
        url_with_jwt = f"{self.url}"
        proxy = (
            self.proxy.url if self.proxy else True
        )  # True is the default value to use proxy from env variables

        self.ws = connect(
            url_with_jwt,
            additional_headers={"x-api-key": self.api_key},
            ssl=self._get_ssl_context(self.verify),
            proxy=proxy,
            open_timeout=TIMEOUT_SECONDS,
        ).__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ws.__exit__(exc_type, exc_val, exc_tb)


class WSAuth:
    """Use as a context manager"""

    def __init__(
        self, auth_manager: Union[WSContextManagerWithJwt, WSContextManagerWithApiKey]
    ):
        self.auth_manager = auth_manager

    def __enter__(self):
        """
        JWT or Api Key based authentication have different ways of handling connection
        """
        return self.auth_manager.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.auth_manager.__exit__(exc_type, exc_val, exc_tb)
