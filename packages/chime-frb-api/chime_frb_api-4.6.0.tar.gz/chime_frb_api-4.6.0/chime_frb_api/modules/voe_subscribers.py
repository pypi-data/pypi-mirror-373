#!/usr/bin/env python
"""CHIME/FRB VOE Subscribers API."""

import logging
from typing import Optional

from attr import ib as attribute
from attr import s as attrs
from attr.validators import instance_of

from chime_frb_api.core import API

log = logging.getLogger(__name__)


class VoeSubscribers(API):
    """CHIME/FRB VOEvent Subscriber API."""

    def __init__(self, API: API):
        """Initialize the CHIME/FRB VOEvent Subscriber API."""
        self.API = API

    def get_all(self):
        """Retrieve all subscribers to the CHIME/FRB VOEvent Service.

        Retrieve all subscribers to the CHIME/FRB
        VOEvent service that are currently saved
        in the "voe_subscribers" RethinkDB table
        in FRB Master.

        Args:
            None

        Returns:
            List of dictionaries
        """
        url = "/v1/voe-subscribers/"
        resp = self.API.get(url=url)
        log.debug(f"Response from {url}: {resp}")
        return resp

    def fetch(self, email_address: Optional[str] = None):
        """Fetch a subscriber to the CHIME/FRB VOEvent Service.

        Retrieve a subscriber to the CHIME/FRB VOEvent
        service by their unique address.

        Args:
            email_address: The email address of the subscriber.

        Returns:
            dict: The subscriber object in the CHIME/FRB VOEvent. Subscribers database
                  that matches the inputted ID.
        """
        if not email_address:
            raise AttributeError("Subscriber email address required")
        url = "/v1/voe-subscribers/"
        resp = self.API.post(url=url, json={"email_address": email_address})
        log.debug(f"Response from {url}: {resp}")
        return resp

    def add(self, payload: dict, is_update: bool = False, wait: float = 10.0):
        """Add a subscriber to the CHIME/FRB VOEvent Service.

        Add a subscriber to the CHIME/FRB VOEvent Service
        by supplying the required details. Subscribers are
        indexed by their unique email address.

        Args:
            payload: The required subscriber details as a dictionary.

        Returns:
            dict: The database response dictionary.
        """

        @attrs(kw_only=True)
        class Subscriber:
            # Required attributes are specified with default=None
            # Email address is the primary key
            email_address = attribute(default=None, validator=instance_of(str))
            name = attribute(default=None, validator=instance_of(str))
            association = attribute(default=None, validator=instance_of(str))
            expires = attribute(default=None, validator=instance_of(str))
            xmls = attribute(default=None, validator=instance_of(bool))
            emails = attribute(default=None, validator=instance_of(bool))
            ip_addresses = attribute(default=None, validator=instance_of(list))

        # If the subscriber data is malformed, the Subscriber class breaks
        sub = Subscriber(**payload)  # noqa F841
        url = "/v1/voe-subscribers/add"
        resp = self.API.post(url=url, json=payload)
        log.debug(f"Response from {url}: {resp}")
        return resp

    def remove(self, email_address: Optional[str] = None):
        """Remove a subscriber from the CHIME/FRB VOEvent Service.

        Remove a subscriber to the CHIME/FRB VOEvent Service
        manually by suppyling both the subscriber ID and
        the name of that subscriber. In an effort to prevent
        mistaken removals, the name of the subscriber must
        match the ID else this process fails.

        Args:
            email_address: The unique email address that the subscriber will be contacted
                           by regarding VOEvents and all service updates.

        Returns:
            dict: The response from the CHIME/FRB VOEvent Subscriber database regarding
                  deletion of the subscriber.
        """
        if not email_address:
            raise AttributeError("Subscriber email address required")
        url = "/v1/voe-subscribers/delete"
        resp = self.API.post(url=url, json={"email_address": email_address})
        log.debug(f"Response (JSON) from {url}: {resp}")
        return resp
