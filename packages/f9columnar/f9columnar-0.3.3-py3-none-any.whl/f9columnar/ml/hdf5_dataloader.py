from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

import numpy as np
import torch
from torch.utils.data import DataLoader

from f9columnar.hdf5_dataloader import (
    Hdf5Iterator,
    get_hdf5_dataloader,
)
from f9columnar.ml.dataloader_helpers import (
    ColumnSelection,
    column_stack_structured_array,
    get_column_selection,
    padding_mask,
)
from f9columnar.ml.imbalanced_sampler import ImbalancedSampler
from f9columnar.ml.scalers import CategoricalFeatureScaler, NumericalFeatureScaler

WeightedBatchType = tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    dict[str, Any],
]


@dataclass(frozen=True, slots=True, repr=False, eq=False)
class StackedDataset:
    """Container for a stacked dataset created from a structured array.

    Attributes
    ----------
    X : np.ndarray
        Feature matrix, typically a 2D or 3D numpy array. If 2D, it is assumed to be of shape (n_samples, n_features).
        If 3D, it is assumed to be of shape (n_samples, n_objects, n_features).
    categ_idx : np.ndarray | None, optional
        Indices of categorical features in the last dimension of X, by default None.
    numer_idx : np.ndarray | None, optional
        Indices of numerical features in the last dimension of X, by default None.
    extra : dict[str, np.ndarray] | None, optional
        Additional data associated with the dataset, such as weights or labels, by default None.
        The keys of the dictionary should be strings, and the values should be numpy arrays.
        If provided, this data can be accessed using the `get_extra` method.
    """

    X: np.ndarray
    categ_idx: np.ndarray | None = None
    numer_idx: np.ndarray | None = None
    extra: dict[str, np.ndarray] | None = field(default_factory=dict)

    @property
    def features(self) -> np.ndarray:
        return self.X

    @property
    def numer_features(self) -> np.ndarray | None:
        if self.numer_idx is None:
            return None

        return self.X[..., self.numer_idx]

    @property
    def categ_features(self) -> np.ndarray | None:
        if self.categ_idx is None:
            return None

        return self.X[..., self.categ_idx]

    def get_extra(self, name: str, default: Any | None = None) -> np.ndarray | None:
        if self.extra is None or name not in self.extra:
            return default

        return self.extra[name]


@dataclass(frozen=True, slots=True, repr=False, eq=False)
class StackedDatasets:
    """Collection of stacked datasets.

    This class allows you to store multiple `StackedDataset` instances, each identified by a unique key (string).
    You can access datasets by their keys, add new datasets, and retrieve the list of available datasets.

    Attributes
    ----------
    _datasets : dict[str, StackedDataset]
        A dictionary that maps dataset names (keys) to their corresponding `StackedDataset` instances (values).
    """

    _datasets: dict[str, StackedDataset] = field(default_factory=dict)

    def keys(self) -> list[str]:
        return list(self._datasets.keys())

    def __setitem__(self, key: str, value: StackedDataset) -> None:
        if not isinstance(value, StackedDataset):
            raise TypeError(f"Value must be an instance of StackedDataset, got {type(value)} instead.")

        self._datasets[key] = value

    def __getitem__(self, item: str) -> StackedDataset:
        return self._datasets[item]

    def get(self, item: str, default: Any | None = None) -> StackedDataset | None:
        if item not in self._datasets:
            return default

        return self._datasets[item]

    def __len__(self) -> int:
        return len(self._datasets)

    def __iter__(self):
        return iter(self._datasets.values())

    def items(self) -> Iterable[tuple[str, StackedDataset]]:
        return self._datasets.items()

    def __repr__(self) -> str:
        return f"StackedDatasets({self.keys()})"

    def __str__(self) -> str:
        return f"StackedDatasets with datasets: {self.keys()}"


@dataclass(slots=True, repr=False, eq=False)
class WeightedBatch:
    """Container for a weighted batch of data.

    All parameters can be either numpy arrays or PyTorch tensors. If numpy arrays are provided, they will be
    converted to PyTorch tensors.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix.
    y : np.ndarray
        Labels for the data.
    w : np.ndarray
        Weights for the data.
    y_aux : np.ndarray
        Auxiliary labels for the data, e.g., signal type or label type.
    """

    _X: np.ndarray | torch.Tensor
    _y: np.ndarray | torch.Tensor | None
    _w: np.ndarray | torch.Tensor | None
    _y_aux: np.ndarray | torch.Tensor | None

    def __post_init__(self) -> None:
        if isinstance(self._X, np.ndarray):
            self._X = torch.from_numpy(self._X)

        if isinstance(self._y, np.ndarray):
            self._y = torch.from_numpy(self._y)

        if isinstance(self._w, np.ndarray):
            self._w = torch.from_numpy(self._w)

        if isinstance(self._y_aux, np.ndarray):
            self._y_aux = torch.from_numpy(self._y_aux)

    @property
    def X(self) -> torch.Tensor:
        return self._X  # type: ignore

    @property
    def y(self) -> torch.Tensor | None:
        return self._y  # type: ignore

    @property
    def w(self) -> torch.Tensor | None:
        return self._w  # type: ignore

    @property
    def y_aux(self) -> torch.Tensor | None:
        return self._y_aux  # type: ignore

    @property
    def feature_shape(self) -> tuple[int, ...]:
        return tuple(self._X.shape)

    @property
    def batch(self) -> tuple[torch.Tensor, torch.Tensor | None, torch.Tensor | None, torch.Tensor | None]:
        return self._X, self._y, self._w, self._y_aux  # type: ignore

    def mask(self, mask: np.ndarray | torch.Tensor) -> WeightedBatch:
        if isinstance(mask, np.ndarray):
            mask = torch.from_numpy(mask)

        return self.__class__(
            self._X[mask],
            self._y[mask] if self._y is not None else None,
            self._w[mask] if self._w is not None else None,
            self._y_aux[mask] if self._y_aux is not None else None,
        )

    def __len__(self) -> int:
        return self._X.shape[0]

    def __getitem__(self, value: slice) -> WeightedBatch:
        if self._y is None:
            y = None
        else:
            y = self._y[value]

        if self._w is None:
            w = None
        else:
            w = self._w[value]

        if self._y_aux is None:
            y_aux = None
        else:
            y_aux = self._y_aux[value]

        return self.__class__(self._X[value], y, w, y_aux)


@dataclass(frozen=True, slots=True, repr=False, eq=False)
class WeightedDatasetBatch:
    """Collection of weighted batches.

    This class allows you to store multiple `WeightedBatch` instances, each identified by a unique key (string).
    You can access batches by their keys, add new batches, and retrieve the list of available batches.

    Attributes
    ----------
    _datasets : dict[str, WeightedBatch]
        A dictionary that maps dataset names (keys) to their corresponding `WeightedBatch` instances (values).
    """

    _datasets: dict[str, WeightedBatch] = field(default_factory=dict)

    def __setitem__(self, key: str, value: WeightedBatch) -> None:
        self._datasets[key] = value

    def __getitem__(self, args: str | tuple[str, slice]) -> WeightedBatch:
        if type(args) is str:
            return self._datasets[args]
        elif type(args) is tuple and len(args) == 2:
            return self._datasets[args[0]][args[1]]
        else:
            raise ValueError(f"Invalid arguments for __getitem__: {args}")

    def __len__(self) -> int:
        return len(self._datasets)

    def keys(self) -> list[str]:
        return list(self._datasets.keys())

    @property
    def feature_shape(self):
        return {k: v.X.shape for k, v in self._datasets.items()}

    @property
    def dim(self) -> int:
        shapes = [v.X.shape[0] for v in self._datasets.values()]

        if len(shapes) == 0:
            raise RuntimeError("No datasets in WeightedDatasetBatch to determine dimension.")

        if len(set(shapes)) != 1:
            raise RuntimeError("All datasets in WeightedDatasetBatch must have the same first dimension.")

        return shapes[0]

    def mask(self, mask: np.ndarray | torch.Tensor, dataset: str | None = None) -> WeightedDatasetBatch:
        if isinstance(mask, np.ndarray):
            mask = torch.from_numpy(mask)

        _masked_datasets = {}
        for key, w_batch in self._datasets.items():
            if dataset is None or key == dataset:
                _masked_datasets[key] = w_batch.mask(mask)
            else:
                _masked_datasets[key] = w_batch

        return self.__class__(_masked_datasets)

    def __repr__(self) -> str:
        return f"WeightedDatasetBatch({self.keys()})"

    def __str__(self) -> str:
        return f"WeightedDatasetBatch with datasets: {self.keys()}"


class MLHdf5Iterator(Hdf5Iterator):
    def __init__(
        self,
        file: str,
        dataset_names: list[str],
        chunk_size: int | None,
        start_entry: int,
        stop_entry: int,
        shuffle: bool = False,
        load_column_names_dct: dict[str, list[str]] | None = None,
        dataset_kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            file=file,
            dataset_names=dataset_names,
            chunk_size=chunk_size,
            start_entry=start_entry,
            stop_entry=stop_entry,
            shuffle=shuffle,
            load_column_names_dct=load_column_names_dct,
            dataset_kwargs=dataset_kwargs,
            filter_dataset_kwargs=False,
        )
        if len(self.dataset_kwargs) == 0:
            raise ValueError("dataset_kwargs must be provided!")

        if "batch_size" not in self.dataset_kwargs:
            raise ValueError("Batch size must be provided in dataset_kwargs!")

        if not self.combined_dataset:
            raise ValueError("MLHdf5Iterator is designed to work with combined datasets only!")

        # batch setup
        self.batch_size = self.dataset_kwargs["batch_size"]

        if self.batch_size is None:
            self.batch_size = self.chunk_size

        self.drop_last = self.dataset_kwargs.get("drop_last", False)

        self.setup_func: Callable[[StackedDatasets, MLHdf5Iterator], WeightedDatasetBatch | None]

        if "setup_func" not in self.dataset_kwargs:
            self.setup_func = default_setup_func
        else:
            self.setup_func = self.dataset_kwargs["setup_func"]

        # setup imbalanced class sampling
        self.imbalanced_sampler: ImbalancedSampler | None

        self.used_imbalanced_sampler = self.dataset_kwargs.get("imbalanced_sampler", None)

        if self.used_imbalanced_sampler is not None:
            imbalanced_sampler_kwargs = self.dataset_kwargs.get("imbalanced_sampler_kwargs", {})
            self.imbalanced_sampler = ImbalancedSampler(self.used_imbalanced_sampler, **imbalanced_sampler_kwargs)
        else:
            self.imbalanced_sampler = None

        # setup column selection
        self.selection: ColumnSelection = self.dataset_kwargs["selection"]

        # feature scaling setup
        self.scaler_type = self.dataset_kwargs.get("scaler_type", None)
        self.scaler_path = self.dataset_kwargs.get("scaler_path", None)

        self.numer_feature_scaler_dct: dict[str, list[NumericalFeatureScaler | None]] = {}
        self.categ_feature_scaler_dct: dict[str, list[CategoricalFeatureScaler | None]] = {}

        self._setup_scalers(self.dataset_kwargs.get("scalers_extra_hash", ""))

        # remove unnecessary dataset kwargs for lighter reports
        self._filter_dataset_kwargs()

        # internal setup
        self.total, self.current = 0, 0

        # internal data types
        self.weighted_dataset_batch: WeightedDatasetBatch

    def _setup_scalers(self, extra_hash: str = "") -> None:
        for dataset_name in self.selection.keys():
            self.numer_feature_scaler_dct[dataset_name] = []
            self.categ_feature_scaler_dct[dataset_name] = []

            for i in range(self.selection[dataset_name].n_objects):
                numer_feature_scaler, categ_feature_scaler = self._setup_dataset_scaler(
                    self.scaler_path,
                    self.scaler_type,
                    dataset_name,
                    postfix=f"{dataset_name}_{i}",
                    extra_hash=extra_hash,
                )
                self.numer_feature_scaler_dct[dataset_name].append(numer_feature_scaler)
                self.categ_feature_scaler_dct[dataset_name].append(categ_feature_scaler)

    def _setup_dataset_scaler(
        self,
        scaler_path: str | None,
        scaler_type: str | None,
        dataset_name: str,
        postfix: str | None = None,
        extra_hash: str = "",
    ) -> tuple[NumericalFeatureScaler | None, CategoricalFeatureScaler | None]:
        if scaler_path is None and scaler_type is None:
            return None, None

        numer_feature_scaler: NumericalFeatureScaler | None
        categ_feature_scaler: CategoricalFeatureScaler | None

        numer_column_names = self.selection[dataset_name].numer_columns
        categ_column_names = self.selection[dataset_name].categ_columns

        if len(numer_column_names) != 0:
            numer_feature_scaler = NumericalFeatureScaler(scaler_type, save_path=scaler_path)
            numer_feature_scaler = numer_feature_scaler.load(numer_column_names, postfix, extra_hash=extra_hash)

            if numer_feature_scaler is None:
                raise RuntimeError("Failed to load numerical feature scaler!")
        else:
            numer_feature_scaler = None

        if len(categ_column_names) != 0:
            categ_feature_scaler = CategoricalFeatureScaler("categorical", save_path=scaler_path)
            categ_feature_scaler = categ_feature_scaler.load(categ_column_names, postfix, extra_hash=extra_hash)

            if categ_feature_scaler is None:
                raise RuntimeError("Failed to load categorical feature scaler!")
        else:
            categ_feature_scaler = None

        return numer_feature_scaler, categ_feature_scaler

    def _scale(self, X: np.ndarray, dataset_name: str, is_numer: bool) -> np.ndarray:
        scalers: list[NumericalFeatureScaler | None] | list[CategoricalFeatureScaler | None]

        if is_numer:
            scalers = self.numer_feature_scaler_dct[dataset_name]
        else:
            scalers = self.categ_feature_scaler_dct[dataset_name]

        n_objects = self.selection[dataset_name].n_objects

        if n_objects == 1:
            scaler = scalers[0]
            if scaler is not None:
                X = scaler.transform(X)
        else:
            X_objects = []
            for i, scaler in enumerate(scalers):
                if scaler is not None:
                    X_i = X[:, i, :]
                    pad_value = self.selection[dataset_name].pad_value

                    if pad_value is not None:
                        mask = padding_mask(X_i, pad_value)

                        X_full = np.full_like(X_i, pad_value)
                        X_full[mask] = scaler.transform(X_i[mask])

                        X_objects.append(X_full)
                    else:
                        X_objects.append(scaler.transform(X_i))
                else:
                    X_objects.append(X[:, i, :])

            X = np.stack(X_objects, axis=1)

        return X

    def _feature_dataset_scale(
        self,
        X_numer: np.ndarray | None,
        X_categ: np.ndarray | None,
        dataset_name: str,
    ) -> tuple[np.ndarray | None, np.ndarray | None]:
        if X_numer is not None:
            X_numer = self._scale(X_numer, dataset_name, is_numer=True)

        if X_categ is not None:
            X_categ = self._scale(X_categ, dataset_name, is_numer=False)

        return X_numer, X_categ

    def split_and_feature_scale(self, dataset_arrays_dct: dict[str, np.ndarray]) -> StackedDatasets:
        stacked_datasets = StackedDatasets()

        for dataset_name, arrays in dataset_arrays_dct.items():
            numer_names = self.selection[dataset_name].numer_columns
            categ_names = self.selection[dataset_name].categ_columns

            extra_names = self.selection[dataset_name].extra_columns
            if len(extra_names) != 0:
                extra = {name: arrays[name].copy() for name in extra_names}
            else:
                extra = None

            if len(numer_names) != 0:
                X_numer_dataset_stack = column_stack_structured_array(arrays, numer_names)
                numer_shape = X_numer_dataset_stack.shape
            else:
                X_numer_dataset_stack = None

            if len(categ_names) != 0:
                X_categ_dataset_stack = column_stack_structured_array(arrays, categ_names)
                categ_shape = X_categ_dataset_stack.shape
            else:
                X_categ_dataset_stack = None

            X_numer_dataset_stack, X_categ_dataset_stack = self._feature_dataset_scale(
                X_numer_dataset_stack, X_categ_dataset_stack, dataset_name
            )

            if X_numer_dataset_stack is not None and X_categ_dataset_stack is not None:
                X_dataset_stack = np.concatenate([X_numer_dataset_stack, X_categ_dataset_stack], axis=-1)
                numer_idx = np.arange(numer_shape[1])
                categ_idx = np.arange(numer_shape[1], numer_shape[1] + categ_shape[1])

            elif X_numer_dataset_stack is not None:
                X_dataset_stack = X_numer_dataset_stack
                categ_idx, numer_idx = None, np.arange(X_numer_dataset_stack.shape[1])

            elif X_categ_dataset_stack is not None:
                X_dataset_stack = X_categ_dataset_stack
                categ_idx, numer_idx = np.arange(X_categ_dataset_stack.shape[1]), None

            else:
                raise RuntimeError("Both X_numer and X_categ are None!")

            stacked_datasets[dataset_name] = StackedDataset(
                X=X_dataset_stack,
                categ_idx=categ_idx,
                numer_idx=numer_idx,
                extra=extra,
            )

        return stacked_datasets

    def on_iter_start_setup(self) -> bool:
        dataset_arrays_dct: dict[str, np.ndarray] = {}

        for dataset_name in self.dataset_names:
            array = self._get_dataset_array(dataset_name)
            dataset_arrays_dct[dataset_name] = array

        stacked_datasets = self.split_and_feature_scale(dataset_arrays_dct)

        setup_func_return = self.setup_func(stacked_datasets, self)

        if setup_func_return is None:
            return False

        self.weighted_dataset_batch = setup_func_return

        if set(self.dataset_names) != set(self.weighted_dataset_batch.keys()):
            logging.critical(f"Expected: {self.dataset_names}, have: {self.weighted_dataset_batch.keys()}!")
            raise RuntimeError("Dataset names mismatch!")

        self.total = self.weighted_dataset_batch.dim

        if self.batch_size > self.total:
            self.batch_size = self.total

        return True

    def make_report(self) -> dict[str, Any]:
        report = super().make_report()
        extra_report = {
            "batch_current": self.current,
            "batch_total": self.total,
            "batch_size": self.batch_size,
            "drop_last": self.drop_last,
            "used_imbalanced_sampler": self.used_imbalanced_sampler,
            "numer_feature_scaler_dct": self.numer_feature_scaler_dct,
            "categ_feature_scaler_dct": self.categ_feature_scaler_dct,
        }
        return report | extra_report

    def close(self) -> None:
        self.handle.close()

    def __iter__(self) -> MLHdf5Iterator:
        return self

    def __next__(self) -> tuple[WeightedDatasetBatch, dict[str, Any]]:
        if self.current == 0:
            start_status = self.on_iter_start_setup()
            if not start_status:
                raise StopIteration

        if self.current == self.total:
            self.close()
            raise StopIteration

        next_current = self.current + self.batch_size
        if next_current >= self.total:
            next_current = self.total

        if self.drop_last:
            if next_current - self.current < self.batch_size:
                self.close()
                raise StopIteration

        iter_weighted_dataset_batch = WeightedDatasetBatch()

        for ds_name in self.weighted_dataset_batch.keys():
            iter_weighted_dataset_batch[ds_name] = self.weighted_dataset_batch[ds_name, self.current : next_current]

        self.current = next_current

        reports = self.make_report()

        return iter_weighted_dataset_batch, reports


def remap_labels_lookup(y: np.ndarray, max_label: int, remap_labels: dict[int, int]) -> tuple[np.ndarray, np.ndarray]:
    lookup = np.full(max_label + 1, -1)

    for old_label, new_label in remap_labels.items():
        lookup[old_label] = new_label

    y = lookup[y]

    mask_unmapped = y != -1

    return y[mask_unmapped], mask_unmapped


def events_collate_fn(batch: Any) -> WeightedBatchType:
    ds, reports = batch[0]["events"], batch[1]

    numer_feature_scaler_dct = reports.pop("numer_feature_scaler_dct")
    categ_feature_scaler_dct = reports.pop("categ_feature_scaler_dct")

    reports["scaler"] = numer_feature_scaler_dct["events"][0]
    reports["categ_scaler"] = categ_feature_scaler_dct["events"][0]

    return ds.X, ds.y, ds.w, ds.y_aux, reports


def default_setup_func(stacked_datasets: StackedDatasets, ml_iterator: MLHdf5Iterator) -> WeightedDatasetBatch:
    weighted_datase_batch = WeightedDatasetBatch()

    for ds_name, ds in stacked_datasets.items():
        X = ds.X.astype(np.float32)
        y = ds.get_extra("label_type", None)
        w = ds.get_extra("weights", None)
        y_aux = None

        if y is not None:
            remap_labels: dict[int, int] | None = ml_iterator.dataset_kwargs.get("remap_labels", None)
            if remap_labels is not None:
                max_label = ml_iterator.dataset_kwargs["max_label"]
                y, mask_unmapped = remap_labels_lookup(y, max_label, remap_labels)
                X = X[mask_unmapped]
                if w is not None:
                    w = w[mask_unmapped]

        if ml_iterator.shuffle:
            shuffle_idx = np.random.permutation(len(X))
            X[:] = X[shuffle_idx]

            if y is not None:
                y[:] = y[shuffle_idx]
            if w is not None:
                w[:] = w[shuffle_idx]

        weighted_datase_batch[ds_name] = WeightedBatch(X, y, w, y_aux)

    return weighted_datase_batch


def get_ml_hdf5_dataloader(
    name: str,
    files: str | list[str],
    column_names: list[str],
    num_workers: int | None = None,
    stage_split_piles: dict[str, list[int] | int] | None = None,
    stage: str | None = None,
    shuffle: bool = False,
    collate_fn: Callable[[list[WeightedBatch]], Any] | None = None,
    dataset_kwargs: dict[str, Any] | None = None,
    dataloader_kwargs: dict[str, Any] | None = None,
) -> tuple[DataLoader, ColumnSelection, int]:
    if type(files) is str and files.endswith("*"):
        use_piles = False
    else:
        use_piles = True

    selection = get_column_selection(files, column_names)

    if dataset_kwargs is None:
        dataset_kwargs = {}

    if type(dataset_kwargs) is not dict:
        raise TypeError(f"dataset_kwargs must be a dict, got {type(dataset_kwargs)} instead.")

    dataset_kwargs["selection"] = selection

    if dataloader_kwargs is not None:
        if "batch_size" not in dataset_kwargs and "batch_size" in dataloader_kwargs:
            dataset_kwargs["batch_size"] = dataloader_kwargs.pop("batch_size")
            logging.info(f"Set batch size to {dataset_kwargs['batch_size']}.")

    dl, num_entries = get_hdf5_dataloader(
        name,
        files,
        dataset_names=selection.keys(),
        num_workers=num_workers,
        chunk_size=None,
        use_piles=use_piles,
        stage_split_piles=stage_split_piles,
        stage=stage,
        shuffle=shuffle,
        hdf5_files_desc_dct=None,
        processors=None,
        combine_datasets=True,
        allow_carrying_over=False,
        iterator_class=MLHdf5Iterator,
        collate_fn=collate_fn,
        dataset_kwargs=dataset_kwargs,
        dataloader_kwargs=dataloader_kwargs,
    )

    return dl, selection, num_entries
