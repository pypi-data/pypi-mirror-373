#!/usr/bin/env python

import pytest
from requests.exceptions import HTTPError

from chime_frb_api.backends import frb_master

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_get_calibration_date():
    calibration = master.calibration.get_calibration(utc_date="20190101")
    assert calibration == []


def test_get_calibration_source():
    calibration = master.calibration.get_calibration(source_name="CAS_A")
    assert calibration == []


def test_get_calibration_both():
    calibration = master.calibration.get_calibration(
        utc_date="20190101", source_name="CAS_A"
    )
    assert calibration == []


def test_bad_get_calibration():
    with pytest.raises(AttributeError):
        master.calibration.get_calibration()


def test_calibration_in_timerange():
    calibration = master.calibration.get_calibration_in_timerange(
        start_utc_date="20190101", stop_utc_date="20190102", source_name="CAS_A"
    )
    assert calibration == []


def test_bad_test_calibration_in_timerange():
    with pytest.raises(AttributeError):
        master.calibration.get_calibration_in_timerange(
            start_utc_date="20190101"
        )


def test_nearest_calibration():
    with pytest.raises(HTTPError):
        master.calibration.get_nearest_calibration(
            utc_date="20190101", ra=11.0, dec=11.0
        )


def test_bad_nearest_calibration():
    with pytest.raises(AttributeError):
        master.calibration.get_nearest_calibration()


def test_get_calibration_product():
    with pytest.raises(HTTPError):
        master.calibration.get_calibration_product(calprod_filepath="test")


def test_bad_get_calibration_spectrum():
    with pytest.raises(AttributeError):
        master.calibration.get_calibration_product()
