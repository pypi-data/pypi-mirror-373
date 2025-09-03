#!/usr/bin/env python

import pytest

from chime_frb_api.backends import frb_master

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_detection():
    """
    Test /v1/voe/detection in DEBUG mode.
    Performs a few checks of the response
    from the endpoint.

    Returns:
    --------
    True
    """
    TEST_DET_EVENT = {
        "VOEvent": {
            "event_no": 1,
            "timestamp_utc": "1995-05-03 00:00:00.000000+00:00",
            "timestamp_utc_error": 0.0,
            "event_category": "UNKNOWN",
            "event_type": "EXTRAGALACTIC",
            "known_source_name": "",
            "known_source_rating": 0.0,
            "dm": 0.0,
            "dm_error": 0.0,
            "combined_snr": 0.0,
            "dm_gal_ne_2001_max": 0.0,
            "dm_gal_ymw_2016_max": 0.0,
            "ra": 0.0,
            "pos_error_semiminor_deg_95": 0.0,
            "dec": 0.0,
            "pos_error_semimajor_deg_95": 0.0,
            "rfi_grade_level2": 0.0,
        }
    }
    voe_status = master.voe.detection(payload=TEST_DET_EVENT, debug=True)
    assert voe_status["type"] == "detection", "Got {}, wanted {}".format(
        voe_status["type"], "detection"
    )
    assert voe_status["voe_created"] is True, "Got {}, wanted {}".format(
        voe_status["voe_created"], True
    )
    assert voe_status["transmission"] == "debug mode", (
        "Got {}, wanted {}".format(voe_status["transmission"], "debug mode")
    )


def test_update():
    """
    Test the /v1/voe/update endpoint in DEBUG mode.
    Perform a few sanity checks on the response from
    the endpoint.

    Returns:
    --------
    True
    """
    TEST_UP_EVENT = {
        "VOEvent": {
            "event_no": 1,
            "event_category": "",
            "event_type": "",
            "timestamp_utc": "1995-05-03 00:00:00.000000+00:00",
            "timestamp_utc_error": 0.0,
            "pipeline_name": "intensity",
            "ra": 0.0,
            "ra_error": 0.0,
            "dec": 0.0,
            "dec_error": 0.0,
            "dm": 0.0,
            "dm_error": 0.0,
            # Optional attributes
            # This class can be instantiated without specifying these
            "beam_numbers": "",
            "width": 0.0,
            "width_error": 0.0,
            "snr": 0.0,
            "flux": 0.0,
            "flux_error": 0.0,
            "gl": 0.0,
            "gb": 0.0,
            "dispersion_smearing": 0.0,
            "dispersion_smearing_error": 0.0,
            "dm_gal_ne_2001_max": 0.0,
            "dm_gal_ymw_2016_max": 0.0,
            "redshift_host": 0.0,
            "redshift_host_error": 0.0,
            "dm_index": 0.0,
            "dm_index_error": 0.0,
            "scattering_timescale": 0.0,
            "scattering_timescale_error": 0.0,
            "scattering_index": 0.0,
            "scattering_index_error": 0.0,
            "spectral_index": 0.0,
            "spectral_index_error": 0.0,
            "fluence": 0.0,
            "fluence_error": 0.0,
            "linear_pol": 0.0,
            "linear_pol_error": 0.0,
            "circular_pol": 0.0,
            "circular_pol_error": 0.0,
            "rm": 0.0,
            "rm_error": 0.0,
        }
    }
    voe_status = master.voe.update(payload=TEST_UP_EVENT, debug=True)
    assert voe_status["type"] == "update", "Got {}, wanted {}".format(
        voe_status["type"], "update"
    )
    assert voe_status["voe_created"] is True, "Got {}, wanted {}".format(
        voe_status["voe_created"], True
    )
    assert voe_status["transmission"] == "debug mode", (
        "Got {}, wanted {}".format(voe_status["transmission"], "debug mode")
    )


def test_retraction():
    """
    Test the /v1/voe/retraction endpoint in DEBUG
    mode. Perform a few sanity checks on the response
    from the endpoint.

    Returns:
    --------
    True
    """
    TEST_RET_EVENT = {
        "VOEvent": {
            "event_no": 1,
            "timestamp_utc": "1997-05-03 00:00:00.000000+00:00",
            "alert_type_retract": "detection",
        }
    }
    voe_status = master.voe.retraction(payload=TEST_RET_EVENT, debug=True)
    assert voe_status["type"] == "retraction", "Got {}, wanted {}".format(
        voe_status["type"], "retraction"
    )
    assert voe_status["voe_created"] is True, "Got {}, wanted {}".format(
        voe_status["voe_created"], True
    )
    assert voe_status["transmission"] == "debug mode", (
        "Got {}, wanted {}".format(voe_status["transmission"], "debug mode")
    )


def test_get_all():
    """
    Test the /v1/voe/ endpoint. Perform a few
    sanity checks on the response from the endpoint.

    Returns:
    --------
    True
    """
    voes = master.voe.get_all()
    for voe in voes:
        if voe["id"] == 1:
            record = voe["record"]
            for i in range(len(record)):
                entry = record[i]
                if i == 0:
                    assert entry["alert_type"] == "detection", (
                        "Got {}, wanted {}".format(
                            entry["alert_type"], "detection"
                        )
                    )
                    assert entry["information_source_type"] == "HEADER", (
                        "Got {}, wanted {}".format(
                            entry["information_source_type"], "HEADER"
                        )
                    )
                elif i == 1:
                    assert entry["alert_type"] == "update", (
                        "Got {}, wanted {}".format(
                            entry["alert_type"], "update"
                        )
                    )
                    assert entry["information_source_type"] == "INTENSITY", (
                        "Got {}, wanted {}".format(
                            entry["information_source_type"], "INTENSITY"
                        )
                    )
                else:
                    assert entry["alert_type"] == "retraction", (
                        "Got {}, wanted {}".format(
                            entry["alert_type"], "retraction"
                        )
                    )
                    assert entry["information_source_type"] == "HUMAN", (
                        "Got {}, wanted {}".format(
                            entry["information_source_type"], "HUMAN"
                        )
                    )


def test_get():
    """
    Test the /v1/voe/{} endpoint with an event number.
    Perform a few sanity checks on the response from
    the endpoint.

    Returns:
    --------
    True
    """
    voe = master.voe.fetch(event_no=1)
    assert voe["id"] == 1, "Got {}, wanted {}".format(voe["id"], 1)
    record = voe["record"]
    assert len(record) == 3, f"Got {len(record)}, wanted {3}"
    for i in range(len(record)):
        entry = record[i]
        if i == 0:
            assert entry["alert_type"] == "detection", (
                "Got {}, wanted {}".format(entry["alert_type"], "detection")
            )
            assert entry["information_source_type"] == "HEADER", (
                "Got {}, wanted {}".format(
                    entry["information_source_type"], "HEADER"
                )
            )
        elif i == 1:
            assert entry["alert_type"] == "update", "Got {}, wanted {}".format(
                entry["alert_type"], "update"
            )
            assert entry["information_source_type"] == "INTENSITY", (
                "Got {}, wanted {}".format(
                    entry["information_source_type"], "INTENSITY"
                )
            )
        else:
            assert entry["alert_type"] == "retraction", (
                "Got {}, wanted {}".format(entry["alert_type"], "retraction")
            )
            assert entry["information_source_type"] == "HUMAN", (
                "Got {}, wanted {}".format(
                    entry["alert_type_retract"], "detection"
                )
            )


def test_bad_get():
    """
    Test the /v1/voe/{} endpoint. Check that
    AttributeError is raised when no event number
    is supplied.

    Returns:
    --------
    True
    """
    with pytest.raises(AttributeError):
        master.voe.fetch()


if __name__ == "__main__":  # pragma: no cover
    """Conduct all the tests in sequence.

    1.  Test sending detection VOEvent for event number 1.

    3.  Test sending update VOEvent for event number 1.

    5.  Test sending retraction VOEvent for event number 1.

    7.  Test getting all VOEvent records in database.

    8.  Test getting single VOEvent record for event number 1.
    9.  Test bad call to getting single VOEvent record.
    """
    (test_detection(),)
    (test_update(),)
    (test_retraction(),)
    (test_get_all(),)
    (test_get(),)
    (test_bad_get(),)
