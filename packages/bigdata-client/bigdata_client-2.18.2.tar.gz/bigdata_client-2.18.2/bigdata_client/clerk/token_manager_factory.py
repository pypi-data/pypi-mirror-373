from typing import Optional, Union

from bigdata_client.clerk.authenticators.dev_instance import (
    ClerkAuthenticatorDevInstance,
)
from bigdata_client.clerk.authenticators.production_instance import (
    ClerkAuthenticatorProductionInstance,
)
from bigdata_client.clerk.constants import ClerkInstanceType
from bigdata_client.clerk.exceptions import ClerkUnexpectedSignInParametersError
from bigdata_client.clerk.models import SignInStrategyType
from bigdata_client.clerk.sign_in_strategies.password import PasswordStrategy
from bigdata_client.clerk.token_manager import ClerkTokenManager

TEMPLATE_NAME = "bigdata_sdk"


def token_manager_factory(
    instance_type: ClerkInstanceType,
    sign_in_strategy: SignInStrategyType,
    clerk_frontend_url: str,
    pool_maxsize: int,
    proxies: Optional[dict],
    verify: Union[bool, str],
    **sign_in_kwargs,
) -> ClerkTokenManager:
    """
    Factory to be used by Clerk consumers

    Args:
        instance_type: Instance type DEV/PROD
        sign_in_strategy: PASSWORD
        clerk_frontend_url: URL of the Clerk frontend
        pool_maxsize: maxsize for the urllib3 pool
        proxies: dict with the proxies in format {protocol: url}
        verify: ssl certificate verification - True, False or path to certificate
        **sign_in_kwargs: extra params required by the factory

    Returns:
        ClerkTokenManager is used for obtaining JWTs

    Raises:
        ClerkUnexpectedSignInParameters
    """

    strategy = _get_strategy(sign_in_strategy, sign_in_kwargs)
    if instance_type == ClerkInstanceType.DEV:
        clerk_instance = ClerkAuthenticatorDevInstance.login_and_activate_session(
            clerk_frontend_url,
            strategy,
            pool_maxsize,
            proxies=proxies,
            verify=verify,
        )
    elif instance_type == ClerkInstanceType.PROD:
        clerk_instance = (
            ClerkAuthenticatorProductionInstance.login_and_activate_session(
                clerk_frontend_url,
                strategy,
                pool_maxsize,
                proxies=proxies,
                verify=verify,
            )
        )
    else:
        raise ValueError(f"Unknown clerk instance: {instance_type}")

    return ClerkTokenManager(
        clerk_authenticator_instance=clerk_instance,
        clerk_jwt_template_name=TEMPLATE_NAME,
    )


def _get_strategy(sign_in_strategy: SignInStrategyType, kwargs: dict):
    if sign_in_strategy == SignInStrategyType.PASSWORD:
        return _get_password_strategy(kwargs)

    raise ValueError(f"Unknown sign in strategy: {sign_in_strategy}")


def _get_password_strategy(kwargs: dict):
    if set(kwargs) != {"password", "email"}:
        raise ClerkUnexpectedSignInParametersError

    return PasswordStrategy(email=kwargs["email"], password=kwargs["password"])
