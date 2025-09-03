#!/usr/bin/env python
"""CHIME/FRB Sources API."""

import logging
from typing import Optional

from chime_frb_api.core import API
from chime_frb_api.core.json_type import JSON

log = logging.getLogger(__name__)


class Sources:
    """CHIME/FRB Sources API.

    Parameters
    ----------
    API : chime_frb_api.core.API class-type

    Returns
    -------
    object-type
    """

    def __init__(self, API: API):
        """Initialize Sources API."""
        self.API = API

    def get_source(self, source_name: str) -> JSON:
        """Astrophysical Source from CHIME/FRB Master.

        Args:
            source_name: Source name, e.g. CAS_A

        Returns:
            dict: Source
        """
        assert source_name, AttributeError("source_name is required")
        return self.API.get(f"/v1/sources/{source_name}")

    def get_source_type(self, source_type: Optional[str] = None) -> JSON:
        """Get CHIME/FRB sources based on type.

        Args:
            source_type: One of ["FRB", "FRB_REPEATER", "PULSAR", "STEADY", "RRAT"]

        Returns:
            dict: Returns a dict of all valid sources
        """
        valid = ["FRB", "FRB_REPEATER", "PULSAR", "STEADY", "RRAT"]
        assert source_type in valid, (
            f"source_type has to be a subset of {valid}"
        )
        return self.API.get(f"/v1/sources/search/type/{source_type}")

    def get_expected_spectrum(self, source_name: str) -> JSON:
        """Expected spectra for a CHIME/FRB Source.

        Args:
            source_name: Source name, e.g. CAS_A

        Returns:
            spectrum : dict
                Returns dict with the following format
                {"freqs": [], "expected_spectrum": []}
        """
        assert source_name, AttributeError("source_name is required")
        return self.API.get(f"/v1/sources/spectrum/{source_name}")
