
from django.conf import settings

from .zego_token04 import generate_token04


def create_zego_token(user_id, expires_in=3600, payload=""):
    """Generate a ZEGOCLOUD Token04 for an authenticated user."""

    app_id = settings.ZEGO_APP_ID
    server_secret = settings.ZEGO_SERVER_SECRET

    if not app_id or not server_secret:
        raise RuntimeError("ZEGOCLOUD credentials are missing.")

    result = generate_token04(
        app_id=int(app_id),
        user_id=str(user_id),
        secret=server_secret,
        effective_time_in_seconds=int(expires_in),
        payload=payload,
    )

    if result.error_code != 0:
        raise ValueError(result.error_message)

    return result.token