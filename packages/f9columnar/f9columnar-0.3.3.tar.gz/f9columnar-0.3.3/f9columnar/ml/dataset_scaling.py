from __future__ import annotations

import logging
import os
from typing import Any

import numpy as np
from torch.utils.data import DataLoader

from f9columnar.ml.dataloader_helpers import ColumnSelection, padding_mask
from f9columnar.ml.hdf5_dataloader import WeightedDatasetBatch, get_ml_hdf5_dataloader
from f9columnar.ml.scalers import CategoricalFeatureScaler, FeatureScaler, NumericalFeatureScaler
from f9columnar.utils.loggers import get_batch_progress


class DatasetScaler:
    def __init__(
        self,
        files: str | list[str],
        scaler_type: str,
        column_names: list[str],
        scaler_save_path: str | None = None,
        n_max: int | float | None = None,
        extra_hash: str | None = None,
        scaler_kwargs: dict[str, Any] | None = None,
        dataset_kwargs: dict[str, Any] | None = None,
        dataloader_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Utility class to perform feature scaling on datasets.

        Parameters
        ----------
        files : str | list[str]
            List of files or a single file path to load the dataset from.
        scaler_type : str
            Type of the feature scaler to use, e.g. "standard", "minmax", etc.
        column_names : list[str]
            List of column names to use for feature scaling.
        scaler_save_path : str | None, optional
            Path to save the feature scaler. If None, it will be set to a default path in the analysis results directory,
            by default None.
        n_max : int | float | None, optional
            Maximum number of events to use for feature scaling. If None, all events will be used, by default None.
        perform_closure : bool, optional
            Whether to perform feature scaling closure. If True, the `closure_config` must be provided, by default False.
        closure_config : dict[str, dict[str, Any]] | None, optional
            Configuration for the feature scaling closure. Needed if `perform_closure` is True.
        scaler_kwargs : dict[str, Any] | None, optional
            Additional keyword arguments to pass to the sklearn feature scaler, by default None.
        dataset_kwargs : dict[str, Any] | None, optional
            Additional keyword arguments to pass to the iterator, by default None.
        dataloader_kwargs : dict[str, Any] | None, optional
            Additional keyword arguments to pass to the dataloader, by default None.
        """
        if scaler_save_path is None:
            scaler_save_path = os.path.join(os.environ["ANALYSIS_ML_RESULTS_DIR"], "scalers")
            os.makedirs(scaler_save_path, exist_ok=True)

        if extra_hash is None:
            self.extra_hash = ""
        else:
            self.extra_hash = extra_hash

        logging.info(f"Saving scalers to {scaler_save_path}.")

        if dataset_kwargs is None:
            dataset_kwargs = {}

        if dataloader_kwargs is None:
            dataloader_kwargs = {}

        self.hdf5_dataloader, self.selection, self.num_entries = self._get_dataloader(
            files,
            column_names,
            dataset_kwargs,
            dataloader_kwargs,
        )

        self.dataset_scalers = self._get_scalers(scaler_type, scaler_save_path, n_max, scaler_kwargs)
        logging.info(f"Scaling datasets: {list(self.dataset_scalers.keys())}")

    def _get_dataloader(
        self,
        files: str | list[str],
        column_names: list[str],
        dataset_kwargs: dict[str, Any],
        dataloader_kwargs: dict[str, Any],
    ) -> tuple[DataLoader, ColumnSelection, int]:
        logging.info("[green]Initializing dataloaders...[/green]")
        dl, selection, num_entries = get_ml_hdf5_dataloader(
            "featureScaling",
            files,
            column_names,
            stage_split_piles=None,
            stage=None,
            dataset_kwargs=dataset_kwargs,
            dataloader_kwargs=dataloader_kwargs,
        )
        return dl, selection, num_entries

    def _get_scalers(
        self,
        scaler_type: str,
        scaler_save_path: str,
        n_max: int | float | None = None,
        scaler_kwargs: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, list[FeatureScaler | None]]]:
        if scaler_kwargs is None:
            scaler_kwargs = {}

        dataset_scalers: dict[str, dict[str, list[FeatureScaler | None]]] = {}

        for dataset_name, column_selection in self.selection.items():
            n_objects = self.selection[dataset_name].n_objects

            numer_scalers: list[FeatureScaler | None] = []
            categ_scalers: list[FeatureScaler | None] = []

            for _ in range(n_objects):
                if len(column_selection.numer_columns) != 0:
                    numer_feature_scaler = NumericalFeatureScaler(
                        scaler_type,
                        n_max=n_max,
                        save_path=scaler_save_path,
                        **scaler_kwargs,
                    )
                else:
                    numer_feature_scaler = None

                if len(column_selection.categ_columns) != 0:
                    categ_feature_scaler = CategoricalFeatureScaler("categorical", scaler_save_path)
                else:
                    categ_feature_scaler = None

                numer_scalers.append(numer_feature_scaler)
                categ_scalers.append(categ_feature_scaler)

            dataset_scalers[dataset_name] = {
                "numer": numer_scalers,
                "categ": categ_scalers,
            }

        return dataset_scalers

    def _get_padding_mask(self, X: np.ndarray, dataset_name: str) -> np.ndarray | None:
        return padding_mask(X, self.selection[dataset_name].pad_value)

    def _scale_dataset_idx(self, ds_batch: WeightedDatasetBatch, dataset_name: str, idx: int) -> bool:
        X = ds_batch[dataset_name].X.numpy()

        if dataset_name != "events":
            X = X[:, idx, :]
            padding_mask = self._get_padding_mask(X, dataset_name)

            if padding_mask is not None:
                X = X[padding_mask]
        else:
            padding_mask = None

        if self.selection[dataset_name].has_categ_columns:
            categ_feature_scaler = self.dataset_scalers[dataset_name]["categ"][idx]

            if categ_feature_scaler is None:
                raise RuntimeError("Categorical feature scaler is None, but categorical columns are present!")

            categ_idx = self.selection[dataset_name].offset_categ_columns_idx
            X_categ = X[:, categ_idx]

            categ_feature_scaler.fit(X_categ)

        if self.selection[dataset_name].has_numer_columns:
            numer_feature_scaler = self.dataset_scalers[dataset_name]["numer"][idx]

            if numer_feature_scaler is None:
                raise RuntimeError("Numerical feature scaler is None, but numerical columns are present!")

            numer_idx = self.selection[dataset_name].offset_numer_columns_idx
            X_numer = X[:, numer_idx]

            numer_fit_result = numer_feature_scaler.fit(X_numer)

            if numer_fit_result is None:
                return True

        return False

    def _scale(self, ds_batch: WeightedDatasetBatch) -> bool:
        for dataset_name in self.dataset_scalers.keys():
            n_objects = self.selection[dataset_name].n_objects
            for i in range(n_objects):
                break_fit = self._scale_dataset_idx(ds_batch, dataset_name, i)
                if break_fit:
                    return True

        return False

    def feature_scale(self) -> None:
        progress = get_batch_progress()
        progress.start()
        bar = progress.add_task("Processing batches", total=None)

        break_fit = False

        for batch in self.hdf5_dataloader:
            ds_batch, _ = batch

            break_fit = self._scale(ds_batch)

            if break_fit:
                logging.info("Breaking feature scaling loop!")
                break

            progress.update(bar, advance=1)

        progress.stop()

        for dataset_name, scalers in self.dataset_scalers.items():
            numer_feature_scalers, categ_feature_scalers = scalers["numer"], scalers["categ"]

            for i, numer_feature_scaler in enumerate(numer_feature_scalers):
                if numer_feature_scaler is not None:
                    if not numer_feature_scaler.is_fitted:
                        numer_feature_scaler.force_fit()
                    numer_columns = self.selection[dataset_name].numer_columns
                    logging.info(f"Saving numerical scaler: {dataset_name} - {i} - {numer_columns}.")
                    numer_feature_scaler.save(numer_columns, postfix=f"{dataset_name}_{i}", extra_hash=self.extra_hash)

            for i, categ_feature_scaler in enumerate(categ_feature_scalers):
                if categ_feature_scaler is not None:
                    categ_columns = self.selection[dataset_name].categ_columns
                    logging.info(f"Saving categorical scaler: {dataset_name} - {i} - {categ_columns}.")
                    categ_feature_scaler.save(categ_columns, postfix=f"{dataset_name}_{i}", extra_hash=self.extra_hash)

        logging.info("[green]Done with feature scaling!")
