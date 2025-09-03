#!/usr/bin/env python
"""CHIME/FRB Event Tracer API."""

import enum
import logging
import time

import pymongo
import requests

# Setup
log = logging.getLogger(__name__)


class Status(enum.Enum):
    """Status enum."""

    complete = 1
    incomplete = 2
    not_required = 3


tsar_classification_stage = "tsar_classification"
baseband_callback_request_stage = "baseband_callback_request"
baseband_conversion_stage = "baseband_conversion"
data_registration_stage = "data_registration"
data_replication_to_minoc_stage = "data_replication_to_minoc"


site_pipeline_stages = [
    baseband_callback_request_stage,
    baseband_conversion_stage,
    data_registration_stage,
    data_replication_to_minoc_stage,
]

sites = ["chime", "kko", "gbo", "hco"]


class TraceUpdater:
    """CHIME/FRB Trace Updater API."""

    def __init__(
        self,
        event_no,
        site,
        db_host="",
        base_url="https://frb.chimenet.ca/frb-master",
    ):
        """Initialize Trace Updater API. Needs event number.

        Args:
            event_no: CHIME/FRB Event number
            site: Site at which we are call this.
            db_host: MongoDB host to connect to if at all.
                     If not provided, we will use REST api.
                     Connecting to database directly will be more robust.
        """
        assert site in sites
        self.site = site
        self.event_no = int(event_no)
        self.db = None
        if db_host:
            client = pymongo.MongoClient(host=db_host, port=27017)
            self.db = client.frb_master
        self.base_url = base_url
        self.create_trace()

    def create_trace(self):
        """Create a new trace."""
        if self.db is None:
            self.__create_trace_via_http()
            return
        if self.db.trace.find_one({"event_no": self.event_no}) is not None:
            log.error(f"Found existing trace for the event {self.event_no}.")
            return
        trace = {"event_no": self.event_no}
        trace[self.__generate_common_key(tsar_classification_stage)] = (
            Status.incomplete.name
        )

        for site in sites:
            for stage in site_pipeline_stages:
                key = self.__generate_site_key(stage, site)
                trace[key] = Status.incomplete.name
        self.db.trace.insert_one(trace)

    def set_tsar_classification_complete(self):
        """Sets tsar classification stage as complete."""
        stage = tsar_classification_stage
        status = Status.complete.name
        if self.db is None:
            self.__update_trace_via_http(stage, status)
            return
        if self.db.trace.find_one({"event_no": self.event_no}) is None:
            log.error(
                f"Could not find existing trace for the event {self.event_no}."
            )
            return
        trace = {}  # noqa: F841
        key = self.__generate_common_key(tsar_classification_stage)
        self.db.trace.find_one_and_update(
            {"event_no": self.event_no}, {"$set": {key: status}}
        )

    def set_baseband_callback_request_complete(self):
        """Sets baseband callback request as complete."""
        stage = baseband_callback_request_stage
        status = Status.complete.name
        if self.db is None:
            self.__update_trace_via_http(stage, status)
            return
        self.__update_trace_via_direct_db(stage, status)

    def set_baseband_conversion_complete(self):
        """Sets baseband conversion as complete."""
        stage = baseband_conversion_stage
        status = Status.complete.name
        if self.db is None:
            self.__update_trace_via_http(stage, status)
            return
        self.__update_trace_via_direct_db(stage, status)

    def set_data_registration_complete(self):
        """Sets data registration as complete."""
        stage = data_registration_stage
        status = Status.complete.name
        if self.db is None:
            self.__update_trace_via_http(stage, status)
            return
        self.__update_trace_via_direct_db(stage, status)

    def set_data_replication_to_minoc_complete(self):
        """Sets data replication to minoc as complete."""
        stage = data_replication_to_minoc_stage
        status = Status.complete.name
        if self.db is None:
            self.__update_trace_via_http(stage, status)
            return
        self.__update_trace_via_direct_db(stage, status)

    def __generate_common_key(self, stage):
        """Generates common key."""
        assert stage != ""
        return f"stages/{stage}"

    def __generate_site_key(self, stage, site):
        """Generates site key."""
        assert stage != ""
        assert stage in site_pipeline_stages
        return f"stages/{stage}/sites/{site}"

    def __update_trace_via_direct_db(self, stage, status):
        """Updates the trace directly in the database.

        Args:
            stage: Stage to update for the trace.
        """
        if self.db.trace.find_one({"event_no": self.event_no}) is None:
            log.error(
                f"Could not find existing trace for the event {self.event_no}."
            )
            return
        trace = {}  # noqa: F841
        assert stage in site_pipeline_stages
        key = self.__generate_site_key(stage, self.site)
        self.db.trace.find_one_and_update(
            {"event_no": self.event_no}, {"$set": {key: status}}
        )

    def __update_trace_via_http(self, stage, status):
        """Updates the trace via http.

        Args:
            stage: Stage to update for the trace.
            status: Status to set the value to.
        """
        attempts = 0
        while attempts <= 100:
            payload = {
                "event": self.event,
                "site": self.site,
                "stage": stage,
                "status": status,
            }
            url = self.base_url + "/v1/event-tracer/update-trace"
            resp = requests.post(url, json=payload)
            if resp["status"] is True:
                # successful response
                break
            time.sleep(0.1)
            attempts += 1

    def __create_trace_via_http(self):
        """Creates the trace via http."""
        attempts = 0
        while attempts <= 100:
            payload = {
                "event": self.event,
                "site": self.site,
            }
            url = self.base_url + "/v1/event-tracer/create-trace"
            resp = requests.post(url, json=payload)
            if resp["status"] is True:
                # successful response
                break
            time.sleep(0.1)
            attempts += 1
