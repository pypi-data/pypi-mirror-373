from __future__ import annotations

import copy
import glob
import json
import logging
import os
from collections.abc import Callable
from itertools import product
from typing import Any, Type

import h5py
import numpy as np
import pandas as pd
import torch
from torch import multiprocessing
from torch.utils.data import DataLoader, IterableDataset

from f9columnar.processors import Processor, ProcessorsGraph
from f9columnar.utils.helpers import get_file_size


class Hdf5Iterator:
    def __init__(
        self,
        file: str,
        dataset_names: list[str],
        chunk_size: int | None,
        start_entry: int,
        stop_entry: int,
        shuffle: bool = False,
        load_column_names_dct: dict[str, list[str]] | None = None,
        filter_dataset_kwargs: bool = True,
        dataset_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.file = file
        self.stop_entry = stop_entry

        if dataset_kwargs is None:
            self.dataset_kwargs = {}
        else:
            self.dataset_kwargs = dataset_kwargs

        self.shuffle = shuffle

        if chunk_size is None:
            self.chunk_size = self.stop_entry - start_entry
        else:
            self.chunk_size = chunk_size

        self.pile_name: str | None = None

        split_file = self.file.split(":")
        self.file = split_file[0]

        if len(split_file) == 3:
            self.pile_name = split_file[1]
            dataset_name = split_file[2]
        else:
            self.pile_name = None
            dataset_name = split_file[1]

        if dataset_name == "combined":
            self.combined_dataset = True
            self.dataset_names = dataset_names
        else:
            self.combined_dataset = False
            self.dataset_names = [dataset_name]

        self.load_columns_dct: dict[str, list[str]] | None = None

        if load_column_names_dct is not None:
            if self.combined_dataset:
                if set(self.dataset_names) != set(load_column_names_dct.keys()):
                    raise ValueError(
                        "load_column_names_dct keys must match dataset_names when combined_dataset is True."
                    )
                self.load_columns_dct = load_column_names_dct
            else:
                self.load_columns_dct = {dataset_name: load_column_names_dct[dataset_name]}

        self.handle = h5py.File(self.file, "r")

        self._current_start_entry = start_entry
        self._current_stop_entry = start_entry + self.chunk_size

        if self._current_stop_entry > self.stop_entry:
            self._current_stop_entry = self.stop_entry

        if filter_dataset_kwargs:
            self._filter_dataset_kwargs()

    def _filter_dataset_kwargs(self, add_types: list[Type[Any]] | None = None) -> None:
        allowed_types = [int, float, str, bool, list, tuple, dict]

        if add_types is not None:
            allowed_types = allowed_types + add_types

        _dataset_kwargs: dict[str, Any] = {}

        for kw_name, kw_value in self.dataset_kwargs.items():
            for allow_type in allowed_types:
                if isinstance(kw_value, allow_type):
                    _dataset_kwargs[kw_name] = kw_value
                    break

        self.dataset_kwargs = _dataset_kwargs

    def close(self) -> None:
        self.handle.close()

    def make_report(self) -> dict[str, Any]:
        report = {
            "file": self.file,
            "dataset_names": self.dataset_names,
            "chunk_size": self.chunk_size,
            "start": self._current_start_entry,
            "stop": self._current_stop_entry,
            "pile_name": self.pile_name,
            "combined_dataset": self.combined_dataset,
            "load_columns_dct": self.load_columns_dct,
        }
        return report | self.dataset_kwargs

    def __iter__(self) -> Hdf5Iterator:
        return self

    def _get_dataset_array(self, dataset_name: str) -> np.ndarray:
        if self.pile_name is None:
            dataset = self.handle[dataset_name]
        else:
            dataset = self.handle[dataset_name][self.pile_name]

        if self.combined_dataset:
            load_columns = self.load_columns_dct.get(dataset_name, None) if self.load_columns_dct is not None else None
        else:
            load_columns = self.load_columns_dct[dataset_name] if self.load_columns_dct is not None else None

        if load_columns:
            arrays = dataset[*load_columns][self._current_start_entry : self._current_stop_entry]
        else:
            arrays = dataset[self._current_start_entry : self._current_stop_entry]

        if self.shuffle:
            np.random.shuffle(arrays)

        return arrays

    def __next__(self) -> tuple[Any, dict[str, Any]]:
        if self._current_start_entry >= self.stop_entry:
            raise StopIteration

        dataset_arrays_dct: dict[str, np.ndarray] = {}

        for dataset_name in self.dataset_names:
            array = self._get_dataset_array(dataset_name)
            dataset_arrays_dct[dataset_name] = array

        self._current_start_entry = self._current_stop_entry
        self._current_stop_entry = min(self._current_stop_entry + self.chunk_size, self.stop_entry)

        reports = self.make_report()

        return dataset_arrays_dct, reports


class Hdf5IteratorDfMaker:
    def __init__(
        self,
        name: str,
        hdf5_files_metadata: dict[str, dict[str, Any]],
        num_workers: int,
        shape: tuple[int, ...],
        chunk_size: int | None = None,
        shuffle: bool = False,
    ) -> None:
        self.name = name
        self.hdf5_files_metadata = hdf5_files_metadata
        self.num_workers = num_workers
        self.shape = shape
        self.chunk_size = chunk_size
        self.shuffle = shuffle

        self.total_num_entries = shape[0]
        self.all_num_entries_dct: dict[str, int] = {}

    def _log_info(self) -> None:
        all_hdf5_files = list(self.hdf5_files_metadata.keys())
        hdf5_files = set([f.split(":")[0] for f in all_hdf5_files])
        hdf5_datasets = set([f.split(":")[1] for f in all_hdf5_files])

        total_files_size = sum([get_file_size(file) for file in hdf5_files])

        info_str = "\n" + 15 * "=" + " info " + 15 * "="
        info_str += f"\nName: {self.name}\n"
        info_str += f"Number of hdf5 files: {len(hdf5_files)}\n"
        info_str += f"Number of datasets: {len(hdf5_datasets)}\n"
        info_str += f"Total size: {total_files_size:.3f} GB\n"
        info_str += f"Total number of entries: {self.total_num_entries}\n"
        info_str += 36 * "="

        logging.info(info_str)

    def _split(self) -> list[dict[str, list[int]]]:
        self._log_info()

        # how many entries each worker will process
        splits = [self.total_num_entries // self.num_workers] * self.num_workers
        splits[-1] += self.total_num_entries % self.num_workers

        self.all_num_entries_dct = {file: metadata["shape"][0] for file, metadata in self.hdf5_files_metadata.items()}
        num_entries_dct = copy.deepcopy(self.all_num_entries_dct)

        # keep track of the start and stop entries for each root file
        hdf5_files_start_dct: dict[str, int] = {file: 0 for file in self.hdf5_files_metadata.keys()}

        result: list[dict[str, list[int]]] = [{} for _ in range(len(splits))]

        done = []
        for i, split in enumerate(splits):
            total = 0
            for hdf5_file, num_entries in num_entries_dct.items():
                if hdf5_file in done:
                    continue

                start_entry = hdf5_files_start_dct[hdf5_file]

                total += num_entries

                if total <= split:
                    result[i][hdf5_file] = [start_entry, self.all_num_entries_dct[hdf5_file]]
                    done.append(hdf5_file)

                    if total == split:
                        break
                    else:
                        continue

                if total > split:
                    delta = num_entries - (total - split)
                    result[i][hdf5_file] = [start_entry, start_entry + delta]
                    hdf5_files_start_dct[hdf5_file] += delta
                    num_entries_dct[hdf5_file] -= delta
                    break

        return result

    def make(self) -> pd.DataFrame:
        split_result = self._split()

        worker_df: dict[str, list] = {
            "worker_id": [],
            "file": [],
            "start": [],
            "stop": [],
            "chunk_size": [],
            "shuffle": [],
        }

        check_total = 0
        for i, result_dct in enumerate(split_result):
            for hdf5_file, start_stop in result_dct.items():
                entry_start, entry_stop = start_stop
                check_total += entry_stop - entry_start

                worker_df["worker_id"].append(i)
                worker_df["file"].append(hdf5_file)
                worker_df["start"].append(entry_start)
                worker_df["stop"].append(entry_stop)
                worker_df["chunk_size"].append(self.chunk_size)
                worker_df["shuffle"].append(self.shuffle)

        if check_total != self.total_num_entries:
            raise ValueError("Total number of entries does not match.")

        return pd.DataFrame(worker_df)


class Hdf5LoaderIterator:
    def __init__(
        self,
        name: str,
        dataset_names: list[str],
        iterators_df: pd.DataFrame,
        worker_id: int,
        processors: list[Callable[[Any, dict], tuple[Any, dict]]] | ProcessorsGraph | None = None,
        hdf5_files_desc_dct: dict[str, dict[str, Any]] | None = None,
        load_column_names_dct: dict[str, list[str]] | None = None,
        iterator_class: Type[Hdf5Iterator] | None = None,
        dataset_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.dataset_names = dataset_names
        self.iterators_df = iterators_df
        self.worker_id = worker_id
        self.processors = processors
        self.hdf5_files_desc_dct = hdf5_files_desc_dct
        self.load_column_names_dct = load_column_names_dct
        self.dataset_kwargs = dataset_kwargs

        if iterator_class is None:
            self.iterator_class = Hdf5Iterator
        else:
            self.iterator_class = iterator_class

        self.current_df_idx, self.current_iterator_idx = 0, 0

    def _make_hdf5_iterator(self, df: pd.Series) -> Hdf5Iterator:
        iterator = self.iterator_class(
            df["file"],
            self.dataset_names,
            chunk_size=df["chunk_size"],
            start_entry=df["start"],
            stop_entry=df["stop"],
            dataset_kwargs=self.dataset_kwargs,
            shuffle=df["shuffle"],
            load_column_names_dct=self.load_column_names_dct,
        )

        return iterator

    def _iterate_df(self) -> None:
        df = self.iterators_df.iloc[self.current_iterator_idx]
        self.iterator = self._make_hdf5_iterator(df)
        self.current_df_idx += 1

    def _run_processors(self, arrays_obj: Any, reports: dict[str, Any]) -> tuple[Any, dict] | dict[str, Processor]:
        if self.processors is None:
            return arrays_obj, reports
        elif type(self.processors) is list:
            for proc in self.processors:
                arrays, reports = proc(arrays_obj, reports)
            return arrays, reports
        elif type(self.processors) is ProcessorsGraph:
            processors = self.processors.fit(arrays_obj, reports)
            return processors
        else:
            raise ValueError(f"Processors {self.processors} is not a valid type.")

    def _make_report(self, reports: Any) -> dict:
        reports = {"name": self.name, "worker_id": self.worker_id} | reports

        if self.hdf5_files_desc_dct is not None:
            file_name = os.path.basename(reports["file"])
            reports = reports | self.hdf5_files_desc_dct[file_name]

        return reports

    def __iter__(self) -> Hdf5LoaderIterator:
        return self

    def __next__(self) -> tuple[Any, dict] | dict[str, Processor]:
        try:
            if self.current_df_idx == self.current_iterator_idx:
                self._iterate_df()

            arrays, reports = next(self.iterator)

        except StopIteration:
            self.iterator.close()
            self.current_iterator_idx += 1

            if self.current_iterator_idx == len(self.iterators_df):
                raise StopIteration

            if self.current_df_idx == self.current_iterator_idx:
                self._iterate_df()

            arrays, reports = next(self.iterator)

        reports = self._make_report(reports)

        processors_return = self._run_processors(arrays, reports)

        return processors_return


class Hdf5IterableDataset(IterableDataset):
    def __init__(
        self,
        name: str,
        files: str | list[str],
        dataset_names: list[str],
        num_workers: int,
        chunk_size: int | None = None,
        use_piles: bool = False,
        stage_split_piles: dict[str, list[int] | int] | None = None,
        stage: str | None = None,
        shuffle: bool = False,
        processors: list[Callable[[Any, dict], tuple[Any, dict]]] | ProcessorsGraph | None = None,
        hdf5_files_desc_dct: dict[str, dict[str, Any]] | None = None,
        load_column_names_dct: dict[str, list[str]] | None = None,
        combine_datasets: bool = False,
        allow_carrying_over: bool = True,
        iterator_class: Type[Hdf5Iterator] | None = None,
        dataset_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Iterable dataset for loading HDF5 files in structured array format.

        Parameters
        ----------
        name : str
            Name of the dataset, used for logging and debugging.
        files : list[str]
            List of HDF5 files to load.
        dataset_names : list[str]
            List of dataset names to load from the HDF5 files.
        num_workers : int
            Number of workers to use for loading the data. If -1, will use all available CPU cores.
        chunk_size : int | None, optional
            Size of the chunks to load from the HDF5 files. If None, will load the entire dataset at once.
            If `use_piles` is True, this parameter is ignored and the chunk size is determined by the pile size.
        use_piles : bool, optional
            Whether to use piles for loading the data. If True, will load data in piles instead of chunks.
            Piles are defined in the metadata of the HDF5 files. If False, will load data in chunks. By default False.
        stage_split_piles : dict[str, list[int] | int] | None, optional
            Dictionary containing the stage split piles. The keys are the stage names and the values are either
            lists of integers representing the indices of the piles to use for each stage, or integers representing
            the number of piles to use for each stage. If None, no stage split piles will be used. By default None.
        stage : str | None, optional
            The stage to use for loading the data. If None, will load all data. If provided, will load only the data for the specified stage.
            This is used in conjunction with `stage_split_piles` to load only the data for the specified stage.
            If `stage_split_piles` is provided, this parameter must also be set. By default None.
        shuffle : bool, optional
            Whether to shuffle the data before loading. If True, will shuffle the data before loading.
        processors : list[Callable[[Any, dict], tuple[Any, dict]]] | ProcessorsGraph | None, optional
            List of processors to apply to the data before loading. Each processor should be a callable that
            takes an array-like object (or a dict) and a dictionary of reports, and returns a tuple of the processed
            array and the updated reports. If a ProcessorsGraph is provided, it will be used to process the data.
            If None, no processors will be applied. By default None.
        hdf5_files_desc_dct : dict[str, dict[str, Any]] | None, optional
            Dictionary containing additional metadata for the HDF5 files. The keys are the file names and the values are
            dictionaries containing metadata for each file. If None, no additional metadata will be used. By default None.
        load_column_names_dct : dict[str, list[str]] | None, optional
            Dictionary containing the column names to load for each dataset. The keys are the dataset names and the values are
            lists of column names to load. If None, all columns will be loaded. By default None.
        combine_datasets : bool, optional
            Whether to combine the datasets into a single dataset. If True, iterator will return a single dataset as
            a dictionary with the dataset names as keys. If False, iterator will return each dataset separately.
        allow_carrying_over : bool, optional
            Whether to allow carrying over the last chunk of data to the next worker, if it is smaller than the chunk size.
            If True, the last chunk will be carried over to the next worker. If False, the last chunk will be merged.
            This is useful when using `chunk_size` to ensure that all data is processed in chunks of similar size, but
            may lead to unexpected behavior if all data is loaded at once. By default True.

        """
        super().__init__()
        if (stage is None) != (stage_split_piles is None):
            raise ValueError("stage and stage_split_piles must be set together.")

        if not allow_carrying_over and chunk_size is not None:
            logging.warning(
                "Allow carry over is set to False, but chunk size is not None. "
                "This may lead to unexpected behavior. Consider setting allow_carrying_over to True."
            )

        if type(files) is str and files.endswith("*"):
            files = glob.glob(f"{files}.hdf5")
            logging.info(f"Wildcard found {len(files)} hdf5 files.")

        if type(files) is not list:
            raise TypeError("Files must be a wildcard * string or a list of strings!")

        if len(files) == 0:
            raise RuntimeError("No HDF5 files found!")

        self.files = files

        if len(self.files) == 1 and (stage or stage_split_piles) and not use_piles:
            raise ValueError("stage and stage_split_piles require use_piles=True.")

        self.name = name
        self.dataset_names = dataset_names
        self.chunk_size = chunk_size
        self.use_piles = use_piles
        self.shuffle = shuffle
        self.hdf5_files_desc_dct = hdf5_files_desc_dct
        self.load_column_names_dct = load_column_names_dct
        self.combine_datasets = combine_datasets
        self.allow_carrying_over = allow_carrying_over
        self.iterator_class = iterator_class
        self.dataset_kwargs = dataset_kwargs

        if num_workers == -1:
            self.num_workers = multiprocessing.cpu_count()
        else:
            self.num_workers = num_workers

        self.stage_idx: list[int] | None = None
        self.total_stage_split: int = 0

        if stage_split_piles is not None:
            if isinstance(stage_split_piles[list(stage_split_piles.keys())[0]], list):
                self.stage_idx, self.total_stage_split = self._get_stage_split_piles_from_lst(stage_split_piles, stage)  # type: ignore
            elif isinstance(stage_split_piles[list(stage_split_piles.keys())[0]], int):
                self.stage_idx, self.total_stage_split = self._get_stage_split_piles_from_int(stage_split_piles, stage)  # type: ignore
            else:
                raise TypeError("stage_split_piles must be a dictionary with lists or integers as values!")

        self.processors = processors
        if isinstance(self.processors, ProcessorsGraph):
            self.processors.copy_processors = True

        self.metadata: dict[str, dict[str, Any]] = {}

        if self.use_piles:
            self._setup_piles()
        else:
            self._setup()

        if self.combine_datasets:
            combined_metadata = self._make_combined_metadata()
            self.metadata = combined_metadata

        self.shape = self._get_total_shape()

        self.worker_iterators_df = self._get_df_iterators()

    def _get_stage_split_piles_from_lst(
        self, stage_split_piles: dict[str, list[int]], stage: str
    ) -> tuple[list[int], int]:
        valid_idx = stage_split_piles[stage]
        return valid_idx, sum([len(v) for v in stage_split_piles.values()])

    def _get_stage_split_piles_from_int(self, stage_split_piles: dict[str, int], stage: str) -> tuple[list[int], int]:
        _split_n_piles, current_idx = {}, 0

        for k in stage_split_piles.keys():
            _split_n_piles[k] = [i for i in range(current_idx, current_idx + stage_split_piles[k])]
            current_idx += stage_split_piles[k]

        valid_idx = _split_n_piles[stage]

        return valid_idx, sum([len(v) for v in _split_n_piles.values()])

    def _setup(self) -> None:
        if self.stage_idx is not None and self.total_stage_split > len(self.files):
            raise RuntimeError(
                f"Total stage split {self.total_stage_split} is greater than number of files {len(self.files)}. "
                "Please check your stage_split_piles configuration."
            )

        if self.stage_idx is not None:
            files = [self.files[i] for i in self.stage_idx]
        else:
            files = self.files

        for file in files:
            for dataset_name in self.dataset_names:
                if dataset_name not in self._get_keys(file):
                    logging.warning(f"Dataset {dataset_name} not found in {file}. Skipping!")
                    continue

                metadata_key = f"{file}:{dataset_name}"

                self.metadata[metadata_key] = {"shape": None}

                shape = self._get_shape(file, dataset_name)
                self.metadata[metadata_key]["shape"] = shape

    def _setup_piles(self) -> None:
        piles_metadata: dict[str, dict[str, Any]] = {}

        for file, dataset_name in product(self.files, self.dataset_names):
            if dataset_name not in self._get_keys(file):
                logging.warning(f"Dataset {dataset_name} not found in {file}. Skipping!")
                continue

            piles_key = f"{file}:{dataset_name}"

            if file not in piles_metadata:
                piles_metadata[piles_key] = {"piles_lst": [], "piles_shapes": []}

            piles_lst = self._get_piles_metadata(file)["piles"][dataset_name]

            if self.stage_idx is not None and self.total_stage_split > len(piles_lst):
                raise RuntimeError(
                    f"Total stage split {self.total_stage_split} is greater than number of piles {len(piles_lst)}. "
                    "Please check your stage_split_piles configuration."
                )

            if self.stage_idx is not None:
                piles_lst = [piles_lst[i] for i in self.stage_idx]

            piles_metadata[piles_key]["piles_lst"] += piles_lst

            piles_shapes = self._get_piles_shape(file, dataset_name, piles_lst)

            if self.stage_idx is not None:
                piles_shapes = [piles_shapes[i] for i in self.stage_idx]

            piles_metadata[piles_key]["piles_shapes"] += piles_shapes

        for piles_key, metadata in piles_metadata.items():
            for pile, shape in zip(metadata["piles_lst"], metadata["piles_shapes"]):
                metadata_key = f"{piles_key}:{pile}"
                self.metadata[metadata_key] = {"shape": shape}

    @staticmethod
    def _get_keys(file_path: str) -> list[str]:
        with h5py.File(file_path, "r") as f:
            keys = list(f.keys())

        return keys

    @staticmethod
    def _get_piles_metadata(file_path: str) -> dict[str, Any]:
        with h5py.File(file_path, "r") as f:
            metadata = json.loads(f["metadata"][()])

        if "piles" not in metadata:
            raise KeyError(f"No piles metadata found in {file_path}. Please disable use_piles.")

        return metadata

    @staticmethod
    def _get_shape(file_path: str, dataset_name: str) -> tuple[int, ...]:
        shape = []

        with h5py.File(file_path, "r") as f:
            rows, columns = f[dataset_name].shape, len(f[dataset_name].dtype.names)

        for r in rows:
            shape.append(r)

        shape.append(columns)

        return tuple(shape)

    @staticmethod
    def _get_piles_shape(file_path: str, dataset_name: str, piles_lst: str) -> list[tuple[int, int]]:
        with h5py.File(file_path, "r") as f:
            shape = [f[dataset_name][pile].shape for pile in piles_lst]

        return shape

    def _get_total_shape(self) -> tuple[int, ...]:
        total_shapes: dict[int, list[int]] = {}

        for i, metadata_shape in enumerate(self.metadata.values()):
            shape = metadata_shape["shape"]

            for i, s in enumerate(shape):
                if i not in total_shapes:
                    total_shapes[i] = []

                total_shapes[i].append(s)

        total_shape = []
        for i, v in total_shapes.items():
            if i == 0:
                total_shape.append(sum(v))
            else:
                total_shape += list(set(v))

        return tuple(total_shape)

    def _make_combined_metadata(self) -> dict[str, dict[str, Any]]:
        _metadata = {}

        for file_key, shape_metadata in self.metadata.items():
            split_file_key = file_key.split(":")

            file_name = split_file_key[0]

            if self.use_piles:
                file_name = f"{file_name}:{split_file_key[2]}"

            if file_name not in _metadata:
                _metadata[file_name] = shape_metadata

        combined_metadata = {}
        for k, v in _metadata.items():
            combined_key = f"{k}:combined"
            combined_metadata[combined_key] = v

        return combined_metadata

    def _get_df_iterators(self) -> pd.DataFrame:
        df = Hdf5IteratorDfMaker(
            self.name,
            self.metadata,
            self.num_workers,
            self.shape,
            self.chunk_size,
            self.shuffle,
        ).make()

        if not self.allow_carrying_over:
            to_merge_df = df[df["start"] != 0]
            df.loc[to_merge_df.index - 1, "stop"] = to_merge_df["stop"].values
            df.drop(to_merge_df.index, inplace=True)
            df.reset_index(drop=True, inplace=True)

        return df

    def __iter__(self) -> Hdf5LoaderIterator:
        worker_info = torch.utils.data.get_worker_info()

        if worker_info is None:
            worker_id = 0
        else:
            worker_id = worker_info.id

        iterators_df = self.worker_iterators_df[self.worker_iterators_df["worker_id"] == worker_id].copy()

        if len(iterators_df) == 0:
            raise StopIteration

        return Hdf5LoaderIterator(
            self.name,
            self.dataset_names,
            iterators_df,
            worker_id,
            self.processors,
            self.hdf5_files_desc_dct,
            self.load_column_names_dct,
            self.iterator_class,
            self.dataset_kwargs,
        )


def default_collate_fn(batch: Any) -> Any:
    return batch


def get_hdf5_dataloader(
    name: str,
    files: str | list[str],
    dataset_names: str | list[str],
    num_workers: int | None = None,
    chunk_size: int | None = None,
    use_piles: bool = False,
    stage_split_piles: dict[str, list[int] | int] | None = None,
    stage: str | None = None,
    shuffle: bool = False,
    hdf5_files_desc_dct: dict[str, dict[str, Any]] | None = None,
    processors: list[Callable[[Any, dict], tuple[Any, dict]]] | ProcessorsGraph | None = None,
    load_column_names_dct: dict[str, list[str]] | None = None,
    combine_datasets: bool = False,
    allow_carrying_over: bool = True,
    iterator_class: Type[Hdf5Iterator] | None = None,
    collate_fn: Callable | None = None,
    dataset_kwargs: dict[str, Any] | None = None,
    dataloader_kwargs: dict[str, Any] | None = None,
) -> tuple[DataLoader, int]:
    if dataloader_kwargs is None:
        dataloader_kwargs = {}

    if num_workers is None and "num_workers" in dataloader_kwargs:
        num_workers = dataloader_kwargs["num_workers"]

    if num_workers == -1:
        num_workers = multiprocessing.cpu_count()
        dataloader_kwargs["num_workers"] = num_workers

    if num_workers is None:
        num_workers = 0
        dataloader_kwargs["num_workers"] = 0
        logging.info("num_workers is set to 0, using single process for loading data.")

    if multiprocessing.get_start_method() == "fork" and num_workers > 0:
        logging.debug("Using 'fork' start method. Consider using 'spawn' or 'forkserver'.")

    if type(dataset_names) is str:
        dataset_names = [dataset_names]
    elif type(dataset_names) is not list:
        raise ValueError("dataset_names must be a string or a list of strings!")

    logging.info(f"Using {num_workers} workers for loading data.")

    hdf5_dataset = Hdf5IterableDataset(
        name,
        files,
        dataset_names,
        num_workers=num_workers if num_workers > 0 else 1,
        chunk_size=chunk_size,
        use_piles=use_piles,
        stage_split_piles=stage_split_piles,
        stage=stage,
        shuffle=shuffle,
        processors=processors,
        hdf5_files_desc_dct=hdf5_files_desc_dct,
        load_column_names_dct=load_column_names_dct,
        combine_datasets=combine_datasets,
        allow_carrying_over=allow_carrying_over,
        iterator_class=iterator_class,
        dataset_kwargs=dataset_kwargs,
    )

    if collate_fn is None:
        collate_fn = default_collate_fn

    dataloader_kwargs.pop("batch_size", None)

    hdf5_dataloader = DataLoader(
        hdf5_dataset,
        batch_size=None,
        collate_fn=collate_fn,
        **dataloader_kwargs,
    )

    return hdf5_dataloader, hdf5_dataset.shape[0]
