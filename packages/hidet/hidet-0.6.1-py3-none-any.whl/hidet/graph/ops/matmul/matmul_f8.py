# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import List, Tuple, Union

import hidet
from hidet.ir import dtypes
from hidet.ir.type import DataType, data_type
from hidet.ir.dtypes import f8e4m3, f32
from hidet.ir.module import IRModule
from hidet.ir.compute import TensorNode
from hidet.ir.task import Task
from hidet.graph.ops.utils import input_like, can_mutually_broadcast
from hidet.ir.library import tune
from hidet.graph.operator import Operator, Tensor
from hidet.utils.py import cdiv, prod
from hidet.graph.ops.utils import broadcast_indices

from hidet.ir.cute.ops import make_tensor, tensor_view, partition_src, partition_dst, copy, mma, rearrange, fill, cast
from hidet.ir.cute import auto_layout, layout_auto, auto_copy
from hidet.ir.cute.layout import TensorLayout
from hidet.ir.cute.algorithm import MmaAtom, TiledMma

from hidet.lang import attrs
from hidet.lang.cuda import blockIdx, syncthreads
from hidet.lang.cuda import cp_async_commit_group, cp_async_wait_group
from hidet.lang.mapping import spatial


# -------------------------------------------------------
compute_capability = hidet.option.cuda.get_arch_pair()
current_compute_capability = compute_capability[0] * 10 + compute_capability[1]

compute_bound_tiled_mma_configurations = [
    # m128n256k32
    ((128, 256), (2, 4), (4, 4)),
    # m256n128k32
    ((256, 128), (4, 2), (4, 4)),
    # m64n256k32
    ((64, 256), (2, 2), (2, 8)),
    # m256n64k32
    ((256, 64), (2, 2), (8, 2)),
    # m128n64k32
    ((128, 64), (2, 2), (4, 2)),
    # m64n128k32
    ((64, 128), (2, 2), (2, 4)),
    # m32n128k32
    ((32, 128), (2, 2), (1, 4)),
    # m32n64k32
    ((32, 64), (2, 2), (1, 2)),
    # m64n64k32
    ((64, 64), (2, 2), (2, 2)),
    # m32n16k32
    ((32, 16), (2, 1), (1, 1)),
]

mma_layout_configurations = [(2, 2), (4, 2), (2, 4), (1, 4), (4, 1), (2, 1), (1, 2), (1, 1)]
mma_num_pid_M_configurations = [1, 2, 3, 4, 6, 8, 12, 16]
mma_num_pid_N_configurations = [1, 2, 3, 4, 6, 8, 12, 16]
acc_reg_nbytes = 4  # .f32 register for f32 acc, .f16x2 register for f16 acc
a_reg_nbytes = 4  # .b32 register, each contains 4 .e4m3/.e5m2
b_reg_nbytes = 4  # .b32 register
default_mma_layout = (2, 2)
default_mma_tile = (4, 4)
default_inner_mma_tile = (1, 2)
default_scale_shapeMNK = (128, 128, 128)

max_register_pressure = 255
max_block_m = 256
max_block_n = 256
default_bR = 2
default_bP = 3
default_bK = 64
TRANSPOSE_B = True
SCALE_DTYPE = f32
# -------------------------------------------------------


def register_tiled_mma(x):
    tiled_mma_space = []
    # Default tiled mma configuration: m128n128k32. bM=128, bN=128, inst_k=32.
    # Uses the m16n8k32.f32.f8type.f8type.f32 instruction
    a = TensorLayout(((4, 8), (4, 2, 2)), ((64, 1), (16, 8, 256)))  # M-major indexing
    b = TensorLayout(((4, 8), (4, 2)), ((32, 1), (8, 128)))  # N-major indexing
    c = TensorLayout(((4, 8), (2, 2)), ((32, 1), (16, 8)))  # M-major indexing

    mma_atom = MmaAtom("warp", (16, 8, 32), a, b, c, c, default_inner_mma_tile)  # m16n16k32

    tiled_mma = TiledMma.make_tiled_mma(mma_atom, default_mma_layout, default_mma_tile)

    tiled_mma_space.append(tiled_mma)

    for _, mma_layout, mma_tile in compute_bound_tiled_mma_configurations:
        tiled_mma_space.append(TiledMma.make_tiled_mma(mma_atom, mma_layout, mma_tile))

    compute_bound = [bMbN for bMbN, _, _ in compute_bound_tiled_mma_configurations]
    _blocks = compute_bound

    for mma_layout_m, mma_layout_n in mma_layout_configurations:
        for mma_num_pid_M in mma_num_pid_M_configurations:
            for mma_num_pid_N in mma_num_pid_N_configurations:
                acc_dtype = f32  # only f32 accumulator works

                tiled_mma = TiledMma.make_tiled_mma(
                    mma_atom, (mma_layout_m, mma_layout_n), (mma_num_pid_M, mma_num_pid_N)
                )
                registers_per_thread = tiled_mma.get_register_pressure(acc_dtype, f8e4m3, f8e4m3, default_bR)

                bM, bN = tiled_mma.c_shape
                if (
                    registers_per_thread > max_register_pressure
                    or bM > max_block_m
                    or bN > max_block_n
                    or (bM, bN) in _blocks
                ):
                    continue
                _blocks.append((bM, bN))
                tiled_mma_space.append(tiled_mma)

    for tiled_mma in tiled_mma_space:
        yield tiled_mma


class MatmulF8Task(Task):
    """
    w8a8 matmul task

    **NOTE**: A is (M,K),K-major. B is (N,K),K-major because it is required to use the `ldmatrix_x4` instruction.
    C is (M,N), N-major.
    """

    def __init__(self, a: TensorNode, b: TensorNode, acc_dtype: DataType, output_dtype: DataType):
        from hidet.ir.compute import cops

        self.a_dtype, self.b_dtype = a.type.dtype, b.type.dtype
        self.output_dtype, self.acc_dtype = output_dtype, acc_dtype
        assert self.a_dtype == self.b_dtype

        self._assert(
            a.shape[-1] == b.shape[-1],
            msg=("Expected A and B with shapes [...,M,K] and [...,N,K], got {} and {}".format(a.shape, b.shape)),
        )

        self._assert(
            can_mutually_broadcast(a.shape[:-2], b.shape[:-2]),
            msg=("Matrix multiplication expects tensor A and B with compatible broadcast shapes"),
        )

        c = cops.matmul(a, b, tb=TRANSPOSE_B)
        c.type.dtype = self.output_dtype

        M, N, K, a_head, b_head, c_head = self.prologue(a, b, c)
        self.shape_MNK = (M, N, K)
        self.head = (a_head, b_head, c_head)

        super().__init__(
            name="matmul_{}.{}.{}.{}".format(self.acc_dtype, self.a_dtype, self.b_dtype, self.acc_dtype),
            inputs=[a, b],
            outputs=[c],
            attributes={'acc_dtype': acc_dtype, 'output_dtype': output_dtype},
        )

    def allow_prologue(self) -> bool:
        return False

    def allow_epilogue(self) -> bool:
        return False

    def implement_cuda(self, working_dir: str) -> List[IRModule]:
        return tune.extract_ir_modules(self.schedule)

    def _get_max_smem(self):
        smem_limits = {70: 96000, 72: 96000, 75: 64000, 80: 163000, 86: 99000, 87: 163000, 89: 99000, 90: 227000}
        return 99000 if current_compute_capability > 90 else smem_limits[current_compute_capability]

    def _get_bP_heuristic(self, bM, bN, bK, a_dtype: DataType):
        maximum_smem_bytes = self._get_max_smem()
        bP = maximum_smem_bytes // ((bM + bN) * bK * a_dtype.nbytes)
        bP = max(3, min(bP, 11))
        return bP

    @staticmethod
    def prologue(A, B, C):
        a_shape: Tuple[int, ...] = A.shape
        b_shape: Tuple[int, ...] = B.shape
        c_shape: Tuple[int, ...] = C.shape

        M, N, K = a_shape[-2], b_shape[-2], a_shape[-1]

        a_head, b_head, c_head = list(a_shape[:-2]), list(b_shape[:-2]), list(c_shape[:-2])
        return M, N, K, a_head, b_head, c_head

    @tune.space(2, tiled_mma=register_tiled_mma, bK=[default_bK], bP=[default_bP], bR=[default_bR])
    def schedule(self, tiled_mma: TiledMma, bK: int = default_bK, bP: int = default_bP, bR: int = default_bR):
        """
        Tuning parameters
        ----------
        tiled_mma : Optional[TiledMma]
            TiledMma object
        bK : Optional[int]
            Block size for K dimension.
        bP : Optional[int]
            Maximum pipeline depth.
        bR : Optional[int]
            Register buffer depth.
        """
        M, N, K = self.shape_MNK
        a_head, b_head, c_head = self.head

        _, inst_k = tiled_mma.a_shape
        bM, bN = tiled_mma.c_shape
        tune.check(
            M % bM == 0 and N % bN == 0 and K % bK == 0, message="M,N,K must be divisible by bM,bN,bK respectively"
        )

        bP = self._get_bP_heuristic(bM, bN, bK, self.a_dtype)
        threads = tiled_mma.get_num_threads()
        maximum_smem_bytes = self._get_max_smem()
        dynamic_smem_bytes = self.a_dtype.nbytes * bP * (bM + bN) * bK
        tune.check(
            dynamic_smem_bytes <= maximum_smem_bytes,
            message=f"Dynamic SMEM size exceeds limit of {maximum_smem_bytes} bytes",
        )

        with hidet.script_module() as script_module:

            @hidet.script
            def gemm(
                a: self.a_dtype[a_head + [M, K]],
                b: self.b_dtype[b_head + [N, K]],
                c: self.output_dtype[c_head + [M, N]],
            ):
                attrs.func_kind = "cuda_kernel"
                attrs.cuda.block_dim = threads
                attrs.cuda.grid_dim = cdiv(M, bM) * cdiv(N, bN), prod(c_head)
                attrs.cuda.dynamic_smem_bytes = 0

                # thread block swizzle
                group_size_m = 8
                pid = blockIdx.x
                num_pid_m = cdiv(M, bM)
                num_pid_n = cdiv(N, bN)
                num_pid_in_group = group_size_m * num_pid_n
                group_id = pid // num_pid_in_group
                first_pid_m = group_id * group_size_m
                group_size_m = min(group_size_m, num_pid_m - first_pid_m)
                pid_m = first_pid_m + (pid % group_size_m)
                pid_n = (pid % num_pid_in_group) // group_size_m

                c_head_index = spatial(*c_head).map(blockIdx.y)
                a_head_index = broadcast_indices(c_head_index, a_head, c_head)
                b_head_index = broadcast_indices(c_head_index, b_head, c_head)

                # Global memory blocks for this CTA
                gA = tensor_view(
                    a[a_head_index][pid_m * bM : (pid_m + 1) * bM, :], TensorLayout((bM, K), (K, 1)), "global"
                )  # (bM, K)
                gB = tensor_view(
                    b[b_head_index][pid_n * bN : (pid_n + 1) * bN, :], TensorLayout((bN, K), (K, 1)), "global"
                )  # (bN, K)
                gC = tensor_view(
                    c[c_head_index][pid_m * bM : (pid_m + 1) * bM, pid_n * bN : (pid_n + 1) * bN],
                    TensorLayout((bM, bN), (N, 1)),
                    "global",
                )  # (bM, bN)

                # Shared memory buffers
                sA = make_tensor(self.a_dtype, TensorLayout((bM, bK, bP), (bK, 1, bM * bK)), "shared")  # (bM, bK, bP)
                sB = make_tensor(self.b_dtype, TensorLayout((bN, bK, bP), (bK, 1, bN * bK)), "shared")  # (bN, bK, bP)
                # Register memory buffers
                rA = make_tensor(self.a_dtype, layout_auto((bM, inst_k * bR)), "register")  # (bM, inst_k * bR)
                rB = make_tensor(self.b_dtype, layout_auto((bN, inst_k * bR)), "register")  # (bN, inst_k * bR)
                rC = make_tensor(self.acc_dtype, layout_auto((bM, bN), (bN, 1)), "register")
                fill(rC, 0.0)

                # partition for GMEM -> SMEM
                tAgA = partition_src(gA, auto_copy())  # (bM, bK, k), where k==ceil(K/bK)
                tAsA = partition_dst(sA, auto_copy())  # (bM, bK, bP)

                tBgB = partition_src(gB, auto_copy())  # (bN, bK, k)
                tBsB = partition_dst(sB, auto_copy())  # (bN, bK, bP)

                # prefill pipeline
                for s in range(bP - 1):
                    copy(auto_copy((bM, bK)), tAgA[:, :, s], tAsA[:, :, s])
                    copy(auto_copy((bN, bK)), tBgB[:, :, s], tBsB[:, :, s])
                    cp_async_commit_group()
                cp_async_wait_group(allow_on_fly_groups=bP - 2)
                syncthreads()

                K_TILE_MAX = (K + bK - 1) // bK
                INST_K_TILE_MAX = bK // inst_k
                k_pipe_read, k_pipe_write = 0, bP - 1

                # partition for SMEM -> RMEM.
                tXsA = partition_src(sA, auto_copy())  # (bM, inst_k, k, bP)
                tXrA = partition_dst(rA, auto_copy())  # (bM, inst_k, bR)

                tXsB = partition_src(sB, auto_copy())  # (bN, inst_k, k, bP)
                tXrB = partition_dst(rB, auto_copy())  # (bN, inst_k, bR)

                # prefill register buffer
                copy(auto_copy(), tXsA[:, :, 0, k_pipe_read], tXrA[:, :, 0])
                copy(auto_copy(), tXsB[:, :, 0, k_pipe_read], tXrB[:, :, 0])

                for ko in range(K_TILE_MAX):
                    for ki in range(INST_K_TILE_MAX):
                        if ki == INST_K_TILE_MAX - 1:  # advance read pipeline
                            cp_async_wait_group(allow_on_fly_groups=bP - 2)
                            syncthreads()

                        # prefetch next inst_k tile into RMEM
                        ki_tile_next = (ki + 1) % INST_K_TILE_MAX
                        copy(auto_copy(), tXsA[:, :, ki_tile_next, k_pipe_read], tXrA[:, :, (ki + 1) % bR])
                        copy(auto_copy(), tXsB[:, :, ki_tile_next, k_pipe_read], tXrB[:, :, (ki + 1) % bR])

                        if ki == 0:  # prefetch next K tile into SMEM
                            if ko + bP - 1 < K_TILE_MAX:
                                copy(auto_copy(), tAgA[:, :, ko + bP - 1], tAsA[:, :, k_pipe_write])
                                copy(auto_copy(), tBgB[:, :, ko + bP - 1], tBsB[:, :, k_pipe_write])
                            k_pipe_write = k_pipe_read
                            cp_async_commit_group()

                        if ki == INST_K_TILE_MAX - 2:
                            # advance read and write pipelines
                            k_pipe_read = 0 if k_pipe_read == bP - 1 else k_pipe_read + 1

                        # perform mma on current inst_k tile (RMEM,RMEM)->RMEM
                        mma(tiled_mma, rC, tXrA[:, :, ki % bR], tXrB[:, :, ki % bR], rC)

                rC_out = rearrange(cast(rC, self.output_dtype), auto_layout, "register")

                tXrC = partition_src(rC_out, auto_copy())
                tXgC = partition_dst(gC, auto_copy())
                copy(auto_copy((bM, bN)), tXrC, tXgC)

            @hidet.script
            def launch(
                a: self.a_dtype[a_head + [M, K]],
                b: self.b_dtype[b_head + [N, K]],
                c: self.output_dtype[c_head + [M, N]],
            ):
                attrs.func_kind = "public"
                gemm(a, b, c)

        return script_module.ir_module()


class MatmulF8ScaledTask(Task):
    """
    w8a8 groupwise scaled matmul task. The inputs are required to be of the following format:

        1. A is (M,K),K-major. B is (N,K),K-major. C is (M,N), N-major.
        2. ScaleA is (num_blocks_K,M),M-major.
        3. ScaleB is (num_blocks_N,num_blocks_K),num_blocks_K-major.

    Currently, the only supported groupwise scaling configuration is blockwise scaling for B and
    per-token-group wise for A. It must follow the below constraints:

        1. group_M == 1
        2. group_N == bN
        3. group_K == bK

    TODO: when generalized groupwise scaled_mm is supported, change function documentation.
    """

    def __init__(
        self,
        a: TensorNode,
        b: TensorNode,
        scale_a: TensorNode,
        scale_b: TensorNode,
        acc_dtype: DataType,
        output_dtype: DataType,
    ):
        from hidet.ir.compute import cops

        self.a_dtype, self.b_dtype = a.type.dtype, b.type.dtype
        self.acc_dtype, self.output_dtype = acc_dtype, output_dtype

        self._assert(self.a_dtype == self.b_dtype)

        self._assert(
            a.shape[-1] == b.shape[-1],
            msg=("Expected A and B with shapes [...,M,K] and [...,N,K], got {} and {}".format(a.shape, b.shape)),
        )

        self._assert(
            can_mutually_broadcast(a.shape[:-2], b.shape[:-2]),
            msg=("Matrix multiplication expects tensor A and B with compatible broadcast shapes"),
        )

        c = cops.matmul(a, b, tb=TRANSPOSE_B)
        c.type.dtype = self.output_dtype

        M, N, K, a_head, b_head, c_head, group_M, group_N, group_K = self.prologue(a, b, c, scale_a, scale_b)
        self.shape_MNK = (M, N, K)
        self.head = (a_head, b_head, c_head)
        self.group_MNK = (group_M, group_N, group_K)

        super().__init__(
            name="scaled_mm_{}.{}.{}.{}".format(self.acc_dtype, self.a_dtype, self.b_dtype, self.acc_dtype),
            inputs=[a, b, scale_a, scale_b],
            outputs=[c],
            attributes={'acc_dtype': acc_dtype, 'output_dtype': output_dtype},
        )

    def allow_prologue(self) -> bool:
        return False

    def allow_epilogue(self) -> bool:
        return False

    def implement_cuda(self, working_dir: str) -> List[IRModule]:
        return tune.extract_ir_modules(self.schedule)

    def _get_max_smem(self):
        smem_limits = {70: 96000, 72: 96000, 75: 64000, 80: 163000, 86: 99000, 87: 163000, 89: 99000, 90: 227000}
        return 99000 if current_compute_capability > 90 else smem_limits[current_compute_capability]

    def _get_bP_heuristic(self, bM, bN, bK, a_dtype: DataType):
        maximum_smem_bytes = self._get_max_smem()
        bP = maximum_smem_bytes // ((bM + bN) * bK * a_dtype.nbytes)
        bP = max(2, min(bP, 11))
        return bP

    def prologue(self, A: TensorNode, B: TensorNode, C: TensorNode, scale_a: TensorNode, scale_b: TensorNode):
        a_shape: Tuple[int, ...] = A.shape
        b_shape: Tuple[int, ...] = B.shape
        c_shape: Tuple[int, ...] = C.shape
        a_scale_shape: Tuple[int, ...] = scale_a.shape
        b_scale_shape: Tuple[int, ...] = scale_b.shape

        M, N, K = a_shape[-2], b_shape[-2], a_shape[-1]
        group_K, group_M = K // a_scale_shape[-2], M // a_scale_shape[-1]
        group_N = N // b_scale_shape[-2]

        self._assert(a_scale_shape[-2] == b_scale_shape[-1], msg="Incompatible shapes for scale_a and scale_b")

        a_head, b_head, c_head = list(a_shape[:-2]), list(b_shape[:-2]), list(c_shape[:-2])
        a_scale_head, b_scale_head = list(a_scale_shape[:-2]), list(b_scale_shape[:-2])
        self._assert(
            a_scale_head == a_head and b_scale_head == b_head, msg="Incompatible shapes for scale_a and scale_b"
        )

        return M, N, K, a_head, b_head, c_head, group_M, group_N, group_K

    @tune.space(2, tiled_mma=register_tiled_mma, bK=[default_scale_shapeMNK[2]], bP=[default_bP], bR=[default_bR])
    def schedule(
        self, tiled_mma: TiledMma, bK: int = default_scale_shapeMNK[2], bP: int = default_bP, bR: int = default_bR
    ):
        """
        Parameters
        ----------
        tiled_mma : Optional[TiledMma]
            TiledMma object
        bK : Optional[int]
            Block size for K dimension.
        bP : Optional[int]
            Maximum pipeline depth.
        bR : Optional[int]
            Register buffer depth.
        """
        M, N, K = self.shape_MNK
        a_head, b_head, c_head = self.head

        _, inst_k = tiled_mma.a_shape
        bM, bN = tiled_mma.c_shape
        num_blocks_M, num_blocks_N, num_blocks_K = cdiv(M, bM), cdiv(N, bN), cdiv(K, bK)
        tune.check(self.group_MNK[0] == 1)  # only allow per token groupwise scaling for A
        tune.check(self.group_MNK[1] == bN and self.group_MNK[2] == bK)  # only allow blockwise scaling for B
        tune.check(N % bN == 0 and K % bK == 0 and M % bM == 0)  # check for valid tiling configuration

        bP = self._get_bP_heuristic(bM, bN, bK, self.a_dtype)
        threads = tiled_mma.get_num_threads()
        maximum_smem_bytes = self._get_max_smem()
        dynamic_smem_bytes = self.a_dtype.nbytes * bP * (bM + bN) * bK
        tune.check(
            dynamic_smem_bytes <= maximum_smem_bytes,
            message=f"Dynamic SMEM size exceeds limit of {maximum_smem_bytes} bytes",
        )

        with hidet.script_module() as script_module:

            @hidet.script
            def gemm(
                a: self.a_dtype[a_head + [M, K]],
                b: self.b_dtype[b_head + [N, K]],
                scale_a: SCALE_DTYPE[a_head + [num_blocks_K, M]],
                scale_b: SCALE_DTYPE[b_head + [num_blocks_N, num_blocks_K]],
                c: self.output_dtype[c_head + [M, N]],
            ):
                attrs.func_kind = "cuda_kernel"
                attrs.cuda.block_dim = threads
                attrs.cuda.grid_dim = num_blocks_M * num_blocks_N, prod(c_head)
                attrs.cuda.dynamic_smem_bytes = 0

                # thread block swizzle
                group_size_m = 8
                pid = blockIdx.x
                num_pid_in_group = group_size_m * num_blocks_N
                group_id = pid // num_pid_in_group
                first_pid_m = group_id * group_size_m
                group_size_m = min(group_size_m, num_blocks_M - first_pid_m)
                pid_m = first_pid_m + (pid % group_size_m)
                pid_n = (pid % num_pid_in_group) // group_size_m

                c_head_index = spatial(*c_head).map(blockIdx.y)
                a_head_index = broadcast_indices(c_head_index, a_head, c_head)
                b_head_index = broadcast_indices(c_head_index, b_head, c_head)

                # Global memory blocks for this CTA
                gA = tensor_view(
                    a[a_head_index][pid_m * bM : (pid_m + 1) * bM, :], TensorLayout((bM, K), (K, 1)), "global"
                )  # (bM, K)
                gB = tensor_view(
                    b[b_head_index][pid_n * bN : (pid_n + 1) * bN, :], TensorLayout((bN, K), (K, 1)), "global"
                )  # (bN, K)
                gC = tensor_view(
                    c[c_head_index][pid_m * bM : (pid_m + 1) * bM, pid_n * bN : (pid_n + 1) * bN],
                    TensorLayout((bM, bN), (N, 1)),
                    "global",
                )  # (bM, bN)

                gScaleA = tensor_view(
                    scale_a[a_head_index][:, pid_m * bM : (pid_m + 1) * bM],
                    TensorLayout((bM, bN, num_blocks_K), (1, 0, M)),
                    "global",
                )  # (bM, num_pid_K)
                gScaleB = tensor_view(
                    scale_b[b_head_index][pid_n, :], TensorLayout((bM, bN, num_blocks_K), (0, 0, 1)), "global"
                )  # (1,num_pid_K)

                # Shared memory buffers
                sA = make_tensor(self.a_dtype, TensorLayout((bM, bK, bP), (bK, 1, bM * bK)), "shared")  # (bM, bK, bP)
                sB = make_tensor(self.b_dtype, TensorLayout((bN, bK, bP), (bK, 1, bN * bK)), "shared")  # (bN, bK, bP)

                sScaleA = make_tensor(SCALE_DTYPE, TensorLayout((bM, bN, bP), (1, 0, bM)), "shared")
                sScaleB = make_tensor(SCALE_DTYPE, TensorLayout((bM, bN, bP), (0, 0, 1)), "shared")

                # Register memory buffers
                rA = make_tensor(self.a_dtype, layout_auto((bM, inst_k * bR)), "register")  # (bM, inst_k * bR)
                rB = make_tensor(self.b_dtype, layout_auto((bN, inst_k * bR)), "register")  # (bN, inst_k * bR)
                rScaleA = make_tensor(SCALE_DTYPE, layout_auto((bM, bN), (1, 0)), "register")
                rScaleB = make_tensor(SCALE_DTYPE, layout_auto((bM, bN), (0, 0)), "register")

                rC = make_tensor(self.acc_dtype, layout_auto((bM, bN), (bN, 1)), "register")
                rCAcc = make_tensor(self.acc_dtype, layout_auto((bM, bN), (bN, 1)), "register")  # accumulator rC
                fill(rC, 0.0)
                fill(rCAcc, 0.0)

                # partition for GMEM -> SMEM
                tAgA = partition_src(gA, auto_copy())  # (bM, bK, k), where k==ceil(K/bK)
                tAsA = partition_dst(sA, auto_copy())  # (bM, bK, bP)

                tBgB = partition_src(gB, auto_copy())  # (bN, bK, k)
                tBsB = partition_dst(sB, auto_copy())  # (bN, bK, bP)

                tAgScaleA = partition_src(gScaleA, auto_copy())
                tAsScaleA = partition_dst(sScaleA, auto_copy())

                tBgScaleB = partition_src(gScaleB, auto_copy())
                tBsScaleB = partition_dst(sScaleB, auto_copy())

                # prefill pipeline
                for s in range(bP - 1):
                    copy(auto_copy((bM, bK)), tAgA[:, :, s], tAsA[:, :, s])
                    copy(auto_copy((bN, bK)), tBgB[:, :, s], tBsB[:, :, s])
                    copy(auto_copy((bM, bN)), tAgScaleA[:, :, s], tAsScaleA[:, :, s])
                    copy(auto_copy((bM, bN)), tBgScaleB[:, :, s], tBsScaleB[:, :, s])
                    cp_async_commit_group()
                cp_async_wait_group(allow_on_fly_groups=bP - 2)
                syncthreads()

                K_TILE_MAX = (K + bK - 1) // bK
                INST_K_TILE_MAX = bK // inst_k
                k_pipe_read, k_pipe_write = 0, bP - 1

                # partition for SMEM -> RMEM.
                tXsA = partition_src(sA, auto_copy())  # (bM, inst_k, k, bP)
                tXrA = partition_dst(rA, auto_copy())  # (bM, inst_k, bR)

                tXsB = partition_src(sB, auto_copy())  # (bN, inst_k, k, bP)
                tXrB = partition_dst(rB, auto_copy())  # (bN, inst_k, bR)

                tXsScaleA = partition_src(sScaleA, auto_copy())
                tXrScaleA = partition_dst(rScaleA, auto_copy())

                tXsScaleB = partition_src(sScaleB, auto_copy())
                tXrScaleB = partition_dst(rScaleB, auto_copy())

                # prefill register buffer
                copy(auto_copy(), tXsA[:, :, 0, k_pipe_read], tXrA[:, :, 0])
                copy(auto_copy(), tXsB[:, :, 0, k_pipe_read], tXrB[:, :, 0])

                for ko in range(K_TILE_MAX):
                    for ki in range(INST_K_TILE_MAX):
                        if ki == INST_K_TILE_MAX - 1:  # advance read pipeline
                            cp_async_wait_group(allow_on_fly_groups=bP - 2)
                            syncthreads()

                        # prefetch next inst_k tile into RMEM
                        ki_tile_next = (ki + 1) % INST_K_TILE_MAX
                        copy(auto_copy(), tXsA[:, :, ki_tile_next, k_pipe_read], tXrA[:, :, (ki + 1) % bR])
                        copy(auto_copy(), tXsB[:, :, ki_tile_next, k_pipe_read], tXrB[:, :, (ki + 1) % bR])

                        if ki == 0:
                            copy(auto_copy((bM, bN)), tXsScaleA[:, :, k_pipe_read], tXrScaleA)
                            copy(auto_copy((bM, bN)), tXsScaleB[:, :, k_pipe_read], tXrScaleB)

                            if ko + bP - 1 < K_TILE_MAX:  # prefetch next K tile into SMEM
                                copy(auto_copy(), tAgA[:, :, ko + bP - 1], tAsA[:, :, k_pipe_write])
                                copy(auto_copy(), tBgB[:, :, ko + bP - 1], tBsB[:, :, k_pipe_write])
                                copy(auto_copy((bM, bN)), tAgScaleA[:, :, ko + bP - 1], tAsScaleA[:, :, k_pipe_write])
                                copy(auto_copy((bM, bN)), tBgScaleB[:, :, ko + bP - 1], tBsScaleB[:, :, k_pipe_write])
                            k_pipe_write = k_pipe_read
                            cp_async_commit_group()

                        if ki == INST_K_TILE_MAX - 2:
                            # advance read and write pipelines
                            k_pipe_read = 0 if k_pipe_read == bP - 1 else k_pipe_read + 1

                        # perform mma on current inst_k tile (RMEM,RMEM)->RMEM
                        mma(tiled_mma, rCAcc, tXrA[:, :, ki % bR], tXrB[:, :, ki % bR], rCAcc)

                    # apply scale
                    rC = rC + rCAcc * rScaleA * rScaleB
                    fill(rCAcc, 0.0)
                rC_out = rearrange(cast(rC, self.output_dtype), auto_layout, "register")

                tXrC = partition_src(rC_out, auto_copy())
                tXgC = partition_dst(gC, auto_copy())
                copy(auto_copy((bM, bN)), tXrC, tXgC)

            @hidet.script
            def launch(
                a: self.a_dtype[a_head + [M, K]],
                b: self.b_dtype[b_head + [N, K]],
                scale_a: SCALE_DTYPE[a_head + [num_blocks_K, M]],
                scale_b: SCALE_DTYPE[b_head + [num_blocks_N, num_blocks_K]],
                c: self.output_dtype[c_head + [M, N]],
            ):
                attrs.func_kind = "public"
                gemm(a, b, scale_a, scale_b, c)

        return script_module.ir_module()


class MatmulF8Operator(Operator):
    def __init__(self, a: Tensor, b: Tensor, acc_dtype: DataType, output_dtype: DataType):
        super().__init__(
            inputs=[a, b],
            attributes={'acc_dtype': acc_dtype, 'output_dtype': output_dtype},
            task=MatmulF8Task(input_like(a, 'a'), input_like(b, 'b'), acc_dtype, output_dtype),
        )


class MatmulF8ScaledOperator(Operator):
    def __init__(
        self,
        a: Tensor,
        b: Tensor,
        scale_a: Tensor,
        scale_b: Tensor,
        acc_dtype: DataType,
        output_dtype: DataType,
        bias: Tensor = None,
    ):
        if bias is not None:
            raise ValueError("bias is not supported for scaled matmul f8")
        super().__init__(
            inputs=[a, b, scale_a, scale_b],
            attributes={'acc_dtype': acc_dtype, 'output_dtype': output_dtype},
            task=MatmulF8ScaledTask(
                input_like(a, 'a'),
                input_like(b, 'b'),
                input_like(scale_a, 'scale_a'),
                input_like(scale_b, 'scale_b'),
                acc_dtype,
                output_dtype,
            ),
        )


def _matmul_f8(
    a: Tensor,
    b: Tensor,
    is_scaled: bool,
    scale_a: Tensor = None,
    scale_b: Tensor = None,
    bias: Tensor = None,
    acc_dtype: Union[DataType, str] = f32,
    output_dtype: Union[DataType, str] = None,
):
    """
    Do not call this function directly
    """

    if len(a.shape) < 2 or len(b.shape) < 2:
        raise ValueError(f"a and b must have at least 2 dimensions, got shape {a.shape} and {b.shape}")
    if (a.dtype != dtypes.f8e4m3 or b.dtype != dtypes.f8e4m3) and (
        a.dtype != dtypes.f8e5m2 or b.dtype != dtypes.f8e5m2
    ):
        raise ValueError(f"matmul_f8 only supports both operands being f8e4m3 or f8e5m2, got {a.dtype} and {b.dtype}")

    if output_dtype is None:
        output_dtype = a.dtype
    acc_dtype, output_dtype = data_type(acc_dtype), data_type(output_dtype)

    if is_scaled:
        return MatmulF8ScaledOperator(a, b, scale_a, scale_b, acc_dtype, output_dtype, bias).outputs[0]
    else:
        return MatmulF8Operator(a, b, acc_dtype, output_dtype).outputs[0]


def matmul_f8(
    a: Tensor, b: Tensor, acc_dtype: Union[DataType, str] = f32, output_dtype: Union[DataType, str] = None
) -> Tensor:
    """
    Matrix multiplication for f8e4m3 and f8e5m2 data types.

    Parameters
    ----------
    a : Tensor
        First input tensor. Must be (...,M,K) K-major.
    b : Tensor
        Second input tensor. Must be (...,N,K) K-major.
    acc_dtype : Optional[DataType]
        Data type for the accumulator.
    output_dtype : Optional[DataType]
        Data type for the output tensor. If None, it will be the same as a and b.
    """

    return _matmul_f8(a, b, False, acc_dtype=acc_dtype, output_dtype=output_dtype)


def matmul_f8_scaled(
    a: Tensor,
    b: Tensor,
    scale_a: Tensor,
    scale_b: Tensor,
    bias: Tensor = None,
    acc_dtype: Union[DataType, str] = f32,
    output_dtype: Union[DataType, str] = None,
):
    """
    Scaled matrix multiplication for f8e4m3 and f8e5m2 data types.

    Parameters
    ----------
    a : Tensor
        First input tensor.
    b : Tensor
        Second input tensor.
    scale_a : Tensor
        Block-wise Scale factor for a.
    scale_b : Tensor
        Block-wise Scale factor for b.
    bias : Optional[Tensor]
        Bias tensor.
    acc_dtype : Optional[DataType]
        Data type for the accumulator.
    output_dtype : Optional[DataType]
        Data type for the output tensor. If None, it will be the same as a and b.
    """

    return _matmul_f8(a, b, True, scale_a, scale_b, bias, acc_dtype, output_dtype)
