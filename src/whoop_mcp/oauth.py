import json
import logging
import secrets
from pathlib import Path
from urllib.parse import urlencode

import httpx

from whoop_mcp.config import (
    WHOOP_CLIENT_ID,
    WHOOP_CLIENT_SECRET,
    WHOOP_REDIRECT_URI,
)


logger = logging.getLogger(__name__)


WHOOP_AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"


WHOOP_SCOPES = [
    "read:profile",
    "read:recovery",
    "read:cycles",
    "read:sleep",
    "read:workout",
    "read:body_measurement",
    "offline",
]


DATA_DIR = Path(".data")
STATE_FILE = DATA_DIR / "oauth_state.txt"
TOKEN_FILE = DATA_DIR / "whoop_tokens.json"


def create_authorization_url() -> tuple[str, str]:
    """
    Create the WHOOP OAuth authorization URL.

    The URL sends the user to WHOOP to authenticate
    and approve the requested scopes.
    """

    if not WHOOP_CLIENT_ID:
        raise RuntimeError(
            "WHOOP_CLIENT_ID is missing"
        )

    if not WHOOP_REDIRECT_URI:
        raise RuntimeError(
            "WHOOP_REDIRECT_URI is missing"
        )

    # 4 random bytes -> 8 hexadecimal characters.
    state = secrets.token_hex(4)

    DATA_DIR.mkdir(exist_ok=True)

    STATE_FILE.write_text(
        state,
        encoding="utf-8",
    )

    params = {
        "client_id": WHOOP_CLIENT_ID,
        "redirect_uri": WHOOP_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(WHOOP_SCOPES),
        "state": state,
    }

    authorization_url = (
        f"{WHOOP_AUTH_URL}?{urlencode(params)}"
    )

    logger.info(
        "WHOOP authorization URL generated"
    )

    return authorization_url, state


def validate_state(
    returned_state: str | None,
) -> bool:
    """
    Verify that WHOOP returned the same OAuth state
    value that was generated before authorization.

    This protects the OAuth flow against CSRF attacks.
    """

    if not returned_state:
        logger.warning(
            "OAuth state validation failed: "
            "returned state is missing"
        )
        return False

    if not STATE_FILE.exists():
        logger.warning(
            "OAuth state validation failed: "
            "stored state file is missing"
        )
        return False

    expected_state = STATE_FILE.read_text(
        encoding="utf-8",
    ).strip()

    valid = secrets.compare_digest(
        expected_state,
        returned_state,
    )

    if valid:
        logger.info(
            "WHOOP OAuth state validated successfully"
        )
    else:
        logger.warning(
            "WHOOP OAuth state validation failed"
        )

    return valid


def save_tokens(tokens: dict) -> None:
    """
    Save the latest WHOOP access and refresh tokens.

    WHOOP refresh tokens rotate, so the latest token
    response must always replace the previous one.
    """

    DATA_DIR.mkdir(exist_ok=True)

    TOKEN_FILE.write_text(
        json.dumps(tokens, indent=2),
        encoding="utf-8",
    )

    logger.info(
        "WHOOP tokens saved successfully"
    )


def load_tokens() -> dict:
    """
    Load the currently stored WHOOP OAuth tokens.
    """

    if not TOKEN_FILE.exists():
        raise RuntimeError(
            "WHOOP token file not found. "
            "Connect your WHOOP account first."
        )

    try:
        tokens = json.loads(
            TOKEN_FILE.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "WHOOP token file contains invalid JSON."
        ) from exc

    if not tokens.get("access_token"):
        raise RuntimeError(
            "WHOOP access token is missing."
        )

    return tokens


async def exchange_code_for_tokens(
    code: str,
) -> dict:
    """
    Exchange the temporary WHOOP authorization code
    for access and refresh tokens.
    """

    if not code:
        raise RuntimeError(
            "Authorization code is missing"
        )

    if not WHOOP_CLIENT_ID:
        raise RuntimeError(
            "WHOOP_CLIENT_ID is missing"
        )

    if not WHOOP_CLIENT_SECRET:
        raise RuntimeError(
            "WHOOP_CLIENT_SECRET is missing"
        )

    if not WHOOP_REDIRECT_URI:
        raise RuntimeError(
            "WHOOP_REDIRECT_URI is missing"
        )

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": WHOOP_CLIENT_ID,
        "client_secret": WHOOP_CLIENT_SECRET,
        "redirect_uri": WHOOP_REDIRECT_URI,
    }

    logger.info(
        "Starting WHOOP authorization-code token exchange"
    )

    try:
        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                WHOOP_TOKEN_URL,
                data=payload,
                headers={
                    "Content-Type":
                    "application/x-www-form-urlencoded"
                },
            )

    except httpx.TimeoutException as exc:
        logger.error(
            "WHOOP token exchange timed out"
        )

        raise RuntimeError(
            "WHOOP token exchange timed out. "
            "Please try again."
        ) from exc

    except httpx.RequestError as exc:
        logger.error(
            "WHOOP token exchange request failed"
        )

        raise RuntimeError(
            "Unable to reach the WHOOP token service."
        ) from exc

    if response.is_error:
        logger.error(
            "WHOOP token exchange failed with HTTP %s",
            response.status_code,
        )

        raise RuntimeError(
            "WHOOP token exchange failed: "
            f"HTTP {response.status_code}"
        )

    tokens = response.json()

    if not tokens.get("access_token"):
        raise RuntimeError(
            "WHOOP did not return an access token."
        )

    if not tokens.get("refresh_token"):
        raise RuntimeError(
            "WHOOP did not return a refresh token."
        )

    save_tokens(tokens)

    logger.info(
        "WHOOP token exchange successful"
    )

    return tokens


async def refresh_access_token() -> dict:
    """
    Refresh an expired WHOOP access token.

    WHOOP returns a new access token and a new
    refresh token. Both must be saved because the
    previous refresh token becomes invalid.
    """

    tokens = load_tokens()

    refresh_token = tokens.get(
        "refresh_token"
    )

    if not refresh_token:
        raise RuntimeError(
            "WHOOP refresh token is missing. "
            "Reconnect your WHOOP account."
        )

    if not WHOOP_CLIENT_ID:
        raise RuntimeError(
            "WHOOP_CLIENT_ID is missing"
        )

    if not WHOOP_CLIENT_SECRET:
        raise RuntimeError(
            "WHOOP_CLIENT_SECRET is missing"
        )

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": WHOOP_CLIENT_ID,
        "client_secret": WHOOP_CLIENT_SECRET,
        "scope": "offline",
    }

    logger.info(
        "Refreshing WHOOP access token"
    )

    try:
        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                WHOOP_TOKEN_URL,
                data=payload,
                headers={
                    "Content-Type":
                    "application/x-www-form-urlencoded"
                },
            )

    except httpx.TimeoutException as exc:
        logger.error(
            "WHOOP token refresh timed out"
        )

        raise RuntimeError(
            "WHOOP token refresh timed out. "
            "Please try again."
        ) from exc

    except httpx.RequestError as exc:
        logger.error(
            "WHOOP token refresh request failed"
        )

        raise RuntimeError(
            "Unable to reach the WHOOP token service."
        ) from exc

    if response.is_error:
        logger.error(
            "WHOOP token refresh failed with HTTP %s",
            response.status_code,
        )

        if response.status_code in {
            400,
            401,
        }:
            raise RuntimeError(
                "WHOOP authorization can no longer "
                "be refreshed. Please reconnect your "
                "WHOOP account."
            )

        raise RuntimeError(
            "WHOOP token refresh failed: "
            f"HTTP {response.status_code}"
        )

    new_tokens = response.json()

    if not new_tokens.get("access_token"):
        raise RuntimeError(
            "WHOOP did not return a new access token."
        )

    if not new_tokens.get("refresh_token"):
        raise RuntimeError(
            "WHOOP did not return a new refresh token."
        )

    save_tokens(new_tokens)

    logger.info(
        "WHOOP token refresh successful"
    )

    return new_tokens