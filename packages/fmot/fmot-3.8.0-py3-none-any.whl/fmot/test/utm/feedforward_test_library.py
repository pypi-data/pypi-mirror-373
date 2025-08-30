from .unittest_objects import UTM, TestSet, TestLibrary
import torch
from torch import nn
import fmot
from torch.nn import functional as F
from itertools import product as iterprod
import numpy as np

feedforward_library = TestLibrary("ff")


class LayerNormUTM(UTM):
    def __init__(self, D):
        super().__init__()
        self.D = D
        self.ln = nn.LayerNorm(D)

    def forward(self, x):
        return self.ln(x)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.D)
        x.dimensions = ["B", "F"]
        return x


feedforward_library["layernorm"] = TestSet(
    utm=LayerNormUTM, par_sets=[{"D": D} for D in [128, 256]]
)


class SoftmaxUTM(UTM):
    def __init__(self, D, temp):
        super().__init__()
        self.D = D
        self.temp = temp

    def forward(self, x):
        return F.softmax(x, dim=-1)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.D) / self.temp
        x.dimensions = ["B", "F"]
        return x


feedforward_library["softmax"] = TestSet(
    utm=SoftmaxUTM,
    par_sets=[dict(D=D, temp=T) for D, T in iterprod([128, 256, 512], [1, 0.5])],
)


class MultilayerLinearUTM(UTM):
    def __init__(self, D, L):
        super().__init__()
        self.D = D
        self.layers = nn.ModuleList()
        for i in range(L):
            self.layers.append(nn.Linear(D, D))

    def forward(self, x):
        for l in self.layers:
            x = l(x).relu()
        return x

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.D)
        x.dimensions = ["B", "F"]
        return x


feedforward_library["multilayer_linear"] = TestSet(
    utm=MultilayerLinearUTM,
    par_sets=[dict(D=D, L=L) for D, L in iterprod([16, 32, 128], [2, 4])],
)

feedforward_library["large_linear"] = TestSet(
    utm=MultilayerLinearUTM,
    par_sets=[
        dict(D=620, L=1),
    ],  # from anomaly_detection MLCommonsTiny Perf benchmark
)


class InterpolatingLUT_UTM(UTM):
    def __init__(self, function, D):
        super().__init__()
        self.interpolate = True
        self.function = function
        self.D = D

    def forward(self, x):
        return self.function(x)

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.D).abs() + 1e-7
        x.dimensions = ["B", "F"]
        return x


feedforward_library["interpolating_lut"] = TestSet(
    utm=InterpolatingLUT_UTM,
    par_sets=[dict(D=64, function=fn) for fn in [torch.tanh, torch.sigmoid, torch.exp]],
)

feedforward_library["add_identity_telescoping_lut"] = TestSet(
    utm=InterpolatingLUT_UTM,
    par_sets=[dict(D=64, function=fn) for fn in [torch.log, torch.log10, torch.log2]],
)

feedforward_library["mul_identity_telescoping_lut"] = TestSet(
    utm=InterpolatingLUT_UTM,
    par_sets=[dict(D=64, function=fn) for fn in [torch.reciprocal, torch.rsqrt]],
)


class CatChunkUTM(UTM):
    def __init__(self, Din):
        super().__init__()
        self.Din = Din

    def forward(self, x):
        x0, x1 = torch.chunk(x, 2, dim=1)
        return torch.cat([x0, x1], dim=1)

    def _get_random_inputs(self, batch_size):
        return torch.randn(batch_size, self.Din)


class CatReLUChunkUTM(CatChunkUTM):
    def forward(self, x):
        x0, x1 = torch.chunk(x, 2, dim=1)
        x0 = x0.relu()
        x1 = x1.relu()
        return torch.cat([x0, x1], dim=1)


feedforward_library["cat_chunk"] = TestSet(
    utm=CatChunkUTM, par_sets=[dict(Din=D) for D in [8, 16, 24]]
)

feedforward_library["cat_relu_chunk"] = TestSet(
    utm=CatReLUChunkUTM, par_sets=[dict(Din=D) for D in [8, 16, 24]]
)


class ReorderCatChunkUTM(UTM):
    def __init__(self, Din):
        super().__init__()
        self.Din = Din
        assert Din % 2 == 0

    def forward(self, x, y):
        xy = torch.cat([x, y], dim=1)
        a, b, c, d = torch.chunk(xy, 4, dim=1)
        badc = torch.cat([b, a, d, c], dim=1)
        ba, dc = torch.chunk(badc, 2, dim=1)
        return ba, dc

    def _get_random_inputs(self, batch_size):
        return torch.randn(batch_size, self.Din), torch.randn(batch_size, self.Din)


feedforward_library["reordering_cat_chunk"] = TestSet(
    utm=ReorderCatChunkUTM,
    par_sets=[dict(Din=D) for D in [128, 256, 102, 384, 512, 768]],
)


class FFTUTM(UTM):
    def __init__(self, nfft, stages):
        super().__init__()
        self.nfft = nfft
        self.stages = stages
        self.fft = fmot.nn.FFT(nfft, stages)

    def forward(self, x):
        return self.fft(x)

    def _get_random_inputs(self, batch_size):
        return torch.randn(batch_size, self.nfft)


feedforward_library["fft"] = TestSet(
    utm=FFTUTM,
    par_sets=[dict(nfft=N, stages=S) for N, S in iterprod([256], [0, 1, 2, 3])],
)


class FCStackReLU(UTM):
    def __init__(self, Din, gain):
        super().__init__()
        self.Din = Din
        self.gain = gain
        self.lin0 = nn.Linear(Din, Din)
        self.lin1 = nn.Linear(Din, Din)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.lin0(x)
        x = self.relu(x)
        x = self.lin1(x)
        x = torch.sigmoid(x)
        return x

    def _get_random_inputs(self, batch_size):
        return torch.randn(batch_size, self.Din) * self.gain


feedforward_library["fc_stack_relu"] = TestSet(
    utm=FCStackReLU,
    par_sets=[dict(Din=D, gain=G) for D, G in iterprod([256], [32, 64, 128, 256])],
)


class FCStackReLU6(FCStackReLU):
    def __init__(self, Din, gain):
        super().__init__(Din, gain)
        self.relu = nn.ReLU6()
        self.allow_fqir_offby = 0


feedforward_library["fc_stack_relu6"] = TestSet(
    utm=FCStackReLU6,
    par_sets=[dict(Din=D, gain=G) for D, G in iterprod([256], [32, 64, 128, 256])],
)


class MagPhaseUTM(UTM):
    def __init__(self, size: int):
        super().__init__()
        self.magphase = fmot.nn.signal_processing.MagPhase()
        self.size = size

    def _get_random_inputs(self, batch_size):
        return (torch.randn(batch_size, self.size), torch.randn(batch_size, self.size))

    def forward(self, re, im):
        return self.magphase(re, im)


feedforward_library["magphase"] = TestSet(utm=MagPhaseUTM, par_sets=[{"size": 128}])


class PReLU_UTM(UTM):
    def __init__(self, ndim: int, size: int, num_parameters=1):
        super().__init__()
        self.prelu = nn.PReLU(num_parameters=num_parameters)
        self.size = size
        self.ndim = ndim
        if ndim == 3:
            self.seq_dim = 2

    def _get_random_inputs(self, batch_size):
        shape = [batch_size, self.size]
        for i in range(self.ndim - 2):
            shape += [i + 7]

        return torch.randn(*shape)

    def forward(self, x):
        return self.prelu(x)


prelu_params = [
    dict(ndim=N, size=S, num_parameters=1) for N, S in iterprod([2, 3], [16])
]
prelu_params += [
    dict(ndim=N, size=S, num_parameters=S) for N, S in iterprod([2, 3], [16, 7])
]

# TODO: need to fix issues with prelu when ndim=3

# feedforward_library["prelu"] = TestSet(
#     utm=PReLU_UTM,
#     par_sets=prelu_params
# )


class GLU_UTM(UTM):
    def __init__(self, dim: int, ndim: int, seq_dim: int = None, size: int = 18):
        super().__init__()
        self.glu = nn.GLU(dim=dim)
        self.size = size
        self.seq_dim = seq_dim
        self.ndim = ndim

    def _get_random_inputs(self, batch_size):
        shape = [batch_size] + [self.size] * (self.ndim - 1)

        return torch.randn(*shape)

    def forward(self, x):
        return self.glu(x)


glu_params = [
    {"dim": 1, "ndim": 2, "seq_dim": None},
    {"dim": 1, "ndim": 3, "seq_dim": 2},
    {"dim": 2, "ndim": 3, "seq_dim": 1},
]
feedforward_library["glu"] = TestSet(utm=GLU_UTM, par_sets=glu_params)
