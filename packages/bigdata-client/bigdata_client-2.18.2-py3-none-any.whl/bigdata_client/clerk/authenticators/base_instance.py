from abc import ABC, abstractmethod
from typing import Optional, Union

import requests

from bigdata_client.clerk.models import RefreshedTokenManagerParams
from bigdata_client.clerk.sign_in_strategies.base import SignInStrategy


class ClerkInstanceBase(ABC):
    def __init__(
        self,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        session: requests.Session,
        clerk_session: str,
    ):
        self.clerk_frontend_api_url = clerk_frontend_api_url
        self.login_strategy = login_strategy
        self.session = session
        self.clerk_session = clerk_session

    @classmethod
    @abstractmethod
    def login_and_activate_session(
        cls,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        pool_maxsize: int,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
    ):
        """
        Performs the authentication flow against Clerk with the chosen strategy by creating
        a session then choosing the first organization the user is a member of (activation).
        Returns a new instance

        Args:
            clerk_frontend_api_url:
            login_strategy:
            pool_maxsize: maxsize for the urllib3 pool
            proxies: dict with the proxies in format {protocol: url}
            verify: ssl connection verification - True, False or path to certificate
        """

    @classmethod
    @abstractmethod
    def get_new_token_manager_params(
        cls,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        pool_maxsize: int,
        proxies: Optional[dict],
        verify: Union[bool, str],
    ) -> RefreshedTokenManagerParams: ...

    @staticmethod
    def _get_user_organization(
        session: requests.Session, clerk_frontend_api_url: str
    ) -> Optional[str]:
        url = f"{clerk_frontend_api_url}me/organization_memberships"
        response = session.get(url=url)
        response.raise_for_status()

        # The user is assumed to belong to 1 org only or to None
        organization_to_activate = None
        organizations_memberships = response.json()["response"]
        if organizations_memberships:
            organization_to_activate = response.json()["response"][0]["organization"][
                "id"
            ]
        return organization_to_activate

    @staticmethod
    def _activate_organization_in_session(
        session: requests.Session, clerk_session: str, clerk_frontend_api_url: str
    ):
        """
        Activate the organization for the selected Clerk session in case the user has an organization.
        """
        user_organization = ClerkInstanceBase._get_user_organization(
            session, clerk_frontend_api_url
        )
        if user_organization:
            # Activate the organization for the clerk session
            url = f"{clerk_frontend_api_url}client/sessions/{clerk_session}/touch"
            response = session.post(
                url=url,
                headers={"content-type": "application/x-www-form-urlencoded"},
                data=f"active_organization_id={user_organization}",
            )
            response.raise_for_status()
