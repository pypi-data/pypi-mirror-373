from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import os
import httpx
import logging


logger = logging.getLogger(__name__)


async def get_spotify_token(
    client_id: str | None = None, client_secret: str | None = None
) -> str:
    """Get a Spotify access token."""
    if not client_id:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        if not client_id:
            raise RuntimeError(
                "No SPOTIFY_CLIENT_ID in the environment or passed to get_spotify_token."
            )

    if not client_secret:
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        if not client_secret:
            raise RuntimeError(
                "No SPOTIFY_CLIENT_SECRET in the environment or passed to get_spotify_token."
            )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        logger.debug("Got access token from Spotify")
        return response.json()["access_token"]


def parse_retry_after(value: str | None) -> float:
    if not value:
        return 1.0
    try:
        return float(value)
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
            return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
        except Exception as err:
            logger.warning(
                f"Unexpected exception when parsing Retry-After value: {err}"
            )
            return 1.0
