#!/usr/bin/env python
"""CHIME/FRB TNS API."""

import datetime
import logging
from typing import Any, Dict

from attr import ib as attribute
from attr import s as attrs
from attr.validators import instance_of

from chime_frb_api.core import API

log = logging.getLogger(__name__)


class TNSAgent(API):
    """CHIME/FRB TNS API.

    Use this class to access the endpoints under
    /v1/tns/ on FRB Master. Allows submitting CHIME/FRB
    data to the Transient Name Server (TNS) for acquiring
    official TNS object names for CHIME/FRB events, and
    for searching the official TNS object name of an
    inputted CHIME/FRB event number.
    """

    def __init__(self, API: API):
        """CHIME/FRB TNS API Initialization."""
        self.API = API

    def format_internal_name(self, event_number: int) -> str:
        """Convert a CHIME/FRB event number to the internal name for TNS.

        Convert a CHIME/FRB event number to an internal name
        for use within the TNS by prepending "chimefrb_" to the
        event number. This will avoid confusion with other TNS
        groups that use event numbers for their internal names.

        Args:
        event_number: The CHIME/FRB event number for the data to be submitted
                      to the TNS.

        Returns:
            internal_name: The properly formatted string suitable for use on the
                           TNS as the internal name for the burst.
        """
        # Just in case the user already had prepended "chimefrb_" ...
        internal_name = "chimefrb_" + (str(event_number)).split("chimefrb_")[-1]
        return internal_name

    def submit(self, payload: dict, debug: bool = True):
        """Submit CHIME/FRB data to the TNS for acquiring an official TNS name.

        Submit meta data required to post CHIME/FRB data on the TNS
        and receive an official TNS object name for the CHIME/FRB event.
        Accesses the /v1/tns/submit POST endpoint in FRB Master.
        Searches the Sandbox TNS at https://sandbox-tns.weizmann.ac.il/api
        when in debug mode. Otherwise searches the Live TNS at
        https://wis-tns.weizmann.ac.il/api.

        Args:
            payload: Payload that must conform to the class::Report in order
                     to upload the FRB JSON report to the TNS successfully.

            debug: If True, the FRB JSON report is posted to the Sandbox TNS.
                   Otherwise, it is posted to the Live TNS.

        Returns:
            JSON: The repsonse from the /v1/tns/submit endpoint.
        """

        @attrs(kw_only=True)
        class Report:
            # Required attributes are specified with default=None and they must
            # generally be given a string formatted non-negative value, or one
            # of a few possible choices (e.g. unit names, Galactic DM models).
            # Non-required attributes are marked with default="" or some other
            # non-None type value, and the FRB JSON report can be submitted
            # with said default value.
            ra_value = attribute(default=None, validator=instance_of(str))
            ra_error = attribute(default=None, validator=instance_of(str))
            ra_units = attribute(default=None, validator=instance_of(str))
            dec_value = attribute(default=None, validator=instance_of(str))
            dec_error = attribute(default=None, validator=instance_of(str))
            dec_units = attribute(default=None, validator=instance_of(str))
            reporting_groupid = attribute(
                default="86", validator=instance_of(str)
            )
            groupid = attribute(default="86", validator=instance_of(str))
            internal_name = attribute(default=None, validator=instance_of(str))
            at_type = attribute(default="5", validator=instance_of(str))
            reporter = attribute(
                default="CHIME/FRB Collaboration", validator=instance_of(str)
            )
            discovery_datetime = attribute(
                default=None, validator=instance_of(str)
            )
            barycentric_event_time = attribute(
                default="", validator=instance_of(str)
            )

            default_end_prop_period = datetime.datetime.utcnow()
            default_end_prop_period += datetime.timedelta(
                days=365
            )  # Default to be proprietary for 1 year
            default_end_prop_period_str = str(default_end_prop_period)[:10]
            end_prop_period = attribute(
                default=default_end_prop_period_str, validator=instance_of(str)
            )

            proprietary_period_groups = attribute(
                default=["", ""], validator=instance_of(list)
            )
            transient_redshift = attribute(
                default="", validator=instance_of(str)
            )
            host_name = attribute(default="", validator=instance_of(str))
            host_redshift = attribute(default="", validator=instance_of(str))
            repeater_of_objid = attribute(
                default="", validator=instance_of(str)
            )
            public_webpage = attribute(
                default="https://www.chime-frb.ca", validator=instance_of(str)
            )
            region_ellipse = attribute(default="", validator=instance_of(str))
            region_ellipse_unitid = attribute(
                default="", validator=instance_of(str)
            )
            region_polygon = attribute(default="", validator=instance_of(str))
            region_filename = attribute(default="", validator=instance_of(str))
            dm = attribute(default=None, validator=instance_of(str))
            dm_err = attribute(default=None, validator=instance_of(str))
            dm_unitid = attribute(default="pc/cc", validator=instance_of(str))
            galactic_max_dm = attribute(
                default=None, validator=instance_of(str)
            )
            galactic_max_dm_model = attribute(
                default=None, validator=instance_of(str)
            )  # Required and must be one of exactly "NE2001" or "YMW16"
            remarks = attribute(default="", validator=instance_of(str))
            # Photometry attributes
            obsdate = attribute(default=None, validator=instance_of(str))
            flux = attribute(
                default=None, validator=instance_of(str)
            )  # Can be set to 0.0 if not available e.g. real-time pipeline
            flux_error = attribute(
                default=None, validator=instance_of(str)
            )  # Can be set to 0.0 if not available e.g. real-time pipeline
            limiting_flux = attribute(
                default=None, validator=instance_of(str)
            )  # Can be set to 0.0 if not available e.g. real-time pipeline
            flux_units = attribute(default="Jy", validator=instance_of(str))
            filter_value = attribute(default="1", validator=instance_of(str))
            instrument_value = attribute(
                default="222", validator=instance_of(str)
            )
            snr = attribute(default=None, validator=instance_of(str))
            fluence = attribute(default="", validator=instance_of(str))
            fluence_err = attribute(default="", validator=instance_of(str))
            fluence_unitid = attribute(
                default="", validator=instance_of(str)
            )  # Not required but if using must be exactly "Jy ms"
            exptime = attribute(default="", validator=instance_of(str))
            observer = attribute(default="Robot", validator=instance_of(str))
            burst_width = attribute(default="", validator=instance_of(str))
            burst_width_err = attribute(default="", validator=instance_of(str))
            burst_width_unitid = attribute(
                default="", validator=instance_of(str)
            )  # Not required but if using must be exactly "s"
            burst_bandwidth = attribute(default="", validator=instance_of(str))
            burst_bandwidth_err = attribute(
                default="", validator=instance_of(str)
            )
            burst_bandwidth_unitid = attribute(
                default="", validator=instance_of(str)
            )  # Not required but if using must be exactly "MHz"
            scattering_time = attribute(default="", validator=instance_of(str))
            scattering_time_err = attribute(
                default="", validator=instance_of(str)
            )
            scattering_time_unitid = attribute(
                default="", validator=instance_of(str)
            )  # Not required but if using must be exactly "s"
            dm_struct = attribute(default="", validator=instance_of(str))
            dm_struct_err = attribute(default="", validator=instance_of(str))
            dm_struct_unitid = attribute(
                default="", validator=instance_of(str)
            )  # Not required but if using must be exactly "pc/cc"
            rm = attribute(default="", validator=instance_of(str))
            rm_err = attribute(default="", validator=instance_of(str))
            rm_unitid = attribute(
                default="", validator=instance_of(str)
            )  # Not required but if using must be exactly "rad m(-2)"
            frac_lin_pol = attribute(default="", validator=instance_of(str))
            frac_lin_pol_err = attribute(default="", validator=instance_of(str))
            frac_circ_pol = attribute(default="", validator=instance_of(str))
            frac_circ_pol_err = attribute(
                default="", validator=instance_of(str)
            )
            ref_freq = attribute(default="600", validator=instance_of(str))
            ref_freq_unitid = attribute(
                default="MHz", validator=instance_of(str)
            )
            inst_bandwidth = attribute(
                default="400", validator=instance_of(str)
            )
            inst_bandwidth_unitid = attribute(
                default="MHz", validator=instance_of(str)
            )
            channels_no = attribute(default="16384", validator=instance_of(str))
            sampling_time = attribute(
                default="0.98304", validator=instance_of(str)
            )  # In milliseconds
            sampling_time_unitid = attribute(
                default="", validator=instance_of(str)
            )  # Not required but if using must be exactly "ms"
            comments = attribute(default="", validator=instance_of(str))

        # Create the Report object.
        # If it is malformed, this will raise a TypeError.
        frb_report: Dict[Any, Any] = payload.get("frb_report", {})
        report = Report(**frb_report)  # noqa
        # Properly format the internal name
        payload["internal_name"] = self.format_internal_name(
            event_number=payload["internal_name"]
        )
        if debug:
            # Do not post to the URL when using debug mode.
            return None
        # Make URL
        url = "/v1/tns/submit{debug}".format(
            debug="?debug=True" if debug else ""
        )
        # Execute Query
        resp = self.API.post(url=url, json=payload)
        log.debug(f"Response from {url}: {resp}")
        return resp

    def search(self, payload: dict, debug: bool = True):
        """Search TNS for TNS objects name of a CHIME/FRB object.

        Search the TNS to retrieve the TNS object name for a CHIME/FRB
        submission by the CHIME/FRB internal name, which in the past was
        the event number but now will be 'chimefrb_' plus the event number.
        In debug mode, this searches the Sandbox TNS at
        https://sandbox-tns.weizmann.ac.il/api. Otherwise, it searches the Live
        TNS at https://wis-tns.weizmann.ac.il/api.

        Args:
            payload: A dictonary with top-level key "search_input" holding a dictionary
                     with one field, "internal_name", with the CHIME/FRB event number to
                     search on the TNS.

            debug: If True, use the Sandbox TNS website to search.
                   Otherwise, use the Live TNS website to search.

        Returns:
            dict: The response from from the endpoint /v1/tns/search/{}.
        """

        @attrs(kw_only=True)
        class Search:
            internal_name = attribute(default=None, validator=instance_of(int))

        # Create the Search object
        # If it is malformed, this will raise a TypeError.
        search_input: Dict[Any, Any] = payload.get("search_input", {})
        search = Search(**search_input)  # noqa
        if debug:
            # Do not post to the URL when using debug mode.
            return None
        # Make URL
        url = "/v1/tns/search/{internal_name}{debug}".format(
            internal_name=str(search.internal_name),
            debug="?debug=True" if debug else "",
        )
        # Execute Query
        resp = self.API.get(url=url)
        log.debug(f"Response from {url}: {resp}")
        return resp
