"""Github Utilities."""

from typing import Dict

from requests import get
from requests.models import Response

from chime_frb_api import get_logger

logger = get_logger(__name__)


def username(token: str) -> str:
    """Get the username of the user associated with the given token.

    Args:
        token (str): GitHub token

    Returns:
        str: GitHub username
    """
    url: str = "https://api.github.com/user"
    headers: Dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    logger.debug(f"Github URL: {url}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Token: {token}")
    resp: Response = get(url, headers=headers)
    resp.raise_for_status()
    username: str = str(resp.json()["login"])
    return username
