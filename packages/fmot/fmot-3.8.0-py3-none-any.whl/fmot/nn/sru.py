import torch
from torch import nn, Tensor
from typing import *


@torch.jit.script
def sru_pointwise(
    x: Tensor,
    wx: Tensor,
    vf: Tensor,
    vr: Tensor,
    bf: Tensor,
    br: Tensor,
    feat_dim: int,
    seq_dim: int,
) -> Tuple[Tensor, Tensor]:
    h3 = wx.shape[feat_dim]
    assert h3 % 3 == 0
    h = h3 // 3
    assert x.shape[feat_dim] == h

    xf, xc, xr = wx.chunk(3, dim=feat_dim)

    xf = xf + bf
    xr = xr + br

    shape = x.shape
    del shape[seq_dim]
    ct = torch.zeros(shape, device=x.device)

    outputs: List[Tensor] = []
    for xt, xft, xct, xrt in zip(
        x.unbind(seq_dim), xf.unbind(seq_dim), xc.unbind(seq_dim), xr.unbind(seq_dim)
    ):
        ft = torch.sigmoid(xft + vf * ct)
        rt = torch.sigmoid(xrt + vr * ct)
        ct = ft * ct + (1 - ft) * xct
        ht = rt * ct + (1 - rt) * xt

        outputs.append(ht)

    output = torch.stack(outputs, dim=seq_dim)
    return output, ct


class SRU(nn.Module):
    """Simple Recurrent Unit
    see [paper](https://arxiv.org/pdf/1709.02755.pdf) for details

    Arguments:
        hidden_size (int): hidden size for SRU cell. Input and output dimensionality
            of SRU is the same.
        batch_first (bool): If True, input and output sequences have shape (batch, time, feature).
            If False, sequences have shape (time, batch, feature). Default True.
    """

    def __init__(self, hidden_size: int, batch_first: bool = True):
        super().__init__()
        self.hidden_size = hidden_size
        self.batch_first = batch_first

        self.u = nn.Linear(hidden_size, 3 * hidden_size, bias=False)

        self.vf = nn.Parameter(torch.randn(hidden_size))
        self.vr = nn.Parameter(torch.randn(hidden_size))
        self.bf = nn.Parameter(torch.zeros(hidden_size))
        self.br = nn.Parameter(torch.zeros(hidden_size))

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        ux = self.u(x)

        if self.batch_first:
            feat_dim = 2
            seq_dim = 1
        else:
            feat_dim = 2
            seq_dim = 0

        y, cfinal = sru_pointwise(
            x,
            ux,
            self.vf,
            self.vr,
            self.bf,
            self.br,
            feat_dim=feat_dim,
            seq_dim=seq_dim,
        )
        return y, cfinal
