#!/usr/bin/env python
"""Test CHIME/FRB VOE Subscribers API."""

import pytest

from chime_frb_api.backends import frb_master

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")

TEST_SUBSCRIBER = {
    "email_address": "andrewzwaniga@gmail.com",
    "name": "ANDREW ZWANIGA",
    "association": "CHIME/FRB",
    "expires": "1995-05-03 00:00:00.000000+00:00",
    "xmls": True,
    "emails": True,
    "ip_addresses": ["xxx.xxx.x.xx"],
}


def test_add():
    """
    Test the /v1/voe-subscribers/add endpoint.

    Start by adding a new CHIME/FRB VOEvent Service
    subscriber, check the database response.

    Returns
    -------
        True
    """
    resp = master.voe_subscribers.add(payload=TEST_SUBSCRIBER)
    assert resp is True


def test_get_all():
    """
    Test the endpoint to get all subscribers currently in the database.

    Check that the only subscriber currently is the one added in the first test.

    Returns
    -------
        True
    """
    subscribers = master.voe_subscribers.get_all()
    assert len(subscribers) == 1
    for subscriber in subscribers:
        for field in subscriber:
            assert subscriber[field] == TEST_SUBSCRIBER[field], (
                f"Wanted {TEST_SUBSCRIBER[field]} got {subscriber[field]}"
            )


def test_get():
    """
    Test endpoint to get a subscriber by their subscriber ID.

    Check that the response matches what was added in the first test.

    Returns
    -------
        True
    """
    subscriber = master.voe_subscribers.fetch(
        email_address=TEST_SUBSCRIBER["email_address"]
    )
    for field in subscriber:
        assert subscriber[field] == TEST_SUBSCRIBER[field], (
            f"Wanted {TEST_SUBSCRIBER[field]} got {subscriber[field]}"
        )


def test_bad_get():
    """
    Test the /v1/voe-subscriber/{} endpoint.

    Check that AttributeError is raised when no email address is provided.

    Returns
    -------
        True
    """
    with pytest.raises(AttributeError):
        master.voe_subscribers.fetch()


def test_bad_delete():
    """
    Test the /v1/voe-subscribers/delete endpint.

    Check that AttributeError is raised when no email address is provided.
    """
    with pytest.raises(TypeError):
        master.voe_subscribers.delete()


def test_delete():
    """
    Test the /v1/voe-subscribers/delete endpoint.

    Check that the database response confirms a deletion has occurred.

    Returns
    -------
        True
    """
    resp = master.voe_subscribers.remove(
        email_address=TEST_SUBSCRIBER["email_address"]
    )
    assert resp is True


if __name__ == "__main__":  # pragma: no cover
    test_add()
    test_get_all()
    test_get()
    test_bad_get()
    test_bad_delete()
    test_delete()
