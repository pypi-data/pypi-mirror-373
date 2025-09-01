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

"""Complexity calculations."""

from collections.abc import Callable
from dataclasses import dataclass

import google_benchmark as gbench
import numpy as np
from scipy.optimize import curve_fit  # type: ignore[import-untyped]

from .utils import _simple_stats


@dataclass
class FitResult:
    """Curve fit result.

    Args:
        bigo (str): Big O notation string identifier.
        params (np.ndarray): coefficient value(s).
        cov (np.ndarray): covariance std of coefficients
        rms (float): root mean square error of fit.

    """

    bigo: str
    params: np.ndarray
    cov: np.ndarray
    rms: float

    @staticmethod
    def _handle(x: np.ndarray) -> str:
        a = " ".join([f"{j:.3E}" for j in x.tolist()])

        return f"[{a}]"

    def __repr__(self) -> str:
        return (
            f"FitResult(bigo={self.bigo},params={self._handle(self.params)}"
            f",cov={self._handle(self.cov)},rms={self.rms:.3f})"
        )


# Define common complexity functions with all coefficients and intercept
Equation = (
    Callable[[np.ndarray, float, float], np.ndarray]
    | Callable[[np.ndarray, float, float, float], np.ndarray]
    | Callable[[np.ndarray, float, float, float, float], np.ndarray]
)


def constant(n: np.ndarray, a: float, b: float) -> np.ndarray:
    """Constant O(1) equation."""
    return a * np.ones_like(n) + b


def logn(n: np.ndarray, a: float, b: float) -> np.ndarray:
    """Log O(logN) equation."""
    return a * np.log2(n) + b


def linear(n: np.ndarray, a: float, b: float) -> np.ndarray:
    """Linear O(N) equation."""
    return a * n + b


def nlogn(n: np.ndarray, a: float, b: float) -> np.ndarray:
    """Log linear O(NlogN) equation."""
    return a * n * np.log2(n) + b


def quadratic(n: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Quadratic O(N^2) equation."""
    return a * np.power(n, 2) + linear(n, b, c)


def cubic(n: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    """Cubic O(N^3) equation."""
    return a * np.power(n, 3) + quadratic(n, b, c, d)


complexity_functions: dict[str, Equation] = {
    # gbench.oNone.name: "",
    gbench.o1.name: constant,
    gbench.oLogN.name: logn,
    gbench.oN.name: linear,
    gbench.oNLogN.name: nlogn,
    gbench.oNSquared.name: quadratic,
    gbench.oNCubed.name: cubic,
}


def compute_rmsd(y_true: np.ndarray, y_pred: np.ndarray, k: int) -> float:
    r"""Mean normalized root mean square deviation (RMSD).

    Args:
        y_true (np.ndarray): observed y values.
        y_pred (np.ndarray): predicted y values.
        k (int): number of parameters used to estimate predicted values.

    Returns:
        (float): normalized RMSD

    Equations:
        $\frac{1}{\bar{y}} \sqrt{\frac{\sum_{i=0}^{N} (y_i - \hat{y}_i)^2}{N - k}}$

    """
    residuals: np.ndarray = y_true - y_pred
    sum_square_error: np.float64 = (residuals * residuals).sum()
    dof: np.int64 = np.prod(y_pred.size) - k

    return float(np.sqrt(sum_square_error / dof) / y_true.mean())


def fit(
    func: Callable,
    label: str,
    x: np.ndarray,
    y: np.ndarray,
    sigma: np.ndarray,
) -> FitResult | None:
    """Fit observed data to an equation.

    Args:
        func (Callable): equation to fit.
        label (str): complexity label
        x (np.ndarray): x input values
        y (np.ndarray): observed y values
        sigma (np.ndarray): observed error in y values

    Returns:
        (FitResult | None) returns fit result if converged.

    """
    popt: np.ndarray
    pcov: np.ndarray
    try:
        popt, pcov, *_ = curve_fit(
            func,
            x,
            y,
            sigma=sigma,
            absolute_sigma=True,
        )
        pred = func(x, *popt)
        cov = np.sqrt(pcov.diagonal())
        rms = compute_rmsd(y, pred, len(popt))

        return FitResult(
            bigo=label,
            params=popt,
            cov=cov,
            rms=rms,
        )

    except RuntimeError:
        return None


def fit_complexity(x: np.ndarray, y: np.ndarray, sigma: np.ndarray) -> list[FitResult]:
    """Perform curve fitting to available complexity algorithms."""
    results: list[FitResult] = []

    for label, func in complexity_functions.items():
        if (res := fit(func, label, x, y, sigma)) is not None:
            results.append(res)

    return results


def analyze_complexity(x: np.ndarray, y: np.ndarray) -> list[FitResult]:
    """Analyze algorithmic complexity."""
    mean, std = _simple_stats(y)

    return sorted(fit_complexity(x, mean, std), key=lambda x: x.rms)


def get_best_fit(fits: list[FitResult]) -> FitResult:
    """Return best fit by minimizing RMSD."""
    return min(fits, key=lambda x: x.rms)
