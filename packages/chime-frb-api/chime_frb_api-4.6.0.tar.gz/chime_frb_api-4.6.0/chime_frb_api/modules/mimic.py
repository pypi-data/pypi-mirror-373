#!/usr/bin/env python
"""CHIME/FRB Mimic Backend."""

import logging
from typing import Optional

from chime_frb_api.core import API
from chime_frb_api.core.json_type import JSON

log = logging.getLogger(__name__)


class Mimic:
    """CHIME/FRB Mimic API."""

    def __init__(self, API: API):
        """CHIME/FRB Mimic Initialization."""
        self.API = API

    def register_injection(self, **kwargs) -> JSON:
        """Register an injection.

        Args:
            **kwargs: Refer to http://frb-vsop.chime:8001/swagger/#/Mimic

        Returns:
            uuid: python dict of the uuids of the registered injection
        """
        return self.API.post(
            url="/v1/mimic/injection", json=kwargs
        )  # pragma: no cover

    def register_detection(self, **kwargs) -> JSON:
        """Register a detection.

        Args:
            **kwargs: Refer to http://frb-vsop.chime:8001/swagger/#/Mimic

        Returns:
            dict
        """
        return self.API.post(
            url="/v1/mimic/detection", json=kwargs
        )  # pragma: no cover

    def get_active_injections(self) -> JSON:
        """Get parameters for all currently active injections.

        Args:
            None

        Returns:
            active_injections: list
        """
        return self.API.get(url="/v1/mimic/active_injections")

    def get_simulated_event(self, uuid: Optional[str] = None) -> JSON:
        """Get the injected and detected parameters for a specific UUID.

        Args:
            uuid: Universally unique identifier for the specific simulated event

        Returns:
            dict

        Raises:
            AttributeError: uuid is required
        """
        if uuid:
            return self.API.get(url=f"/v1/mimic/{uuid}")
        else:
            raise AttributeError("uuid is required")

    def get_uuids(self) -> JSON:
        """Get UUIDs for all simulated events.

        Args:
            None

        Returns:
            dict
        """
        return self.API.get(url="/v1/mimic/uuids")

    def get_all_injection_programs(self) -> JSON:
        """Get all unique injection programs.

        Args:
            None

        Returns:
            dict
        """
        return self.API.get(url="/v2/mimic/injection/programs")
