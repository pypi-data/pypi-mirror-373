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

"""Custom BenchMatcha exception definitions.

Considerations:
    * All custom exceptions should be defined within this module for better project
      organization. This also prevents proliferation of custom errors as project scales.
    * Custom exceptions should define a class method named `response` to construct and
      standardize verbiage of output message. It has the nice side effect of providing
      example context for usage.
    * Before creating a custom error, determine if available exceptions can be used
      instead.

"""

from __future__ import annotations

from json import JSONDecodeError
from typing import Self, TypeVar


E = TypeVar("E", bound=Exception)

_exception_register: set[type[Exception]] = {
    TypeError,
    ValueError,
    RuntimeError,
    JSONDecodeError,
    FileNotFoundError,
}


def register_custom_exception(cls: type[E]) -> type[E]:
    """Register custom exceptions."""
    _exception_register.add(cls)

    return cls


@register_custom_exception
class SchemaError(Exception):
    """Unsupported json schema."""

    @classmethod
    def response(cls, version: str) -> Self:
        """Define standard response message."""
        msg: str = f"Unsupported json schema version: {version}"

        return cls(msg)


@register_custom_exception
class ParsingError(Exception):
    """Failed to parse json output (from Google Benchmark)."""

    @classmethod
    def response(cls) -> Self:
        """Define standard response message."""
        return cls(
            "Failed to parse json data. Please confirm benchmarks do not contain "
            "print statements or write to stdout, which can interfere with output."
        )
