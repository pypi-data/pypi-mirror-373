# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Streaming ingest error for handling errors that are specific to the streaming ingest client."""

from __future__ import annotations

from enum import Enum
from typing import Optional


class StreamingIngestErrorCode(Enum):
    """Enumeration of all possible streaming ingest error codes.

    These error codes correspond to the IngestError variants in the Rust implementation
    and provide type-safe error handling.
    """

    # 400 Bad Request
    CONFIG_ERROR = "ConfigError"
    INVALID_REQUEST = "InvalidRequest"
    INVALID_ARGUMENT = "InvalidArgument"
    SF_API_USER_ERROR = "SfApiUserError"
    NOT_IMPLEMENTED = "NotImplemented"
    HTTP_CLIENT_NON_RETRYABLE_ERROR = "HttpClientNonRetryableError"
    SF_API_PIPE_FAILED_OVER_ERROR = "SfApiPipeFailedOverError"
    CHANNEL_ALREADY_EXISTS = "ChannelAlreadyExists"

    # 401 Unauthorized
    AUTH_TOKEN_ERROR = "AuthTokenError"
    SF_API_AUTH_ERROR = "SfApiAuthError"

    # 404 Not Found
    CHANNEL_NOT_FOUND = "ChannelNotFound"

    # 408 Request Timeout
    CHANNEL_WAIT_FOR_FLUSH_TIMEOUT = "ChannelWaitForFlushTimeout"
    CLIENT_WAIT_FOR_FLUSH_TIMEOUT = "ClientWaitForFlushTimeout"

    # 409 Conflict
    CLOSED_CHANNEL_ERROR = "ClosedChannelError"
    CLOSED_CLIENT_ERROR = "ClosedClientError"
    CHANNEL_CLOSED_BY_USER = "ChannelClosedByUser"
    INVALID_CHANNEL_ERROR = "InvalidChannelError"
    INVALID_CLIENT_ERROR = "InvalidClientError"
    INPUT_CHANNEL_CLOSED = "InputChannelClosed"
    OUTPUT_CHANNEL_CLOSED = "OutputChannelClosed"

    # 429 Too Many Requests
    RECEIVER_SATURATED = "ReceiverSaturated"
    MEMORY_THRESHOLD_EXCEEDED = "MemoryThresholdExceeded"
    MEMORY_THRESHOLD_EXCEEDED_IN_CONTAINER = "MemoryThresholdExceededInContainer"

    # 500 Internal Server Error
    FATAL = "Fatal"
    NON_FATAL = "NonFatal"
    MUTEX_LOCK_FAILED = "MutexLockFailed"
    SF_API_UNEXPECTED_BEHAVIOR_ERROR = "SfApiUnexpectedBehaviorError"
    SF_API_INTERNAL_SERVER_ERROR = "SfApiInternalServerError"
    FILE_UPLOAD_ERROR = "FileUploadError"
    HTTP_RETRIES_EXHAUSTED_ERROR = "HttpRetriesExhaustedError"
    CLOSE_ALL_CHANNELS_FAILED_ERROR = "CloseAllChannelsFailedError"

    # 503 Service Unavailable
    HTTP_RETRYABLE_CLIENT_ERROR = "HttpRetryableClientError"

    @classmethod
    def from_string(cls, error_code_str: str) -> Optional["StreamingIngestErrorCode"]:
        """Convert a string error code to enum value if it exists.

        Args:
            error_code_str: The error code string to convert

        Raises:
            ValueError: If the error code string is invalid

        Returns:
            The matching StreamingIngestErrorCode enum value, or None if not found
        """
        try:
            return cls(error_code_str)
        except ValueError as e:
            raise ValueError(f"Invalid error code: {error_code_str}") from e


class StreamingIngestError(Exception):
    """A class for all streaming ingest errors."""

    def __init__(
        self,
        error_code: StreamingIngestErrorCode,
        message: str,
        http_status_code: int,
        http_status_name: str,
    ):
        """Initialize the StreamingIngestError.

        Args:
            error_code: The error code of the error
            message: The message of the error
            http_status_code: The HTTP status code of the error
            http_status_name: The HTTP status name of the error
        """
        super().__init__(message)
        self._error_code = error_code
        self._message = message
        self._http_status_code = http_status_code
        self._http_status_name = http_status_name

    @property
    def error_code(self) -> StreamingIngestErrorCode:
        """The error code of the error."""
        return self._error_code

    @property
    def message(self) -> str:
        """The message of the error."""
        return self._message

    @property
    def http_status_code(self) -> int:
        """The HTTP status code of the error."""
        return self._http_status_code

    @property
    def http_status_name(self) -> str:
        """The HTTP status name of the error."""
        return self._http_status_name

    def __str__(self) -> str:
        """Return the string representation of the StreamingIngestError."""
        return f"{self.error_code.value}: {self.message} (HTTP {self.http_status_code} {self.http_status_name})"

    def __repr__(self) -> str:
        """Return the string representation of the StreamingIngestError."""
        return f"{self.__class__.__name__}(error_code={self.error_code!r}, message={self.message!r}, http_status_code={self.http_status_code!r}, http_status_name={self.http_status_name!r})"

    def __eq__(self, other: object) -> bool:
        """Check if the StreamingIngestError is equal to another object."""
        if not isinstance(other, StreamingIngestError):
            return False
        return (
            self.error_code == other.error_code
            and self.message == other.message
            and self.http_status_code == other.http_status_code
            and self.http_status_name == other.http_status_name
        )
