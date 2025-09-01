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

"""Primary Benchmark Runner."""

import argparse
import logging
import os
import sys
from json import JSONDecodeError

import google_benchmark as gbench
import orjson
import plotly.graph_objs as go  # type: ignore[import-untyped]
from wurlitzer import pipes  # type: ignore[import-untyped]

from . import plotting

# from .complexity import analyze_complexity
from .config import Config, update_config_from_pyproject
from .errors import ParsingError
from .handlers import HandleText
from .sifter import collect_benchmarks, load_benchmark
from .structure import BenchmarkArray, BenchmarkContext, parse_version


log: logging.Logger = logging.getLogger(__name__)


def manage_registration(path: str) -> None:
    """Manage import, depending on whether path is a directory or file."""
    abspath: str = os.path.abspath(path)
    log.debug("Loading path: %s", abspath)
    if not os.path.exists(abspath):
        raise FileNotFoundError("Invalid filepath")

    if os.path.isdir(abspath):
        collect_benchmarks(abspath)

    elif os.path.isfile(abspath) and abspath.endswith(".py"):
        load_benchmark(abspath, os.path.abspath(os.path.dirname(abspath)))

    else:
        log.warning(
            "Unsupported path provided. While the path does exist, it is neither a"
            " python file nor a directory: %s",
            abspath,
        )
        raise TypeError(f"Unsupported path type: {abspath}")


def plot_benchmark_array(benchmark: BenchmarkArray) -> go.Figure:
    """Plot benchmark array."""
    fig = go.Figure()
    fig.add_trace(
        plotting.create_scatter_trace(
            benchmark.size,
            benchmark.cpu_time,
            "CPU Time",
            Config.color,
        )
    )

    fig.add_trace(
        plotting.draw_complexity_line(
            benchmark.size,
            benchmark.complexity.cpu_coefficient,
            benchmark.complexity.big_o,
            f"CPU Time Fit ({benchmark.complexity.big_o})",
            Config.line_color,
        )
    )

    fig.add_annotation(
        **plotting.create_annotation_text(
            benchmark.complexity.big_o,
            benchmark.complexity.rms,
        )
    )

    vals, labels = plotting.construct_log2_axis(benchmark.size)
    if (p := len(vals) // Config.x_axis) > 0:
        vals = vals[:: p + 1]
        labels = labels[:: p + 1]

    fig.update_layout(
        title=f"Benchmark Results<br><i>{benchmark.function}</i>",
        xaxis=dict(
            type="log",
            tickvals=vals,
            ticktext=labels,
            tickmode="array",
            title="Input Size (n)",
        ),
        yaxis=dict(
            title=f"Time ({benchmark.unit})",
            type="log",
            dtick=1,
            exponentformat="power",
        ),
        legend_title="Timing",
        font=dict(
            family=Config.font,
            size=12,
        ),
    )

    return fig


# TODO: Consider defining CLI Exit Status in an Enum
def _run() -> BenchmarkContext:
    if "--benchmark_format=json" not in sys.argv:
        sys.argv.append("--benchmark_format=json")

    # TODO: create python bindings of google_benchmark library to call and collect json
    #       data without serializing and capturing stdout.
    # Read this excellent blog regarding redirecting stdout from c libraries:
    # https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python/
    with pipes() as (stdout, stderr):
        try:
            gbench.main()

        # NOTE: bypass sys.exit(0) call from main
        except SystemExit:
            ...

    text: str = stdout.read()
    error: str = stderr.read()
    stdout.close(), stderr.close()  # pylint: disable=W0106

    # Pass stderr from google_benchmark
    if len(error):
        log.error(error)

    handler = HandleText(text)
    try:
        obj: dict = handler.handle()
    except JSONDecodeError as e:
        raise ParsingError.response() from e

    context: BenchmarkContext = parse_version(obj)

    return context


def save(context: BenchmarkContext, cache_dir: str) -> None:
    """Save benchmark data."""
    for j in context.benchmarks:
        figure: go.Figure = plot_benchmark_array(j)
        plotting.to_html(figure, os.path.join(cache_dir, "out.html"), "a")

    # TODO: Save data to database. Serialize to json in the interim.
    database: str = os.path.join(cache_dir, "benchmark.json")
    data: list[dict] = []
    if os.path.exists(database):
        with open(database, "br") as f:
            data = orjson.loads(f.read())

    data.append(context.to_json())
    serialized: bytes = orjson.dumps(
        data,
        option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS,
    )

    with open(database, "bw") as f:
        f.write(serialized)


def run(cache_dir: str) -> None:
    """BenchMatcha Runner."""
    context: BenchmarkContext = _run()

    # TODO: Capture re-analyzed complexity information. Determine where to store, or
    #       how to present this information in a manner that is useful.
    # for bench in context.benchmarks:
    #     analyze_complexity(bench.size, bench.real_time)

    save(context, cache_dir)


def get_args() -> argparse.Namespace:
    """Get BenchMatcha command line arguments and reset to support google_benchmark."""
    args = argparse.ArgumentParser("benchmatcha", conflict_handler="error")
    args.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Set Logging Level to DEBUG.",
        required=False,
    )
    args.add_argument(
        "-c",
        "--color",
        default=None,
        help="Scatterplot marker color.",
        required=False,
    )
    args.add_argument(
        "-l",
        "--line-color",
        default=None,
        help="Scatterplot complexity fit line color.",
        required=False,
    )
    args.add_argument(
        "-x",
        "--x-axis",
        default=None,
        help="Maximum Number of units displayed on x-axis.",
        required=False,
        type=int,
    )

    cwd: str = os.getcwd()
    args.add_argument(
        "--config",
        default=os.path.join(cwd, "pyproject.toml"),
        help="Path location of pyproject.toml configuration file. "
        "Defaults to Current Working Directory.",
    )
    args.add_argument(
        "--cache",
        default=os.path.join(cwd, ".benchmatcha"),
        help="Path location of cache directory. Defaults to Current Working Directory.",
    )
    args.add_argument(
        "--path",
        action="extend",
        nargs="+",
        help="Valid file or directory path to benchmarks.",
    )

    # Capture anything that doesn't fit (to be fed downstream to google_benchmark cli)
    args.add_argument("others", nargs=argparse.REMAINDER)

    # TODO: Plotting over time (pulling from database)
    # sub = args.add_subparsers()
    # plot = sub.add_parser("plot")
    # plot.add_argument(
    #     "--min-date",
    #     default=None,
    #     help="Filter data after minimum date (inclusive).",
    # )
    # plot.add_argument(
    #     "--max-date",
    #     default=None,
    #     help="Filter data before date (inclusive).",
    # )
    # plot.add_argument("--host", default=None, help="Filter data by specific host.")
    # plot.add_argument("--os", default=None, help="Filter data by specific OS type.")
    # plot.add_argument(
    #     "--function",
    #     default=None,
    #     help="Filter data to present a specific function name.",
    # )
    known, unknown = args.parse_known_args()

    # NOTE: Only validate `benchmark_format` argument from google_benchmark cli, since
    #       we require json format to correctly work downstream. All other argument
    #       validations should be handled by google_benchmark cli parsing directly.
    problems: list[str] = []
    for k in filter(
        lambda x: isinstance(x, str) and "--benchmark_format=" in x,
        unknown,
    ):
        if "json" not in k:
            log.warning("Benchmark Format must be json: `%s`", k)
            problems.append(k)
    for p in problems:
        unknown.remove(p)

    # Prune / Reset for google_benchmark
    sys.argv = [sys.argv[0], *unknown, *known.others]

    return known


def main() -> None:
    """Primary CLI Entry Point."""
    args: argparse.Namespace = get_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        log.setLevel(logging.DEBUG)

    if os.path.exists(args.config):
        log.debug("Updating default configuration from file: %s", args.config)
        update_config_from_pyproject(args.config)

    # NOTE: Configuration Args should overwrite values set in config file
    if args.color is not None:
        log.debug("Overriding color from arg: %s", args.color)
        Config.color = args.color

    if args.line_color is not None:
        log.debug("Overriding line_color from arg: %s", args.line_color)
        Config.line_color = args.line_color

    if args.x_axis is not None:
        log.debug("Overriding x_axis from arg: %s", args.x_axis)
        Config.x_axis = args.x_axis

    # Create cache directory if it does not exist
    if not os.path.exists(cache := args.cache):
        log.debug("Creating cache directory at: %s", cache)
        os.mkdir(cache)

    # Natively handle multiple provided paths
    for path in args.path:
        manage_registration(path)

    run(cache)
