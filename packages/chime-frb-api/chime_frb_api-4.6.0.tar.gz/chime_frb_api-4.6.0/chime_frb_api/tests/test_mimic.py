#!/usr/bin/env python

import pytest

from chime_frb_api.backends import frb_master

INJECTION = {
    "timeout_sec": 0,
    "injection_time": "string",
    "timestamp_fpga": 0,
    "pulse_width_ms": 0,
    "dm": 0,
    "bandwidth": 0,
    "beams": [0],
    "snr": 0,
    "fluence": 0,
    "ra": 0,
    "dec": 0,
    "injection_program": "string",
    "injection_program_id": "string",
    "extra_injection_parameters": {},
}


master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_active_injections():
    injections = master.mimic.get_active_injections()
    assert injections == []


def test_simulated_event():
    event = master.mimic.get_simulated_event(uuid=123)
    assert event == {"injection": None, "detection": None}


def test_uuids():
    uuids = master.mimic.get_uuids()
    assert uuids == []


def test_bad_simuldated_event():
    with pytest.raises(AttributeError):
        master.mimic.get_simulated_event()


def test_injection_programs():
    programs = master.mimic.get_all_injection_programs()
    assert programs == []
