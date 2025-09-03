"""A Python client for interacting with the Keystone API."""

import logging.config

from .client import AsyncKeystoneClient, KeystoneClient
from .http import AsyncHTTPClient, HTTPClient

# Configure application logging
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "kclient_filter": {
            "()": "keystone_client.log.ContextFilter",
        }
    },
    "loggers": {
        "kclient": {
            "level": "DEBUG",
            "propagate": False,
            "filters": ["kclient_filter"],
        }
    },
})
