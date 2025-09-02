from typing import Optional

import jwt


def get_token_claim(token: str, claim: str) -> Optional[str]:
    return jwt.decode(token, options={"verify_signature": False}).get(claim)
