from typing import Any

import awkward as ak
import numpy as np
from numba import njit


@njit
def _get_subleading(sorted_array: ak.Array) -> np.ndarray:
    subleading_array = np.empty(len(sorted_array))

    for i, sub_array in enumerate(sorted_array):
        if len(sub_array) == 1:
            subleading_array[i] = sub_array[0]
        else:
            subleading_array[i] = sub_array[1]

    return subleading_array


def ak_subleading(array: ak.Array) -> ak.Array:
    if ak.any(ak.num(array) == 0):
        raise ValueError("Array should not contain empty subarrays.")

    idx = ak.argsort(abs(array), axis=1, ascending=False)

    subleading_array = _get_subleading(array[idx])
    subleading_array = ak.Array(subleading_array)

    return subleading_array


@njit
def _get_unique(array: ak.Array, array_builder: ak.ArrayBuilder) -> ak.ArrayBuilder:
    for sub_arr in array:
        unique = np.unique(np.asarray(sub_arr))

        array_builder.begin_list()
        for u in unique:
            array_builder.append(u)
        array_builder.end_list()

    return array_builder


def ak_unique(array: ak.Array) -> ak.Array:
    array = ak.fill_none(array, [])

    builder = ak.ArrayBuilder()
    builder = _get_unique(array, builder)

    array = builder.snapshot()
    return array


def check_numpy_type(array: ak.Array | np.ndarray | Any, check_1d: bool = True) -> bool:
    if type(array) is ak.Array and type(array.type.content) is ak.types.NumpyType:
        return True
    elif type(array) is np.ndarray:
        if check_1d and array.ndim != 1:
            raise ValueError("Array should be 1D.")
        return True
    else:
        return False


def check_list_type(array: ak.Array | Any) -> bool:
    if type(array) is ak.Array and type(array.type.content) is ak.types.ListType:
        return True
    else:
        return False
