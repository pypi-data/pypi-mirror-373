# BSD 3-Clause License
#
# Copyright (c) 2025, Spill-Tea
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Miscellaneous utilities."""

from __future__ import annotations

import enum
import sys

import numpy as np


def power_of_2(x: int) -> int:
    """Retrieve the next power of 2, if value is not already one."""
    x -= 1
    mod: int = 1
    size: int = sys.getsizeof(x)
    while mod < size:
        x |= x >> mod
        mod *= 2

    return x + 1


def _simple_stats(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute mean and standard deviation."""
    mean: np.ndarray = np.nanmean(x, axis=1)
    std: np.ndarray = np.nanstd(x, axis=1, ddof=1)

    return mean, std


# pylint: disable=invalid-name
# https://github.com/google/benchmark/blob/main/src/complexity.cc#L52-L69
class BigO(enum.StrEnum):
    """Big o notation string identifiers."""

    o1 = "(1)"
    oN = "N"
    oNSquared = "N^2"
    oNCubed = "N^3"
    oLogN = "lgN"
    oNLogN = "NlgN"
    oLambda = "f(N)"

    @classmethod
    def get(cls, value: str) -> str:
        """Get value from key string."""
        # e.g. "o1" -> "(1)"
        return cls[value].value

    @classmethod
    def back(cls, value: str) -> str:
        """Get key string from value."""
        # e.g. "(1)" -> "o1"
        return cls(value).name
