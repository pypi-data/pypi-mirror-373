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
# ruff: noqa: F401

from hidet.ir.dtypes import name2dtype, sname2dtype
from hidet.ir.dtypes.integer_subbyte import (
    i1,
    i2,
    i3,
    i4,
    int1b,
    int2b,
    int3b,
    int4b,
    u1,
    u2,
    u3,
    u4,
    uint1b,
    uint2b,
    uint3b,
    uint4b,
)

from .floats import f8e4m3, f8e5m2, float8_e4m3, float8_e5m2
from .floats_subbyte import (
    f3e1m1,
    f4e1m2,
    f4e2m1,
    f5e1m3,
    f5e2m2,
    f5e3m1,
    f6e2m3,
    f6e3m2,
    f6e4m1,
    f7e2m4,
    f7e3m3,
    f7e4m2,
    f7e5m1,
    float3_e1m1,
    float4_e1m2,
    float4_e2m1,
    float5_e1m3,
    float5_e2m2,
    float5_e3m1,
    float6_e2m3,
    float6_e3m2,
    float6_e4m1,
    float7_e2m4,
    float7_e3m3,
    float7_e4m2,
    float7_e5m1,
)
from .integer_subbyte import (
    i5,
    i6,
    i7,
    int5b,
    int6b,
    int7b,
    u5,
    u6,
    u7,
    uint5b,
    uint6b,
    uint7b,
)
from .vector import uint32x1, uint32x2, uint32x4

for dtype in [
    uint32x4,
    uint32x2,
    float7_e2m4,
    float7_e3m3,
    float7_e4m2,
    float7_e5m1,
    float6_e2m3,
    float6_e3m2,
    float6_e4m1,
    float5_e1m3,
    float5_e2m2,
    float5_e3m1,
    float4_e1m2,
    float4_e2m1,
    float3_e1m1,
    int5b,
    int6b,
    int7b,
    uint5b,
    uint6b,
    uint7b,
]:
    name2dtype[dtype.name] = dtype
    sname2dtype[dtype.short_name] = dtype
