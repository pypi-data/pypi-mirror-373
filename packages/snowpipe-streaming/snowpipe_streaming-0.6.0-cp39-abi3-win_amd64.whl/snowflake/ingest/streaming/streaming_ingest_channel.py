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

"""Streaming ingest channel for appending data into Snowflake tables."""

from __future__ import annotations

import time
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional

import msgspec

from snowflake.ingest.streaming._python_ffi import (
    PyChannel as _StreamingIngestChannel,
)
from snowflake.ingest.streaming._utils import (
    _rethrow_ffi_errors,
)
from snowflake.ingest.streaming.channel_status import ChannelStatus
from snowflake.ingest.streaming.streaming_ingest_error import (
    StreamingIngestError,
    StreamingIngestErrorCode,
)

WAIT_FOR_COMMIT_CHECK_INTERVAL_SECONDS = 1


class StreamingIngestChannel:
    """A channel for streaming data ingestion into Snowflake using the Snowflake Ingest SDK.

    The channel is used to ingest data into Snowflake tables in a streaming fashion. Each channel
    is associated with a specific account/database/schema/pipe combination and is created by calling
    StreamingIngestClient.open_channel() and closed by calling StreamingIngestChannel.close().

    The channel provides methods for appending single rows or batches of rows into Snowflake,
    with support for offset tokens to track ingestion progress and enable replay capabilities
    in case of failures.

    Note:
        This class should not be instantiated directly. Use StreamingIngestClient.open_channel()
        to create channel instances.

    """

    @_rethrow_ffi_errors
    def __init__(self, channel: _StreamingIngestChannel, *, _internal: bool = False):
        """Initialize a StreamingIngestChannel instance.

        This constructor creates a Python wrapper around the underlying Rust StreamingIngestChannel
        implementation, providing a convenient Python interface for streaming data ingestion
        operations into Snowflake.

        Args:
            channel: The underlying Rust StreamingIngestChannel instance that handles the
                actual streaming ingest operations
            _internal: Internal parameter used to prevent direct instantiation of this class.
                This parameter must be set to True when creating instances internally.

        Note:
            This class should not be instantiated directly by users. Instead, use
            StreamingIngestClient.open_channel() to create channel instances, which will
            handle the proper initialization and setup of the streaming ingest channel.

        Raises:
            ValueError: If instantiated directly without the _internal parameter set to True,
                indicating improper direct instantiation

        """
        if not _internal:
            raise ValueError(
                "StreamingIngestChannel cannot be instantiated directly. "
                "Use StreamingIngestClient.open_channel() instead."
            )
        self._channel = channel
        self._serializer = msgspec.json.Encoder()

    @_rethrow_ffi_errors
    def __del__(self) -> None:
        """Delete the channel."""
        if self._channel is not None:
            self.close()

    @_rethrow_ffi_errors
    def initiate_flush(self) -> None:
        """Initiate a flush of the channel.

        Initiates a flush of all buffered data maintained for this Channel but does not wait for the
        flush to complete. Calls to append_rows are still allowed on the Channel after invoking this
        API.

        This method triggers an immediate flush of all currently buffered data in this specific
        channel, similar to the client-level :meth:`~snowflake.ingest.streaming.streaming_ingest_client.StreamingIngestClient.initiate_flush`
        but scoped to only this channel. The flush operation will occur asynchronously and this method
        returns immediately.

        This method is useful when you want to force immediate transmission
        of buffered data without waiting for automatic flush triggers (time-based or size-based). It
        provides fine-grained control over when data gets sent to Snowflake on a per-channel basis.
        However, calling initiate_flush at a high rate will lead to a drop in overall throughput,
        potential increase in costs, and could lead to higher incidence of throttling by the Snowflake
        Service.

        Raises:
            StreamingIngestError: If initiating the flush fails
        """
        self._channel.initiate_flush()

    @_rethrow_ffi_errors
    def wait_for_flush(self, timeout_seconds: Optional[int] = None) -> None:
        """Wait for the channel to flush all buffered data.

        Waits for all buffered data in this channel to be flushed to the Snowflake server side.
        This method triggers a flush of all pending data and waits for the flush operation to complete.
        If the timeout is reached, a TimeoutError is raised.

        Args:
            timeout_seconds: Optional timeout in seconds for the flush operation. Defaults to None if no timeout is desired.

        Raises:
            ValueError: If timeout_seconds is negative
            TimeoutError: If the timeout is reached
            StreamingIngestError: If waiting for the flush fails
        """
        if timeout_seconds is not None and timeout_seconds < 0:
            raise ValueError("timeout_seconds cannot be negative")

        self._channel.wait_for_flush(timeout_seconds)

    def wait_for_commit(
        self,
        token_checker: Callable[[str], bool],
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """Wait for the channel to commit all buffered data.

        Waits for offset token to be committed in the snowflake sever side by checking
        whether the latest committed offset token meets the commit condition provided by the
        token_checker. Note that snowflake commits offset token in batch, so the token_checker should be
        able to handle the case where the latest committed offset token passed the expected ones. That
        said, the token_checker usually does a range check whether the provided token is greater or
        equal to the expected one, not a exact match.

        Args:
            token_checker: A callable that tests whether the current committed offset token from the
                server meets the desired condition. The callable receives the latest committed offset
                token (which may be None) and should return True when the wait condition is satisfied.
            timeout_seconds: Optional timeout in seconds for the commit operation. Defaults to None if no timeout is desired.

        Raises:
            ValueError: If token_checker is not callable or timeout_seconds is negative
            StreamingIngestError: If waiting for the commit fails
            TimeoutError: If the timeout is reached
        """
        if timeout_seconds is not None and timeout_seconds < 0:
            raise ValueError("timeout_seconds cannot be negative")

        if not callable(token_checker):
            raise ValueError("token_checker must be callable")

        start_time = time.time()
        while timeout_seconds is None or time.time() - start_time < timeout_seconds:
            status = self.get_channel_status()
            if token_checker(status.latest_committed_offset_token):
                return
            if status.status_code != "SUCCESS":
                raise StreamingIngestError(
                    StreamingIngestErrorCode.INVALID_CHANNEL_ERROR,
                    "Channel is invalid in the remote with status: "
                    + status.status_code,
                    HTTPStatus.CONFLICT.value,
                    HTTPStatus.CONFLICT.name,
                )

            time.sleep(WAIT_FOR_COMMIT_CHECK_INTERVAL_SECONDS)

        raise TimeoutError("Wait for commit timed out")

    def append_row(
        self,
        row: Dict[str, Any],
        offset_token: Optional[str] = None,
    ) -> None:
        """Append a single row into the channel.

        Args:
            row: Dictionary representing the row data to append with keys as column names and values as column values. Values can be of the following types:
                - None: null values
                - bool: boolean values (True, False)
                - int: integer values
                - float: floating-point values
                - str: string values
                - bytes: byte strings
                - bytearray: mutable byte arrays
                - tuple: tuples of values
                - list: lists of values
                - dict: nested dictionaries
                - set: sets of values
                - frozenset: immutable sets of values
                - datetime.datetime: datetime objects
                - datetime.date: date objects
                - datetime.time: time objects
                - decimal.Decimal: decimal values for precise numeric operations
            offset_token: Optional offset token, used to track the ingestion progress and replay
                ingestion in case of failures. It could be null if user don't plan on replaying or
                can't replay.

        Raises:
            ValueError, TypeError: If the row cannot be serialized to JSON
            StreamingIngestError: If the row appending fails

        """
        self.append_rows([row], offset_token, offset_token)

    @_rethrow_ffi_errors
    def append_rows(
        self,
        rows: List[Dict[str, Any]],
        start_offset_token: Optional[str] = None,
        end_offset_token: Optional[str] = None,
    ) -> None:
        """Append multiple rows into the channel.

        Args:
            rows: List of dictionaries representing the row data to append. Each dictionary's values can be of the following types:
                - None: null values
                - bool: boolean values (True, False)
                - int: integer values
                - float: floating-point values
                - str: string values
                - bytes: byte strings
                - bytearray: mutable byte arrays
                - tuple: tuples of values
                - list: lists of values
                - dict: nested dictionaries
                - set: sets of values
                - frozenset: immutable sets of values
                - datetime.datetime: datetime objects
                - datetime.date: date objects
                - datetime.time: time objects
                - decimal.Decimal: decimal values for precise numeric operations
            start_offset_token: Optional start offset token of the batch/row-set.
            end_offset_token: Optional end offset token of the batch/row-set.

        Raises:
            ValueError, TypeError: If the rows cannot be serialized to JSON
            StreamingIngestError: If the rows appending fails

        """
        try:
            json_bytes = self._serializer.encode_lines(rows)
        except Exception as e:
            raise ValueError(f"Failed to serialize rows to JSON: {e}") from e

        self._channel.append_rows(
            json_bytes, len(rows), start_offset_token, end_offset_token
        )

    @_rethrow_ffi_errors
    def get_latest_committed_offset_token(self) -> Optional[str]:
        """Get the latest committed offset token for the channel.

        Returns:
            Optional[str]: The latest committed offset token for the channel, or None if the channel is brand new.

        Raises:
            StreamingIngestError: If getting the latest committed offset token fails
        """
        return self.get_channel_status().latest_committed_offset_token

    @_rethrow_ffi_errors
    def get_channel_status(self) -> ChannelStatus:
        """Get the status of the channel.

        Returns:
            ChannelStatus: The status of the channel.

        Raises:
            StreamingIngestError: If getting the channel status fails
        """
        status = self._channel.get_channel_status()
        return ChannelStatus(
            database_name=status.database_name,
            schema_name=status.schema_name,
            pipe_name=status.pipe_name,
            channel_name=status.channel_name,
            status_code=status.status_code,
            latest_committed_offset_token=status.latest_committed_offset_token,
            created_on_ms=status.created_on_ms,
            rows_inserted=status.rows_inserted,
            rows_parsed=status.rows_parsed,
            rows_error_count=status.rows_error_count,
            last_error_offset_upper_bound=status.last_error_offset_upper_bound,
            last_error_message=status.last_error_message,
            last_error_timestamp_ms=status.last_error_timestamp_ms,
            snowflake_avg_processing_latency_ms=status.snowflake_avg_processing_latency_ms,
            last_refreshed_on_ms=status.last_refreshed_on_ms,
        )

    @_rethrow_ffi_errors
    def close(
        self,
        drop: bool = False,
        wait_for_flush: bool = True,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """Close the channel.

        Args:
            drop: Whether to drop the channel, defaults to False
            wait_for_flush: Whether to wait for the flush to complete. Default is True.
            timeout_seconds: The timeout in seconds for the flush, None means no timeout. Default is None.

        Raises:
            ValueError: If timeout_seconds is negative
            StreamingIngestError: If closing the channel fails
        """
        if timeout_seconds is not None and timeout_seconds < 0:
            raise ValueError("timeout_seconds cannot be negative")

        self._channel.close(drop, wait_for_flush, timeout_seconds)

    def is_closed(self) -> bool:
        """Check if the channel is closed.

        Returns:
            bool: True if the channel is closed, False otherwise
        """
        return self._channel.is_closed()

    @property
    def db_name(self) -> str:
        """Get the database name."""
        return self._channel.db_name

    @property
    def channel_name(self) -> str:
        """Get the channel name."""
        return self._channel.channel_name

    @property
    def schema_name(self) -> str:
        """Get the schema name."""
        return self._channel.schema_name

    @property
    def pipe_name(self) -> str:
        """Get the pipe name."""
        return self._channel.pipe_name

    def __enter__(self) -> StreamingIngestChannel:
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Exit the context manager."""
        self.close()
        return False
