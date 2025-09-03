#  Copyright © 2025 Bentley Systems, Incorporated
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import unittest
from datetime import datetime, time, timezone
from typing import TypeVar


def utc_datetime(
    year: int, month: int = 1, day: int = 1, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0
) -> datetime:
    """Create a datetime object in UTC time."""
    return datetime(year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc)


def utc_time(hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0) -> time:
    """Create a time object in UTC time."""
    return time(hour, minute, second, microsecond, tzinfo=timezone.utc)


_FT = TypeVar("_FT")


def long_test(test: _FT) -> _FT:
    """Decorator to mark a test as long-running.

    This decorator should be used to mark tests that take a long time to run, or that require a lot of resources. The
    decorator will cause the test to be skipped by default, and will be run only if the `CI` environment variable is
    set (as is the case in GitHub workflows).
    """
    return unittest.skipUnless("CI" in os.environ, "Make local testing faster")(test)
