#!/usr/bin/env python

import datetime
import random

from chime_frb_api.backends import frb_master

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def make_random_payload(payload):
    """
    Use a model payload that and fill numerical quantities with
    randomized values so that we can subnmit an FRB JSON report
    to the Sandbox TNS.

    Parameters:
    -----------
    payload : dict
        Input model payload with data destined for the sandbox
        TNS.

    Returns:
    --------
    payload : dict
        Modified model payload with randomized
        values.
    """

    def make_datetime_str(dt):
        """
        Return a string format of the inputted datetime.datetime
        object with the microseconds truncated to 3 digits. This
        is required for all TNS submissions.

        Parameters:
        -----------
        dt : datetime.datetime
            The datetime.datetime object to transform to the
            proper string format.
        """
        micro = dt.microsecond
        sub_str = str(dt).split(".")
        if micro > 1000:
            f = round(micro / 1000)
            if f < 100:
                if f < 10:
                    s = "00" + str(f)
                else:
                    s = "0" + str(f)
            else:
                s = str(f)
        dt_str = sub_str[0] + "." + s
        return dt_str

    dt = datetime.datetime.utcnow()
    dt_str = make_datetime_str(dt)
    dt_str = str(dt)

    y, m, d = dt.year, dt.month, dt.day
    y_str = str(y)
    if m < 10:
        m_str = "0" + str(m)
    else:
        m_str = str(m)
    if d < 10:
        d_str = "0" + str(d)
    else:
        d_str = str(d)
    # Create a random 6-character string of lowercase letters
    # This is attached to the internal name to keep it unique
    rand_str = str(chr(97 + round(random.random() * (122 - 97))))
    rand_str_2 = str(chr(97 + round(random.random() * (122 - 97))))
    rand_str_3 = str(chr(97 + round(random.random() * (122 - 97))))
    rand_str_4 = str(chr(97 + round(random.random() * (122 - 97))))
    rand_str_5 = str(chr(97 + round(random.random() * (122 - 97))))
    rand_str_6 = str(chr(97 + round(random.random() * (122 - 97))))
    payload["internal_name"] = "FRB{}{}{}test{}{}{}{}{}{}".format(
        y_str,
        m_str,
        d_str,
        rand_str,
        rand_str_2,
        rand_str_3,
        rand_str_4,
        rand_str_5,
        rand_str_6,
    )
    payload["ra_value"] = (str(round(random.random() * 360.0, 2)),)
    payload["ra_error"] = (str(1 + round(random.random() * 60.0)),)
    payload["ra_units"] = ("arcmin",)

    payload["dec_value"] = (str(round(random.random() * 90.0, 2)),)
    payload["dec_error"] = (str(1 + round(random.random() * 60.0)),)
    payload["dec_units"] = ("arcmin",)

    payload["discovery_datetime"] = dt_str
    end_prop_date = dt + datetime.timedelta(
        days=30
    )  # proprietary period ends 30 days after submission
    payload["end_prop_period"] = str(end_prop_date)[
        :10
    ]  # Has format YYYY-MM-DD

    # Randomized numerical values of DM and SNR
    # The distributions sampled from are uniform
    dm = 1 + round(random.random() * 3000)
    dm_err = (dm / 100) + 1
    snr = round(random.random() * 100)
    payload["dm"] = str(dm)
    payload["dm_err"] = str(dm_err)
    payload["dm_unitid"] = "pc/cc"
    payload["obsdate"] = dt_str
    payload["snr"] = str(snr)

    return payload


def test_submit():
    """
    Test the /v1/tns/submit endpoint in DEBUG mode.
    Perform a few checks of the response from the
    endpoint.
    """
    TEST_PAYLOAD = {
        "frb_report": {
            "ra_value": "",
            "ra_error": "",
            "ra_units": "",
            "dec_value": "",
            "dec_error": "",
            "dec_units": "",
            "reporting_groupid": "86",  # This is the TNS group ID for CHIME/FRB
            "groupid": "86",  # This is the TNS group ID for CHIME/FRB
            "internal_name": "",
            "at_type": "5",
            "reporter": "CHIME/FRB Collaboration",
            "discovery_datetime": "",
            "barycentric_event_time": "",
            "end_prop_period": "2021-09-28",
            "proprietary_period_groups": ["", ""],
            "transient_redshift": "",
            "host_name": "",
            "host_redshift": "",
            "repeater_of_objid": "",
            "public_webpage": "https://www.chime-frb.ca",
            "region_ellipse": "",
            "region_ellipse_unitid": "",
            "region_polygon": "",
            "region_filename": "",
            "dm": "",
            "dm_err": "",
            "dm_unitid": "",
            "galactic_max_dm": "",
            "galactic_max_dm_model": "NE2001",
            "remarks": "Randomized data for a fake observation to \
                test CHIME/FRB-to-TNS automated service",
            "obsdate": "2019-10-21 14:18:08.616658",
            "flux": "0.0",
            "flux_error": "0.0",
            "limiting_flux": "0.0",
            "flux_units": "Jy",
            "filter_value": "1",
            "instrument_value": "222",
            "snr": "",
            "fluence": "",
            "fluence_err": "",
            "fluence_unitid": "",
            "exptime": "",
            "observer": "Robot",
            "burst_width": "",
            "burst_width_err": "",
            "burst_width_unitid": "",
            "burst_bandwidth": "",
            "burst_bandwidth_err": "",
            "burst_bandwidth_unitid": "",
            "scattering_time": "",
            "scattering_time_err": "",
            "scattering_time_unitid": "",
            "dm_struct": "",
            "dm_struct_err": "",
            "dm_struct_unitid": "",
            "rm": "",
            "rm_err": "",
            "rm_unitid": "rad m(-2)",
            "frac_lin_pol": "",
            "frac_lin_pol_err": "",
            "frac_circ_pol": "",
            "frac_circ_pol_err": "",
            "ref_freq": "600",
            "ref_freq_unitid": "MHz",
            "inst_bandwidth": "400",
            "inst_bandwidth_unitid": "MHz",
            "channels_no": "16384",
            "sampling_time": "0.98304",
            "sampling_time_unitid": "ms",
            "comments": "Randomly generated values",
        }
    }
    payload = make_random_payload(TEST_PAYLOAD)
    tns_status = master.tns.submit(payload=payload, debug=True)
    # The submission should return None because we do not use the URL
    # when testing.
    assert tns_status is None, f"Got {None} wanted {tns_status}"


def test_search():
    """
    Test the /v1/tns/search/{} endpoint in DEBUG mode.
    Perform a few checks of the response from the endpoint.
    """
    internal_name = 9386707
    TEST_PAYLOAD = {"search_input": {"internal_name": internal_name}}
    tns_status = master.tns.search(payload=TEST_PAYLOAD)
    # The query should return Non because we do not use the URL
    # when testing.
    assert tns_status is None, f"Got {None} wanted {tns_status}"
