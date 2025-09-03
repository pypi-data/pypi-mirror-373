#!/usr/bin/env python
"""Test the API."""

import pytest

from chime_frb_api import core


def test_bad_initialization():
    """Test that the API raises an exception when initialized with bad values."""
    with pytest.raises(Exception):
        core.API()


def test_authorization_with_userpass():
    """Test that the API can authorize with a username and password."""
    master = core.API(base_url="http://localhost:8001")
    master.generate_token(username="debug", password="debug")
    auth = master.authorize()
    assert auth is True
    reauth = master.reauthorize()
    assert reauth is True


def test_authorize_with_token():
    """Test that the API can authorize with a token."""
    master = core.API(base_url="http://localhost:8001")
    response = master._session.post(
        url=master.base_url + "/auth",
        json={"username": "debug", "password": "debug"},
    )
    tokens = response.json()
    access_token = tokens.get("access_token", None)
    refresh_token = tokens.get("refresh_token", None)
    auth = master.authorize(
        access_token=access_token, refresh_token=refresh_token
    )
    assert auth is True


def test_auth_with_bad_values():
    """Test that the API raises an exception when initialized with bad values."""
    master = core.API(base_url="http://localhost:8001")
    with pytest.raises(Exception):
        master.authorize(
            access_token="bad_access_token",
            refresh_token="bad_refresh_token",
            username="bad",
            password="also_bad",
        )


def test_reauth_with_bad_tokens():
    """Test that the API raises an exception when initialized with bad values."""
    master = core.API(base_url="http://localhost:8001")
    with pytest.raises(Exception):
        master.reauthorize(
            access_token="bad_access_token", refresh_token="bad_refresh_token"
        )


def test_reauth_without_tokens():
    """Test that the API raises an exception when initialized with bad values."""
    master = core.API(base_url="http://localhost:8001")
    with pytest.raises(Exception):
        master.reauthorize()
