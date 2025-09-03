#!/usr/bin/env python
"""CHIME/FRB API Calibration Module."""

from typing import Optional

from chime_frb_api.core import API
from chime_frb_api.core.json_type import JSON


class Calibration:
    """CHIME/FRB Calibration API."""

    def __init__(self, API: API):
        """Initializes the Calibration API."""
        self.API = API

    def get_calibration(
        self, utc_date: Optional[str] = None, source_name: Optional[str] = None
    ) -> JSON:
        """Get all CHIME/FRB calibration products for given date.

        Fetches all CHIME/FRB calibration data products for a specific utc_date,
        source_name or a combination of both filters. Atleast one is required.

        Args:
            utc_date: UTC date in the format YYYYMMDD, e.g. 20190101
        source_name: Name of the calibration source, e.g. CAS_A

        Returns:
            calibration_data_product : JSON

        Raises:
            AttributeError
        """
        if isinstance(utc_date, type(None)) and isinstance(
            source_name, type(None)
        ):
            raise AttributeError("either utc_date or source_name is required")
        url = "/v1/calibration"
        # Build the url in the format BASE/SOURCE/DATE
        if isinstance(source_name, str):
            url += f"/{source_name}"
        if isinstance(utc_date, str):
            url += f"/{utc_date}"
        return self.API.get(url)

    def get_calibration_in_timerange(
        self,
        start_utc_date: Optional[str] = None,
        stop_utc_date: Optional[str] = None,
        source_name: Optional[str] = None,
    ) -> JSON:
        """Get all CHIME/FRB calibration products for given time range.

        Fetches all CHIME/FRB calibration data products for a specific time
        range within start_utc_date and stop_utc_date. You can further, filter
        the results based on source_name.

        Args:
            start_utc_date: UTC date in the format YYYYMMDD, e.g. 20190101
            stop_utc_date: UTC date in the format YYYYMMDD, e.g. 20190101
            source_name: Name of the calibration source, e.g. CAS_A

        Returns:
            calibration_data_product : JSON

        Raises:
            AttributeError
        """
        if isinstance(start_utc_date, type(None)) or isinstance(
            stop_utc_date, type(None)
        ):
            raise AttributeError(
                "both start_utc_date and stop_utc_date are required"
            )
        url = "/v1/calibration"
        if isinstance(source_name, str):
            url += f"/{source_name}"
        url += f"/{start_utc_date}-{stop_utc_date}"
        return self.API.get(url)

    def get_nearest_calibration(
        self,
        utc_date: Optional[str] = None,
        ra: Optional[float] = None,
        dec: Optional[float] = None,
    ) -> JSON:
        """Get the nearest CHIME/FRB calibration products for given ra and dec.

        Fetches all CHIME/FRB calibration data products for a given
        right ascension, declication and utc_date combination.

        Args:
            ra: Right Ascension
            dec: Declication
            utc_date: UTC date in the format YYYYMMDD, e.g. 20190101

        Returns:
            calibration_data_product : JSON

        Raises:
            AttributeError
        """
        if (
            isinstance(ra, type(None))
            or isinstance(dec, type(None))
            or isinstance(utc_date, type(None))
        ):
            raise AttributeError("ra, dec and utc_date are all required")
        url = f"/v1/calibration/nearest/{utc_date}/{ra}/{dec}"
        return self.API.get(url)

    def get_calibration_product(
        self, calprod_filepath: Optional[str] = None
    ) -> JSON:
        """Fetches the CHIME/FRB calibration spectrum.

        Args:
            calprod_filepath: The path of the .npz file containing the 16K BF/Jy
                calibration spectrum and calibration diagnostic information on the
                CHIME/FRB Archiver.

        Returns:
            calibration_product : JSON
                {"calibration_spectrum": [],
                 "effective_bandwidth": 0,
                  "beam_num": 0,
                  "fwhm": 0,
                  "fwhm_err": 0,
                  "fwhm_fit_rsquared": 0}

        Raises:
            AttributeError
        """
        if isinstance(calprod_filepath, type(None)):
            raise AttributeError("calprod_filepath is required")
        payload = {"calprod_filepath": calprod_filepath}
        url = "/v1/calibration/get-calibration"
        return self.API.post(url=url, json=payload)
