from fmot.nn.temporal_unfold import TemporalUnfold1d
from fmot.nn import atomics, SuperStructure
from fmot.nn.composites import Softmax
import torch
from torch import nn
import math


class SlidingSelfAttention(nn.Module):
    def __init__(self, in_features: int, winlen: int, d_model: int, n_heads: int):
        super().__init__()
        self.in_features = in_features
        self.winlen = winlen
        self.d_model = d_model
        self.n_heads = n_heads

        self.lin = nn.Linear(in_features, 3 * d_model, bias=False)
        self.unfold = TemporalUnfold1d(winlen, dilation=1)

        self.attn_scale = math.sqrt(1 / d_model)

    def forward(self, x):
        B, N, F = x.shape
        W = self.winlen
        D = self.d_model

        # project to Q, K, V
        q, k, v = torch.chunk(self.lin(x), 3, dim=-1)

        # Each of these tensors is of shape (B, N, W*D)
        ku = self.unfold(k.transpose(1, 2)).transpose(1, 2)
        vu = self.unfold(v.transpose(1, 2)).transpose(1, 2)

        # Reshape to (B, N, W, D)
        kr = torch.reshape(ku, (B, N, W, D))
        vr = torch.reshape(vu, (B, N, W, D))

        # Attention!
        # q.unsqueeze(-2) shape: (B, N, 1, d)
        # kr shape: (B, N, W, d)
        # q @ kr.T: (B, N, 1, W)
        logits = torch.matmul(q.unsqueeze(-2), kr.transpose(-1, -2))
        attn = torch.softmax(logits, dim=-1)
        outs = torch.matmul(attn, vr)  # (B, N, 1, d)
        outs = torch.squeeze(outs, -2)
        return outs


def get_gamma(d_model, winlen):
    mat = torch.zeros(winlen, winlen * d_model)


class QATSlidingSelfAttention(SuperStructure):
    def __init__(self, in_features: int, winlen: int, d_model: int, n_heads: int):
        super().__init__()
        self.in_features = in_features
        self.winlen = winlen
        self.d_model = d_model
        self.n_heads = n_heads

        self.lin = nn.Linear(in_features, 3 * d_model, bias=False)
        self.unfold = TemporalUnfold1d(winlen, dilation=1)
        self.chunk = atomics.Chunk(3, dim=-1)
        self.kv_chunk = atomics.Chunk(self.winlen, dim=-1)
        self.sim_mul = atomics.VVMul()
        self.sim_sum = atomics.Sum(-1)
        self.sim_cat = atomics.Cat(-1)
        self.softmax_scale = atomics.VIMul(math.sqrt(1 / d_model))

        # self.softmax =

    @torch.jit.ignore
    def forward(self, x):
        B, N, F = x.shape
        W = self.winlen
        D = self.d_model

        # project to Q, K, V
        q, k, v = self.chunk(self.lin(x))

        # Each of these tensors is of shape (B, N, W*D)
        ku = self.unfold(k.transpose(1, 2)).transpose(1, 2)
        vu = self.unfold(v.transpose(1, 2)).transpose(1, 2)

        ks = self.kv_chunk(ku)
        # vs = self.kv_chunk(vu)

        sims = []
        for i in range(self.winlen):
            sims.append(self.sim_sum(self.sim_mul(ks[i], q)))

        sim = self.sim_cat(sims)
        sim = self.softmax_scale(sim)

        # # Reshape to (B, N, W, D)
        # kr = torch.reshape(ku, (B, N, W, D))
        # vr = torch.reshape(vu, (B, N, W, D))

        # # Attention!
        # # q.unsqueeze(-2) shape: (B, N, 1, d)
        # # kr shape: (B, N, W, d)
        # # q @ kr.T: (B, N, 1, W)
        # logits = torch.matmul(q.unsqueeze(-2), kr.transpose(-1, -2))
        # attn = torch.softmax(logits, dim=-1)
        # outs = torch.matmul(attn, vr) # (B, N, 1, d)
        # outs = torch.squeeze(outs, -2)
        # return outs


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    model = QATSlidingSelfAttention(64, 5, 64, 1)

    x = torch.zeros(8, 10, 64)
    x[:, 0] += 1

    with torch.no_grad():
        y = model(x)

    plt.plot(y[0, :, 0])
    plt.show()
