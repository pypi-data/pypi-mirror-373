#!/usr/bin/env python

from chime_frb_api.stations import drao

site = drao.DRAO(debug=True, base_url="http://localhost:8001")


def test_version():
    for i in range(2):
        version = site.frb_master.version()
        assert isinstance(version, str)
