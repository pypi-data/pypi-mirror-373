import urllib.parse

from bigdata_client.clerk.sign_in_strategies.base import SignInStrategy


class PasswordStrategy(SignInStrategy):
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def get_payload(self):
        email = urllib.parse.quote(self.email)  # replace chars + -> %2B, required!
        password = urllib.parse.quote(self.password)
        return f"strategy={self.strategy_name}&identifier={email}&password={password}"

    def get_headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @property
    def strategy_name(self) -> str:
        return "password"

    def __eq__(self, other):
        """Equality check for PasswordStrategy, used in tests"""
        if not isinstance(other, PasswordStrategy):
            return False
        return (
            self.email == other.email
            and self.password == other.password
            and self.strategy_name == other.strategy_name
        )
