from .unittest_objects import UTM, TestSet, TestLibrary
import torch
from torch import nn
from itertools import product as iterprod
import numpy as np
from ...sparse import pencil_pruning
import fmot
from fmot.nn import PrecisionSplit

atomic_library = TestLibrary("atomic")

INCLUDE_IMM = False

"""
Elementwise Add/Subtract/Multiply Tests
"""


class VVAddUTM(UTM):
    def __init__(self, hidden_size, alpha):
        """
        :param int hidden_size: input dimensionality
        :param float alpha: y's scaling relative to x in _get_random_inputs
        """
        super().__init__()
        self.hidden_size = hidden_size
        self.alpha = alpha

    def forward(self, x, y):
        return x + y

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.hidden_size)
        y = self.alpha * torch.randn(batch_size, self.hidden_size)
        x.dimensions = ["B", "F"]
        y.dimensions = ["B", "F"]
        return x, y


vvadd_set = TestSet(
    utm=VVAddUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["vvadd"] = vvadd_set


class VIAddUTM(UTM):
    def __init__(self, hidden_size, imm):
        """
        :param int hidden_size: input dimensionality
        :param float/int imm: scalar immediate to be added
        """
        super().__init__()
        self.hidden_size = hidden_size
        self.imm = imm

    def forward(self, x):
        return x + self.imm

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.hidden_size)
        x.dimensions = ["B", "F"]
        return x


viadd_set = TestSet(
    utm=VIAddUTM,
    par_sets=[
        dict(hidden_size=H, imm=i) for H, i in iterprod([16], [-10, -0.1, 0.1, 5])
    ],
)
if INCLUDE_IMM:
    atomic_library["viadd"] = viadd_set


class VIAddStaticUTM(UTM):
    def __init__(self, hidden_size, alpha):
        """
        :param int hidden_size: input dimensionality
        :param float/int imm: scalar immediate to be added
        """
        super().__init__()
        self.hidden_size = hidden_size
        self.alpha = alpha

    def forward(self, x):
        return x + 0.73

    def _get_random_inputs(self, batch_size):
        x = self.alpha * torch.randn(batch_size, self.hidden_size)
        x.dimensions = ["B", "F"]
        return x


viaddstatic_set = TestSet(
    utm=VIAddStaticUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([16], [0.1, 1, 10])],
)
atomic_library["viadd_static"] = viaddstatic_set


class IVSubUTM(VIAddUTM):
    def forward(self, x):
        return self.imm - x


ivsub_set = TestSet(
    utm=IVSubUTM,
    par_sets=[dict(hidden_size=H, imm=i) for H, i in iterprod([16], [-10, 0.1, 5, 3])],
)
if INCLUDE_IMM:
    atomic_library["ivsub"] = ivsub_set


class IVSubStaticUTM(VIAddStaticUTM):
    def forward(self, x):
        return 0.73 - x


ivsubstatic_set = TestSet(
    utm=IVSubStaticUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
if INCLUDE_IMM:
    atomic_library["ivsub_static"] = ivsubstatic_set


class VVSubUTM(VVAddUTM):
    def forward(self, x, y):
        return x - y


vvsub_set = TestSet(
    utm=VVSubUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["vvsub"] = vvsub_set


class VVMulUTM(VVAddUTM):
    def forward(self, x, y):
        return x * y


class NegVVAddUTM(VVAddUTM):
    def forward(self, x, y):
        return -x + y


negvvadd_set = TestSet(
    utm=NegVVAddUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["negvvadd"] = negvvadd_set


class NegVVSubUTM(VVAddUTM):
    def forward(self, x, y):
        return -x - y


negvvsub_set = TestSet(
    utm=NegVVSubUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["negvvsub"] = negvvsub_set

vvmul_set = TestSet(
    utm=VVMulUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["vvmul"] = vvmul_set


class VIMulUTM(VIAddUTM):
    def forward(self, x):
        return x * self.imm


vimul_set = TestSet(
    utm=VIMulUTM,
    par_sets=[
        dict(hidden_size=H, imm=i)
        for H, i in iterprod([8, 16], [-10, -1, -0.1, 0.1, 1, 10])
    ],
)
if INCLUDE_IMM:
    atomic_library["vimul"] = vimul_set


class VIMulStaticUTM(VIAddStaticUTM):
    def forward(self, x):
        return 0.73 * x


vimulstatic_set = TestSet(
    utm=VIMulStaticUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["vimul_static"] = vimulstatic_set

"""
Activation Function Tests
"""


class ActUTM(UTM):
    def __init__(self, fn, hidden_size, alpha):
        super().__init__()
        self.fn = fn
        self.hidden_size = hidden_size
        self.alpha = alpha
        self.interpolate = False

    def forward(self, x):
        return self.fn(x)

    def _get_random_inputs(self, batch_size):
        x = self.alpha * torch.randn(batch_size, self.hidden_size)
        x.dimensions = ["B", "F"]
        return x


class ReluUTM(ActUTM):
    def __init__(self, hidden_size, alpha):
        super().__init__(torch.relu, hidden_size, alpha)


relu_set = TestSet(
    utm=ReluUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["relu"] = relu_set


class TanhUTM(ActUTM):
    def __init__(self, hidden_size, alpha):
        super().__init__(torch.tanh, hidden_size, alpha)


tanh_set = TestSet(
    utm=TanhUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["tanh"] = tanh_set


class SigmoidUTM(ActUTM):
    def __init__(self, hidden_size, alpha):
        super().__init__(torch.sigmoid, hidden_size, alpha)


sigmoid_set = TestSet(
    utm=SigmoidUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([8, 16], [0.1, 1, 10])],
)
atomic_library["sigmoid"] = sigmoid_set


class GeluUTM(ActUTM):
    def __init__(self, hidden_size, alpha):
        super().__init__(torch.nn.functional.gelu, hidden_size, alpha)


gelu_set = TestSet(
    utm=GeluUTM,
    par_sets=[dict(hidden_size=H, alpha=a) for H, a in iterprod([16], [0.1, 1, 10])],
)
atomic_library["gelu"] = gelu_set

"""
MatMul/AddMM Test cases
"""


class RowMajorMatmulUTM(UTM):
    def __init__(self, input_size, hidden_size, alpha):
        super().__init__()
        self.input_size = input_size
        self.weight = nn.Parameter(torch.randn(hidden_size, input_size))
        self.alpha = alpha

    def forward(self, x):
        return torch.matmul(x, self.weight.t())

    def _get_random_inputs(self, batch_size):
        x = self.alpha * torch.randn(batch_size, self.input_size)
        x.dimensions = ["B", "F"]
        return x


row_major_matmul_set = TestSet(
    utm=RowMajorMatmulUTM,
    par_sets=[
        dict(input_size=D, hidden_size=H, alpha=a)
        for D, H, a in iterprod([32, 256, 512], [32, 256, 512], [1])
    ],
)
atomic_library["row_major_matmul"] = row_major_matmul_set


class ColMajorMatmulUTM(UTM):
    def __init__(self, input_size, hidden_size, alpha):
        super().__init__()
        self.input_size = input_size
        self.weight = nn.Parameter(torch.randn(input_size, hidden_size))
        self.alpha = alpha

    def forward(self, x):
        return torch.matmul(x, self.weight)

    def _get_random_inputs(self, batch_size):
        x = self.alpha * torch.randn(batch_size, self.input_size)
        x.dimensions = ["B", "F"]
        return x


col_major_matmul_set = TestSet(
    utm=ColMajorMatmulUTM,
    par_sets=[
        dict(input_size=D, hidden_size=H, alpha=a)
        for D, H, a in iterprod([32, 256, 512], [32, 256, 512], [1])
    ],
)
atomic_library["col_major_matmul"] = row_major_matmul_set


class RowMajorAddMMUTM(UTM):
    def __init__(self, input_size, hidden_size, alpha):
        super().__init__()
        self.lin = nn.Linear(input_size, hidden_size)
        self.input_size = input_size
        self.alpha = alpha

    def forward(self, x):
        return self.lin(x)

    def _get_random_inputs(self, batch_size):
        x = self.alpha * torch.randn(batch_size, self.input_size)
        x.dimensions = ["B", "F"]
        return x


row_major_addmm_set = TestSet(
    utm=RowMajorAddMMUTM,
    par_sets=[
        dict(input_size=D, hidden_size=H, alpha=a)
        for D, H, a in iterprod([32, 256, 512], [32, 256, 512], [1])
    ],
)
atomic_library["row_major_addmm"] = row_major_addmm_set


class SparseReLUUTM(UTM):
    def __init__(self, hidden_size, theta):
        super().__init__()
        self.theta = nn.Parameter(torch.ones(hidden_size) * theta)
        self.hidden_size = hidden_size

    def forward(self, x):
        return (x - self.theta).relu()

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.hidden_size)
        x.dimensions = ["B", "F"]
        return x


sparse_relu_set = TestSet(
    utm=SparseReLUUTM,
    par_sets=[
        dict(hidden_size=H, theta=T)
        for H, T in iterprod([8, 16], np.linspace(-2.0, 2.0, 10))
    ],
)
atomic_library["sparse_relu"] = sparse_relu_set


class USProdUTM(UTM):
    def __init__(self, input_size, hidden_size, par_sparsity, bias, theta):
        super().__init__()
        self.input_size = input_size
        self.linear = nn.Linear(input_size, hidden_size, bias=bias)
        pencil_pruning(self.linear, "weight", par_sparsity, 8)
        self.theta = theta

    def forward(self, x):
        x_sp = (x - self.theta).relu()
        return self.linear(x_sp)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.input_size)
        x.dimensions = ["B", "F"]
        return x


usprod_pars = []
for D, H, P, B, T in iterprod([64, 256, 512], [256], [0.8, 0.85, 0.9], [True], [1]):
    usprod_pars.append(
        dict(input_size=D, hidden_size=H, par_sparsity=P, bias=B, theta=T)
    )
atomic_library["usprod"] = TestSet(utm=USProdUTM, par_sets=usprod_pars)


class UVProdUTM(UTM):
    def __init__(self, input_size, hidden_size, par_sparsity, bias):
        super().__init__()
        self.input_size = input_size
        self.linear = nn.Linear(input_size, hidden_size, bias=bias)
        self.par_sparsity = par_sparsity
        self.numel = par_sparsity * input_size * hidden_size
        pencil_pruning(self.linear, "weight", par_sparsity, 8)

    def forward(self, x):
        return self.linear(x)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.input_size)
        x.dimensions = ["B", "F"]
        return x


uvprod_pars = []
for D, H, P, B in iterprod([64, 256, 512], [256], [0.8, 0.85, 0.9], [True]):
    uvprod_pars.append(dict(input_size=D, hidden_size=H, par_sparsity=P, bias=B))
atomic_library["uvprod"] = TestSet(utm=UVProdUTM, par_sets=uvprod_pars)

from typing import List, Tuple
from torch import Tensor


class CatUTM(UTM):
    def __init__(self, D0, D1):
        super().__init__()
        self.D0 = D0
        self.D1 = D1

    def forward(self, x0, x1):
        return torch.cat([x0, x1], dim=-1)

    def _get_random_inputs(self, batch_size):
        x, y = torch.randn(batch_size, self.D0), torch.randn(batch_size, self.D1)
        dimensions = ["B", "F"]
        x.dimensions = dimensions
        y.dimensions = dimensions
        return x, y


atomic_library["cat"] = TestSet(
    utm=CatUTM,
    par_sets=[dict(D0=D0, D1=D1) for D0, D1 in iterprod([3, 5, 8], [3, 5, 8])],
)


class ChunkUTM(UTM):
    def __init__(self, D, nchunks):
        super().__init__()
        self.D = D
        self.nchunks = nchunks

    def forward(self, x: Tensor) -> List[Tensor]:
        return torch.chunk(x, self.nchunks, dim=-1)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.D)
        x.dimensions = ["B", "F"]
        return x


atomic_library["chunk"] = TestSet(
    utm=ChunkUTM, par_sets=[dict(D=D, nchunks=N) for D, N in iterprod([32, 34], [2])]
)
atomic_library["null_chunk"] = TestSet(utm=ChunkUTM, par_sets=[dict(D=32, nchunks=1)])


class Gt0UTM(UTM):
    def __init__(self, D):
        super().__init__()
        self.D = D
        self.gt = fmot.nn.Gt0()

    def forward(self, x):
        return self.gt(x)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.D)
        x.dimensions = ["B", "F"]
        return x


atomic_library["gt0"] = TestSet(utm=Gt0UTM, par_sets=[dict(D=D) for D in [16, 32, 64]])


class ShiftUTM(UTM):
    def __init__(self, shamt, D):
        super().__init__()
        self.D = D
        self.shift = fmot.nn.Shift(shamt)

    def forward(self, x):
        return self.shift(x)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.D)
        x.dimensions = ["B", "F"]
        return x


atomic_library["shift"] = TestSet(
    utm=ShiftUTM,
    par_sets=[dict(D=D, shamt=S) for D, S in iterprod([16, 32, 64], [-3, 3])],
)


class BlockDiagLinearUTM(UTM):
    def __init__(self, din, dout, num_blocks, bias=True):
        super().__init__()
        self.din = din
        self.dout = dout
        self.num_blocks = num_blocks
        self.weight = fmot.nn.BlockDiagLinear(din, dout, num_blocks, bias)

    def forward(self, x):
        return self.weight(x)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.din)
        x.dimensions = ["B", "F"]
        return x


atomic_library["block_diag_linear"] = TestSet(
    utm=BlockDiagLinearUTM,
    par_sets=[
        dict(din=din, dout=dout, num_blocks=N, bias=B)
        for din, dout, N, B in iterprod([64, 128], [64, 128], [4, 8], [True])
    ],
)


class PrecisionSplitUTM(UTM):
    def __init__(self, bits_a, bits_b, num_channels=128):
        super().__init__(skip_mixed=True, skip_standard=True)
        self.D = num_channels
        self.bits_a = bits_a
        self.bits_b = bits_b

        self.prec_split = PrecisionSplit([bits_a, bits_b], [16, 16])

    def forward(self, x):
        a, b = self.prec_split(x)

        return a, b

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.D)
        x.dimensions = ["B", "F"]
        return x


atomic_library["prec_split"] = TestSet(
    utm=PrecisionSplitUTM,
    par_sets=[
        dict(bits_a=bits_a, bits_b=bits_b)
        for bits_a, bits_b in iterprod([7, 9], [7, 9])
    ],
)
