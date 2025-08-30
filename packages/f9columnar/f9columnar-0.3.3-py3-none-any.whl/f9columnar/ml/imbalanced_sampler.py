from typing import Any

import numpy as np
from imblearn.base import BaseSampler
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler


class ImbalancedSampler:
    def __init__(self, sampler_name: str, random_state: int | None = None, **sampler_kwargs: Any) -> None:
        self.sampler_name = sampler_name
        self.random_state = random_state
        self.sampler_kwargs = sampler_kwargs

        self.sampler = self._get_sampler()

    def _get_sampler(self) -> BaseSampler:
        if self.sampler_name == "RandomOverSampler":
            return RandomOverSampler(random_state=self.random_state, **self.sampler_kwargs)
        elif self.sampler_name == "RandomUnderSampler":
            return RandomUnderSampler(random_state=self.random_state, **self.sampler_kwargs)
        else:
            raise ValueError(f"Sampler {self.sampler_name} is not supported!")

    def fit(self, X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        X_resampled, y_resampled = self.sampler.fit_resample(X, y)

        return X_resampled, y_resampled
