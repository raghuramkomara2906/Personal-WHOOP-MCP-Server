import logging
from datetime import datetime, timedelta, timezone

import httpx

from whoop_mcp.exceptions import (
    WhoopAPIError,
    WhoopAuthenticationError,
)
from whoop_mcp.normalizers import (
    normalize_body_measurements,
    normalize_cycle_collection,
    normalize_recovery_collection,
    normalize_sleep_collection,
    normalize_workout_collection,
)
from whoop_mcp.oauth import (
    load_tokens,
    refresh_access_token,
)


logger = logging.getLogger(__name__)


WHOOP_API_BASE = "https://api.prod.whoop.com/developer"


class WhoopClient:
    """
    Client for authenticated communication with the WHOOP API.

    Handles:
    - OAuth access tokens
    - automatic token refresh
    - WHOOP API requests
    - date filtering
    - normalized WHOOP responses
    """

    def __init__(self):
        self.tokens = load_tokens()

    @property
    def access_token(self) -> str:
        """
        Return the current WHOOP access token.
        """

        access_token = self.tokens.get("access_token")

        if not access_token:
            raise WhoopAuthenticationError(
                "WHOOP access token is missing. "
                "Please reconnect your WHOOP account."
            )

        return access_token

    def _headers(self) -> dict:
        """
        Build HTTP headers required by the WHOOP API.
        """

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    def _date_params(
        self,
        days: int,
    ) -> dict:
        """
        Build WHOOP start/end date parameters.
        """

        if days < 1 or days > 365:
            raise ValueError(
                "days must be between 1 and 365"
            )

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        return {
            "start": start.isoformat().replace(
                "+00:00",
                "Z",
            ),
            "end": end.isoformat().replace(
                "+00:00",
                "Z",
            ),
            "limit": 25,
        }

    async def _get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        """
        Send an authenticated GET request to WHOOP.

        If WHOOP returns 401, refresh the access token
        and retry the request once.
        """

        url = f"{WHOOP_API_BASE}{endpoint}"

        try:
            async with httpx.AsyncClient(
                timeout=30.0
            ) as client:

                response = await client.get(
                    url,
                    headers=self._headers(),
                    params=params,
                )

                # Access token expired.
                if response.status_code == 401:
                    logger.warning(
                        "WHOOP access token expired; "
                        "attempting refresh"
                    )

                    try:
                        self.tokens = (
                            await refresh_access_token()
                        )

                    except Exception as exc:
                        raise WhoopAuthenticationError(
                            "WHOOP authorization could "
                            "not be refreshed. Please "
                            "reconnect your WHOOP account."
                        ) from exc

                    response = await client.get(
                        url,
                        headers=self._headers(),
                        params=params,
                    )

        except httpx.TimeoutException as exc:
            logger.error(
                "WHOOP API request timed out: %s",
                endpoint,
            )

            raise WhoopAPIError(
                "WHOOP API request timed out. "
                "Please try again."
            ) from exc

        except httpx.RequestError as exc:
            logger.error(
                "Unable to reach WHOOP API: %s",
                endpoint,
            )

            raise WhoopAPIError(
                "Unable to reach the WHOOP API. "
                "Please try again."
            ) from exc

        # Authentication still failed after refresh.
        if response.status_code == 401:
            raise WhoopAuthenticationError(
                "WHOOP authorization is no longer valid. "
                "Please reconnect your WHOOP account."
            )

        if response.status_code == 403:
            raise WhoopAuthenticationError(
                "WHOOP denied access to this resource. "
                "Check the authorized OAuth scopes."
            )

        if response.status_code == 429:
            raise WhoopAPIError(
                "WHOOP API rate limit reached. "
                "Please try again later."
            )

        if response.status_code >= 500:
            raise WhoopAPIError(
                "WHOOP is currently unable to process "
                "the request. Please try again later."
            )

        if response.is_error:
            raise WhoopAPIError(
                "WHOOP API request failed with "
                f"HTTP {response.status_code}."
            )

        try:
            return response.json()

        except ValueError as exc:
            raise WhoopAPIError(
                "WHOOP returned an invalid response."
            ) from exc

    # --------------------------------------------------
    # Raw WHOOP API methods
    # --------------------------------------------------

    async def get_profile(self) -> dict:
        """
        Retrieve the authenticated user's basic profile.
        """

        return await self._get(
            "/v2/user/profile/basic"
        )

    async def get_recovery(
        self,
        days: int = 7,
    ) -> dict:
        """
        Retrieve raw WHOOP recovery data.
        """

        return await self._get(
            "/v2/recovery",
            params=self._date_params(days),
        )

    async def get_cycles(
        self,
        days: int = 7,
    ) -> dict:
        """
        Retrieve raw WHOOP cycle data.
        """

        return await self._get(
            "/v2/cycle",
            params=self._date_params(days),
        )

    async def get_sleep(
        self,
        days: int = 7,
    ) -> dict:
        """
        Retrieve raw WHOOP sleep data.
        """

        return await self._get(
            "/v2/activity/sleep",
            params=self._date_params(days),
        )

    async def get_workouts(
        self,
        days: int = 30,
    ) -> dict:
        """
        Retrieve raw WHOOP workout data.
        """

        return await self._get(
            "/v2/activity/workout",
            params=self._date_params(days),
        )

    async def get_body_measurements(
        self,
    ) -> dict:
        """
        Retrieve raw WHOOP body measurements.
        """

        return await self._get(
            "/v2/user/measurement/body"
        )

    # --------------------------------------------------
    # Model-friendly normalized methods
    # --------------------------------------------------

    async def get_recovery_clean(
        self,
        days: int = 7,
    ) -> list[dict]:
        """
        Retrieve normalized WHOOP recovery records.
        """

        raw = await self.get_recovery(
            days=days
        )

        return normalize_recovery_collection(
            raw
        )

    async def get_cycles_clean(
        self,
        days: int = 7,
    ) -> list[dict]:
        """
        Retrieve normalized WHOOP cycle records.
        """

        raw = await self.get_cycles(
            days=days
        )

        return normalize_cycle_collection(
            raw
        )

    async def get_sleep_clean(
        self,
        days: int = 7,
    ) -> list[dict]:
        """
        Retrieve normalized WHOOP sleep records.
        """

        raw = await self.get_sleep(
            days=days
        )

        return normalize_sleep_collection(
            raw
        )

    async def get_workouts_clean(
        self,
        days: int = 30,
    ) -> list[dict]:
        """
        Retrieve normalized WHOOP workout records.
        """

        raw = await self.get_workouts(
            days=days
        )

        return normalize_workout_collection(
            raw
        )

    async def get_body_measurements_clean(
        self,
    ) -> dict:
        """
        Retrieve normalized WHOOP body measurements.
        """

        raw = await self.get_body_measurements()

        return normalize_body_measurements(
            raw
        )