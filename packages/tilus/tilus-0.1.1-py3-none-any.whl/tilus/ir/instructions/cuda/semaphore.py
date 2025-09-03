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
from __future__ import annotations

from dataclasses import dataclass

from hidet.ir.expr import Expr

from tilus.ir.inst import Instruction


@dataclass(frozen=True, eq=False)
class LockSemaphoreInst(Instruction):
    semaphore: Expr
    value: Expr

    @staticmethod
    def create(
        semaphore: Expr,
        value: Expr,
    ) -> LockSemaphoreInst:
        return LockSemaphoreInst(inputs=(), output=None, semaphore=semaphore, value=value)


@dataclass(frozen=True, eq=False)
class ReleaseSemaphoreInst(Instruction):
    semaphore: Expr
    value: Expr

    @staticmethod
    def create(
        semaphore: Expr,
        value: Expr,
    ) -> ReleaseSemaphoreInst:
        return ReleaseSemaphoreInst(inputs=(), output=None, semaphore=semaphore, value=value)
