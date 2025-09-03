#!/usr/bin/env python

import pytest

from chime_frb_api.backends import frb_master


@pytest.fixture(scope="module")
def master():
    yield frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


def test_get_jobs(master):
    jobs = master.swarm.get_jobs()
    assert jobs == []


def test_spawn_job(master):
    spawn_status = master.swarm.spawn_job(
        image_name="alpine",
        command=["uname"],
        arguments=[],
        job_name="swarm-job",
        mount_archiver=False,
        swarm_network=False,
    )
    assert "ID" in spawn_status.keys()


def test_job_status(master):
    job_status = master.swarm.get_job_status("swarm-job")
    assert job_status == {"swarm-job": "pending"}


def test_job_logs(master):
    job_logs = master.swarm.get_logs("swarm-job")
    assert job_logs == {"swarm-job": ""}


def test_prune_job(master):
    prune_status = master.swarm.prune_jobs("swarm-job")
    assert prune_status == {}


def test_kill_job(master):
    kill_status = master.swarm.kill_job("swarm-job")
    assert kill_status == {"swarm-job": True}


def test_jobs_running(master):
    jobs = master.swarm.jobs_running(job_names="test")
    assert jobs is False


def test_run_fitburst(master):
    with pytest.raises(Exception):
        master.swarm.run_fitburst(event_number=1, arguments=[])


def test_failed_job_cleanup(master):
    status = master.swarm.kill_failed_jobs(job_name="nothing")
    assert status == {}
