from torch import nn


class SuperStructure(nn.Module):
    def __init__(self):
        super().__init__()


class ProtectedModule(nn.Module):
    def __init__(self):
        super().__init__()


SUPERSTRUCT_DIC = {
    SuperStructure,
}
