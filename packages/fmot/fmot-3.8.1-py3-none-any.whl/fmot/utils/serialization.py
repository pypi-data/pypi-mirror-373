import torch
from torch.serialization import FILE_LIKE
from typing import Any


def save(object: Any, path: FILE_LIKE):
    """
    Saves an object to a disk file. Safe wrapper around torch.save. Can be used to
    serialize FQIR as well as model state-dicts.

    Arguments:
        object (Any): saved object
        path: a file-like object. Typical convention is for filename to end in `.pt`
    """
    torch.save(object, path)


def load(path: FILE_LIKE, map_location="cpu"):
    """
    Loads an object serialized with :attr:`fmot.save` from disk.

    Wraps :attr:`torch.load` to maintain compatibility with loading FQIR graphs.

    Arguments:
        path: a file-like object to load
        map_location (str): device to load the object to, default :attr:`"cpu"`
    """
    obj = torch.load(path, weights_only=False, map_location=map_location)

    return obj
