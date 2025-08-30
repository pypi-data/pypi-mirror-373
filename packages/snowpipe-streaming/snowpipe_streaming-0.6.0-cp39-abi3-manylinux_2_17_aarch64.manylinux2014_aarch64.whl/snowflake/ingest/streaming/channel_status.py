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

"""Channel status information returned to users."""

from __future__ import annotations

from typing import Optional


class ChannelStatus:
    """Channel status information returned to users.

    Provides access to channel status information including the channel name,
    status code, and latest committed offset token from Snowflake server.

    """

    def __init__(
        self,
        database_name: str,
        schema_name: str,
        pipe_name: str,
        channel_name: str,
        status_code: str,
        latest_committed_offset_token: Optional[str],
        created_on_ms: int,
        rows_inserted: int,
        rows_parsed: int,
        rows_error_count: int,
        last_error_offset_upper_bound: Optional[str],
        last_error_message: Optional[str],
        last_error_timestamp_ms: Optional[int],
        snowflake_avg_processing_latency_ms: Optional[int],
        last_refreshed_on_ms: int,
    ):
        """Initialize ChannelStatus.

        Args:
            database_name: The database name of the channel
            schema_name: The schema name of the channel
            pipe_name: The pipe name of the channel
            channel_name: The name of the channel
            status_code: The status code for the channel from Snowflake server
            latest_committed_offset_token: The latest committed offset token for the channel
            created_on_ms: The created on timestamp in ms for the channel
            rows_inserted: The rows inserted for the channel
            rows_parsed: The rows parsed for the channel
            rows_error_count: The rows error count for the channel
            last_error_offset_upper_bound: The last error offset upper bound for the channel
            last_error_message: The last error message for the channel
            last_error_timestamp_ms: The last error timestamp in ms for the channel
            snowflake_avg_processing_latency_ms: The snowflake avg processing latency in ms for the
                channel to ingest data in the snowflake server side
            last_refreshed_on_ms: The last refreshed on timestamp in ms for the channel
        """
        self._database_name = database_name
        self._schema_name = schema_name
        self._pipe_name = pipe_name
        self._channel_name = channel_name
        self._status_code = status_code
        self._latest_committed_offset_token = latest_committed_offset_token
        self._created_on_ms = created_on_ms
        self._rows_inserted = rows_inserted
        self._rows_parsed = rows_parsed
        self._rows_error_count = rows_error_count
        self._last_error_offset_upper_bound = last_error_offset_upper_bound
        self._last_error_message = last_error_message
        self._last_error_timestamp_ms = last_error_timestamp_ms
        self._snowflake_avg_processing_latency_ms = snowflake_avg_processing_latency_ms
        self._last_refreshed_on_ms = last_refreshed_on_ms

    @property
    def database_name(self) -> str:
        """Get the database name."""
        return self._database_name

    @database_name.setter
    def database_name(self, value: str) -> None:
        """Set the database name."""
        self._database_name = value

    @property
    def schema_name(self) -> str:
        """Get the schema name."""
        return self._schema_name

    @schema_name.setter
    def schema_name(self, value: str) -> None:
        """Set the schema name."""
        self._schema_name = value

    @property
    def pipe_name(self) -> str:
        """Get the pipe name."""
        return self._pipe_name

    @pipe_name.setter
    def pipe_name(self, value: str) -> None:
        """Set the pipe name."""
        self._pipe_name = value

    @property
    def channel_name(self) -> str:
        """Get the channel name.

        Returns:
            str: The name of the channel
        """
        return self._channel_name

    @channel_name.setter
    def channel_name(self, value: str) -> None:
        """Set the channel name.

        Args:
            value: The new channel name
        """
        self._channel_name = value

    @property
    def status_code(self) -> str:
        """Get the status code for the channel.

        Returns:
            str: The status code from Snowflake server
        """
        return self._status_code

    @status_code.setter
    def status_code(self, value: str) -> None:
        """Set the status code for the channel.

        Args:
            value: The new status code
        """
        self._status_code = value

    @property
    def latest_committed_offset_token(self) -> Optional[str]:
        """Get the latest committed offset token for the channel.

        Returns:
            Optional[str]: The latest committed offset token, or None if no commits yet
        """
        return self._latest_committed_offset_token

    @property
    def latest_offset_token(self) -> Optional[str]:
        """Get the latest committed offset token for the channel.

        Deprecated: Use latest_committed_offset_token instead.

        Returns:
            Optional[str]: The latest committed offset token, or None if no commits yet
        """
        return self._latest_committed_offset_token

    @latest_committed_offset_token.setter
    def latest_committed_offset_token(self, value: Optional[str]) -> None:
        """Set the latest committed offset token for the channel.

        Args:
            value: The new offset token, or None
        """
        self._latest_committed_offset_token = value

    @property
    def created_on_ms(self) -> int:
        """Get the created on timestamp in ms for the channel."""
        return self._created_on_ms

    @created_on_ms.setter
    def created_on_ms(self, value: int) -> None:
        """Set the created on timestamp in ms for the channel."""
        self._created_on_ms = value

    @property
    def rows_inserted(self) -> int:
        """Get the rows inserted for the channel."""
        return self._rows_inserted

    @rows_inserted.setter
    def rows_inserted(self, value: int) -> None:
        """Set the rows inserted for the channel."""
        self._rows_inserted = value

    @property
    def rows_parsed(self) -> int:
        """Get the rows parsed for the channel."""
        return self._rows_parsed

    @rows_parsed.setter
    def rows_parsed(self, value: int) -> None:
        """Set the rows parsed for the channel."""
        self._rows_parsed = value

    @property
    def rows_error_count(self) -> int:
        """Get the rows error count for the channel."""
        return self._rows_error_count

    @rows_error_count.setter
    def rows_error_count(self, value: int) -> None:
        """Set the rows error count for the channel."""
        self._rows_error_count = value

    @property
    def last_error_offset_upper_bound(self) -> Optional[str]:
        """Get the last error offset upper bound for the channel."""
        return self._last_error_offset_upper_bound

    @last_error_offset_upper_bound.setter
    def last_error_offset_upper_bound(self, value: Optional[str]) -> None:
        """Set the last error offset upper bound for the channel."""
        self._last_error_offset_upper_bound = value

    @property
    def last_error_message(self) -> Optional[str]:
        """Get the last error message for the channel."""
        return self._last_error_message

    @last_error_message.setter
    def last_error_message(self, value: Optional[str]) -> None:
        """Set the last error message for the channel."""
        self._last_error_message = value

    @property
    def last_error_timestamp_ms(self) -> Optional[int]:
        """Get the last error timestamp in ms for the channel."""
        return self._last_error_timestamp_ms

    @last_error_timestamp_ms.setter
    def last_error_timestamp_ms(self, value: Optional[int]) -> None:
        """Set the last error timestamp in ms for the channel."""
        self._last_error_timestamp_ms = value

    @property
    def snowflake_avg_processing_latency_ms(self) -> Optional[int]:
        """Get the snowflake avg processing latency in the snowflake server side for the channel to ingest data."""
        return self._snowflake_avg_processing_latency_ms

    @snowflake_avg_processing_latency_ms.setter
    def snowflake_avg_processing_latency_ms(self, value: Optional[int]) -> None:
        """Set the snowflake avg processing latency in the snowflake server side for the channel to ingest data."""
        self._snowflake_avg_processing_latency_ms = value

    @property
    def last_refreshed_on_ms(self) -> int:
        """Get the last refreshed on timestamp in ms for the channel.  Channels is periodically refreshed every second in the background."""
        return self._last_refreshed_on_ms

    @last_refreshed_on_ms.setter
    def last_refreshed_on_ms(self, value: int) -> None:
        """Set the last refreshed on timestamp in ms for the channel. Channels is periodically refreshed every second in the background."""
        self._last_refreshed_on_ms = value

    def __repr__(self) -> str:
        """Return string representation of ChannelStatus."""
        return (
            f"ChannelStatus(database_name='{self.database_name}', "
            f"schema_name='{self.schema_name}', "
            f"pipe_name='{self.pipe_name}', "
            f"channel_name='{self.channel_name}', "
            f"status_code='{self.status_code}', "
            f"latest_committed_offset_token={self.latest_committed_offset_token!r}, "
            f"created_on_ms={self.created_on_ms}, "
            f"rows_inserted={self.rows_inserted}, "
            f"rows_parsed={self.rows_parsed}, "
            f"rows_error_count={self.rows_error_count}, "
            f"last_error_offset_upper_bound={self.last_error_offset_upper_bound!r}, "
            f"last_error_message={self.last_error_message!r}, "
            f"last_error_timestamp_ms={self.last_error_timestamp_ms}, "
            f"snowflake_avg_processing_latency_ms={self.snowflake_avg_processing_latency_ms}, "
            f"last_refreshed_on_ms={self.last_refreshed_on_ms})"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"Channel '{self.channel_name}': {self.status_code}"
