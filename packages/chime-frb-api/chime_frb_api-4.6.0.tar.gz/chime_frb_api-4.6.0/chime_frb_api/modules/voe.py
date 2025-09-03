#!/usr/bin/env python
"""CHIME/FRB VOE Backend."""

import logging
from typing import Optional

from attr import ib as attribute
from attr import s as attrs
from attr.validators import instance_of

from chime_frb_api.core import API

log = logging.getLogger(__name__)


class Voe(API):
    """CHIME/FRB VOEvents API.

    Access the endpoints under /v1/voe/ on FRB Master.
    """

    def __init__(self, API: API):
        """Initialise the VOE API."""
        self.api = API

    def get_all(self):
        """Retrieve all VOEvents from FRBMaster.

        Args:
            None

        Returns:
            voe : dict
                Response from the endpoint as a dictionary
                indicating the database activity.

        """
        log.debug("Fetching all VOEvent records (no XMLs) from frb-master")
        return self.api.get(url="/v1/voe")

    def fetch(self, event_no: Optional[int] = None):
        """Retrieve all VOEvent records stored for an event number from FRB Master.

        This will contain the full VOEvent XML documents.

        Args:
            event_no: The CHIME/FRB unique event number.

        Returns:
            voe : dict
                Response from the endpoint as a dictionary
                indicating the database activity.
        """
        if not event_no:
            raise AttributeError("CHIME/FRB event number is required")
        log.debug(
            f"Fetching CHIME/FRB VOEvent record for event number {event_no}"
        )
        return self.api.get(url=f"/v1/voe/{event_no}")

    def detection(
        self, payload: dict, debug: bool = True, ip_address: str = ""
    ):
        """Send a detection-type or subsequent-type VOEvent.

        Args:
            payload: The dictionary to be inputted should have a top-level key
                     called "VOEvent" that contains a dictionary of key-value pairs,
                     some of which are required and others are optional.

            debug: If True, the debug URL is accessed so that a VOEvent
                   will not be published to the VOEvent Network.

            ip_address: If a non-empty string is supplied, trial the CHIME/FRB VOEvent
                        Service by publishing a role="test" detection-type VOEvent
                        to a Comet VOEvent broker running at the specified IP address.

        Returns:
            status : dict
                Response from the endpoint as a dictionary
                indicating the status of the VOEvent translation
                and publication process.
        """

        @attrs(kw_only=True)
        class Detection:
            # Required attributes are specified with default=None
            event_no = attribute(default=None, validator=instance_of(int))
            timestamp_utc = attribute(default=None, validator=instance_of(str))
            timestamp_utc_error = attribute(
                default=None, validator=instance_of(float)
            )
            event_category = attribute(default=None, validator=instance_of(str))
            event_type = attribute(default=None, validator=instance_of(str))
            known_source_name = attribute(
                default=None, validator=instance_of(str)
            )
            known_source_rating = attribute(
                default=None, validator=instance_of(float)
            )
            dm = attribute(default=None, validator=instance_of(float))
            dm_error = attribute(default=None, validator=instance_of(float))
            combined_snr = attribute(default=None, validator=instance_of(float))
            dm_gal_ne_2001_max = attribute(
                default=None, validator=instance_of(float)
            )
            dm_gal_ymw_2016_max = attribute(
                default=None, validator=instance_of(float)
            )
            ra = attribute(default=None, validator=instance_of(float))
            # L2-L3 localization error in right ascension (semi-minor)
            pos_error_semiminor_deg_95 = attribute(
                default=None, validator=instance_of(float)
            )
            dec = attribute(default=None, validator=instance_of(float))
            # L2-L3 localization error in declination (semi-major)
            pos_error_semimajor_deg_95 = attribute(
                default=None, validator=instance_of(float)
            )
            rfi_grade_level2 = attribute(
                default=None, validator=instance_of(float)
            )

        # Create the detection object
        # If it is malformed, this will raise a TypeError
        # E.g. if there is no "VOEvent" in payload,
        # it is defaulted to None, and passing None to Detection Class
        # will break it
        voevent: dict = payload.get("VOEvent", {})
        detection = Detection(**voevent)  # noqa
        # Make URL
        url = "/v1/voe/detection{}{}".format(
            "?debug=1" if debug else "", "?trial=1" if ip_address != "" else ""
        )
        payload["ip_address"] = ip_address
        # Execute Query
        resp = self.api.post(url=url, json=payload)
        log.debug(f"Response from {url}: {resp}")
        return resp

    def update(self, payload: dict, debug: bool = True, ip_address: str = ""):
        """Send a update-type VOEvent.

        Send an update-type VOEvent by providing
        a payload that follows the Event model defined
        in FRB Master models.

        Args:
            payload: dict
                The dictionary should have a primary key called
                "VOEvent" that holds a dictionary of values, some
                of which are required and others which are optional.
                This is left flexible to allow input from various
                different offline analysis pipelines.

            debug: bool
                If True, the debug URL is accessed so that a VOEvent
                will not be sent.

            ip_address: str
                If a non-empty string is supplied, trial the CHIME/FRB VOEvent
                Service by publishing a role="test" update-type VOEvent
                to a Comet VOEvent broker running at the specified IP address.

        Returns:
            status : dict
                Response from the endpoint as a dictionary
                indicating the status of the VOEvent translation
                and publication process.
        """

        @attrs(kw_only=True)
        class Update:
            # Required attributes are specified with default=None
            # Instantiating this blocked without these
            event_no = attribute(default=None, validator=instance_of(int))
            event_category = attribute(default=None, validator=instance_of(str))
            event_type = attribute(default=None, validator=instance_of(str))
            timestamp_utc = attribute(default=None, validator=instance_of(str))
            timestamp_utc_error = attribute(
                default=None, validator=instance_of(float)
            )
            pipeline_name = attribute(default=None, validator=instance_of(str))
            ra = attribute(default=None, validator=instance_of(float))
            ra_error = attribute(default=None, validator=instance_of(float))
            dec = attribute(default=None, validator=instance_of(float))
            dec_error = attribute(default=None, validator=instance_of(float))
            dm = attribute(default=None, validator=instance_of(float))
            dm_error = attribute(default=None, validator=instance_of(float))

            # Optional attributes
            # This class can be instantiated without specifying these
            beam_numbers = attribute(validator=instance_of(str))
            width = attribute(validator=instance_of(float))
            width_error = attribute(validator=instance_of(float))
            snr = attribute(validator=instance_of(float))
            flux = attribute(validator=instance_of(float))
            flux_error = attribute(validator=instance_of(float))
            # Galactic longitude (gl)
            gl = attribute(validator=instance_of(float))
            # Galactic latitude (gb)
            gb = attribute(validator=instance_of(float))
            dispersion_smearing = attribute(validator=instance_of(float))
            dispersion_smearing_error = attribute(validator=instance_of(float))
            dm_gal_ne_2001_max = attribute(validator=instance_of(float))
            dm_gal_ymw_2016_max = attribute(validator=instance_of(float))

            redshift_host = attribute(validator=instance_of(float))
            redshift_host_error = attribute(validator=instance_of(float))
            dm_index = attribute(validator=instance_of(float))
            dm_index_error = attribute(validator=instance_of(float))
            scattering_timescale = attribute(validator=instance_of(float))
            scattering_timescale_error = attribute(validator=instance_of(float))
            scattering_index = attribute(validator=instance_of(float))
            scattering_index_error = attribute(validator=instance_of(float))
            spectral_index = attribute(validator=instance_of(float))
            spectral_index_error = attribute(validator=instance_of(float))
            fluence = attribute(validator=instance_of(float))
            fluence_error = attribute(validator=instance_of(float))
            linear_pol = attribute(validator=instance_of(float))
            linear_pol_error = attribute(validator=instance_of(float))
            circular_pol = attribute(validator=instance_of(float))
            circular_pol_error = attribute(validator=instance_of(float))
            # Rotation measure
            rm = attribute(validator=instance_of(float))
            # Error in rotation measure
            rm_error = attribute(validator=instance_of(float))

        # Create the Update object
        # If it is malformed, this will raise a TypeError
        voevent = payload.get("VOEvent", {})
        update = Update(**voevent)  # noqa
        # Make URL
        url = "/v1/voe/update{}{}".format(
            "?debug=1" if debug else "", "?trial=1" if ip_address != "" else ""
        )
        payload["ip_address"] = ip_address
        # Execute Query
        resp = self.api.post(url=url, json=payload)
        log.debug(f"Response from {url}: {resp}")
        return resp

    def retraction(
        self, payload: dict, debug: bool = True, ip_address: str = ""
    ):
        """Send a retraction-type VOEvent.

        Send a VOEvent that acts as a retraction for
        a previously issued VOEvent, in the event of a
        mis-identification of a new source, of a repeat
        burst from a known source, or perhaps a mis-fire
        of an update-type alert.

        Args:
            payload : dict
                The dictionary should have a top-level key
                called "VOEvent" that contains a dictionary
                of required key-value pairs.

            debug : bool
                If True, the debug URL is accessed so that a VOEvent
                will not be published to the VOEvent Network.

            ip_address : str
                If a non-empty string is supplied, trial the CHIME/FRB VOEvent
                Service by publishing a role="test" retraction-type VOEvent
                to a Comet VOEvent broker running at the specified IP address.

        Returns:
            status : dict
                Response from the endpoint as a dictionary
                indicating the status of the VOEvent translation
                and publication process.
        """

        @attrs(kw_only=True)
        class Retraction:
            # Required attributes are specified with default=None
            event_no = attribute(default=None, validator=instance_of(int))
            timestamp_utc = attribute(default=None, validator=instance_of(str))
            alert_type_retract = attribute(
                default=None, validator=instance_of(str)
            )

        # Create the Retraction object
        # If it is malformed, this will raise a TypeError
        voevent: dict = payload.get("VOEvent", {})
        retraction = Retraction(**voevent)  # noqa
        # Make URL
        url = "/v1/voe/retraction{}{}".format(
            "?debug=1" if debug else "", "?trial=1" if ip_address != "" else ""
        )
        payload["ip_address"] = ip_address
        # Execute Query
        resp = self.api.post(url=url, json=payload)
        log.debug(f"Response from {url}: {resp}")
        return resp
