#!/usr/bin/env python
"""CHIME/FRB Parameters API."""

import datetime
import logging
from typing import Any, List, Optional

from chime_frb_api.core import API

log = logging.getLogger(__name__)


class Parameters:
    """CHIME/FRB Parameters API."""

    def __init__(self, API: API):
        """Initialize the Parameters API."""
        self.API = API

    def get_node_info(self, node_name: Optional[str] = None):
        """Get CHIME/FRB Compute Node Information.

        Args:
            node_name: CHIME/FRB Compute Node Name, e.g. cf1n1

        Returns:
            dict
        """
        try:
            assert isinstance(node_name, str), (
                "node_name is required, e.g. cf1n1"
            )
            return self.API.get(f"/v1/parameters/get-node-info/{node_name}")
        except AssertionError as e:
            raise NameError(e)

    def get_beam_info(self, beam_number=None):
        """Get CHIME/FRB Beam Information.

        Args:
            beam_number: CHIME/FRB Beam Number, e.g. 2238

        Returns:
            dict

        Raises:
            TypeError: If beam_number is not provided or not an integer
        """
        if beam_number is None:
            raise TypeError("beam_number parameter is required")

        if not isinstance(beam_number, int):
            raise TypeError(
                f"beam_number must be an integer, got {type(beam_number).__name__}"
            )

        try:
            return self.API.get(f"/v1/parameters/get-beam-info/{beam_number}")
        except AssertionError as e:
            raise TypeError(f"invalid beam_number: {e}")

    def get_frame0_nano(self, event_date: datetime.datetime):
        """Get the frame0_nano for any given UTC Timestamp.

        Args:
            event_date: Datetime object containing the time of the event

        Returns:
            frame0_nano (float): frame0_nano time for the event datetime

        Raises:
            RuntimeError
        """
        raise NotImplementedError(
            "Currently not implemented"
        )  # pragma: no cover

    def get_datapaths(self, event_number: Optional[int] = None) -> list:
        """Returns top-level folders for each CHIME/FRB event number.

        Args:
            event_number: CHIME/FRB Event Number

        Returns:
            List of data paths

        Raises:
            AttributeError: if event_number is not provided
        """
        if event_number:  # pragma: no cover
            return self.API.get(url=f"/v1/events/datapaths/{event_number}")
        else:
            raise AttributeError("event_number is required")

    def get_datapath_size(self, datapath: Optional[str] = None) -> int:
        """Returns the size (in bytes) of a folder and its sub-directories.

        Args:
            datapath: Absolute path to directory

        Returns:
            integer: Size of the directory in bytes
        """
        if datapath:  # pragma: no cover
            return self.API.post(
                url="/v1/events/datapath/size", json={"datapath": datapath}
            )
        else:
            raise AttributeError("datapath is required")

    def get_max_size(
        self, datapath: Optional[str] = None, fileformat: Optional[str] = None
    ) -> int:  # pragma: no cover
        """Returns the maximum size of a file under a datapath.

        Args:
            datapath: Absolute path to directory
            fileformat: Format of the file to search

        Returns:
            max_file_size: maximum file size in bytes
        """
        assert datapath and fileformat, "datapath and fileformat required"
        payload = {"datapath": datapath, "fileformat": fileformat}
        return self.API.post(url="/v1/events/datapath/max-size", json=payload)

    def get_filenames(
        self, event_number: Optional[int] = None
    ) -> List[Any]:  # pragma: no cover
        """Get analysed data product filenames for an event.

        Args:
            event_number: CHIME/FRB Event Number

        Returns:
            filenames: Returns a list of filenames attached to an event
        """
        return self.API.get(f"/v1/events/filenames/{event_number}")
