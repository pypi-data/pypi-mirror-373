import torch
from torch import nn, Tensor
from fmot.nn import GMACv2
from fmot.precisions import Precision


class Cast16(nn.Module):
    def __init__(self):
        super().__init__()
        self.gmac = GMACv2(16, torch.tensor([1]))

    def forward(self, x):
        return self.gmac([], [], [x])


class Multiply(nn.Module):
    def __init__(self, act_precision: Precision):
        super().__init__()
        self.gmac = GMACv2(act_precision)

    def forward(self, x, y):
        return self.gmac([x], [y], [])


class Add(nn.Module):
    def __init__(self, act_precision: Precision):
        super().__init__()
        self.gmac = GMACv2(act_precision, torch.tensor([1, 1]))

    def forward(self, x, y):
        return self.gmac([], [], [x, y])


class ComplexMultiply(nn.Module):
    def __init__(self, act_precision: Precision):
        super().__init__()
        self.neg = GMACv2(act_precision, torch.tensor([-1]))
        self.gmac = GMACv2(act_precision)

    def forward(self, x_re, x_im, y_re, y_im):
        # z_re = x_re * y_re - x_im * y_im
        # z_im = x_re * y_im + x_im * y_re

        neg_x_im = self.neg([], [], [x_im])

        z_re = self.gmac([x_re, neg_x_im], [y_re, y_im], [])
        z_im = self.gmac([x_re, x_im], [y_im, y_re], [])

        return z_re, z_im
