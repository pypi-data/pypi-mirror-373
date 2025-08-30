class Precision:
    def __init__(self, name: str, bitwidth: int):
        self.name = name
        self.bitwidth = bitwidth

        if bitwidth not in [8, 16, 24]:
            raise ValueError(f"bitwidth {bitwidth} is not allowed")

    def range(self):
        return [-(2 ** (self.bitwidth - 1)), 2 ** (self.bitwidth - 1) - 1]

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Precision):
            return self.bitwidth == other.bitwidth
        elif isinstance(other, int):
            return self.bitwidth == other
        else:
            raise RuntimeError(
                f"Comparision between {self} and {other} failed, "
                "expected other to be of type Precision or int."
            )


int8 = Precision("int8", 8)
int16 = Precision("int16", 16)
int24 = Precision("int24", 24)


def get_precision(bits: int):
    return {8: int8, 16: int16, 24: int24}[bits]
