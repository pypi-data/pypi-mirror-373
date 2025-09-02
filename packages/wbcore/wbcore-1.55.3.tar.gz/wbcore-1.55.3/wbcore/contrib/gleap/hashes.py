import hashlib
import hmac


def get_hash_from_user(user_id: int | str, secret: str) -> str:
    if isinstance(user_id, int):
        user_id = str(user_id)

    return hmac.new(
        bytes(secret, encoding="utf-8"),
        bytes(user_id, encoding="utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
