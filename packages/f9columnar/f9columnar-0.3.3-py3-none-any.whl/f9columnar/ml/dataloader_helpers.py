from __future__ import annotations

import glob
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Iterable

import h5py
import numpy as np

from f9columnar.utils.helpers import dump_json


def column_stack_structured_array(structured_array: np.ndarray, fields: list[str] | None = None) -> np.ndarray:
    if fields is None:
        fields = structured_array.dtype.names

    stack_lst = [structured_array[field] for field in fields]

    return np.stack(stack_lst, axis=len(structured_array.shape), dtype=np.float32)


def padding_mask(X: np.ndarray, pad_value: float | None) -> np.ndarray | None:
    if pad_value is None:
        return None

    return ~(X == pad_value).all(axis=1)


def _find_first_hdf5(pattern: str) -> str | None:
    matches = glob.glob(pattern)

    if len(matches) == 0:
        return None
    else:
        return matches[0]


def resolve_hdf5_path(hdf5_files: str | list[str], environ_resolve_variable: str = "ANALYSIS_ML_DATA_DIR") -> str:
    """Resolves path to an HDF5 file, supporting wildcards and fallback search in the ANALYSIS_ML_DATA_DIR."""

    if type(hdf5_files) is list:
        hdf5_file = hdf5_files[0]
    else:
        hdf5_file = hdf5_files  # type: ignore

    data_dir = os.environ.get(environ_resolve_variable, None)

    # handle wildcard path
    if hdf5_file.endswith("*"):
        wildcard_hdf5_file = _find_first_hdf5(f"{hdf5_file}.hdf5")

        if wildcard_hdf5_file:
            return wildcard_hdf5_file
        else:
            if data_dir is None:
                raise RuntimeError(f"No {environ_resolve_variable} set and no HDF5 file found matching {hdf5_file}!")

            fallback_hdf5_file = _find_first_hdf5(os.path.join(data_dir, "*.hdf5"))

            if fallback_hdf5_file:
                logging.warning(f"Using fallback HDF5 file: {fallback_hdf5_file}")
                return fallback_hdf5_file
            else:
                raise RuntimeError(f"No HDF5 files found matching {hdf5_file} or {data_dir}/*.hdf5!")

    # handle absolute path
    if not os.path.exists(hdf5_file):
        if data_dir is None:
            raise RuntimeError(f"HDF5 file not found at '{hdf5_file}' and no {environ_resolve_variable} set!")

        fallback_hdf5_file = os.path.join(data_dir, os.path.basename(hdf5_file))

        if not os.path.exists(fallback_hdf5_file):
            raise RuntimeError(f"HDF5 file not found at '{hdf5_file}' or '{fallback_hdf5_file}'!")

        logging.warning(f"Using fallback HDF5 file: {fallback_hdf5_file}")
        return fallback_hdf5_file

    return hdf5_file


def get_hdf5_metadata(hdf5_file_path: str | list[str], resolve_path: bool = False) -> dict[str, Any]:
    if resolve_path:
        hdf5_file_path = resolve_hdf5_path(hdf5_file_path)

    with h5py.File(hdf5_file_path, "r") as f:
        metadata = json.loads(f["metadata"][()])

    return metadata


def get_hdf5_columns(hdf5_file: str, resolve_path: bool = False) -> dict[str, list[str]]:
    if resolve_path:
        hdf5_file = resolve_hdf5_path(hdf5_file)

    columns_dct = {}

    with h5py.File(hdf5_file, "r") as f:
        for dataset_name in f.keys():
            if dataset_name == "metadata":
                continue

            dataset = f[dataset_name]
            columns_dct[dataset_name] = list(dataset.dtype.names)

    return columns_dct


def get_hdf5_dtypes(hdf5_file: str, resolve_path: bool = False) -> dict[str, dict[str, str]]:
    if resolve_path:
        hdf5_file = resolve_hdf5_path(hdf5_file)

    dtypes_dct = {}

    with h5py.File(hdf5_file, "r") as f:
        for dataset_name in f.keys():
            if dataset_name == "metadata":
                continue

            dataset = f[dataset_name]
            dtypes_dct[dataset_name] = {col: str(dataset[col].dtype) for col in dataset.dtype.names}

    return dtypes_dct


def get_hdf5_shapes(hdf5_file: str, resolve_path: bool = False) -> dict[str, tuple[int, ...]]:
    if resolve_path:
        hdf5_file = resolve_hdf5_path(hdf5_file)

    shapes_dct = {}

    with h5py.File(hdf5_file, "r") as f:
        for dataset_name in f.keys():
            if dataset_name == "metadata":
                continue

            dataset_shape = f[dataset_name].shape
            feature_shape = len(f[dataset_name].dtype.names)

            shapes_dct[dataset_name] = (*dataset_shape, feature_shape)

    return shapes_dct


@dataclass(slots=True, eq=False)
class DatasetColumn:
    """Container representing the columns of a dataset in an HDF5 file."""

    column_name: str
    all_columns: list[str]
    used_columns: list[str]
    extra_columns: list[str]
    numer_columns: list[str]
    categ_columns: list[str]
    numer_columns_idx: np.ndarray
    categ_columns_idx: np.ndarray
    shape: tuple[int, ...]
    pad_value: float | None
    labels: dict[str, int] | None

    offset_used_columns: list[str] = field(init=False)
    offset_numer_columns_idx: np.ndarray = field(init=False)
    offset_categ_columns_idx: np.ndarray = field(init=False)

    has_numer_columns: bool = field(init=False)
    has_categ_columns: bool = field(init=False)

    n_objects: int = field(init=False)

    def __post_init__(self) -> None:
        self.offset_used_columns = self.numer_columns + self.categ_columns

        self.offset_numer_columns_idx = np.arange(len(self.numer_columns_idx))
        self.offset_categ_columns_idx = np.arange(
            len(self.numer_columns_idx), len(self.numer_columns_idx) + len(self.categ_columns_idx)
        )

        self.has_numer_columns = len(self.numer_columns) > 0
        self.has_categ_columns = len(self.categ_columns) > 0

        if len(self.shape) == 2:
            self.n_objects = 1
        else:
            self.n_objects = self.shape[1]

    def __repr__(self) -> str:
        return f"{self.column_name}Column(all_columns={len(self.all_columns)}, used_columns={len(self.used_columns)})"

    def __str__(self) -> str:
        s = f"{self.column_name}Column(all_columns={len(self.all_columns)}, used_columns={len(self.used_columns)}, "
        s += f"extra_columns={len(self.extra_columns)}, numer_columns={len(self.numer_columns)}, "
        s += f"categ_columns={len(self.categ_columns)})"
        return s

    def to_dict(self) -> dict[str, Any]:
        return {
            "column_name": self.column_name,
            "all_columns": self.all_columns,
            "used_columns": self.used_columns,
            "extra_columns": self.extra_columns,
            "numer_columns": self.numer_columns,
            "categ_columns": self.categ_columns,
            "numer_columns_idx": self.numer_columns_idx.tolist(),
            "categ_columns_idx": self.categ_columns_idx.tolist(),
            "shape": self.shape,
            "pad_value": self.pad_value,
            "offset_used_columns": self.offset_used_columns,
            "offset_numer_columns_idx": self.offset_numer_columns_idx.tolist(),
            "offset_categ_columns_idx": self.offset_categ_columns_idx.tolist(),
            "has_numer_columns": self.has_numer_columns,
            "has_categ_columns": self.has_categ_columns,
            "n_objects": self.n_objects,
        }

    def to_json(self, output_file: str) -> None:
        return dump_json(self.to_dict(), output_file)


@dataclass(frozen=True, slots=True, eq=False)
class ColumnSelection:
    """Container for selected columns from multiple datasets in HDF5 files."""

    _selection: dict[str, DatasetColumn] = field(default_factory=dict)

    def keys(self) -> list[str]:
        return list(self._selection.keys())

    def __len__(self) -> int:
        return len(self._selection)

    def __setitem__(self, dataset_name: str, dataset_column: DatasetColumn) -> None:
        self._selection[dataset_name] = dataset_column

    def __getitem__(self, dataset_name: str) -> Any:
        return self._selection[dataset_name]

    def __contains__(self, dataset_name: str) -> bool:
        return dataset_name in self._selection

    def __repr__(self) -> str:
        columns_repr = ", ".join([f"{k}: {v.__repr__()}" for k, v in self._selection.items()])
        return f"ColumnSelection({columns_repr})"

    def __str__(self) -> str:
        columns_str = ", ".join([f"{k}: {v.__str__()}" for k, v in self._selection.items()])
        return f"ColumnSelection({columns_str})"

    def items(self) -> Iterable[tuple[str, DatasetColumn]]:
        return self._selection.items()

    def to_dict(self) -> dict[str, Any]:
        return {k: v.to_dict() for k, v in self._selection.items()}

    def to_json(self, output_file: str) -> None:
        return dump_json(self.to_dict(), output_file)


def column_selection_from_dict(columns_dct: dict[str, Any]) -> ColumnSelection:
    selection = ColumnSelection()

    for dataset_name in columns_dct.keys():
        dataset_columns = columns_dct[dataset_name]

        selection[dataset_name] = DatasetColumn(
            dataset_name,
            dataset_columns["all_columns"],
            dataset_columns["used_columns"],
            dataset_columns["extra_columns"],
            dataset_columns["numer_columns"],
            dataset_columns["categ_columns"],
            np.array(dataset_columns["numer_columns_idx"]),
            np.array(dataset_columns["categ_columns_idx"]),
            tuple(dataset_columns["shape"]),
            dataset_columns.get("pad_value", None),
            dataset_columns.get("labels", None),
        )

    return selection


def get_column_selection(hdf5_files: str | list[str], column_names: list[str]) -> ColumnSelection:
    """Get column (feature) selection from HDF5 files.

    Parameters
    ----------
    hdf5_files : str | list[str]
        Provided HDF5 file(s) to select columns from. Can be a single file or a list of files.
        If a list is provided, the first file will be used. If a wildcard is used, the first matching file will be used.
        If no file is found, the function will try to resolve the path using the ANALYSIS_ML_DATA_DIR environment variable.
        If no file is found, an error will be raised.
    column_names : list[str]
        List of column names to select from the HDF5 file(s).
    scale_columns_dct : dict[str, float] | None, optional
        Dictionary of column names and their scaling factors. If None, all columns will be scaled by 1.0.
        Defaults to None. Example: {'column1': 0.5, 'column2': 2.0}.

    Returns
    -------
    ColumnSelection
        A ColumnSelection object containing the selected columns for each dataset in the HDF5 file(s).
    """
    resolved_hdf5_file_path = resolve_hdf5_path(hdf5_files)

    all_columns_dct = get_hdf5_columns(resolved_hdf5_file_path)

    used_columns_dct: dict[str, list[str]] = {}

    column_names = sorted(list(set(column_names)))

    for dataset_name, columns in all_columns_dct.items():
        for used_column in column_names:
            if used_column in columns:
                if dataset_name not in used_columns_dct:
                    used_columns_dct[dataset_name] = []

                used_columns_dct[dataset_name].append(used_column)

    dtypes_dct = get_hdf5_dtypes(resolved_hdf5_file_path)

    numer_column_names: dict[str, list[str]] = {}
    categ_column_names: dict[str, list[str]] = {}

    numer_columns_idx_dct: dict[str, np.ndarray] = {}
    categ_columns_idx_dct: dict[str, np.ndarray] = {}

    extra_columns: dict[str, list[str]] = {}

    for dataset_name, type_columns_dct in dtypes_dct.items():
        if dataset_name not in used_columns_dct:
            continue

        num_column_lst: list[str] = []
        categ_column_lst: list[str] = []
        extra_lst: list[str] = []

        num_columns_idx, categ_columns_idx, c = [], [], 0
        for i, column_name in enumerate(used_columns_dct[dataset_name]):
            if column_name.endswith("_type"):
                extra_lst.append(column_name)
                continue

            if column_name == "weights":
                extra_lst.append(column_name)
                continue

            if column_name not in type_columns_dct:
                raise ValueError(f"Column {column_name} not found in dataset {dataset_name}!")

            column_type = type_columns_dct[column_name]

            if "float" in column_type:
                num_column_lst.append(column_name)
                num_columns_idx.append(i)
            elif "int" in column_type:
                categ_column_lst.append(column_name)
                categ_columns_idx.append(i)
                c += 1
            else:
                raise ValueError(f"Unsupported column type {column_type} for column {column_name}!")

        numer_column_names[dataset_name] = num_column_lst
        categ_column_names[dataset_name] = categ_column_lst
        extra_columns[dataset_name] = extra_lst

        numer_columns_idx_dct[dataset_name] = np.array(num_columns_idx)
        categ_columns_idx_dct[dataset_name] = np.array(categ_columns_idx)

    shapes_dct = get_hdf5_shapes(resolved_hdf5_file_path)

    metadata = get_hdf5_metadata(resolved_hdf5_file_path)
    pad_values = metadata.get("pad_values", None)
    labels = metadata.get("labels", None)

    selection = ColumnSelection()

    for dataset_name in used_columns_dct.keys():
        if dataset_name in pad_values:
            pad_value = float(pad_values[dataset_name])
        else:
            pad_value = None

        selection[dataset_name] = DatasetColumn(
            dataset_name,
            all_columns_dct[dataset_name],
            used_columns_dct[dataset_name],
            extra_columns[dataset_name],
            numer_column_names[dataset_name],
            categ_column_names[dataset_name],
            numer_columns_idx_dct[dataset_name],
            categ_columns_idx_dct[dataset_name],
            shapes_dct[dataset_name],
            pad_value,
            labels,
        )

    return selection


def get_hdf5_writer_branches(
    config_dct: dict[str, Any],
) -> tuple[dict[str, list[str]], dict[str, dict[str, list[str]]], dict[str, int], dict[str, float]]:
    """Get the branches for HDF5 writer from the contents configuration.

    Parameters
    ----------
    config_dct : dict[str, Any]
        Configuration dictionary containing "flat" and "jagged" keys with their respective configurations.

    Note
    ----
    - "flat" key should contain a dictionary with "output", and optionally "extra_input", and "extra_output" keys.
    - "jagged" key should contain a dictionary where each key is a physics object name and the value is a dictionary
    with "output", and optionally "extra_input", and "extra_output" keys, along with "max_length" and "pad_value".

    Returns
    -------
    tuple[dict[str, list[str]], dict[str, dict[str, list[str]]], dict[str, int], dict[str, float]]
        A tuple containing:
        - flat_branches: A dictionary with flat branches.
        - jagged_branches: A dictionary with jagged branches.
        - max_lengths: A dictionary with maximum lengths for jagged branches.
        - pad_values: A dictionary with padding values for jagged branches.
    """
    flat_config = config_dct.get("flat", None)
    jagged_config = config_dct.get("jagged", None)

    flat_branches: dict[str, list[str]] = {}
    jagged_branches: dict[str, dict[str, list[str]]] = {}

    if flat_config is not None:
        flat_branches["output"] = list(flat_config["output"])
        flat_branches["extra_input"] = list(flat_config.get("extra_input", []))
        flat_branches["extra_output"] = list(flat_config.get("extra_output", []))

    max_lengths: dict[str, int] = {}
    pad_values: dict[str, float] = {}

    if jagged_config is not None:
        jagged_keys = jagged_config.keys()

        for key in jagged_keys:
            jagged_branches[key] = {}
            jagged_branches[key]["output"] = list(jagged_config[key]["output"])
            jagged_branches[key]["extra_input"] = list(jagged_config[key].get("extra_input", []))
            jagged_branches[key]["extra_output"] = list(jagged_config[key].get("extra_output", []))

            max_lengths[key] = jagged_config[key]["max_length"]
            pad_values[key] = jagged_config[key]["pad_value"]

    return flat_branches, jagged_branches, max_lengths, pad_values
