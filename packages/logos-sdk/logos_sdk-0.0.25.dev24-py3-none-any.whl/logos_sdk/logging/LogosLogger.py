import os
import logging
from google.cloud.logging import Client as LoggerClient
from dotenv import load_dotenv
from logos_sdk import DEVELOPMENT, TESTING, CLOUD_DEVELOPMENT, PRODUCTION


class LogosLogger:
    def __init__(self, name="logos-logging", labels=None, trace=None):

        load_dotenv()

        self.labels = labels
        self.trace = trace
        self.name = name
        self.settings = {}
        self.accesses = []

        # if current environment is local development or Bitbucket pipeline testing, we do not care
        # we want the name of the logger to be 'logos-logging', because it is not being sent to Cloud
        # and we want to be able to test it as a real thing. On the other hand, if we are in production or
        # cloud development, we need to be logging the logs into Cloud, therefore these two environments need
        # to be separated, so that the logs do not clash.

        if os.environ.get(DEVELOPMENT):
            self.env = DEVELOPMENT
        elif os.environ.get(TESTING):
            self.env = TESTING
        elif os.environ.get(CLOUD_DEVELOPMENT):
            self.env = CLOUD_DEVELOPMENT
        else:
            self.env = PRODUCTION

        if self.env == DEVELOPMENT or self.env == TESTING:
            self.stream_logger = logging.getLogger(name=self.name)
        else:
            if self.env == CLOUD_DEVELOPMENT and self.name == "logos-logging":
                self.name = "logos-logging-development"

            self.cloud_client = LoggerClient()
            self.cloud_logger = self.cloud_client.logger(name=self.name)

    def get_name(self):
        return self.name

    def log(
        self, message, severity, results=None, version="1.0", issues=None, log_type=None
    ):
        labels = (
            self.labels
            if log_type is None
            else {"log_type": log_type, **(self.labels or {})}
        )
        if self.env == DEVELOPMENT or self.env == TESTING:
            self.stream_logger.log(
                msg={
                    "message": message,
                    "settings": self.settings,
                    "accesses": self.accesses,
                    "result": results,
                    "issues": issues,
                    "result_version": version,
                },
                level=severity,
                extra={
                    "json_fields": {
                        "logging.googleapis.com/trace": self.trace,
                        "logging.googleapis.com/labels": labels,
                    }
                },
            )
        else:
            self.cloud_logger.log_struct(
                info={
                    "message": message,
                    "settings": self.settings,
                    "accesses": self.accesses,
                    "result": results,
                    "issues": issues,
                    "result_version": version,
                },
                labels=labels,
                severity=logging.getLevelName(severity),
                trace=self.trace,
            )
