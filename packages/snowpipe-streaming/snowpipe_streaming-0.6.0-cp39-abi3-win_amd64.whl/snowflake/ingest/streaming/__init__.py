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

from snowflake.ingest.streaming._version import __version__

try:
    from snowflake.ingest.streaming._python_ffi import bootstrap

    # Automatically initialize the SDK when this module is imported
    bootstrap(__version__)
except Exception as e:
    raise RuntimeError(
        "Failed to initialize snowflake.ingest.streaming: {}".format(e)
    ) from e


from snowflake.ingest.streaming.channel_status import ChannelStatus
from snowflake.ingest.streaming.streaming_ingest_channel import StreamingIngestChannel
from snowflake.ingest.streaming.streaming_ingest_client import StreamingIngestClient
from snowflake.ingest.streaming.streaming_ingest_error import (
    StreamingIngestError,
    StreamingIngestErrorCode,
)

__all__ = [
    "__version__",
    "StreamingIngestClient",
    "StreamingIngestChannel",
    "ChannelStatus",
    "StreamingIngestError",
    "StreamingIngestErrorCode",
]
