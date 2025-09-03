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
from tilus import SharedLayout
from tilus.ir import SharedTensor
from tilus.ir.instructions import StoreSharedGenericInst, StoreSharedInst
from tilus.ir.instructions.cuda.ldmatrix import LoadMatrixConfig
from tilus.ir.layout import LayoutOperationError, ops
from tilus.ir.layout.inference.rule import LayoutInferenceContext, LayoutInferenceRule, register_rule


@register_rule(StoreSharedGenericInst)
@register_rule(StoreSharedInst)
class StoreSharedSwizzleRule(LayoutInferenceRule):
    @staticmethod
    def inference(
        ctx: LayoutInferenceContext, inst: StoreSharedInst | StoreSharedGenericInst
    ) -> dict[SharedTensor, SharedLayout]:
        a = inst.inputs[0].as_shared_tensor()
        b = inst.inputs[1].as_register_tensor()

        if not (a.optional_layout is None and b.optional_layout is not None):
            return {}

        for config in LoadMatrixConfig.all():
            if config.nbytes != a.dtype.nbytes:
                continue
            try:
                ops.divide(b.layout, config.ldmatrix_layout)
            except LayoutOperationError:
                continue

            # use swizzle layout since we are using ldmatrix instruction
            from tilus.lang.modules.cuda import cuda

            return {a: cuda.swizzled_shared_layout(dtype=a.dtype, shape=a.shape)}

        return {}
