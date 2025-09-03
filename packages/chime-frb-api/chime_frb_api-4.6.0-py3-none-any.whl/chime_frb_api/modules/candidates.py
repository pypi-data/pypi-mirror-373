#!/usr/bin/env python
"""CHIME/FRB Candidate Module."""

import logging

from chime_frb_api.core import API

log = logging.getLogger(__name__)


class Candidates:
    """CHIME/FRB Candidates API."""

    def __init__(self, API: API):
        """CHIME/FRB Candidates Initialization."""
        self.API = API

    def get_all_candidates(self) -> list:
        """Get all CHIME/FRB Candidates from Candidates Database.

        Args:
            None

        Returns:
            List of all CHIME/FRB Candidates
        """
        return self.API.get("/v1/candidates")
