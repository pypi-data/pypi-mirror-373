from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class OpCount:
    """
    Dataclass object holding opcount values, with the ability to convert
    opcounts into energy estimates
    """

    mem_read_bytes: int = 0
    mem_write_bytes: int = 0
    acc_read_numel: int = 0
    acc_write_numel: int = 0
    table_read_bytes: int = 0
    # Logical operation counting
    macs: int = 0
    emacs: int = 0  # effective macs (if matrix and vector were dense)
    additions: int = 0
    multiplies: int = 0
    luts: int = 0
    other_logic: int = 0

    def weight(self):
        return (
            self.mem_read_bytes * 8
            + self.mem_write_bytes * 8
            + self.table_read_bytes * 8
            + self.acc_read_numel * 8
            + self.acc_write_numel * 8
        )

    def energy(self, config=None):
        raise NotImplementedError(
            "Energy estimation not enabled -- please use the behavioral simulator instead."
        )

    def __add__(self, other):
        assert isinstance(other, OpCount)
        kwargs = {}
        self_dict = asdict(self)
        other_dict = asdict(other)
        for k, v in self_dict.items():
            kwargs[k] = v + other_dict[k]
        return OpCount(**kwargs)

    def _mul(self, other):
        if isinstance(other, np.int64):
            other = int(other)
        if isinstance(other, (int, float)):
            kwargs = {}
            for k, v in asdict(self).items():
                kwargs[k] = v * other
            return OpCount(**kwargs)
        else:
            raise ValueError(
                f"Opcount cannot be multiplied by type: {type(other)}"
                + f"other: {other}"
            )

    def __mul__(self, other):
        return self._mul(other)

    def __rmul__(self, other):
        return self._mul(other)

    def ops(self):
        return self.macs

    def eops(self):
        return self.emacs

    def total_ops(self):
        return (
            self.macs + self.additions + self.multiplies + self.luts + self.other_logic
        )

    def total_eops(self):
        return (
            self.emacs + self.additions + self.multiplies + self.luts + self.other_logic
        )

    def memory_ops_bytes(self):
        return self.mem_read_bytes + self.mem_write_bytes
