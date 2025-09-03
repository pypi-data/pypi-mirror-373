"""Test Events API."""

import re

import pytest
import requests

from chime_frb_api.backends import frb_master

TEST_EVENT = {
    "id": 9386707,
    "fpga_time": 39927134208,
    "event_type": "EXTRAGALACTIC",
    "beam_numbers": [166, 1166],
    "measured_parameters": [
        {
            "pipeline": {
                "name": "realtime",
                "status": "completed",
                "logs": "event added manually in frb-master from l4",
            },
            "datetime": "2018-07-25 17:59:43.000000",
            "beam_number": 166,
            "dm": 716.5512084961,
            "dm_error": 1.61749708229307,
            "width": 3.93216,
            "snr": 19.2393493652344,
            "flux": 195.998616836148,
            "flux_error": 377.690847014669,
            "spectral_index": 0.0,
            "spectral_index_error": 0.0,
            "ra": 94.3578481588603,
            "ra_error": 0.0187359652645082,
            "dec": 66.5836698280485,
            "dec_error": 0.335355768540145,
            "galactic_dm": {"dm_model": "NE2001", "dm": 71.2463867297951},
        }
    ],
}

TEST_EVENT2 = {
    "id": 2,
    "fpga_time": 39927134208,
    "event_type": "EXTRAGALACTIC",
    "beam_numbers": [166, 1166],
    "measured_parameters": [],
}

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_add_events():
    """Test adding events."""
    request = requests.post("http://localhost:8001/v1/events/", json=TEST_EVENT)
    assert request.status_code == 200
    request = requests.post(
        "http://localhost:8001/v1/events/", json=TEST_EVENT2
    )
    assert request.status_code == 200


def test_get_event():
    """Test that the event is returned."""
    event = master.events.get_event(9386707)
    assert event["id"] == 9386707


def test_get_event_with_list():
    """Test fetching event data using get_event with a list of event ids."""
    event_data = master.events.get_event([TEST_EVENT["id"], TEST_EVENT2["id"]])
    returned_ids = event_data.keys()
    assert str(TEST_EVENT["id"]) in returned_ids
    assert str(TEST_EVENT2["id"]) in returned_ids
    assert isinstance(event_data, dict)


def test_get_event_invalid_type():
    """Test that TypeError is raised for invalid event_number type."""
    error_msg = (
        "event_number (the event IDs) must be either an int or a list of ints"
    )
    with pytest.raises(TypeError, match=re.escape(error_msg)):
        master.events.get_event("invalid_type")

    with pytest.raises(TypeError, match=re.escape(error_msg)):
        master.events.get_event({"invalid": "type"})


def test_get_event_empty_list():
    """Test get_event with an empty list."""
    with pytest.raises(ValueError, match="event_number is required."):
        master.events.get_event([])


def test_get_event_single_item_list():
    """Test get_event with a single-item list returns dict format."""
    event_data = master.events.get_event([TEST_EVENT["id"]])
    assert isinstance(event_data, dict)
    assert event_data["id"] == TEST_EVENT["id"]


def test_get_event_with_multiple_items():
    """Test fetching event data by list of event ids."""
    event_data = master.events.get_event([TEST_EVENT["id"], TEST_EVENT2["id"]])
    returned_ids = event_data.keys()
    assert str(TEST_EVENT["id"]) in returned_ids
    assert str(TEST_EVENT2["id"]) in returned_ids
    assert isinstance(event_data, dict)
    assert len(event_data) == 2


def test_exception_measured_parameters():
    """Test that an exception is raised when the measured parameters are not provided."""
    with pytest.raises(TypeError):
        master.events.add_measured_parameters()


def test_name_error_meas_params():
    """Test that an exception is raised when the measured parameters malformed."""
    parameters = {
        "dm": 1.0,
        "dm_error": 1.0,
        "galactic_dm": {},
        "expected_spectrum": [],
        "beam_number": 1123,
        "bad_parameter": "asda",
    }
    with pytest.raises(NameError):
        master.events.add_measured_parameters(
            event_number="9386707", measured_parameters=parameters
        )


def test_type_error_meas_param():
    """Test that an exception is raised when the measured parameters malformed."""
    parameters = {
        "pipeline": {
            "name": "test",
            "status": "test",
            "log": "test",
            "version": "test",
        },
        "dm": 1.0,
        "dm_error": 1.0,
        "galactic_dm": {},
        "expected_spectrum": [],
        "beam_number": 1.0,
    }
    with pytest.raises(TypeError):
        master.events.add_measured_parameters(
            event_number="9386707", measured_parameters=parameters
        )


def test_bad_meas_param():
    """Test that an exception is raised when the measured parameters malformed."""
    parameters = {
        "pipeline": {
            "name": "test",
            "status": "test",
            "log": "test",
            "version": "test",
        },
        "dm": 1,
    }
    with pytest.raises(TypeError):
        master.events.add_measured_parameters(
            event_number="5000000", measured_parameters=parameters
        )
    parameters = {
        "pipeline": {
            "name": "test",
            "status": "test",
            "log": "test",
            "version": "test",
        },
        "galactic_dm": [],
    }
    with pytest.raises(TypeError):
        master.events.add_measured_parameters(
            event_number="5000000", measured_parameters=parameters
        )
    parameters = {
        "pipeline": {
            "name": "test",
            "status": "test",
            "log": "test",
            "version": "test",
        },
        "gain": 1,
    }
    with pytest.raises(TypeError):
        master.events.add_measured_parameters(
            event_number="5000000", measured_parameters=parameters
        )


def test_measured_parameters():
    """Test that the measured parameters are added."""
    parameters = {
        "pipeline": {
            "name": "test",
            "status": "test",
            "log": "test",
            "version": "test",
        },
        "dm": 1.0,
        "dm_error": 1.0,
        "nchain_end": 100,
        "nchain_start": 10,
        "nwalkers_end": 1000,
        "nwalkers_start": 100,
        "dof": 100,
        "ra_list": [0.0, 12.4],
        "ra_list_error": [0.1, 0.1],
        "dec_list": [-1.2, 49.0],
        "dec_list_error": [0.1, 0.1],
        "x_list": [0.2, 0.3],
        "x_list_error": [0.01, 0.01],
        "y_list": [23.1, 45.3],
        "y_list_error": [0.01, 0.1],
        "max_log_prob": [0.6, 1.0],
        "chi2_list": [100.0, 123.4],
        "galactic_dm": {},
        "expected_spectrum": [],
        "beam_number": 1123,
        "is_bandpass_calibrated": True,
        "fitburst_reference_frequency": 600.0,
        "fitburst_reference_frequency_scattering": 600.0,
        "ftest_statistic": 0.5,
        "sub_burst_dm": [1.0],
        "sub_burst_dm_error": [1.0],
        "sub_burst_snr": [10.0],
        "sub_burst_width": [1.0],
        "fixed": {"dm": True, "width": False},
        "bw_low_frequencies_mhz": [400.2, 537.5],
        "bw_high_frequencies_mhz": [727.7, 800.2],
        "bw_chi2_reduced": [0.9, 1.5],
        "bw_rpl_fit": [[1e-01, 2e02, -3e01], [2e-01, 1e02, -5e01]],
        "mb_bandwidth_mhz": 400.0,
        "chi2": 1.0,
        "nfitdata": 1024,
        "npars": 10,
    }
    status = master.events.add_measured_parameters(
        event_number=9386707, measured_parameters=parameters
    )
    assert status is True


def test_no_event():
    """Test that an exception is raised when the event number is not provided."""
    with pytest.raises(TypeError):
        master.events.get_event()
