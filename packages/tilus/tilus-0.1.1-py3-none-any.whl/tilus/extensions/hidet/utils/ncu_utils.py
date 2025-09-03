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
# pylint: disable=subprocess-run-check
import argparse
import importlib
import os
import pickle
import subprocess
import sys
import traceback
from typing import Any

_nsys_path: str = "/usr/local/cuda/bin/ncu"
_ncu_ui_path: str = "/usr/local/cuda/bin/ncu-ui"
_ncu_ui_template = "{ncu_ui_path} {report_path}"
_ncu_template = """
{ncu_path}
--export {report_path}
--kernel-name regex:"{kernel_regex}"
--force-overwrite
--set full
--rule CPIStall 
--rule FPInstructions 
--rule HighPipeUtilization 
--rule IssueSlotUtilization 
--rule LaunchConfiguration 
--rule Occupancy 
--rule PCSamplingData 
--rule SOLBottleneck 
--rule SOLFPRoofline 
--rule SharedMemoryConflicts 
--rule SlowPipeLimiter 
--rule ThreadDivergence 
--rule UncoalescedGlobalAccess
--rule UncoalescedSharedAccess 
--import-source yes
--check-exit-code yes
{python_executable} {python_script} {args}
""".replace("\n", " ").strip()


class NsightComputeReport:
    def __init__(self, report_path: str):
        self.report_path: str = report_path

    def visualize(self):
        command = _ncu_ui_template.format(ncu_ui_path=_ncu_ui_path, report_path=self.report_path)
        subprocess.run(command, shell=True)


def _ncu_run_func(script_path, func_name, args_pickled_path):
    with open(args_pickled_path, "rb") as f:
        args, kwargs = pickle.load(f)

    # remove the dir path of the current script from sys.path to avoid module overriding
    sys.path = [path for path in sys.path if not path.startswith(os.path.dirname(__file__))]

    try:
        sys.path.append(os.path.dirname(script_path))
        module = importlib.import_module(os.path.basename(script_path)[:-3])
    except Exception as e:
        raise RuntimeError("Can not import the python script: {}".format(script_path)) from e

    if not hasattr(module, func_name):
        raise RuntimeError('Can not find the function "{}" in {}'.format(func_name, script_path))

    func = getattr(module, func_name)

    try:
        func(*args, **kwargs)
    except Exception as e:
        raise RuntimeError('Error when running the function "{}"'.format(func_name)) from e


def ncu_set_path(ncu_path: str) -> None:
    # pylint: disable=global-variable-not-assigned
    global _nsys_path
    _ncu_path = ncu_path


def ncu_run(func: Any, *args: Any, kernel_regex: str = ".*", **kwargs: Any) -> NsightComputeReport:
    import inspect
    import tempfile

    # get the python script path and function name
    script_path: str = inspect.getfile(func)
    func_name: str = func.__name__

    # report path
    report_path_template: str = os.path.join(os.path.dirname(script_path), "ncu-reports/report{}.ncu-rep")
    idx = 0
    while os.path.exists(report_path_template.format(idx)):
        idx += 1
    report_path = report_path_template.format(idx)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    # dump args
    args_path: str = tempfile.mktemp() + ".pkl"
    with open(args_path, "wb") as f:
        pickle.dump((args, kwargs), f)

    command = _ncu_template.format(
        ncu_path=_nsys_path,
        report_path=report_path,
        kernel_regex=kernel_regex,
        python_executable=sys.executable,
        python_script=__file__,
        args="{} {} {}".format(script_path, func_name, args_path),
    )
    print("Running Nsight Compute command:")
    print(command.replace("--", "\n\t--"))

    status = subprocess.run(
        command,
        shell=True,
    )

    if status.returncode != 0:
        raise RuntimeError("Error when running Nsight Compute.")

    return NsightComputeReport(report_path)


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("script_path", type=str)
        parser.add_argument("func", type=str)
        parser.add_argument("args", type=str)
        args = parser.parse_args()
        _ncu_run_func(args.script_path, args.func, args.args)
    except Exception as e:
        print("Error when running the script: {}".format(e))
        print("Traceback:")
        traceback.print_exc()
        raise e


if __name__ == "__main__":
    main()
