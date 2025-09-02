import threading
from http import HTTPStatus
from typing import Optional

import requests.exceptions

from bigdata_client.clerk.authenticators.base_instance import ClerkInstanceBase
from bigdata_client.clerk.exceptions import ClerkAuthError, raise_errors_as_clerk_errors
from bigdata_client.constants import THREAD_WAIT_TIMEOUT
from bigdata_client.exceptions import BigdataClientAuthFlowError


class ClerkTokenManager:
    def __init__(
        self,
        clerk_authenticator_instance: ClerkInstanceBase,
        clerk_jwt_template_name: Optional[str] = None,
    ):
        """
        Class responsible from getting a JWT and refreshing it from Clerk.
        When the session expires it refreshes it to get a new JWT.

        Args:
            clerk_authenticator_instance: Contains the authorized session with Clerk.
            clerk_jwt_template_name:
        """
        self._clerk_jwt_template_name = clerk_jwt_template_name
        self._clerk_frontend_api_url = (
            clerk_authenticator_instance.clerk_frontend_api_url
        )
        self._session = clerk_authenticator_instance.session
        self._clerk_session = clerk_authenticator_instance.clerk_session
        self._clerk_authenticator_instance = clerk_authenticator_instance
        self._login_strategy = clerk_authenticator_instance.login_strategy
        self._jwt: str = ""

    @raise_errors_as_clerk_errors
    def refresh_session_token(self) -> str:
        """
        To be called when the token is invalid. It refreshes
        the clerk session if it expired.
        Returns:
            jwt
        """
        try:
            self._jwt = self._get_new_session_token()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == HTTPStatus.UNAUTHORIZED:
                # Refresh clerk session if it expired
                self._refresh_token_manager()
                self._jwt = self._get_new_session_token()
            else:
                raise ClerkAuthError(str(e)) from e

        return self._jwt

    def refresh_session_token_with_backoff(self) -> str:
        backoff_count = 3
        for n in range(backoff_count):
            try:
                return self.refresh_session_token()
            except ClerkAuthError:
                self._refresh_token_manager()

        raise ClerkAuthError("Refreshing the token failed. Please try again later.")

    def get_session_token(self) -> str:
        """Returns the last generated JWT"""
        return self._jwt

    def _get_new_session_token(self) -> str:
        url = f"{self._clerk_frontend_api_url}client/sessions/{self._clerk_session}/tokens"
        if self._clerk_jwt_template_name:
            url = f"{url}/{self._clerk_jwt_template_name}"
        response = self._session.post(url=url)
        response.raise_for_status()
        return response.json()["jwt"]

    def _refresh_token_manager(self) -> None:
        params = self._clerk_authenticator_instance.get_new_token_manager_params(
            self._clerk_frontend_api_url,
            self._login_strategy,
            pool_maxsize=self._session.adapters["https://"]._pool_maxsize,
            proxies=self._session.proxies,
            verify=self._session.verify,
        )
        self._session = params.session
        self._clerk_session = params.clerk_session


class TokenManagerWithConcurrency:
    """
    It checks if the token used must be refreshed by the thread and refreshes it if needed.
    """

    def __init__(self, token_manager: ClerkTokenManager):
        self.token_manager = token_manager
        self.lock = threading.Lock()
        self.event = threading.Event()
        self.event.set()  # So it starts unblocked

    def refresh_jwt(self, token_used: str):
        """
        Only one thread can refresh the token:
            - that is the thread that enters the block while event.is_set()
            - and the used token is the same as the current token
        """
        with self.lock:
            refresh_jwt = (
                self.event.is_set()
                and token_used == self.token_manager.get_session_token()
            )
            if refresh_jwt:
                self.event.clear()

        if refresh_jwt:
            self.token_manager.refresh_session_token_with_backoff()
            self.event.set()
        else:
            # This method returns the internal flag on exit, so it will always return True
            # except if a timeout is given and the operation times out.
            exit_flag = self.event.wait(timeout=THREAD_WAIT_TIMEOUT)
            # throw an error in case not able to sign in during timeout
            if not exit_flag:
                raise BigdataClientAuthFlowError(
                    "Refreshing the token failed. Please try again later."
                )

    def wait(self, timeout: int):
        self.event.wait(timeout=timeout)

    def get_session_token(self):
        return self.token_manager.get_session_token()
