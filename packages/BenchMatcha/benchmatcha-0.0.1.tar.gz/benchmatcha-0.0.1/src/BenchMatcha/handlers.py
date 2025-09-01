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

"""IO handlers to transform using json library."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from io import IOBase
from typing import IO, Any


def is_readable_io_protocol(obj: object) -> bool:
    """Determine if object implements readable IO interface."""
    methods: set[str] = {
        "read",
        "readable",
        "write",
        # "writeable",  # temporary file handler does not have this method.
        "seek",
        "seekable",
        "tell",
        "close",
        "closed",  # property
        "flush",
    }

    return (
        isinstance(obj, IO | IOBase) or all(map(lambda x: hasattr(obj, x), methods))
    ) and obj.readable()  # type: ignore[attr-defined]


class Handler(ABC):
    """Abstract Handler protocol."""

    @abstractmethod
    def handle(self) -> dict[str, Any]:
        """Handle parsing of object."""
        raise NotImplementedError("Must implement.")


class HandleText(Handler):
    """Handle loading text (string) to json object."""

    text: str

    def __init__(self, text: str):
        self.text = text

    def handle(self) -> dict[str, Any]:
        return json.loads(self.text)


class HandleBytes(Handler):
    """Handle loading bytes to json object."""

    text: bytes
    encoding: str

    def __init__(self, text: bytes, encoding: str = "utf8"):
        self.text = text
        self.encoding = encoding

    def handle(self) -> dict[str, Any]:
        return HandleText(self.text.decode(self.encoding)).handle()


class HandleIO(Handler):
    """Handle loading io data to json object."""

    stream: IOBase
    encoding: str

    def __init__(self, stream: IOBase, encoding: str = "utf8"):
        self.stream = stream
        if not self.stream.readable():
            raise TypeError("Unreadable stream.")

        self.encoding = encoding

    def handle(self) -> dict[str, Any]:
        text = self.stream.read()
        if isinstance(text, bytes):
            handler: Handler = HandleBytes(text, self.encoding)

        else:
            handler = HandleText(text)

        return handler.handle()


class HandlePath(Handler):
    """Handle loading data from file to json object."""

    path: str
    encoding: str

    def __init__(self, path: str, encoding: str = "utf8"):
        self.path = path
        self.encoding = encoding

    def handle(self) -> dict[str, Any]:
        if not os.path.exists(self.path):
            return HandleText(self.path).handle()

        with open(self.path, "r", encoding=self.encoding) as f:
            return HandleIO(f).handle()


def dispatch(obj: object, encoding: str = "utf8") -> Handler:
    """Dispatch appropriate handler in response to input object type."""
    if isinstance(obj, str):
        return HandlePath(obj)

    elif isinstance(obj, bytes):
        return HandleBytes(obj, encoding)

    elif is_readable_io_protocol(obj):
        return HandleIO(obj, encoding)  # type: ignore[arg-type]

    raise TypeError(f"Unsupported object type: {type(obj)}")


def load(obj: object, encoding: str = "utf8") -> dict[str, Any]:
    """Load json data."""
    return dispatch(obj, encoding).handle()
