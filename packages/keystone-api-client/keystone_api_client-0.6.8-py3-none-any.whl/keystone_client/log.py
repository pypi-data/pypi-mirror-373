"""Components for integrating with the standard Python logging system.

The `log` module defines extensions to Python’s logging framework that
extend log records with application-specific context. These components
are initialized automatically with the package and are not intended
for direct import.
"""

import logging


class DefaultContextAdapter(logging.LoggerAdapter):
    """Logging adapter used to inject default context values into a logger instance."""

    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        """Merge default values into context values passed directly into log calls."""

        kwargs["extra"] = {**self.extra, **kwargs.get("extra", {})}
        return msg, kwargs


class ContextFilter(logging.Filter):
    """Logging filter used to ensure standard application values exist for all log records.

    Attributes enforced by this filter:
        - cid
        - baseurl
        - method
        - endpoint
        - url
    """

    required_attr = ("cid", "baseurl", "method", "endpoint", "url")

    def filter(self, record: logging.LogRecord) -> True:
        """Ensure a log record has all required contextual attributes.

        Any missing contextual attributes are set to an empty string.

        Args:
            record: The log record to process.

        Returns:
           Always returns `True`.
        """

        for attr in self.required_attr:
            if not hasattr(record, attr):
                setattr(record, attr, "")

        # Return `True` to indicate the record should be logged
        return True
