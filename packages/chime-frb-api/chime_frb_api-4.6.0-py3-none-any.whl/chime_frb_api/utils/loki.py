"""Loki handler."""

from logging import Formatter, Logger

import requests
from logging_loki import LokiHandler


def add_handler(
    logger: Logger, site: str, pipeline: str, loki_url: str
) -> bool:
    """Add a Loki handler to the logger.

    Args:
        logger (Logger): Python logger
        site (str): Work site
        pipeline (str): Pipeline name
        loki_url (str): Loki URL

    Raises:
        AttributeError: Loki not ready.

    Returns:
        bool: Loki handler status
    """
    status: bool = False
    try:
        loki_sc = requests.get(
            loki_url.replace("loki/api/v1/push", "ready")
        ).status_code
        if loki_sc == 200:
            loki_handler = LokiHandler(
                url=loki_url,
                tags={"site": site, "pipeline": pipeline},
                version="1",
            )
            loki_handler.setFormatter(
                Formatter("%(levelname)s %(tag)s %(name)s %(message)s")
            )
            loki_handler.setLevel("ERROR")
            logger.root.addHandler(loki_handler)
            logger.debug(f"Loki URL: {loki_url}")
            status = True
        else:
            raise AttributeError("Loki not ready.")
    except Exception as error:
        logger.debug(error)
    finally:
        return status
