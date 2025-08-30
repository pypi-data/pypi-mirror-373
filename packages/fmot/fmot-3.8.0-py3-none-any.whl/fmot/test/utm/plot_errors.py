from fmot.test.utm.quant_tolerances import load_tolerances, measure_errors
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

MERGE_GROUPS = {
    "matmul": ["linear", "matmul", "addmm", "usprod", "uvprod"],
    "mul": ["vimul", "vvmul"],
    "cat/chunk": ["cat", "chunk"],
    "add/sub": ["vvadd", "vvsub", "viadd"],
    "telescoping_lut": ["telescoping_lut"],
    "relu": ["relu"],
    "conv1d": ["conv1d"],
    "custom_rnn": ["prev_state", "adaptive_femto_gru"],
}


def filter_errors():
    errors = measure_errors()
    errors_dbl = defaultdict(list)
    errors_std = defaultdict(list)
    errors_eig = defaultdict(list)

    for k, v in errors.items():
        name, prec = k.split("-")
        lib, *others = name.split("_")
        name = "_".join(list(others))
        testcase, __ = name.rsplit("_", 1)

        for gname, members in MERGE_GROUPS.items():
            for member in members:
                if member in testcase:
                    testcase = gname

        if prec == "double":
            errors_dbl[testcase].append(v)
        elif prec == "standard":
            errors_std[testcase].append(v)
        elif prec == "eights":
            errors_eig[testcase].append(v)

    def reduce(x):
        for k, v in x.items():
            x[k] = np.mean(v)
        return x

    errors_dbl, errors_std, errors_eig = map(
        reduce, [errors_dbl, errors_std, errors_eig]
    )

    return errors_dbl, errors_std, errors_eig


def barplot_tolerances():
    dbl, std, eig = filter_errors()

    xvals = np.arange(len(std))
    width = 0.2
    gap = 0.25

    keys = list(dbl.keys())
    std_vals = []
    dbl_vals = []
    eig_vals = []
    for k in keys:
        std_vals.append(std[k])
        dbl_vals.append(dbl[k])
        eig_vals.append(eig[k])

    fig, ax = plt.subplots()
    plt.bar(xvals, std_vals, width, label="STANDARD")
    plt.bar(xvals + gap, eig_vals, width, label="EIGHTS")
    plt.bar(xvals + 2 * gap, dbl_vals, width, label="DOUBLE")
    plt.legend()
    plt.xticks(xvals, keys, rotation=90)
    plt.yscale("log")
    plt.grid(axis="y")
    fig.subplots_adjust(bottom=0.25)
    plt.show()


if __name__ == "__main__":
    barplot_tolerances()
