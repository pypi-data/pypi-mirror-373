"""
This module defines a custom logging handler that uploads log messages to a MinIO
bucket.
"""

import logging
import io

from anhaltai.gbif_downloader.config import LOG_PATH
from anhaltai.gbif_downloader.utils import upload_with_retry


class MinioLogHandler(logging.Handler):
    """
    Custom logging handler that uploads log messages to a MinIO bucket.
    This handler buffers log messages and uploads them to a specified object in a
    MinIO bucket. It uses a semaphore to limit the number of concurrent uploads.
    The log messages are formatted as plain text and encoded in UTF-8 before being
    uploaded.
    """

    def __init__(self):
        super().__init__()
        self.object_name = LOG_PATH
        self.log_buffer = ""

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record by formatting it and uploading it to the MinIO bucket.
        Args:
            record: The log record to be emitted.
        """
        log_entry = self.format(record)
        self.log_buffer += log_entry + "\n"

        try:
            log_bytes = self.log_buffer.encode("utf-8")
            upload_with_retry(
                object_name=self.object_name,
                data_bytes=io.BytesIO(log_bytes),
                data_length=len(log_bytes),
                content_type="text/plain",
            )
        except OSError as e:
            logging.error("Error when writing MinIO-Log: %s", e)
