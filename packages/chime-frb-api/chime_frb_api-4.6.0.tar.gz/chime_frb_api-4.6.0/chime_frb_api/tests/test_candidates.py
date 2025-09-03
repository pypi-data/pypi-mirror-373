#!/usr/bin/env python
from chime_frb_api.backends import frb_master

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_get_all_candidates():
    candidates = master.candidates.get_all_candidates()
    assert isinstance(candidates, list)
