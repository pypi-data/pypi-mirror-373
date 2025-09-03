# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from pathlib import Path
from typing import Any

from hidet.option import get_option as _get_hidet_option
from hidet.option import register_option as _register_hidet_option
from hidet.option import set_option as _set_hidet_option


def _get_default_cache_dir() -> str:
    """Get the default cache directory by checking if the current file is inside a Git repository.

    If the current file is inside a Git repository, the cache directory will be set to '.cache' in the root of the
    repository. Otherwise, the cache directory will be set to '~/.cache/tilus'.

    Returns
    -------
    default_cache_dir: str
        The default cache directory.
    """
    import subprocess

    try:
        # check if the current file is inside a Git repository
        subprocess.run(
            ["git", "-C", str(Path(__file__).parent), "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        path = Path(__file__).parents[2] / ".cache"
    except subprocess.CalledProcessError:
        path = Path.home() / ".cache" / "tilus"
    return str(path)


def _register_options():
    """
    Register all options for the tilus package.
    """
    _register_hidet_option(
        "tilus.cache_dir",
        type_hint="str",
        default_value=_get_default_cache_dir(),
        description="The directory to store the cache files.",
    )
    _register_hidet_option(
        "tilus.parallel_workers",
        type_hint="int",
        default_value=os.cpu_count(),
        description="The number of parallel workers the tilus package could use for parallel jobs.",
    )
    _register_hidet_option(
        "tilus.debug.dump_ir",
        type_hint="bool",
        default_value=False,
        description="Whether to dump the IR during compilation.",
    )
    _register_hidet_option(
        "tilus.debug.launch_blocking",
        type_hint="bool",
        default_value=False,
        description="Whether to block the launch of the kernel until the kernel is finished.",
    )


_register_options()


def get_option(name: str) -> Any:
    """
    Get the value of an option.
    Parameters
    ----------
    name: str
        The name of the option.

    Returns
    -------
    value: Any
        The value of the option.
    """
    return _get_hidet_option("tilus." + name)


def cache_dir(dir_path: str | Path) -> None:
    """
    Set the cache directory for the compiled programs.

    Parameters
    ----------
    dir_path: str or Path
        The path to the cache directory.
    """
    _set_hidet_option("tilus.cache_dir", str(dir_path))


def parallel_workers(n: int) -> None:
    """
    Set the number of parallel workers the tilus package could use for parallel jobs (e.g., parallel compilation).

    Parameters
    ----------
    n: int
        The number of parallel workers.
    """
    return _set_hidet_option("tilus.parallel_workers", n)


class debug:
    @staticmethod
    def dump_ir(enable: bool = True) -> None:
        """
        Whether to dump the IR during compilation.

        Parameters
        ----------
        enable: bool
            The flag to enable or disable dumping the IR. Default is True.
        """
        return _set_hidet_option("tilus.debug.dump_ir", enable)

    @staticmethod
    def launch_blocking(enabled: bool = True) -> None:
        """
        Whether to block the launch of the kernel until the kernel is finished.

        Parameters
        ----------
        enabled: bool
            The flag to enable or disable blocking the launch of the kernel. Default is True.
        """
        return _set_hidet_option("tilus.debug.launch_blocking", enabled)
