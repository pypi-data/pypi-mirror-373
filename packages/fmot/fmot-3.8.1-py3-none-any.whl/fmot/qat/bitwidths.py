"""Manage precision levels for hardware integer arithmetic"""


class Bitwidth:
    """Represents a precision level"""

    def __init__(self, bitwidth, role=None):
        self.bitwidth = bitwidth
        self.role = role

    def set_role(self, role):
        self.role = role

    def __repr__(self):
        return f"fqint{self.bitwidth}"

    def __eq__(self, other):
        assert isinstance(other, Bitwidth), f"other={other} is not a Bitwidth"
        return other.bitwidth == self.bitwidth


fqint4 = Bitwidth(4)
fqint8 = Bitwidth(8)
fqint16 = Bitwidth(16)
fqint24 = Bitwidth(24)


class BitwidthConfig:
    """A container that stores bitwidths for activations, weight matrices, and lookup table addresses

    Args:
        activations: Activation bitwidth
        weights: Weight matrix bitwidth
        lut: LUT address bitwidth (default fqint8)
    """

    def __init__(self, activations, weights, lut=fqint8):
        act = Bitwidth(activations, "activations")
        self.activations = act  #: bitwidth for activations, and 1D parameters
        weight = Bitwidth(weights, "weights")
        self.weights = weight  #: bitwidth of parameters with at least 2 dimensions (matrices, etc.)
        lut = Bitwidth(lut, "lut")
        self.lut = lut  #: bitwidth of LUT address space, standard is fqint8 across the hardware

    def get_bitwidth(self, role):
        assert role in ["activations", "weights", "lut"]
        return getattr(self, role)


double = BitwidthConfig(activations=16, weights=8, lut=8)
standard = BitwidthConfig(activations=8, weights=4, lut=8)
eights = BitwidthConfig(activations=8, weights=8, lut=8)

bw_conf_dict = {"double": double, "standard": standard, "eights": eights}
