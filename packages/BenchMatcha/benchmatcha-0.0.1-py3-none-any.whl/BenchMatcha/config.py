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

"""Default runner configuration."""

import logging

import toml  # type: ignore[import-untyped]

from . import plotting


log: logging.Logger = logging.getLogger(__name__)


class Config:
    """default configuration.

    Attributes:
        color (str): plot marker color.
        line_color (str): plot line color.
        font (str): plot font family style.
        x_axis (int): Maximum number of line ticks on x-axis.

    """

    color: str = plotting.Prism[3]
    line_color: str = plotting.Prism[4]
    font: str = "Space Grotesk Light, Courier New, monospace"
    x_axis: int = 13


class ConfigUpdater:
    """Configuration updater through pyproject config file.

    Args:
        path (str): path to valid configuration file.
        config (Config): configuration class to update.

    """

    path: str
    config: type[Config]

    def __init__(self, path: str, config: type[Config] = Config) -> None:
        self.path = path
        self.config = config

    def load(self) -> dict:
        """Load toml data from path."""
        return toml.load(self.path)

    def _update(self, data: dict) -> None:
        for key, value in data.get("tool", {}).get("BenchMatcha", {}).items():
            if not hasattr(self.config, key):
                log.info("Unsupported tool key: %s", key)
                continue

            setattr(self.config, key, value)

    def update(self) -> None:
        """Parse toml path and update default configuration."""
        data: dict = self.load()
        self._update(data)


def update_config_from_pyproject(path: str) -> None:
    """Update default config from pyproject toml file.

    Example:

        .. code-block: toml

            [tool.BenchMatcha]
            color="#FFF"
            line_color="#333"
            font="Courier"
            x_axis=5

    """
    cu = ConfigUpdater(path)
    cu.update()
