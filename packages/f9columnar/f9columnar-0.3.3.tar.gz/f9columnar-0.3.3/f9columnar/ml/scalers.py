from __future__ import annotations

import copy
import hashlib
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    MaxAbsScaler,
    MinMaxScaler,
    PowerTransformer,
    QuantileTransformer,
    RobustScaler,
    StandardScaler,
)

from f9columnar.utils.helpers import dump_pickle, load_pickle


class LogitTransform(BaseEstimator, TransformerMixin):
    def __init__(self, alpha: float = 1e-6, validate: bool = True) -> None:
        super().__init__()
        self.alpha = alpha
        self.validate = validate

    def validate_data(self, X: np.ndarray) -> None:
        if self.validate:
            test = (X + self.alpha >= 0) & (X - self.alpha <= 1)
            if not test.all():
                raise ValueError("Input data out of bounds!")

    def logistic_transform(self, x: np.ndarray) -> np.ndarray:
        x = (x - 0.5 * self.alpha) / (1 - self.alpha)
        return 1 / (1 + np.exp(-x))

    def logit_transform(self, x: np.ndarray) -> np.ndarray:
        x = x * (1 - self.alpha) + 0.5 * self.alpha
        return np.log(x / (1 - x))

    def fit(self, X: np.ndarray, y=None) -> LogitTransform:
        return self

    def transform(self, X: np.ndarray, y=None) -> np.ndarray:
        self.validate_data(X)
        return self.logit_transform(X)

    def fit_transform(self, X: np.ndarray, y=None) -> np.ndarray:
        return self.transform(X)

    def inverse_transform(self, X: np.ndarray, y=None) -> np.ndarray:
        return self.logistic_transform(X)


class FeatureScaler(ABC):
    def __init__(self, scaler_type: str | None, save_path: str | None = None, **scaler_kwargs: Any):
        """Base class for feature scalers.

        TNAnalysis scalers: https://gitlab.cern.ch/tadej/TNAnalysis/-/blob/main/src/fill/ml/FeatureScalers.h?ref_type=heads

        Parameters
        ----------
        scaler_type : str | None
            String to identify the scaler. Should be one of the following: If None, assume loading a previously saved
            scaler, by default None.
        save_path : str | None, optional
            Path to save the scaler, by default None.
        """
        self.scaler_type = scaler_type
        self.save_path = save_path
        self.scaler_kwargs = scaler_kwargs

        self.is_fitted = False

    @abstractmethod
    def fit(self, X: np.ndarray) -> FeatureScaler | None:
        pass

    def force_fit(self) -> None:
        """Force fit the scaler. Should be implemented in subclasses if needed."""
        raise NotImplementedError("force_fit method not implemented in subclass!")

    @abstractmethod
    def transform(self, X: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        pass

    def save(self, column_names: list[str] | None = None, postfix: str | None = None, extra_hash: str = "") -> None:
        if self.save_path is None or self.scaler_type is None:
            raise ValueError("No save path provided!")

        os.makedirs(self.save_path, exist_ok=True)

        if column_names is not None:
            hash_name = hashlib.md5(("".join(sorted(column_names)) + extra_hash).encode()).hexdigest()
            save_str = f"{self.scaler_type}_{hash_name}"
        else:
            save_str = f"{self.scaler_type}"

        if postfix is not None:
            save_str += f"_{postfix}"

        save_name = os.path.join(self.save_path, f"{save_str}.p")

        dump_pickle(save_name, self.__dict__)

    def load(self, column_names: list[str] | None = None, postfix: str | None = None, extra_hash: str = "") -> Any:
        if self.save_path is None:
            raise ValueError("No save path provided!")

        if column_names is not None:
            hash_name = hashlib.md5(("".join(sorted(column_names)) + extra_hash).encode()).hexdigest()
            load_str = f"{self.scaler_type}_{hash_name}"
        else:
            load_str = f"{self.scaler_type}"

        if postfix is not None:
            load_str += f"_{postfix}"

        load_name = os.path.join(self.save_path, f"{load_str}.p")

        try:
            loaded = load_pickle(load_name)
        except Exception as e:
            logging.error(f"Failed to load scaler from {load_name}, because {e}! Cannot use scaling.")
            return None

        self.__dict__.update(loaded)

        return self


class NumericalFeatureScaler(FeatureScaler):
    def __init__(
        self,
        scaler_type: str | None,
        partial_fit: bool = False,
        n_max: int | float | None = None,
        save_path: str | None = None,
        **scaler_kwargs: Any,
    ) -> None:
        super().__init__(scaler_type, save_path, **scaler_kwargs)

        if partial_fit:
            if self.scaler_type not in ["minmax", "maxabs", "standard"]:
                raise ValueError(f"Invalid scale type: {self.scaler_type} for partial fit!")

        self.partial_fit = partial_fit

        self.n_max: int | float

        if n_max is not None:
            self.n_max = int(n_max)
        else:
            logging.debug("No maximum number of events provided! Using all events for scaling.")
            self.n_max = np.inf

        self.n_total = 0
        self.cat_X: np.ndarray | None = None

        self.scaler = self._select_scaler()

    def _select_scaler(self):
        if self.scaler_type == "minmax":
            return MinMaxScaler(**self.scaler_kwargs)
        elif self.scaler_type == "maxabs":
            return MaxAbsScaler(**self.scaler_kwargs)
        elif self.scaler_type == "standard":
            return StandardScaler(**self.scaler_kwargs)
        elif self.scaler_type == "robust":
            return RobustScaler(**self.scaler_kwargs)
        elif self.scaler_type == "quantile":
            return QuantileTransformer(**self.scaler_kwargs)
        elif self.scaler_type == "power":
            return PowerTransformer(**self.scaler_kwargs)
        elif self.scaler_type == "logit":
            return Pipeline(
                steps=[
                    ("minmax", MinMaxScaler()),
                    ("logit", LogitTransform()),
                ],
            )
        elif self.scaler_type == "standard_logit":
            return Pipeline(
                steps=[
                    ("sigmoid transform", MinMaxScaler()),
                    ("logit transform", LogitTransform()),
                    ("normal transform", StandardScaler()),
                ]
            )
        elif self.scaler_type is None:
            return None
        else:
            raise ValueError(f"Invalid scale type: {self.scaler_type}!")

    def fit(self, X: np.ndarray) -> NumericalFeatureScaler | None:
        if X.shape[0] == 0:
            return self

        if self.partial_fit:
            return self._partial_fit(X)
        else:
            return self._accumulated_fit(X)

    def _partial_fit(self, X: np.ndarray) -> NumericalFeatureScaler | None:
        self.scaler.partial_fit(X)
        self.n_total += X.shape[0]

        self.is_fitted = True

        if self.n_total >= self.n_max:
            logging.info(f"Reached maximum number of events: {self.n_total}/{self.n_max}!")
            return None
        else:
            return self

    def _accumulated_fit(self, X: np.ndarray) -> NumericalFeatureScaler | None:
        if self.cat_X is None:
            self.cat_X = X
        else:
            self.cat_X = np.concatenate([self.cat_X, X])

        self.n_total += X.shape[0]

        if self.n_total >= self.n_max:
            logging.info(f"Reached maximum number of events: {self.n_total}/{self.n_max}!")
            self.scaler.fit(self.cat_X)
            self.cat_X = None
            self.is_fitted = True
            return None
        else:
            return self

    def force_fit(self) -> None:
        if self.is_fitted:
            logging.warning("Scaler is already fitted!")
            return None
        self.scaler.fit(self.cat_X)
        self.cat_X = None
        self.is_fitted = True

    def transform(self, X: np.ndarray) -> np.ndarray:
        if X.shape[0] == 0:
            return X

        return self.scaler.transform(X)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)

    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        if X.shape[0] == 0:
            return X

        return self.scaler.inverse_transform(X)

    def load(
        self, column_names: list[str] | None = None, postfix: str | None = None, extra_hash: str = ""
    ) -> NumericalFeatureScaler | None:
        return super().load(column_names, postfix, extra_hash)


class CategoricalFeatureScaler(FeatureScaler):
    def __init__(self, scaler_type: str, save_path: str | None = None, **scaler_kwargs: Any) -> None:
        """Transforms categorical features into labels. Same as [1], but for multiple columns and partial fit.

        Parameters
        ----------
        scaler_type : str
            Arbitrary string to identify the scaler. Should be 'categorical'.
        save_path : str | None, optional
            Path to save the scaler, by default None.

        References
        ----------
        [1] - https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.LabelEncoder.html

        """
        super().__init__(scaler_type, save_path, **scaler_kwargs)
        self.categories: list[dict[float, int]] = []  # different categories per column

        self._unique_categories: dict[int, np.ndarray] = {}
        self.max_offset = 0

        self.inverse_categories: list[dict[int, float]] = []
        self.inverse_max_offset = 0

    def fit(self, X: np.ndarray) -> CategoricalFeatureScaler:
        n_columns = X.shape[1]

        if len(self.categories) == 0:
            self.categories = [{} for _ in range(n_columns)]

        for n in range(n_columns):
            un, un_counts = np.unique(X[:, n], return_counts=True)

            counts_dct = self.categories[n]
            for u, counts in zip(un, un_counts):
                u = float(u)

                if u not in counts_dct:
                    counts_dct[u] = 0

                counts_dct[u] += int(counts)

        self.is_fitted = True
        return self

    def transform(self, X: np.ndarray, inplace: bool = True, to_int: bool = False) -> np.ndarray:
        if X.shape[0] == 0:
            return X

        if not inplace:
            _X = copy.deepcopy(X)

        for n, counts_dct in enumerate(self.categories):
            for i, u in enumerate(counts_dct.keys()):
                if inplace:
                    X[X[:, n] == u, n] = i + self.max_offset
                else:
                    _X[_X[:, n] == u, n] = i + self.max_offset

        if inplace:
            X = X - self.max_offset

            if to_int:
                X = X.astype(np.int64)

            return X

        _X = _X - self.max_offset

        if to_int:
            _X = _X.astype(np.int64)

        return _X

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        logging.warning("Fit transform not supported for CategoricalFeatureScaler!")
        return X

    def inverse_transform(self, X: np.ndarray, inplace: bool = True, to_int: bool = False) -> np.ndarray:
        if X.shape[0] == 0:
            return X

        if not inplace:
            _X = copy.deepcopy(X)

        for n, inverse_counts_dct in enumerate(self.inverse_categories):
            for i, u in inverse_counts_dct.items():
                if inplace:
                    X[X[:, n] == i, n] = u + self.inverse_max_offset
                else:
                    _X[_X[:, n] == i, n] = u + self.inverse_max_offset

        if inplace:
            X = X - self.inverse_max_offset

            if to_int:
                X = X.astype(np.int64)

            return X

        _X = _X - self.inverse_max_offset

        if to_int:
            _X = _X.astype(np.int64)

        return _X

    def save(self, column_names: list[str] | None = None, postfix: str | None = None, extra_hash: str = "") -> None:
        for k, categ_dct in enumerate(self.categories):
            self.categories[k] = {k: v for k, v in sorted(categ_dct.items(), key=lambda item: item[0], reverse=False)}
            self.categories[k] = {k: i for i, k in enumerate(self.categories[k].keys())}

            self._unique_categories[k] = np.array(list(categ_dct.keys()))

        max_offsets = []
        for k_arr in self._unique_categories.values():
            max_offsets.append(np.sum(np.abs(k_arr)) + 1)  # use sum because of negative values and +1 to offset 0

        self.max_offset = int(np.max(max_offsets))

        inverse_max_offsets = []
        for categ_dct in self.categories:
            inverse_counts_dct = {}

            total_i = 0
            for i, k_in in enumerate(categ_dct.keys()):
                inverse_counts_dct[i] = float(k_in)
                total_i += 1

            self.inverse_categories.append(inverse_counts_dct)
            inverse_max_offsets.append(total_i + 1)

        self.inverse_max_offset = int(np.max(inverse_max_offsets))

        return super().save(column_names, postfix, extra_hash)

    def load(
        self, column_names: list[str] | None = None, postfix: str | None = None, extra_hash: str = ""
    ) -> CategoricalFeatureScaler | None:
        return super().load(column_names, postfix, extra_hash)

    def get_unique_categories(self):
        return self._unique_categories
