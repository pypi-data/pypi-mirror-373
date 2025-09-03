"""Copy work products."""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from chime_frb_api import get_logger
from chime_frb_api.configs import MOUNTS, TEST_MOUNTS
from chime_frb_api.workflow import Work

logger = get_logger("workflow")


def work_products(work: Work, test_mode: bool = False) -> Work:
    """Create id based directory structure and copy files.

    Args:
        work(Work): Work object.

    Returns:
        work(Work): Modified work object.
    """
    try:
        date = datetime.fromtimestamp(work.creation).strftime("%Y%m%d")  # type: ignore
        if test_mode is False:
            destination = Path(
                f"{MOUNTS.get(work.site)}/workflow/{date}/{work.pipeline}/{work.id}"
            )
        else:
            destination = Path(
                f"{TEST_MOUNTS.get(work.site)}/workflow/{date}/{work.pipeline}/{work.id}"
            )
        destination.mkdir(parents=True, exist_ok=True)
        if (
            destination.exists()
            and destination.is_dir()
            and os.access(destination, os.W_OK)
        ):
            if work.products:
                for index, product in enumerate(work.products):
                    shutil.copy(product, destination.as_posix())
                    work.products[index] = (
                        destination / product.split("/")[-1]
                    ).as_posix()
            if work.plots:
                for index, plot in enumerate(work.plots):
                    shutil.copy(plot, destination.as_posix())
                    work.plots[index] = (
                        destination / plot.split("/")[-1]
                    ).as_posix()
            if work.site == "canfar" and not test_mode:
                try:
                    subprocess.run(
                        f"setfacl -R -m g:chime-frb-ro:r {destination.as_posix()}"
                    )
                    subprocess.run(
                        f"setfacl -R -m g:chime-frb-rw:rw {destination.as_posix()}"
                    )
                except FileNotFoundError as error:
                    logger.exception(error)
                    logger.debug(
                        "Linux dependency 'acl' not installed. Trying to use chgrp and chmod instead."  # noqa: E501
                    )
                    subprocess.run(
                        f"chgrp -R chime-frb-rw {destination.as_posix()}"
                    )
                    subprocess.run(f"chmod g+w {destination.as_posix()}")
        else:
            raise FileNotFoundError(
                f"Check {destination.as_posix()} was created."
            )
    except Exception as error:
        logger.exception(error)
    finally:
        return work
