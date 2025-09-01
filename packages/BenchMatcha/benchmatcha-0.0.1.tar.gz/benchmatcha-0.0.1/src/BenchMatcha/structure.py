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

"""Data structures defining json output of google benchmark suite."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, Self

import numpy as np

from .errors import SchemaError


BuildType = Literal["release", "debug"]
SUPPORTED_VERSIONS: tuple[int, ...] = (1,)


def parse_datetime(x: str) -> datetime:
    """Parse ISO 8601 datetime string."""
    return datetime.fromisoformat(x).astimezone(UTC)


def _get_function(record: dict[str, str]) -> list[str]:
    return record["name"].split("/")


def get_function_name(record: dict[str, str]) -> str:
    """Retrieve and parse function name."""
    return _get_function(record)[0]


def get_size(record: dict[str, str]) -> int:
    """Get complexity size, n."""
    return int(_get_function(record)[1])


@dataclass
class Cache:
    """System cache information.

    Args:
        type (str): cache type
        level (int):
        size (int): cache size
        num_sharing (int):

    """

    type: str
    level: int
    size: int
    num_sharing: int

    @classmethod
    def from_json(cls, record: dict[str, Any]) -> Self:
        """Convert dictionary object to Cache."""
        return cls(
            type=record["type"],
            level=record["level"],
            size=record["size"],
            num_sharing=record["num_sharing"],
        )

    def to_json(self) -> dict:
        """Convert to json dictionary object."""
        return self.__dict__.copy()


@dataclass
class BenchmarkRecord:
    """Benchmark result record.

    Args:
        function (str): function name or alias
        size (int): Input size
        threads (int): thread id
        iterations (int): number of iterations performed per measurement
        real_time (float): total real time per measurement
        cpu_time (float): total cpu time per measurement
        time_unit (str): unit of time

    """

    function: str
    size: int
    threads: int
    iterations: int
    real_time: float
    cpu_time: float
    time_unit: str

    @classmethod
    def from_json(cls, record: dict[str, Any]) -> Self:
        """Convert dictionary object to BenchmarkRecord."""
        function: str = get_function_name(record)
        size: int = get_size(record)

        return cls(
            function=function,
            size=size,
            threads=record["threads"],
            iterations=record["iterations"],
            real_time=record["real_time"],
            cpu_time=record["cpu_time"],
            time_unit=record["time_unit"],
        )


@dataclass
class ComplexityInfo:
    """Algorithmic time complexity result.

    Args:
        function (str): function name or alias.
        big_o (str): BigO notation.
        real_coefficient (float): real time coefficient.
        cpu_coefficient (float): cpu time coefficient.
        rms (float): root mean square error of fit.

    """

    function: str
    big_o: str
    real_coefficient: float
    cpu_coefficient: float
    rms: float = 0.0

    @classmethod
    def from_json(cls, record: dict[str, Any]) -> Self:
        """Convert dictionary object to ComplexityInfo."""
        function: str = get_function_name(record)

        return cls(
            function=function,
            big_o=record["big_o"],
            real_coefficient=record["real_coefficient"],
            cpu_coefficient=record["cpu_coefficient"],
        )

    def to_json(self) -> dict:
        """Convert to json dictionary object."""
        return self.__dict__.copy()


@dataclass
class BenchmarkArray:
    """Reformatted Benchmark result as an array.

    Args:
        function (str): function name or alias
        unit (str): unit of time
        size (np.ndarray): Input size
        iterations (np.ndarray): number of iterations performed per measurement
        real_time (np.ndarray): total real time per measurement
        cpu_time (np.ndarray): total cpu time per measurement
        complexity (ComplexityInfo): algorithmic time complexity information

    """

    function: str
    unit: str
    size: np.ndarray  # 1D array
    iterations: np.ndarray  # 2D array (n_sizes x repetitions)
    real_time: np.ndarray  # 2D array (n_sizes x repetitions)
    cpu_time: np.ndarray  # 2D array (n_sizes x repetitions)
    complexity: ComplexityInfo

    def to_json(self) -> dict:
        """Convert to json dictionary object."""
        d = self.__dict__.copy()
        d["complexity"] = self.complexity.to_json()

        return d


def get_benchmark_records(
    data: list[dict[str, Any]],
) -> dict[str, list[BenchmarkRecord]]:
    """Group and parse benchmark results."""
    grouped_records = defaultdict(list)
    for record in data:
        if record["run_type"] != "iteration":
            continue
        br = BenchmarkRecord.from_json(record)
        grouped_records[br.function].append(br)

    return grouped_records


def get_complexity_info(data: list[dict[str, Any]]) -> dict[str, ComplexityInfo]:
    """Capture and parse complexity information from benchmarks."""
    complexity_info: dict[str, ComplexityInfo] = {}
    # First pass: grab complexity information
    for record in data:
        if (
            record.get("run_type") != "aggregate"
            or record.get("aggregate_name") != "BigO"
        ):
            continue
        ci = ComplexityInfo.from_json(record)
        complexity_info[ci.function] = ci

    # Second pass: grab rms fit error information
    for record in data:
        if (
            record.get("run_type") != "aggregate"
            or record.get("aggregate_name") != "RMS"
        ):
            continue
        function: str = get_function_name(record)
        if function in complexity_info:
            complexity_info[function].rms = record["rms"]

    return complexity_info


def convert_to_arrays(
    grouped_records: dict[str, list[BenchmarkRecord]],
    complexity_data: dict[str, ComplexityInfo],
) -> list[BenchmarkArray]:
    """Reorganize benchmark data into numpy arrays."""
    grouped_arrays: list[BenchmarkArray] = []

    for function, records in grouped_records.items():
        size_to_times: defaultdict[int, list[tuple[int, float, float]]] = defaultdict(
            list
        )
        for record in records:
            size_to_times[record.size].append(
                (
                    record.iterations,
                    record.real_time,
                    record.cpu_time,
                )
            )

        sorted_sizes: list[int] = sorted(size_to_times)
        iter_arr: list[list[int]] = []
        real_arr: list[list[float]] = []
        cpu_arr: list[list[float]] = []
        container: list[list[int] | list[float]]
        idx: int

        for size in sorted_sizes:
            times: list[tuple[int, float, float]] = size_to_times[size]
            for idx, container in zip(  # type: ignore[assignment]
                range(3), (iter_arr, real_arr, cpu_arr), strict=True
            ):
                container.append([t[idx] for t in times])

        # TODO: validate time unit is consistent. Adjust if assumption not true.
        grouped_arrays.append(
            BenchmarkArray(
                function=function,
                unit=records[0].time_unit,
                size=np.asarray(sorted_sizes, dtype=np.int64),
                iterations=np.asarray(iter_arr, dtype=np.int64),
                real_time=np.asarray(real_arr, dtype=np.float64),
                cpu_time=np.asarray(cpu_arr, dtype=np.float64),
                complexity=complexity_data[function],
            )
        )

    return grouped_arrays


# TODO: Consider how we would capture custom data (Counters).
# TODO: Capture additional information not included in google_benchmark output
#       (e.g. git sha)
@dataclass
class BenchmarkContext:
    """Google benchmark context."""

    # pylint: disable=R0902
    date: datetime
    host_name: str
    executable: str
    num_cpus: int
    mhz_per_cpu: int
    caches: list[Cache]
    cpu_scaling_enabled: bool
    load_avg: list[float]
    library_version: str
    library_build_type: BuildType
    json_schema_version: int
    benchmarks: list[BenchmarkArray]
    aslr_enabled: bool

    @classmethod
    def from_json(cls, record: dict[str, Any]) -> Self:
        """Convert dictionary object to BenchmarkContext."""
        context: dict = record.get("context", {}).copy()
        caches: list[Cache] = [Cache.from_json(i) for i in context.pop("caches", [])]
        date: datetime = parse_datetime(
            context.pop("date", datetime.now(UTC).isoformat())
        )
        benchmarks: list[BenchmarkArray] = convert_to_arrays(
            get_benchmark_records(record["benchmarks"]),
            get_complexity_info(record["benchmarks"]),
        )

        # NOTE: key found on linux machines (remote testing), but not encountered on mac
        aslr = bool(context.pop("aslr_enabled", False))

        return cls(
            **{k: v for k, v in context.items() if k in cls.__annotations__},
            caches=caches,
            date=date,
            benchmarks=benchmarks,
            aslr_enabled=aslr,
        )

    def to_json(self) -> dict:
        """Convert to json dictionary object."""
        data = self.__dict__.copy()
        data["caches"] = [i.to_json() for i in self.caches]
        data["benchmarks"] = [j.to_json() for j in self.benchmarks]

        return data


def parse_version(record: dict[str, Any]) -> BenchmarkContext:
    """Map schema version to correct parsing engine."""
    schema_version = int(record.get("context", {}).get("json_schema_version", -1))
    if schema_version not in SUPPORTED_VERSIONS:
        raise SchemaError.response(str(schema_version))

    match schema_version:
        case 1:
            return BenchmarkContext.from_json(record)
        case _:
            raise SchemaError.response(str(schema_version))
