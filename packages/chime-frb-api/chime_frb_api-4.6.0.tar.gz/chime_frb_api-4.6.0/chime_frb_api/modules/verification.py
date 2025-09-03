#!/usr/bin/env python

import logging

from chime_frb_api.core import API

log = logging.getLogger(__name__)


class Verification:
    """
    CHIME/FRB Verification API
    """

    def __init__(self, API: API):
        self.API = API

    def get_all_new_candidate_verifications(self) -> list:
        """Retrieves all CHIME/FRB Verification records of type `NEW CANDIDATE`."""
        return self.API.get("/v1/verification/get-verifications/NEW CANDIDATE")

    def get_all_known_candidate_verifications(self) -> list:
        """Retrieves all CHIME/FRB Verification records of type `KNOWN CANDIDATE`."""
        return self.API.get(
            "/v1/verification/get-verifications/KNOWN CANDIDATE"
        )

    def add_verification(self, event_id, verification: dict) -> dict:
        """Adds a new CHIME/FRB Verification record to Verification Database.

        Args:
            verification (dict): A dictionary of CHIME/FRB Verification record.
        """
        return self.API.post(
            f"/v1/verification/add-user-classification/{event_id}",
            json=verification,
        )

    def get_verification_for_event(self, event_id) -> dict:
        """Retrieves a CHIME/FRB Verification record for a given event_id.

        Args:
            event_id (str): The event_id of the CHIME/FRB Verification record.
        Returns:
            A dictionary containing verification record for that event.
        """
        return self.API.get(f"/v1/verification/get-verification/{event_id}")

    def get_conflicting_verifications_faint(self) -> list:
        """Retrieves verification records for events that have conflicting tsar verifications and at least one classification of FAINT.

        Returns:
            A list of dictionaries each contains an eligible event verification record.
        """
        return self.API.get(
            "/v1/verification/get-conflicting-verifications-faint"
        )
