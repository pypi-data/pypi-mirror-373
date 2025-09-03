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

from collections.abc import Iterator, Sequence
from threading import Lock
from typing import TypeVar

from ..interfaces import IFeedback

__all__ = [
    "NoFeedback",
    "PartialFeedback",
    "iter_with_fb",
]

_N_DIGITS = 4  # Let's maintain a user-friendly number of dp.


class _NoFeedback(IFeedback):
    def progress(self, progress: float, message: str | None = None) -> None:
        pass


NoFeedback = _NoFeedback()
"""A default feedback object that does nothing. Use this when no feedback is needed."""


class PartialFeedback(IFeedback):
    """A wrapper for IFeedback objects that subdivides the feedback range."""

    def __init__(self, parent: IFeedback, start: float, end: float) -> None:
        """
        :param parent: The parent feedback object to subdivide.
        :param start: The start of the partial feedback range.
        :param end: The end of the partial feedback range.
        """
        self.__offset = start
        self.__factor = end - start

        self.__lock = Lock()
        self.__parent = parent

    def progress(self, progress: float, message: str | None = None) -> None:
        """Update the progress of the feedback object.

        :param progress: The progress value, between 0 and 1.
        :param message: An optional message to display.
        """
        partial_progress = round(self.__offset + (progress * self.__factor), ndigits=_N_DIGITS)
        with self.__lock:
            self.__parent.progress(partial_progress, message)


T = TypeVar("T")


def iter_with_fb(elements: Sequence[T], feedback: IFeedback | None = None) -> Iterator[tuple[T, IFeedback]]:
    """Iterate over a sequence of elements, dividing feedback uniformly throughout the range.

    :param elements: The sequence of elements to iterate over.
    :param feedback: A feedback object to subdivide.

    :yields: A tuple containing a sequence element, and a new feedback object for that element.
    """
    if len(elements) == 0:
        return

    fb_part_size = 1 / len(elements)
    for i, element in enumerate(elements):
        if feedback is None:
            yield element, NoFeedback
        else:
            start = round(i * fb_part_size, ndigits=_N_DIGITS)
            end = round((i + 1) * fb_part_size, ndigits=_N_DIGITS)
            yield element, PartialFeedback(feedback, start, end)
            feedback.progress(end)
