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

"""Internal utilities for the streaming ingest package."""

import json
from functools import wraps

from snowflake.ingest.streaming.streaming_ingest_error import (
    StreamingIngestError,
    StreamingIngestErrorCode,
)


def _copy_exception_context(new_error: Exception, original_error: Exception) -> None:
    """Copy relevant context from original exception to new exception.

    This preserves important debugging information while allowing for clean
    exception replacement.

    Args:
        new_error: The new exception to copy context to
        original_error: The original exception to copy context from
    """
    if (
        hasattr(original_error, "__traceback__")
        and original_error.__traceback__ is not None
    ):
        new_error.__traceback__ = original_error.__traceback__

    if hasattr(original_error, "__cause__") and original_error.__cause__ is not None:
        new_error.__cause__ = original_error.__cause__

    if (
        hasattr(original_error, "__context__")
        and original_error.__context__ is not None
    ):
        new_error.__context__ = original_error.__context__


def _rethrow_ffi_errors(func):
    """Decorator to catch RuntimeError from FFI calls and rethrow as StreamingIngestError or TimeoutError.

    This decorator handles the conversion of RuntimeError exceptions (typically
    from Rust FFI calls) into StreamingIngestError or TimeoutError exceptions with proper
    error categorization and messaging, while preserving the original error location
    and context by copying relevant exception attributes.

    The RuntimeError message from the Rust FFI is expected to be in JSON format:
    {"error_code": "ErrorType", "message": "Error description", "http_status_code": status_code, "http_status_name": status_name}

    Args:
        func: The function to wrap with FFI error handling

    Returns:
        The wrapped function that converts FFI RuntimeError to StreamingIngestError or TimeoutError
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            try:
                error_data = json.loads(str(e))
                error_code = error_data.get("error_code", "Unknown")
                message = error_data.get("message", str(e))
                http_status_code = error_data.get("http_status_code", 0)
                http_status_name = error_data.get("http_status_name", "Unknown")

                # Convert string to enum, fallback to FATAL for unknown error codes
                try:
                    error_code_enum = StreamingIngestErrorCode.from_string(error_code)
                except ValueError:
                    # Unknown error code from Rust, fallback to FATAL and include original in message
                    error_code_enum = StreamingIngestErrorCode.FATAL
                    message = f"Unknown error code '{error_code}': {message}"

                if (
                    error_code_enum
                    == StreamingIngestErrorCode.CLIENT_WAIT_FOR_FLUSH_TIMEOUT
                    or error_code_enum
                    == StreamingIngestErrorCode.CHANNEL_WAIT_FOR_FLUSH_TIMEOUT
                ):
                    raise TimeoutError(message) from e

                new_error = StreamingIngestError(
                    error_code_enum, message, http_status_code, http_status_name
                )
                _copy_exception_context(new_error, e)
                raise new_error from None
            except (json.JSONDecodeError, KeyError):
                # Fallback: re-raise original error if JSON parsing fails
                raise e

    return wrapper
