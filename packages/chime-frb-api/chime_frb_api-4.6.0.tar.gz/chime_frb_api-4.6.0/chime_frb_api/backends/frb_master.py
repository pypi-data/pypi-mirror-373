#!/usr/bin/env python
"""CHIME/FRB Master Backend."""

import logging
from typing import Any, Dict

from chime_frb_api.core import API
from chime_frb_api.modules import (
    calibration,
    candidates,
    events,
    mimic,
    parameters,
    sources,
    swarm,
    tns,
    verification,
    voe,
    voe_subscribers,
)

log = logging.getLogger(__name__)


class FRBMaster:
    """CHIME/FRB Master."""

    def __init__(self, debug: bool = False, **kwargs):
        """CHIME/FRB Master Initialization."""
        # Instantiate FRB/Master Core API
        kwargs.setdefault(
            "default_base_urls",
            [
                "http://frb-vsop.chime:8001",
                "https://frb.chimenet.ca/frb-master",
            ],
        )
        self.API = API(debug=debug, **kwargs)
        # Instantiate FRB Master Components
        self.swarm = swarm.Swarm(self.API)
        self.events = events.Events(self.API)
        self.parameters = parameters.Parameters(self.API)
        self.calibration = calibration.Calibration(self.API)
        self.mimic = mimic.Mimic(self.API)
        self.sources = sources.Sources(self.API)
        self.voe = voe.Voe(self.API)
        self.voe_subscribers = voe_subscribers.VoeSubscribers(self.API)
        self.tns = tns.TNSAgent(self.API)
        self.candidates = candidates.Candidates(self.API)
        self.verification = verification.Verification(self.API)

    def version(self) -> str:
        """Fetch version from frb-master.

        Returns:
            Version string.
        """
        # Version of the frb-master API client is connected to
        try:
            version: Dict[str, Any] = self.API.get("/version")
            return str(version.get("version", "unknown"))
        except Exception as error:  # pragma: no cover
            log.warning(error)
            return "error"
