#!/usr/bin/env python


import pytest

from chime_frb_api.backends import frb_master

master = frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_node_info():
    node_info = master.parameters.get_node_info(node_name="cf1n1")
    assert node_info == {
        "beams": [8, 9, 10, 11, 12, 13, 14, 15],
        "ip_addrs": ["10.6.201.11", "10.7.201.11"],
    }


def test_exception_get_node_info():
    with pytest.raises(NameError):
        master.parameters.get_node_info()


def test_beam_info():
    beam_info = master.parameters.get_beam_info(beam_number=1234)
    assert beam_info == {
        "hostname": "cf7n1",
        "ip_addr": "10.6.207.11",
        "rpc_server": "tcp://10.6.207.11:5555",
    }


def test_exception_get_beam_info():
    with pytest.raises(TypeError):
        master.parameters.get_beam_info()
