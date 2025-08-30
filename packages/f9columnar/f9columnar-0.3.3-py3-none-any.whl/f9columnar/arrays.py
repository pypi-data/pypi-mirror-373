from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any, Self

import awkward as ak
import numpy as np

from f9columnar.processors import Processor
from f9columnar.utils.ak_helpers import check_list_type, check_numpy_type


@dataclass
class BaseArrays:
    array: ak.Array
    fields: list[str] = dataclass_field(default_factory=list)

    def __post_init__(self) -> None:
        self.fields = self.array.fields

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.array), len(self.fields))

    def mask(self, mask: ak.Array | np.ndarray, inplace: bool = True) -> Self:
        if inplace:
            self.array = self.array[mask]
            return self
        else:
            return self.__class__(self.array[mask])

    def _check_type(self, value: Any) -> bool:
        raise NotImplementedError

    def __getitem__(self, value: str | int | slice | ak.Array | np.ndarray) -> ak.Array:
        if type(value) is str:
            return self.array[value]
        elif type(value) is int:
            return self.array[value]
        elif type(value) is slice:
            return self.array[value]
        elif type(value) is ak.Array or type(value) is np.ndarray:
            return self.mask(value)
        else:
            raise ValueError("Value must be a field name or an array mask!")

    def __setitem__(self, field: str, new_array: ak.Array | np.ndarray) -> BaseArrays:
        if not self._check_type(new_array):
            raise ValueError(f"Field {field} is not of the correct type!")

        self.array[field] = new_array
        self.fields.append(field)

        return self

    def __add__(self, other: BaseArrays) -> BaseArrays:
        try:
            self.array = ak.concatenate([self.array, other.array], axis=1)
        except Exception as e:
            raise ValueError("The two arrays are not compatible for concatenation!") from e

        self.fields += other.fields
        return self

    def __delitem__(self, field: str) -> BaseArrays:
        self.array = ak.without_field(self.array, field)
        self.fields.remove(field)
        return self

    def __len__(self) -> int:
        if isinstance(self.array, ak.Array):
            return len(self.array)
        elif isinstance(self.array, ak.Record):
            return 1
        else:
            raise ValueError("Invalid array type!")


@dataclass
class FlatArrays(BaseArrays):
    def _check_type(self, array: ak.Array | np.ndarray | Any) -> bool:
        return check_numpy_type(array)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(shape={self.shape})"


@dataclass
class JaggedArrays(BaseArrays):
    def _check_type(self, array: ak.Array | Any) -> bool:
        return check_list_type(array)

    def _get_non_empty_mask(self, all_fields: bool = True) -> ak.Array:
        if not all_fields:
            return ak.num(self.array[self.fields[0]]) > 0

        for i, field in enumerate(self.fields):
            mask = ak.num(self.array[field]) > 0
            if i == 0:
                non_empty_mask = mask
            else:
                non_empty_mask = non_empty_mask & mask

        return non_empty_mask

    def remove_empty(self, all_fields: bool = True) -> JaggedArrays:
        mask = self._get_non_empty_mask(all_fields)
        self.mask(mask, inplace=True)
        return self

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(shape={self.shape})"


class Arrays:
    def __init__(self, flat_arrays: FlatArrays | None = None, jagged_arrays: JaggedArrays | None = None) -> None:
        """This class is used to store flat and jagged arrays separately. It is used to store awkward arrays in a more
        structured way. The funconality is similar to `ak.Array` but with seperate handling of flat and jagged arrays.
        It is intended to make it easier to work with ntuples that contain both flat and jagged fields.

        Parameters
        ----------
        flat_arrays : FlatArrays
            Flat arrays.
        jagged_arrays : JaggedArrays
            Jagged arrays.

        Other Parameters
        ----------------
        flat_fields : list
            List of flat fields.
        jagged_fields : list
            List of jagged fields.
        fields : list
            List of all fields.

        Attributes
        ----------
        shape : tuple
            Shape of the arrays (number of events, number of flat array, number of jagged arrays).

        """
        self.flat_arrays = flat_arrays
        self.jagged_arrays = jagged_arrays

        self.flat_fields: list[str] = []
        self.jagged_fields: list[str] = []
        self.fields: list[str] = []

        self.update_fields()

    def update_fields(self) -> Arrays:
        self.fields = []

        if self.flat_arrays is not None:
            self.flat_fields = self.flat_arrays.fields
            self.fields += self.flat_fields

        if self.jagged_arrays is not None:
            self.jagged_fields = self.jagged_arrays.fields
            self.fields += self.jagged_fields

        return self

    @property
    def shape(self) -> tuple[int, int, int]:
        return (len(self), len(self.flat_fields), len(self.jagged_fields))

    def remove_empty(self, return_mask: bool = False, all_fields: bool = True) -> Arrays | ak.Array | None:
        if self.jagged_arrays is None:
            if return_mask:
                return None
            else:
                return self

        non_empty_mask = self.jagged_arrays._get_non_empty_mask(all_fields)

        if return_mask:
            return non_empty_mask
        else:
            return self.mask_flat_inplace(non_empty_mask)

    def mask_flat(self, mask: ak.Array | np.ndarray) -> tuple[FlatArrays | None, JaggedArrays | None]:
        if self.flat_arrays is not None:
            flat_masked = self.flat_arrays.mask(mask, inplace=False)
        else:
            flat_masked = None

        if self.jagged_arrays is not None:
            jagged_masked = self.jagged_arrays.mask(mask, inplace=False)
        else:
            jagged_masked = None

        return flat_masked, jagged_masked

    def mask_flat_inplace(self, mask: ak.Array | np.ndarray) -> Arrays:
        if self.flat_arrays is not None:
            self.flat_arrays.mask(mask, inplace=True)

        if self.jagged_arrays is not None:
            self.jagged_arrays.mask(mask, inplace=True)

        return self

    def mask_jagged(self, mask: ak.Array | np.ndarray) -> JaggedArrays | None:
        if self.jagged_arrays is not None:
            jagged_masked = self.jagged_arrays.mask(mask, inplace=False)
        else:
            jagged_masked = None

        return jagged_masked

    def mask_jagged_inplace(self, mask: ak.Array | np.ndarray) -> Arrays:
        if self.jagged_arrays is not None:
            self.jagged_arrays.mask(mask, inplace=True)

        return self

    def _get_by_field(self, field: str) -> ak.Array | None:
        if self.flat_arrays is not None and field in self.flat_fields:
            return self.flat_arrays[field]
        elif self.jagged_arrays is not None and field in self.jagged_fields:
            return self.jagged_arrays[field]
        else:
            raise KeyError(f"Field {field} not found in flat or jagged fields!")

    def _get_new_sliced_arrays(self, slice_idx: int | slice) -> Arrays:
        flat_slice, jagged_slice = None, None

        if self.flat_arrays is not None:
            flat_slice = FlatArrays(self.flat_arrays[slice_idx])

        if self.jagged_arrays is not None:
            jagged_slice = JaggedArrays(self.jagged_arrays[slice_idx])

        return self.__class__(flat_arrays=flat_slice, jagged_arrays=jagged_slice)

    def _get_new_masked_arrays(self, mask: ak.Array | np.ndarray) -> Arrays:
        if self.flat_arrays is None and self.jagged_arrays is None:
            return self

        if check_numpy_type(mask):
            flat_masked, jagged_masked = self.mask_flat(mask)
        elif self.jagged_arrays is not None and check_list_type(mask):
            flat_masked, jagged_masked = self.flat_arrays, self.mask_jagged(mask)
        else:
            raise ValueError("Invalid mask type!")

        return self.__class__(flat_arrays=flat_masked, jagged_arrays=jagged_masked)

    def __getitem__(self, value: str | int | slice | ak.Array | np.ndarray) -> ak.Array | Arrays:
        if type(value) is str:
            return self._get_by_field(value)
        elif type(value) is int or type(value) is slice:
            return self._get_new_sliced_arrays(value)
        elif type(value) is ak.Array or type(value) is np.ndarray:
            return self._get_new_masked_arrays(value)
        else:
            raise ValueError("Value must be a field name, int, array mask or slice!")

    def __setitem__(self, field: str, new_array: ak.Array | np.ndarray) -> Arrays:
        if check_numpy_type(new_array):
            if self.flat_arrays is None:
                self.flat_arrays = FlatArrays(ak.Array({field: new_array}))
            else:
                self.flat_arrays[field] = new_array
        elif check_list_type(new_array):
            if self.jagged_arrays is None:
                self.jagged_arrays = JaggedArrays(ak.Array({field: new_array}))
            else:
                self.jagged_arrays[field] = new_array
        else:
            raise ValueError("Array is not of the correct type!")

        self.update_fields()

        return self

    def __add__(self, other: Arrays) -> Arrays:
        if self.flat_arrays is not None and other.flat_arrays is not None:
            self.flat_arrays += other.flat_arrays  # type: ignore

        if self.flat_arrays is None and other.flat_arrays is not None:
            self.flat_arrays = other.flat_arrays

        if self.jagged_arrays is not None and other.jagged_arrays is not None:
            self.jagged_arrays += other.jagged_arrays  # type: ignore

        if self.jagged_arrays is None and other.jagged_arrays is not None:
            self.jagged_arrays = other.jagged_arrays

        self.update_fields()

        return self

    def __delitem__(self, field: str) -> Arrays:
        if self.flat_arrays is not None and field in self.flat_fields:
            del self.flat_arrays[field]

            if len(self.flat_arrays.fields) == 0:
                self.flat_arrays = None
        elif self.jagged_arrays is not None and field in self.jagged_fields:
            del self.jagged_arrays[field]

            if len(self.jagged_arrays.fields) == 0:
                self.jagged_arrays = None
        else:
            raise KeyError(f"Field {field} not found in flat or jagged fields!")

        self.fields.remove(field)

        return self

    def __len__(self) -> int:
        if self.flat_arrays is None and self.jagged_arrays is not None:
            return len(self.jagged_arrays)
        elif self.flat_arrays is not None and self.jagged_arrays is None:
            return len(self.flat_arrays)
        elif self.flat_arrays is not None and self.jagged_arrays is not None:
            len_flat, len_jagged = len(self.flat_arrays), len(self.jagged_arrays)
            if len_flat != len_jagged:
                raise RuntimeError("Flat and jagged arrays have different lengths!")
            else:
                return len_flat
        else:
            logging.warning("No flat or jagged arrays found!")
            return 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(shape={self.shape})"

    def __str__(self) -> str:
        return self.__repr__()


class GroupArrays:
    def __init__(self, group_arrays: dict[str, Arrays]) -> None:
        """A dictionary wrapper for `Arrays` objects. This class is used to store multiple `Arrays` objects.

        Parameters
        ----------
        group_arrays : dict
            Dictionary of `Arrays` objects.

        Other Parameters
        ----------------
        group_field_map : dict
            Dictionary mapping group names to fields.
        field_group_map : dict
            Dictionary mapping fields to group names.
        groups : list
            List of group names.
        fields : list
            List of all fields.
        working_group : str or Noneq
            Name of the working group. If set, the length of the `GroupArrays` object will be the length this group.

        Note
        ----
        This class is used for seperating different groups (each represented by an `Arrays` object). For example, groups
        can be used to seperate different particle types in an ntuple. Groups can be "electron", "muon", "jet", etc. Each
        group has its own `Arrays` object with flat and jagged fields.

        """
        self.group_arrays = group_arrays

        self.group_field_map: dict[str, list[str]] = {}
        self.field_group_map: dict[str, str] = {}

        self.groups: list[str] = []
        self.fields: list[str] = []

        self.working_group: str | None = None

        self.update_fields()

    def update_fields(self) -> None:
        self.group_field_map, self.field_group_map = {}, {}

        for group, arrays in self.group_arrays.items():
            fields = arrays.fields
            self.group_field_map[group] = fields

            for field in fields:
                self.field_group_map[field] = group

        self.groups = list(self.group_arrays.keys())
        self.fields = list(self.field_group_map.keys())

    def set_working_group(self, group: str) -> GroupArrays:
        if group not in self.groups:
            raise ValueError(f"Group {group} not found!")

        self.working_group = group
        return self

    @property
    def shape(self) -> dict[str, tuple[int, int, int]]:
        return {group: arrays.shape for group, arrays in self.group_arrays.items()}

    def remove_empty(
        self, group: str | None = None, return_mask: bool = False, remove_other: bool = True
    ) -> GroupArrays | ak.Array:
        non_empty_masks = []

        if group is None:
            for group_name, group_array in self.group_arrays.items():
                if not remove_other and group_name == "other":
                    continue

                mask = group_array.remove_empty(return_mask=True, all_fields=False)
                if mask is not None:
                    non_empty_masks.append(mask)

            non_empty_mask = non_empty_masks.pop(0)
            for mask in non_empty_masks:
                non_empty_mask = non_empty_mask & mask  # type: ignore
        else:
            if group == "other":
                raise ValueError("Cannot remove empty from 'other' group!")

            mask = self.group_arrays[group].remove_empty(return_mask=True, all_fields=False)
            non_empty_mask = mask

        if return_mask:
            return non_empty_mask

        if non_empty_mask is None:
            logging.warning("No non-empty mask found!")
            return self

        if group is None:
            for group_array in self.group_arrays.values():
                group_array.mask_flat_inplace(non_empty_mask)
        else:
            self.group_arrays[group].mask_flat_inplace(non_empty_mask)
            if remove_other:
                self.group_arrays["other"].mask_flat_inplace(non_empty_mask)

        return self

    def __setitem__(self, value: str | tuple[str, str], new_array: Arrays | ak.Array | np.ndarray) -> GroupArrays:
        if type(value) is tuple:
            group, field = value
        elif type(value) is str:
            group, field = "other", value
        else:
            raise TypeError(f"Invalid type for {value}!")

        if field is not None and group != "other" and not field.startswith(f"{group}_"):
            field = f"{group}_{field}"

        if group in self.groups:
            if type(new_array) is Arrays:
                if field is not None:
                    raise ValueError("Field name must be None when setting Arrays object!")
                else:
                    self.group_arrays[group] = self.group_arrays[group] + new_array  # type: ignore
            elif type(new_array) is ak.Array or type(new_array) is np.ndarray:
                arrays = self.group_arrays[group]
                arrays[field] = new_array
                self.group_arrays[group] = arrays
            else:
                raise TypeError(f"Invalid type for {new_array}!")
        else:
            if type(new_array) is Arrays:
                if field is not None:
                    raise ValueError("Field name must be None when setting Arrays object!")
                else:
                    self.group_arrays[group] = new_array  # type: ignore
            elif type(new_array) is np.ndarray:
                new_array = ak.Array({field: new_array})
            elif type(new_array) is ak.Array:
                new_array = ak.Array({field: new_array})
            else:
                raise TypeError(f"Invalid type for {new_array}!")

            if type(new_array) is ak.Array or type(new_array) is np.ndarray:
                arrays_handler = ArraysHandler()
                self.group_arrays[group] = arrays_handler.make_arrays(new_array)

        self.update_fields()

        return self

    def __getitem__(
        self, value: str | tuple[str, str | int | slice | ak.Array | np.ndarray]
    ) -> ak.Array | Arrays | GroupArrays:
        if type(value) is tuple:
            value, other_value = value
        else:
            value, other_value = value, None

        if type(value) is not str and value is not None:
            raise TypeError(f"Invalid type for {value}. Shoule be group name, field name or None for all groups!")

        elif other_value is None:
            if value in self.groups:
                return self.group_arrays[value]
            elif value in self.fields:
                group = self.field_group_map[value]
                return self.group_arrays[group][value]
            else:
                raise KeyError(f"Group or field {value} not found!")

        elif type(other_value) is str:
            return self.group_arrays[value][other_value]

        elif type(other_value) is not str:
            new_group_arrays = copy.deepcopy(self.group_arrays)

            if value is None:
                for group, arrays in self.group_arrays.items():  # type: ignore
                    new_group_arrays[group] = arrays[other_value]

                return self.__class__(group_arrays=new_group_arrays)

            if value in self.groups:
                group, field = value, None
            elif value in self.fields:
                group, field = self.field_group_map[value], value
            else:
                raise KeyError(f"Group or field {value} not found!")

            if field is None:
                new_group_arrays[group] = new_group_arrays[group][other_value]
            else:
                raise ValueError("Field modification would make array irregular!")

            return self.__class__(group_arrays=new_group_arrays)

        else:
            raise TypeError(f"Invalid type for {other_value}!")

    def __delitem__(self, value: str) -> GroupArrays:
        if value not in self.groups and value not in self.fields:
            raise KeyError(f"Group or field {value} not found!")

        if value in self.fields:
            group = self.field_group_map[value]
            del self.group_arrays[group][value]

        if value in self.groups:
            del self.group_arrays[value]

        self.update_fields()

        return self

    def __len__(self) -> int:
        len_dct = {group: len(arrays) for group, arrays in self.group_arrays.items()}

        if self.working_group is not None:
            return len_dct[self.working_group]

        len_lst = list(len_dct.values())

        if len(set(len_lst)) != 1:
            raise RuntimeError("Groups have different lengths. Set a working group!")

        return len_lst[0]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(groups={self.shape})"

    def __str__(self) -> str:
        return self.__repr__()


class ArraysHandler:
    @staticmethod
    def _get_fields(arrays: ak.Array) -> tuple[list[str], list[str], list[str]]:
        arrays_contents = arrays.type.content.contents
        arrays_fields = arrays.type.content.fields

        flat_fields, jagged_fields, other_fields = [], [], []

        for content, array_field in zip(arrays_contents, arrays_fields):
            if isinstance(content, ak.types.NumpyType):
                flat_fields.append(array_field)
            elif isinstance(content, ak.types.ListType):
                jagged_fields.append(array_field)
            else:
                other_fields.append(array_field)

        return flat_fields, jagged_fields, other_fields

    def make_arrays(self, arrays: ak.Array) -> Arrays:
        flat_fields, jagged_fields, _ = self._get_fields(arrays)

        flat_arrays, jagged_arrays = None, None

        if len(flat_fields) != 0:
            flat_arrays = arrays[flat_fields]
            flat_arrays = FlatArrays(flat_arrays)

        if len(jagged_fields) != 0:
            jagged_arrays = arrays[jagged_fields]
            jagged_arrays = JaggedArrays(jagged_arrays)

        arrays = Arrays(flat_arrays=flat_arrays, jagged_arrays=jagged_arrays)

        return arrays

    def make_array_groups(self, arrays: ak.Array, groups: list[str]) -> GroupArrays:
        fields = arrays.fields

        group_arrays_dct, all_group_fields = {}, []

        for group in groups:
            group_fields = [field for field in fields if field.startswith(f"{group}_")]
            all_group_fields += group_fields

            group_arrays = arrays[group_fields]
            group_arrays_dct[group] = self.make_arrays(group_arrays)

        non_group_fields = list(set(fields) - set(all_group_fields))

        if len(non_group_fields) != 0:
            non_group_arrays = arrays[non_group_fields]
            group_arrays_dct["other"] = self.make_arrays(non_group_arrays)

        arrays = GroupArrays(group_arrays=group_arrays_dct)

        return arrays


class ArraysProcessor(Processor):
    def __init__(self, groups: list[str] | None = None) -> None:
        """Processor to separate flat and jagged fields into two arrays from an awkward array.

        Parameters
        ----------
        groups : list, optional
            List of group names. If provided, the arrays will be separated into groups based on the group names. If
            not provided, the arrays will be separated into flat and jagged fields.

        Note
        ----
        This will modify the input arrays. It is intended to be used as the first processor in the analysis chain in
        the case of ntuples that contain both flat and jagged fields.

        Returns
        -------
        Returned arrays `GroupArrays` if groups are provided, otherwise `Arrays` object.

        """
        super().__init__(name="arraysProcessor")
        self.groups = groups
        self.arrays_handler = ArraysHandler()

    def run(self, arrays: ak.Array) -> dict[str, Arrays | GroupArrays]:
        if self.groups is None:
            arrays = self.arrays_handler.make_arrays(arrays)
        else:
            arrays = self.arrays_handler.make_array_groups(arrays, self.groups)

        return {"arrays": arrays}


def arrays_to_ak(arrays: Arrays) -> ak.Array:
    fields: dict[str, ak.Array] = {}

    if arrays.flat_arrays is not None:
        for field in arrays.flat_arrays.fields:
            fields[field] = arrays.flat_arrays.array[field]

    if arrays.jagged_arrays is not None:
        for field in arrays.jagged_arrays.fields:
            fields[field] = arrays.jagged_arrays.array[field]

    return ak.zip(fields, depth_limit=1)


def group_arrays_to_ak(group_arrays: GroupArrays) -> ak.Array:
    group_fields: dict[str, ak.Array] = {}

    for _, arrays in group_arrays.group_arrays.items():
        if arrays.flat_arrays is not None:
            for field in arrays.flat_arrays.fields:
                group_fields[field] = arrays.flat_arrays.array[field]

        if arrays.jagged_arrays is not None:
            for field in arrays.jagged_arrays.fields:
                group_fields[field] = arrays.jagged_arrays.array[field]

    return ak.zip(group_fields, depth_limit=1)
