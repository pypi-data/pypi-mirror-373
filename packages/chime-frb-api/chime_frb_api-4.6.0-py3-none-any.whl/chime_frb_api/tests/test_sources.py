#!/usr/bin/env python

import pytest

from chime_frb_api.backends import frb_master

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_sources_error():
    with pytest.raises(TypeError):
        master.sources.get_source()


def test_get_expected_spectrum_error():
    with pytest.raises(TypeError):
        master.sources.get_expected_spectrum()
