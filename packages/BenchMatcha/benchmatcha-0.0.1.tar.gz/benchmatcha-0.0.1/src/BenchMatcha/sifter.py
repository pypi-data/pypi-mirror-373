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

"""Discovery of benchmark tests to register."""

import glob
import os
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

from _pytest.pathlib import import_path


def scandir(filepath: str) -> Iterator[os.DirEntry[str]]:
    """Simple wrapper around os.scandir to use more simply as an iterator."""
    with os.scandir(os.path.abspath(filepath)) as scanner:
        yield from scanner


class Collector:
    """Collection interface."""

    root: str
    pattern: str

    def __init__(self, root: str, pattern: str = "bench*.py") -> None:
        self.root = root
        self.pattern = pattern

    def get(self, path: str) -> Iterator[str]:
        """Get paths of a given pattern."""
        yield from glob.iglob(path, root_dir=self.root)

    def collect(self, path: str) -> Iterator[str]:
        """Recursive collection of pattern matching filepaths."""
        yield from self.get(os.path.join(path, self.pattern))
        for candidate in scandir(path):
            if candidate.is_dir(follow_symlinks=False):
                yield from self.collect(candidate.path)


def collect(root: str, pattern: str = "bench*.py") -> Iterator[str]:
    """Collect relevant filepaths recursively stemming from root directory."""
    col = Collector(root, pattern)

    yield from col.collect(root)


def load_benchmark(path: str, root: str) -> ModuleType:
    """Load a benchmark suite."""
    return import_path(
        os.path.abspath(path),
        root=Path(root).absolute().resolve(),
        consider_namespace_packages=False,
    )


def collect_benchmarks(root: str) -> None:
    """Collect all benchmarks from a variety of benchmark suites."""
    root = os.path.abspath(root)
    for j in collect(root):
        load_benchmark(j, root=root)
