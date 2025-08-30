import logging
import multiprocessing
import os
from collections import deque
from typing import Any

import awkward as ak
import h5py
import numpy as np

from f9columnar.ml.hdf5_writer import ArraysHdf5Writer
from f9columnar.processors import Processor


class ProcessorArraysHdf5Writer(ArraysHdf5Writer):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)

    def add_data(
        self,
        data_dct: dict[str, np.ndarray],
        dataset_name: str,
        idx: tuple[int, int],
        resize: tuple | None = None,
    ) -> None:
        with h5py.File(self.file_path, "a") as f:
            dataset = f[dataset_name]

            if resize:
                dataset.resize(resize)

            start, end = idx
            for column_name, column_data in data_dct.items():
                dataset[column_name, start:end] = column_data

    def close_write_handle(self):
        raise NotImplementedError("This method is not implemented in ProcessorArraysHdf5Writer.")


class Hdf5WriterProcessor(Processor):
    def __init__(
        self,
        file_path: str,
        postprocessor_name: str = "hdf5WriterProcessor",
        flat_column_names: list[str] | None = None,
        jagged_column_names: dict[str, list[str]] | None = None,
        chunk_shape: int = 1000,
        max_lengths: dict[str, int] | int = 10,
        pad_values: dict[str, float] | float | None = 0.0,
        n_piles: int | None = None,
        pile_assignment: str = "random",
        save_node: str = "output",
        merge_piles: bool = True,
        enforce_dtypes: dict[str, str] | None = None,
        full_metadata: bool = False,
        max_workers: int | None = None,
        **hdf5_kwargs,
    ) -> None:
        """HDF5 writer for physics objects. It supports both flat and jagged arrays.

        Parameters
        ----------
        file_path : str
            Path to the created HDF5 file.
        postprocessor_name : str, optional
            Name of the postprocessor to use in the graph. Default is "hdf5WriterProcessor".
        flat_column_names : list[str] | None, optional
            List of flat column names to be saved in the HDF5 file. If None, jagged_column_names must be provided.
        jagged_column_names : dict[str, list[str]] | None, optional
            Dictionary of jagged column names to be saved in the HDF5 file. The keys are the names of the physics
            objects (e.g. electrons, jets, etc.), and the values are lists of column names for each physics object.
            If None, flat_column_names must be provided.
        chunk_shape : int, optional
            Number of events to be saved in each chunk. This is used to split the data into chunks for writing.
        max_lengths : dict[str, int] | int, optional
            Maximum length of the jagged arrays. If an int is provided, it will be used for all jagged arrays.
            If a dictionary is provided, the keys must match the keys in jagged_column_names and the values are the
            maximum lengths for each jagged array.
        pad_values : dict[str, float] | float | None, optional
            Values to pad the jagged arrays with. If a float is provided, it will be used for all jagged arrays.
            If a dictionary is provided, the keys must match the keys in jagged_column_names and the values are the
            pad values for each jagged array. If None, no padding will be applied and the resulting arrays will be
            numpy masked arrays.
        n_piles : int | None, optional
            Number of piles to split the data into. If None, the data will be saved in a single dataset.
        pile_assignment : str, optional
            Method of assigning data to piles. Can be 'deque' or 'random'. If 'deque', the data will be assigned to
            piles in a double-ended queue fashion. If 'random', the data will be assigned to piles randomly.
        save_node : str, optional
            Name of the node in the processor that contains the arrays to be saved. Default is "output".
        merge_piles : bool, optional
            If True, the data from all piles will be merged into a single dataset. If False, each pile will be saved
            in a separate file. Default is True.
        enforce_dtypes : dict[str, str] | None, optional
            Dictionary of dtypes to enforce for each column. The keys are the column names and the values are the dtypes.
            If None, the dtypes will be inferred from the arrays.
        full_metadata : bool, optional
            If True, full metadata will be saved in the HDF5 file. If False, reduced metadata will be saved.
            Default is False.
        max_workers : int, optional
            Number of workers to use for writing the data. Default is 1.
        **hdf5_kwargs : Any
            Additional keyword arguments to be passed to the h5py.File.create_dataset method.
        """
        super().__init__(name=postprocessor_name, allow_copy=False)
        if flat_column_names is not None and len(flat_column_names) == 0:
            logging.warning("flat_column_names is an empty list, no flat arrays will be saved.")
            flat_column_names = None

        if jagged_column_names is not None and len(jagged_column_names) == 0:
            logging.warning("jagged_column_names is an empty dictionary, no jagged arrays will be saved.")
            jagged_column_names = None

        if flat_column_names is None and jagged_column_names is None:
            raise ValueError("At least one of flat_column_names or jagged_column_names must be provided.")

        if enforce_dtypes is not None:
            logging.info(f"Enforcing types {list(enforce_dtypes.values())} for branches {list(enforce_dtypes.keys())}.")

        if full_metadata:
            logging.info("Full metadata enabled.")
        else:
            logging.info("Reduced metadata enabled.")

        self.file_path = file_path
        self.chunk_shape = chunk_shape

        if max_workers == 0 or max_workers is None:
            self.max_workers = 1
        elif max_workers == -1:
            self.max_workers = multiprocessing.cpu_count()
        else:
            self.max_workers = max_workers

        if n_piles is None:
            self.n_piles = self.max_workers
        else:
            self.n_piles = n_piles

        self.pile_assignment = pile_assignment
        self.merge_piles = merge_piles
        self.enforce_dtypes = enforce_dtypes
        self.full_metadata = full_metadata

        self.save_node = save_node

        if n_piles is not None:
            if merge_piles:
                logging.info(f"Saving {self.n_piles} merged piles.")
            else:
                logging.info(f"Saving {self.n_piles} separate piles.")

        self.hdf5_kwargs = hdf5_kwargs

        self.object_info_dct: dict[str, dict[str, int]] = {}
        self.object_piles_info_dct: dict[str, dict[int, dict[str, int]]] = {}

        self.object_column_names_dct: dict[str, list[str]] = {}

        self.pad_values: dict[str, float] | None = None
        self.max_lengths: dict[str, int] = {}

        self.writers: list[ProcessorArraysHdf5Writer] = []

        if flat_column_names is not None:
            self.write_flat = True
            self.object_column_names_dct["events"] = flat_column_names
        else:
            self.write_flat = False

        if jagged_column_names is not None:
            self.write_jagged = True

            self._set_max_lengths(jagged_column_names, max_lengths)
            self._set_pad_values(jagged_column_names, pad_values)

            for physics_object_name, physics_object_column_names in jagged_column_names.items():
                self.object_column_names_dct[physics_object_name] = physics_object_column_names
        else:
            self.write_jagged = False

        self.flat_column_names, self.jagged_column_names = flat_column_names, jagged_column_names

        self._pile_deque: deque[int] | None = None

        self._has_piles_lst = False
        self._created_datasets = False
        self._current_pile_idx = 0

        self._worker_id: int
        self._current_dataset_name: str
        self._piles_lst: list[int]
        self._worker_offsets: dict[int, int]

    def _setup_piles_lst(self, worker_id: int) -> None:
        if self._has_piles_lst:
            return None

        piles_lst_split = np.array_split([i for i in range(self.n_piles)], self.max_workers)
        self._piles_lst = [int(i) for i in piles_lst_split[worker_id]]
        self._worker_offsets = {i: len(piles_lst_split[i]) * i for i in range(len(piles_lst_split))}

        if self.pile_assignment == "deque":
            self._pile_deque = deque(map(int, self._piles_lst))

        self._worker_id = worker_id
        self._has_piles_lst = True

    def _set_max_lengths(self, jagged_column_names: dict[str, list[str]], max_lengths: dict[str, int] | int) -> None:
        if type(max_lengths) is int:
            self.max_lengths = {column_name: max_lengths for column_name in jagged_column_names.keys()}
        elif type(max_lengths) is dict:
            self.max_lengths = max_lengths
        else:
            raise TypeError("max_lengths must be an int or a dictionary with column names as keys.")

    def _set_pad_values(
        self, jagged_column_names: dict[str, list[str]], pad_values: dict[str, float] | float | None
    ) -> None:
        if pad_values is None:
            self.pad_values = None
        elif type(pad_values) is float:
            self.pad_values = {column_name: pad_values for column_name in jagged_column_names.keys()}
        elif type(pad_values) is dict:
            self.pad_values = pad_values
        else:
            raise TypeError("pad_values must be a float, None or a dictionary with column names as keys.")

    def _make_metadata(self, events_metadata: dict[str, Any], jagged_metadata: dict[str, Any]) -> dict[str, Any]:
        metadata = events_metadata | jagged_metadata

        piles_metadata: dict[str, list[str]] = {}

        if self.full_metadata:
            if "events_piles" in metadata:
                piles_metadata["events"] = metadata["events_piles"]
                metadata.pop("events_piles")

            if "jagged_piles" in metadata:
                piles_metadata.update(metadata["jagged_piles"])
                metadata.pop("jagged_piles")

            if len(piles_metadata) != 0:
                metadata["piles"] = piles_metadata
        else:
            metadata = {}

        if self.pad_values is not None:
            metadata["pad_values"] = self.pad_values

        return metadata

    def _get_flat_dtypes(self, arrays: ak.Array) -> np.dtype:
        dtypes_dct: dict[str, Any] = {"names": [], "formats": []}

        if self.flat_column_names is None:
            raise RuntimeError("Flat column names must be provided for flat arrays!")

        for column_name in self.flat_column_names:
            if column_name not in arrays.fields:
                raise RuntimeError(f"Column {column_name} not found in arrays!")

            dtypes_dct["names"].append(column_name)

            if self.enforce_dtypes is not None and column_name in self.enforce_dtypes:
                dtypes_dct["formats"].append(self.enforce_dtypes[column_name])
            else:
                dtypes_dct["formats"].append(ak.type(arrays[column_name]).content.primitive)

        return np.dtype(dtypes_dct)  # type: ignore

    def _get_jagged_dtypes(self, arrays: ak.Array) -> dict[str, np.dtype]:
        dtypes_dct: dict[str, np.dtype] = {}

        if self.jagged_column_names is None:
            raise RuntimeError("Jagged column names must be provided for jagged arrays!")

        for physics_object_name, physics_object_column_names in self.jagged_column_names.items():
            dct: dict[str, list[str]] = {"names": [], "formats": []}

            for column_name in physics_object_column_names:
                if column_name not in arrays.fields:
                    raise RuntimeError(f"Column {column_name} not found in arrays!")

                dct["names"].append(column_name)

                if self.enforce_dtypes is not None and column_name in self.enforce_dtypes:
                    dct["formats"].append(self.enforce_dtypes[column_name])
                else:
                    dct["formats"].append(ak.type(arrays[column_name]).content.content.primitive)

            dtypes_dct[physics_object_name] = np.dtype(dct)  # type: ignore

        return dtypes_dct

    def _create_events_datasets(self, dtype: np.dtype) -> dict[str, Any]:
        if self.flat_column_names is None:
            raise RuntimeError("Flat column names must be provided for event datasets!")

        writers: list[ProcessorArraysHdf5Writer] = []
        metadata: dict[str, Any] = {}

        dataset_names = [f"events/p{p}" for p in self._piles_lst]

        if self.merge_piles:
            writers.append(ProcessorArraysHdf5Writer(self.file_path))
        else:
            for i in self._piles_lst:
                file_name = os.path.join(os.path.dirname(self.file_path), f"p{i}.hdf5")
                writers.append(ProcessorArraysHdf5Writer(file_name))

        if not self.merge_piles:
            for w in writers:
                w.create_datasets(
                    dataset_names=["events"],
                    mode="w",
                    shape=(self.chunk_shape,),
                    maxshape=(None,),
                    dtype=dtype,
                    **self.hdf5_kwargs,
                )
        else:
            writers[0].create_datasets(
                dataset_names=dataset_names,
                mode="w",
                shape=(self.chunk_shape,),
                maxshape=(None,),
                dtype=dtype,
                **self.hdf5_kwargs,
            )

        metadata["events_columns"] = self.flat_column_names

        self.object_piles_info_dct["events"] = {}
        for p in self._piles_lst:
            self.object_piles_info_dct["events"][p] = {
                "current_idx": 0,
                "current_shape": self.chunk_shape,
            }

        self.object_column_names_dct["events"] = self.flat_column_names

        if self.merge_piles:
            metadata["events_piles"] = [f"p{i}" for i in self._piles_lst]

        self.writers = writers

        return metadata

    def _create_jagged_datasets(self, dtype: dict[str, np.dtype]) -> dict[str, Any]:
        if self.jagged_column_names is None:
            raise RuntimeError("Jagged column names must be provided for jagged datasets!")

        metadata: dict[str, Any] = {}
        piles_metadata: dict[str, list[str]] = {}

        if len(self.writers) == 0:
            has_writers = False
            writers: list[ProcessorArraysHdf5Writer] = []
        else:
            has_writers = True
            writers = self.writers

        for i, (physics_object_name, physics_object_column_names) in enumerate(self.jagged_column_names.items()):
            dataset_names = [f"{physics_object_name}/p{p}" for p in self._piles_lst]
            if i == 0 and not has_writers:
                if self.merge_piles:
                    writers.append(ProcessorArraysHdf5Writer(self.file_path))
                else:
                    for p in self._piles_lst:
                        file_name = os.path.join(os.path.dirname(self.file_path), f"p{p}.hdf5")
                        writers.append(ProcessorArraysHdf5Writer(file_name))

            max_length = self.max_lengths[physics_object_name]
            physics_object_dtype = dtype[physics_object_name]

            mode = "a" if has_writers or i != 0 else "w"

            if not self.merge_piles:
                for w in writers:
                    w.create_datasets(
                        dataset_names=[physics_object_name],
                        mode=mode,
                        shape=(self.chunk_shape, max_length),
                        maxshape=(None, max_length),
                        dtype=physics_object_dtype,
                        **self.hdf5_kwargs,
                    )
            else:
                writers[0].create_datasets(
                    dataset_names=dataset_names,
                    mode=mode,
                    shape=(self.chunk_shape, max_length),
                    maxshape=(None, max_length),
                    dtype=physics_object_dtype,
                    **self.hdf5_kwargs,
                )

            metadata[f"{physics_object_name}_columns"] = physics_object_column_names

            self.object_piles_info_dct[physics_object_name] = {}
            for p in self._piles_lst:
                self.object_piles_info_dct[physics_object_name][p] = {
                    "current_idx": 0,
                    "current_shape": self.chunk_shape,
                }
            piles_metadata[physics_object_name] = [f"p{i}" for i in self._piles_lst]

            self.object_column_names_dct[physics_object_name] = physics_object_column_names

        if self.merge_piles:
            metadata["jagged_piles"] = piles_metadata

        if not has_writers:
            self.writers = writers

        return metadata

    def _get_flat_arrays(self, arrays: ak.Array, column_names: list[str]) -> list[np.ndarray]:
        save_arrays = []

        for column_name in column_names:
            if column_name not in arrays.fields:
                raise RuntimeError(f"Column {column_name} not found in arrays!")

            column = ak.to_numpy(arrays[column_name])
            save_arrays.append(column)

        return save_arrays

    def _get_jagged_arrays(self, arrays: ak.Array, column_names: list[str]) -> list[np.ndarray]:
        save_arrays = []

        for column_name in column_names:
            if column_name not in arrays.fields:
                raise RuntimeError(f"Column {column_name} not found in arrays!")

            column_matrix = arrays[column_name]
            elements_type = str(ak.type(column_matrix)).split("*")[-1].strip()
            column_matrix = ak.pad_none(column_matrix, self.max_lengths[self._current_dataset_name], clip=True)

            if self.pad_values is not None:
                pad_value = self.pad_values[self._current_dataset_name]
                column_matrix = ak.fill_none(column_matrix, getattr(np, elements_type)(pad_value))

            column_matrix = ak.to_numpy(column_matrix)

            save_arrays.append(column_matrix)

        return save_arrays

    def _get_pile_idx(self) -> int:
        if self.pile_assignment == "deque":
            if self._pile_deque is None:
                raise RuntimeError("Pile deque is not initialized!")

            idx = self._pile_deque[0]
            self._pile_deque.rotate(-1)
            return idx
        else:
            return np.random.choice(len(self._piles_lst))

    def set_current_idx(self, value: int) -> None:
        self.object_piles_info_dct[self._current_dataset_name][self.current_pile_idx]["current_idx"] = value
        return None

    def set_current_shape(self, value: int) -> None:
        self.object_piles_info_dct[self._current_dataset_name][self.current_pile_idx]["current_shape"] = value
        return None

    def set_current_pile_idx(self, value: int) -> None:
        self._current_pile_idx = value + self._worker_offsets[self._worker_id]
        return None

    @property
    def current_idx(self) -> int:
        return self.object_piles_info_dct[self._current_dataset_name][self.current_pile_idx]["current_idx"]

    @property
    def current_shape(self) -> int:
        return self.object_piles_info_dct[self._current_dataset_name][self.current_pile_idx]["current_shape"]

    @property
    def current_pile_idx(self) -> int:
        return self._current_pile_idx

    def _write_object_arrays(
        self,
        arrays: ak.Array,
        dataset_name: str,
        column_names: list[str],
        pile_idx_lst: list[int],
        is_flat: bool = True,
    ) -> None:
        self._current_dataset_name = dataset_name

        if not self._created_datasets:
            if self.write_flat:
                flat_dtypes = self._get_flat_dtypes(arrays)
                events_metadata = self._create_events_datasets(flat_dtypes)
            else:
                events_metadata = {}

            if self.write_jagged:
                jagged_dtypes = self._get_jagged_dtypes(arrays)
                jagged_metadata = self._create_jagged_datasets(jagged_dtypes)
            else:
                jagged_metadata = {}

            metadata = self._make_metadata(events_metadata, jagged_metadata)

            for w in self.writers:
                w.add_metadata(metadata)

            self._created_datasets = True

        if is_flat:
            save_arrays = self._get_flat_arrays(arrays, column_names)
        else:
            save_arrays = self._get_jagged_arrays(arrays, column_names)

        save_arrays_idx = np.arange(len(arrays))

        array_chunks = (len(arrays) + self.chunk_shape - 1) // self.chunk_shape
        chunk_save_arrays_idx = np.array_split(save_arrays_idx, array_chunks)

        for i, chunk_array_idx in enumerate(chunk_save_arrays_idx):
            real_idx = pile_idx_lst[i]
            self.set_current_pile_idx(real_idx)

            n_chunk = len(chunk_array_idx)

            start_idx = self.current_idx
            stop_idx = start_idx + n_chunk

            self.set_current_idx(stop_idx)

            resize: tuple[int, ...] | None = None

            if self.current_idx > self.current_shape:
                if is_flat:
                    resize = (stop_idx,)
                else:
                    resize = (stop_idx, self.max_lengths[self._current_dataset_name])

                self.set_current_shape(stop_idx)

            if not self.merge_piles:
                current_dataset_name = self._current_dataset_name
            else:
                current_dataset_name = f"{self._current_dataset_name}/p{self.current_pile_idx}"

            if not self.merge_piles:
                writer = self.writers[real_idx]
            else:
                writer = self.writers[0]

            chunk_arrays_dct: dict[str, np.ndarray] = {}
            for column_name, save_array in zip(column_names, save_arrays):
                chunk_arrays_dct[column_name] = save_array[chunk_array_idx]

            writer.add_data(chunk_arrays_dct, current_dataset_name, idx=(start_idx, stop_idx), resize=resize)

    def run(self, arrays: ak.Array) -> dict[str, ak.Array]:
        if len(arrays) == 0:
            return {"arrays": arrays}

        worker_id = self.reports["worker_id"]  # type: ignore[index]
        self._setup_piles_lst(worker_id)

        n_add_iters = (len(arrays) + self.chunk_shape - 1) // self.chunk_shape
        pile_idx_lst = [self._get_pile_idx() for _ in range(n_add_iters)]

        for physics_object_name, physics_object_column_names in self.object_column_names_dct.items():
            self._write_object_arrays(
                arrays,
                dataset_name=physics_object_name,
                column_names=physics_object_column_names,
                pile_idx_lst=pile_idx_lst,
                is_flat=(physics_object_name == "events"),
            )

        return {"arrays": arrays}
