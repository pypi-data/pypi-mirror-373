"""Test Event Tracer API."""

import time

import pymongo
import pytest

from chime_frb_api.modules import event_tracer

EVENT_NO = int(time.time())
DB_HOST = "localhost"
SITE = "chime"
EMPTY_SITE = ""

test_db_client = pymongo.MongoClient(host=DB_HOST)
test_db = test_db_client.frb_master


def test_trace_updater_empty_site():
    with pytest.raises(AssertionError):
        event_tracer.TraceUpdater(EVENT_NO, EMPTY_SITE, DB_HOST)


def test_create_trace():
    tu = event_tracer.TraceUpdater(EVENT_NO, SITE, DB_HOST)
    got = test_db.trace.find_one({"event_no": EVENT_NO})
    del got["_id"]
    assert got is not None
    want = {
        "event_no": EVENT_NO,
        "stages/tsar_classification": event_tracer.Status.incomplete.name,
    }
    for site in ["chime", "kko", "gbo", "hco"]:
        want[f"stages/baseband_callback_request/sites/{site}"] = (
            event_tracer.Status.incomplete.name
        )
        want[f"stages/baseband_conversion/sites/{site}"] = (
            event_tracer.Status.incomplete.name
        )
        want[f"stages/data_registration/sites/{site}"] = (
            event_tracer.Status.incomplete.name
        )
        want[f"stages/data_replication_to_minoc/sites/{site}"] = (
            event_tracer.Status.incomplete.name
        )
    for k, v in want.items():
        assert got[k] == v
    assert len(got) == len(want)


def test_tsar_classification_complete():
    tu = event_tracer.TraceUpdater(EVENT_NO, SITE, DB_HOST)
    tu.set_tsar_classification_complete()
    got = test_db.trace.find_one({"event_no": EVENT_NO})
    assert got is not None
    assert (
        got["stages/tsar_classification"] == event_tracer.Status.complete.name
    )


def test_baseband_callback_request_complete():
    tu = event_tracer.TraceUpdater(EVENT_NO, SITE, DB_HOST)
    tu.set_baseband_callback_request_complete()
    got = test_db.trace.find_one({"event_no": EVENT_NO})
    assert got is not None
    assert (
        got[f"stages/baseband_callback_request/sites/{SITE}"]
        == event_tracer.Status.complete.name
    )


def test_baseband_conversion_complete():
    tu = event_tracer.TraceUpdater(EVENT_NO, SITE, DB_HOST)
    tu.set_baseband_conversion_complete()
    got = test_db.trace.find_one({"event_no": EVENT_NO})
    assert got is not None
    assert (
        got[f"stages/baseband_conversion/sites/{SITE}"]
        == event_tracer.Status.complete.name
    )


def test_data_registration_complete():
    tu = event_tracer.TraceUpdater(EVENT_NO, SITE, DB_HOST)
    tu.set_data_registration_complete()
    got = test_db.trace.find_one({"event_no": EVENT_NO})
    assert got is not None
    assert (
        got[f"stages/data_registration/sites/{SITE}"]
        == event_tracer.Status.complete.name
    )


def test_data_replication_to_minoc_complete():
    tu = event_tracer.TraceUpdater(EVENT_NO, SITE, DB_HOST)
    tu.set_data_replication_to_minoc_complete()
    got = test_db.trace.find_one({"event_no": EVENT_NO})
    assert got is not None
    assert (
        got[f"stages/data_replication_to_minoc/sites/{SITE}"]
        == event_tracer.Status.complete.name
    )
