# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Helpers for various collections."""

from __future__ import annotations

from typing import Any

import numpy as np
import xxhash


def make_hash(obj: Any) -> int:  # noqa: ANN401
    """
    Make a hash from a dictionary, list, tuple or set to any level.

    From: https://stackoverflow.com/questions/5884066/hashing-a-dictionary

    Parameters
    ----------
    obj
        Input collection.

    Returns
    -------
    :
        Hash.

    """
    new_hash = xxhash.xxh64()
    if isinstance(obj, (set, tuple, list)):
        return hash(tuple(make_hash(e) for e in obj))

    if isinstance(obj, np.ndarray):
        # numpy arrays behave funny for hashing
        new_hash.update(obj)  # type: ignore
        val = new_hash.intdigest()
        new_hash.reset()
        return val

    if not isinstance(obj, dict):
        return hash(obj)

    tuple_of_hashes = ((key, make_hash(val)) for key, val in obj.items())
    return hash(frozenset(sorted(tuple_of_hashes)))


def without(dict_in: dict, keys: list) -> dict:
    """
    Copy a dictionary excluding a specific list of keys.

    Parameters
    ----------
    dict_in
        Input dictionary.
    keys
        List of keys to exclude.

    Returns
    -------
    :
        Filtered dictionary.

    """
    if not isinstance(keys, list):
        keys = [keys]
    new_d = dict_in.copy()
    for key in keys:
        new_d.pop(key)
    return new_d
