from functools import wraps
from typing import Optional


class ClerkAuthError(Exception):
    """Base exception"""

    def __init__(self, msg: Optional[str] = None):
        msg = msg or "Unknown authentication error"
        super().__init__(msg)


class ClerkAuthUnsupportedError(ClerkAuthError):
    """For handling unsupported features"""

    def __init__(self, msg: Optional[str] = None):
        msg = msg or "Sign in process failed, unsupported login strategy."
        super().__init__(msg)


class ClerkUnexpectedSignInParametersError(ClerkAuthError):
    """For handling sign in kwargs"""

    def __init__(self, msg: Optional[str] = None):
        msg = msg or "Sign in process failed, unexpected sign in parameters."
        super().__init__(msg)


class ClerkInvalidCredentialsError(ClerkAuthError):
    """When the sign in process fails"""

    def __init__(self, msg: Optional[str] = None):
        msg = msg or "Sign in process failed, check your credentials."
        super().__init__(msg)


class ClerkTooManySignInAttemptsError(ClerkAuthError):
    """Clerk rate limit"""

    def __init__(self, *, retry_after: str = None, msg: Optional[str] = None):
        default_msg = "Sign in process failed, too many logins for the same IP in a row"
        if retry_after:
            default_msg = f"{default_msg}. Retry after {retry_after} seconds."
        msg = msg or default_msg
        super().__init__(msg)


def raise_errors_as_clerk_errors(func):
    """
    Try/except to raise BaseClerkError. Decorator to be used
    for the methods that are exposed to the user.

    Args:
        func:

    Returns:

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, ClerkAuthError):
                raise e
            raise ClerkAuthError(e) from e

    return wrapper
