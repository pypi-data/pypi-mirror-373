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

"""Plotting utilities."""

from collections.abc import Callable

import numpy as np
import plotly.graph_objs as go  # type: ignore[import-untyped]
from plotly.express import colors  # type: ignore[import-untyped]
from plotly.io import to_json as _to_json  # type: ignore[import-untyped]

from .utils import _simple_stats, power_of_2


Prism: list[str] = colors.qualitative.Prism[:]


def to_html(figure: go.Figure, path: str, mode: str = "w") -> None:
    """Saves a plotly figure in HTML Format to a file.

    Args:
        figure (go.Figure): Plotly figure.
        path (str): Filepath to save plotly figure.
        mode (str): Writing mode ("a" | "w")

    Returns:
        (None) Appends/writes figure to html filepath.

    """
    with open(path, mode) as f:
        f.write(figure.to_html(full_html=False, include_plotlyjs="cdn"))


def to_json(figure: go.Figure, path: str) -> None:
    """Serialize a plotly figure to a json file."""
    with open(path, "w") as f:
        f.write(_to_json(figure, False, False, True, engine="orjson"))


def construct_log2_axis(x: np.ndarray) -> tuple[list[int], list[str]]:
    """Build a log2 power axis for plotly."""
    labels: list[str] = []
    values: list[int] = []

    minimum = int(x.min())
    maximum = power_of_2(int(x.max())) + 1
    current = power_of_2(minimum)
    if current >= minimum:
        current = max(1, current // 2)
    power = int(np.log2(current))

    while current < maximum:
        values.append(int(current))
        labels.append(f"2<sup>{power}</sup>")
        current *= 2
        power += 1

    return values, labels


def create_scatter_trace(
    x: np.ndarray,
    y: np.ndarray,
    name: str,
    color: str,
) -> go.Scatter:
    """Create scatter trace of mean and std.

    Args:
        x (np.ndarray): x values
        y (np.ndarray): y values
        name (str): name to give plot
        color (str): trace color

    Returns:
        (go.Scatter) scatter plot trace of data.

    """
    mean, std = _simple_stats(y)

    return go.Scatter(
        mode="lines+markers",
        x=x,
        y=mean,
        name=name,
        line=dict(color=color, dash="dot"),
        error_y=dict(type="data", array=std, visible=True),
    )


def box_plot(
    x: np.ndarray,
    y: np.ndarray,
    name: str,
    color: str,
    line_color: str,
) -> go.Box:
    """Construct a box plot.

    Args:
        x (np.ndarray): x values
        y (np.ndarray): y values
        name (str): name to give plot
        color (str): marker color
        line_color (str): line color

    Returns:
        (go.Box) boxplot trace of data.

    """
    q1, med, q3 = np.nanquantile(y, [0.25, 0.5, 0.75], 1)
    mean, std = _simple_stats(y)

    return go.Box(
        name=name,
        x=x,
        mean=mean,
        sd=std,
        q1=q1,
        median=med,
        q3=q3,
        marker_color=color,
        marker_line_color=line_color,
    )


def create_annotation_text(
    label: str,
    error: float,
) -> dict:
    """Build a simple annotation data of complexity fit information.

    Args:
        label (str): Complexity label
        error (float): error to fit (e.g. RMSD)

    Example:

        .. code-block:: python

            benchmark: BenchmarkArray
            figure = go.Figure()
            figure.add_annotation(
                **create_annotation_text(
                    benchmark.complexity.bigo,
                    benchmark.complexity.rms,
                )
            )

    """
    a = f"{error:.2f}% "
    b = f"O({label}) "
    length = max(len(a), len(b))
    c = f" Complexity: {b: >{length}}"
    d = f"        RMS: {a: >{length}}"

    return dict(
        xref="paper",
        yref="paper",
        x=0.01,
        y=0.99,
        showarrow=False,
        text=f"{c}<br>{d}",
        align="left",
        bgcolor="rgba(255,255,255,0.6)",
        bordercolor="black",
        borderwidth=1,
    )


_benchmark_map: dict[str, Callable[[np.ndarray, float], np.ndarray]] = {
    "(1)": lambda n, c: c * np.ones_like(n),
    "N": lambda n, c: c * n,
    "lgN": lambda n, c: c * np.log2(n),
    "NlgN": lambda n, c: c * n * np.log2(n),
    "N^2": lambda n, c: c * n**2,
    "N^3": lambda n, c: c * n**3,
}


def get_big_o_function(label: str) -> Callable[[np.ndarray, float], np.ndarray]:
    """Map the big-O notation label (from google benchmark) to function."""
    return _benchmark_map.get(label, lambda n, c: c * n)


def draw_complexity_line(
    x: np.ndarray,
    coefficient: float,
    big_o: str,
    name: str,
    color: str,
) -> go.Scatter:
    """Create a scatter plot to describe google benchmark complexity information.

    Args:
        x (np.ndarray): x axis data (n).
        coefficient (float): multiplier
        big_o (str): label describing algorithmic complexity.
        name (str): name (label) to give trace on plot.
        color (str): color of line.

    Returns:
        (go.Scatter): scatter plot trace of complexity information.

    """
    func: Callable[[np.ndarray, float], np.ndarray] = get_big_o_function(big_o)
    y: np.ndarray = func(x, coefficient)

    return go.Scatter(
        x=x,
        y=y,
        name=name,
        mode="lines",
        line=dict(
            color=color,
            dash="dash",
            shape="spline",
        ),
        opacity=0.7,
    )
