#!/usr/bin/env python
from chime_frb_api.backends import frb_master

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_get_all_new_candidate_verifications():
    verifications = master.verification.get_all_new_candidate_verifications()
    assert verifications == []


def test_get_all_known_candidate_verifications():
    verifications = master.verification.get_all_known_candidate_verifications()
    assert verifications == []
