import matplotlib.pyplot as plt
from itertools import zip_longest
from matplotlib import cm
from typing import *

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.text import Annotation
from matplotlib.transforms import Transform, Bbox


def get_hierarchical_ticks(full_labels, levels=1):
    tick_levels = [[] for _ in range(levels)]
    for _, name in enumerate(full_labels):
        split = name.split(".")
        for i, spl in zip_longest(range(levels), split[:levels], fillvalue=None):
            tick_levels[i].append(spl)

    return tick_levels


def plot_merged_labels(ax, *labellists):
    for i, labellist in enumerate(labellists):
        starts = []
        ends = []
        labels = []
        prev = None

        cmap = cm.get_cmap("Accent")

        for j, xx in enumerate(labellist):
            if prev is None:
                if xx is not None:
                    starts.append(j)
                    labels.append(xx)
            elif xx is None:
                ends.append(j)
            elif xx != prev:
                ends.append(j)
                starts.append(j)
                labels.append(xx)
            prev = xx
        if xx is not None:
            ends.append(j + 1)

        colors = [cmap(((k % 2) / 2 + i / 4) % 1) for k in range(len(starts))]

        se = [(s, e - s) for s, e in zip(starts, ends)]
        ax.broken_barh(se, (i, 1), facecolors=colors)
        for start, end, label in zip(starts, ends, labels):
            ax.text(
                x=(start + end) / 2,
                y=i + 0.5,
                s=label,
                ha="center",
                va="center",
                color="k",
                rotation=270,
                fontsize=4,
            )
