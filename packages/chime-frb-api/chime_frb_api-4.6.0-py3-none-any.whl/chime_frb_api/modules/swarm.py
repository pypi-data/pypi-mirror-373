#!/usr/bin/env python
"""CHIME/FRB Swarm API."""

import logging
from time import sleep
from typing import Dict, List, Optional

from chime_frb_api.core import API

log = logging.getLogger(__name__)


class Swarm:
    """CHIME/FRB Swarm API.

    Args:
        API : chime_frb_api.core.API
            Base class handling the actual HTTP requests.
    """

    def __init__(self, API: API):
        """Initialize the Swarm API."""
        self.API = API

    def get_jobs(self) -> List[str]:
        """Returns the name of all jobs on the analysis cluster.

        Args:
            None

        Returns:
            List[str]: List of job names.
        """
        jobs: List[str] = self.API.get(url="/v1/swarm/jobs")
        return jobs

    def get_job_status(self, job_name: str) -> Dict[str, str]:
        """Get job[s] status with a regex match to argument job_name.

        Args:
            job_name: Name of the job

        Returns:
            { job_name : STATUS } : dict

            Where STATUS can be,
            NEW         The job was initialized.
            PENDING     Resources for the job were allocated.
            ASSIGNED    Docker assigned the job to nodes.
            ACCEPTED    The job was accepted by a worker node.
            PREPARING   Docker is preparing the job.
            STARTING    Docker is starting the job.
            RUNNING     The job is executing.
            COMPLETE    The job exited without an error code.
            FAILED      The job exited with an error code.
            SHUTDOWN    Docker requested the job to shut down.
            REJECTED    The worker node rejected the job.
            ORPHANED    The node was down for too long.
            REMOVE      The job is not terminal but the associated job was removed
        """
        return self.API.get(f"/v1/swarm/job-status/{job_name}")

    def spawn_job(
        self,
        image_name: str,
        command: list,
        arguments: list,
        job_name: str,
        mount_archiver: bool = True,
        swarm_network: bool = True,
        job_mem_limit: int = 4294967296,
        job_mem_reservation: int = 268435456,
        job_cpu_limit: float = 1,
        job_cpu_reservation: float = 1,
        environment: dict = {},
    ) -> Dict[str, str]:
        """Spawn a job on the CHIME/FRB Analysis Cluster.

        Args:
            image_name: Name of the container image
            command: Command to run in the container
            arguments: Arguments to the command
            job_name: Unique name for the job
            mount_archiver: Mount Site Data Archivers, by default True
            swarm_network: Mount Cluster Network, by default True
            job_mem_limit: Memory limit in bytes, by default 4294967296
            job_mem_reservation: Minimum memory reserved, by default 268435456
            job_cpu_limit: Maximum cpu cores job can use, by default 1
            job_cpu_reservation: Minimum cores reservers for the job, default 1
            environment: ENV to pass to the container, default is {}

        Returns:
            JSON
                [description]
        """
        payload = {
            "image_name": image_name,
            "command": command,
            "arguments": arguments,
            "job_name": job_name,
            "mount_archiver": mount_archiver,
            "swarm_network": swarm_network,
            "job_mem_reservation": job_mem_reservation,
            "job_mem_limit": job_mem_limit,
            "job_cpu_limit": job_cpu_limit,
            "job_cpu_reservation": job_cpu_reservation,
            "environment": environment,
        }
        return self.API.post(url="/v1/swarm/spawn-job", json=payload)

    def get_logs(self, job_name: str) -> Dict[str, str]:
        """Return logs from a CHIME/FRB Job.

        Args:
            job_name: Unique name for the cluster job

        Returns:
            job_logs : dict
        """
        return self.API.get(f"/v1/swarm/logs/{job_name}")

    def prune_jobs(self, job_name: str) -> Dict[str, bool]:
        """Remove COMPLETED jobs with a regex match to argument job_name.

        Args:
            job_name: Unique name for the cluster job

        Returns:
            dict: {job_name : boolean}
        """
        return self.API.get(url=f"/v1/swarm/prune-job/{job_name}")

    def kill_job(self, job_name: str) -> Dict[str, bool]:
        """Remove (forcibly) job with ANY status but with an exact match to job_name.

        Args:
            job_name: Unique name for the cluster job

        Returns:
            dict: {job_name : boolean}
        """
        return self.API.get(url=f"/v1/swarm/kill-job/{job_name}")

    def kill_failed_jobs(
        self, job_name: Optional[str] = None
    ) -> Dict[str, bool]:
        """Remove FAILED jobs with a regex match to job_name.

        Args:
            job_name: Unique name for the cluster job

        Returns:
            dict: {job_name : boolean}
        """
        assert isinstance(job_name, str), "job_name <str> is required"
        status = {}
        for job in self.get_jobs():
            if job_name in job:  # pragma: no cover
                if self.get_job_status(job)[job] == "failed":
                    status[job] = self.kill_job(job)[job]
        return status

    def jobs_running(self, job_names: List[str]) -> bool:
        """Monitor job[s] on CHIME/FRB Analysis Cluster.

        Monitors job[s] on the CHIME/FRB Analysis Cluster untill they are either
        COMPLETE, FAILED or SHUTDOWN

        Args:
            job_names: A list of string job_name paramerters to monitor
        """
        running_statuses = [
            "new",
            "pending",
            "assigned",
            "accepted",
            "preparing",
            "starting",
            "running",
        ]
        if isinstance(job_names, str):
            job_names = [job_names]
        jobs_status = {}
        for job in job_names:
            status = self.get_job_status(job)
            jobs_status[job] = status
            for running in running_statuses:
                if running in status.values():
                    return True  # pragma: no cover
        return False

    def monitor_jobs(
        self, job_name: str, error_logs: bool = False
    ) -> bool:  # pragma: no cover
        """Continously monitor job[s] on the CHIME/FRB Analysis Cluster.

        Args:
            job_name: Regular expression matching to the job_name
            error_logs: Print error logs, by default False

        Returns:
            bool: Status of the pipeline
        """
        log.info("================================================")
        log.info(f"Monitoring Pipeline: {job_name}")
        log.info("================================================")
        initiating = [
            "new",
            "accepted",
            "pending",
            "starting",
            "preparing",
            "assigned",
        ]
        status = self.get_job_status(job_name)
        while any([n in initiating for n in status.values()]):
            sleep(30)
            status = self.get_job_status(job_name)
        # Initiation
        log.info("Pipeline Initiation: Complete")
        log.info("================================================")
        log.info("Pipeline Processing: Started")
        status = self.get_job_status(job_name)
        while "running" in status.values():
            log.info("Pipeline Processing: Running")
            sleep(120)
            status = self.get_job_status(job_name)
        log.info("Pipeline Processing: Complete")
        log.info("================================================")
        log.info("Pipeline Completion Status")
        completed = failed = 0
        for key, value in status.items():
            if value == "completed":
                completed += 1
            else:
                failed += 1
        log.info(f"Completed : {(completed / len(status)) * 100}%")
        log.info(f"Failed    : {(failed / len(status)) * 100}%")
        log.info("================================================")
        log.info("Pipeline Cleanup: Started")
        self.prune_jobs(job_name)
        # Make sure all jobs were pruned, if not report and kill them
        # TODO: In the future respawn "failed" jobs
        status = self.get_job_status(job_name)
        if len(status.keys()) > 0:
            log.error("Pipeline Cleanup: Failed Jobs Detected")
            for job in status.keys():
                log.error(f"Job Name : {key}")
                log.error(f"Job Removal: {self.kill_job(job)}")
            log.info("Pipeline Cleanup: Completed with Failed Jobs")
            return False
        log.info("Pipeline Cleanup: Completed")
        log.info("================================================")
        return True

    def spawn_baseband_job(
        self,
        event_number: int,
        task_name: str,
        arguments: list = [],
        job_id: Optional[int] = None,
        image_name: str = "chimefrb/baseband-localization:latest",
        command: list = ["baseband_analysis/pipelines/cluster/cluster_cli.py"],
        job_name: Optional[str] = None,
        job_mem_limit: int = 10 * 1024**3,
        job_mem_reservation: int = 10 * 1024**3,
        environment: dict = {},
        **kwargs,
    ) -> Dict[str, str]:  # pragma: no cover
        """Spawn a CHIME/FRB Baseband job on the Analysis Cluster.

        Args:
            event_number: ID of the event to process.
            task_name: Name of the task to run. Eg. localization
            arguments: Arguments to the command.
                       Default: None.
            job_id: ID of the job to run.
                    Default: None.
            command: The command to be run in the container.
                     Default: cluster_cli.py.
            image_name: Name of the container image to spawn the job with
                        Default: chimefrb/baseband-analysis:latest
            job_name: Unique name for the cluster job
                      Default: baseband-EVENT_NUMBER-TASK_NAME-UUID_CODE
            job_mem_limit: Memory limit of the created container in bytes
                           Default: 10 GB
            job_mem_reservation: Minimum memory reserved of the created container in
                                 bytes.
                                 Default: 10 GB
            environment: ENV variables to pass to the container
                         Default: read authentication tokens from the environment
            kwargs: Additional parameters for spawn_job
        """
        environment.setdefault("FRB_MASTER_ACCESS_TOKEN", self.API.access_token)
        environment.setdefault(
            "FRB_MASTER_REFRESH_TOKEN", self.API.refresh_token
        )

        if job_id is None:
            job_argument = []
        else:
            job_argument = ["--job-id", str(job_id)]

        if job_name is None:
            if (job_id is None) or (job_id < 0):
                job_name = f"baseband-{event_number}-{task_name}"
            else:
                job_name = f"baseband-{event_number}-{task_name}-{job_id}"

        out = self.spawn_job(
            image_name=image_name,
            command=command + [task_name],
            arguments=["--event-number", str(event_number)]
            + job_argument
            + ["--"]
            + arguments,
            job_name=job_name,
            job_mem_limit=job_mem_limit,
            job_mem_reservation=job_mem_reservation,
            job_cpu_limit=2,
            job_cpu_reservation=2,
            environment=environment,
            **kwargs,
        )

        return out
