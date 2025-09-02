from http import HTTPStatus
from typing import Optional, Union

import requests

from bigdata_client.clerk.authenticators.base_instance import ClerkInstanceBase
from bigdata_client.clerk.exceptions import (
    ClerkAuthError,
    ClerkAuthUnsupportedError,
    ClerkInvalidCredentialsError,
    ClerkTooManySignInAttemptsError,
    raise_errors_as_clerk_errors,
)
from bigdata_client.clerk.models import RefreshedTokenManagerParams
from bigdata_client.clerk.sign_in_strategies.base import SignInStrategy
from bigdata_client.clerk.sign_in_strategies.password import PasswordStrategy


class ClerkAuthenticatorDevInstance(ClerkInstanceBase):
    @classmethod
    @raise_errors_as_clerk_errors
    def login_and_activate_session(
        cls,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        pool_maxsize: int,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
    ) -> "ClerkAuthenticatorDevInstance":
        """
        Performs the authentication flow against Clerk with the chosen strategy by creating
        a session then choosing the first organization the user is a member of (activation).
        Args:
            clerk_frontend_api_url:
            login_strategy:
            pool_maxsize: maxsize for the urllib3 pool
            proxies: dict with the proxies in format {protocol: url}
            verify: ssl connection verification - True, False or path to certificate

        Returns: ClerkAuthenticatorDevInstance
        """
        if not isinstance(login_strategy, PasswordStrategy):
            raise ClerkAuthUnsupportedError("Unsupported SignInStrategy")
        dev_browser_token = cls._get_dev_browser_token(
            clerk_frontend_api_url, proxies=proxies, verify=verify
        )
        session = requests.Session()
        session.mount(
            "https://", requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize)
        )
        if proxies:
            session.proxies.update(proxies)
        session.verify = verify
        session.params = {"__dev_session": dev_browser_token}
        clerk_session = cls._sign_in(session, clerk_frontend_api_url, login_strategy)
        cls._activate_organization_in_session(
            session, clerk_session, clerk_frontend_api_url
        )

        return cls(
            clerk_frontend_api_url=clerk_frontend_api_url,
            login_strategy=login_strategy,
            session=session,
            clerk_session=clerk_session,
        )

    @classmethod
    def get_new_token_manager_params(
        cls,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        pool_maxsize: int,
        proxies: Optional[dict],
        verify: Union[bool, str],
    ):
        dev_browser_token = cls._get_dev_browser_token(
            clerk_frontend_api_url, proxies=proxies, verify=verify
        )
        session = requests.Session()
        session.mount(
            "https://", requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize)
        )

        if proxies:
            session.proxies.update(proxies)
        session.verify = verify
        session.params = {"__dev_session": dev_browser_token}
        clerk_session = cls._sign_in(session, clerk_frontend_api_url, login_strategy)
        cls._activate_organization_in_session(
            session, clerk_session, clerk_frontend_api_url
        )
        return RefreshedTokenManagerParams(session=session, clerk_session=clerk_session)

    @staticmethod
    def _get_dev_browser_token(
        clerk_frontend_api_url: str, proxies: Optional[dict], verify: Union[bool, str]
    ) -> str:
        """
        This is used to authenticate Development Instances with the DevBrowser scheme.
        It must be set before making any request to a dev instance, even for endpoints that are public.
        """
        response = requests.post(
            url=f"{clerk_frontend_api_url}dev_browser", proxies=proxies, verify=verify
        )
        response.raise_for_status()

        return response.json()["token"]

    @staticmethod
    def _sign_in(
        session: requests.Session, clerk_frontend_api_url: str, strategy: SignInStrategy
    ) -> str:
        url = f"{clerk_frontend_api_url}client/sign_ins"
        response = session.post(
            url=url, data=strategy.get_payload(), headers=strategy.get_headers()
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                raise ClerkInvalidCredentialsError from e
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                raise ClerkTooManySignInAttemptsError(
                    retry_after=response.headers.get("Retry-After")
                ) from e
            raise ClerkAuthError(str(e)) from e

        return response.json()["response"]["created_session_id"]
