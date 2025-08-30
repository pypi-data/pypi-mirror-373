from __future__ import annotations

import copy
import time
from abc import abstractmethod
from typing import Any

import awkward as ak
import numpy as np

from f9columnar.histograms import HistogramProcessor
from f9columnar.processors import Processor


class ProcessorsCollection:
    def __init__(self, collection_name: str, *objects: Processor) -> None:
        self.collection_name = collection_name
        self.objects: dict[str, Processor] = {}

        for obj in objects:
            if obj.name in self.objects:
                raise ValueError(f"{obj.name} already exists in the {self.collection_name} collection!")
            else:
                self.objects[obj.name] = obj

        self.branch_names = self._get_branch_names()

    def __getitem__(self, name: str) -> Processor:
        return self.objects[name]

    def add(self, *objs: Processor | ProcessorsCollection) -> ProcessorsCollection:
        for obj in objs:
            if isinstance(obj, ProcessorsCollection):
                for v in obj.objects.values():
                    if v in self.objects:
                        raise ValueError(f"{v.name} already exists in the {self.collection_name} collection!")
                    else:
                        self.objects[v.name] = v
            elif isinstance(obj, Processor):
                if obj in self.objects:
                    raise ValueError(f"{obj.name} already exists in the {self.collection_name} collection!")
                else:
                    self.objects[obj.name] = obj
            else:
                raise ValueError(f"Invalid object type {type(obj)}!")

        self.branch_names = self._get_branch_names()

        return self

    def __add__(self, other: list | Processor | ProcessorsCollection) -> ProcessorsCollection:
        if type(other) is list:
            return self.add(*other)
        elif isinstance(other, Processor) or isinstance(other, ProcessorsCollection):
            return self.add(other)
        else:
            raise ValueError(f"Invalid object type {type(other)}!")

    def _get_branch_names(self) -> list[str]:
        all_branch_names = []

        for v in self.objects.values():
            if not hasattr(v, "branch_name") and not hasattr(v, "branch_names"):
                continue

            attr_branch_name = getattr(v, "branch_name", None)
            attr_branch_names = getattr(v, "branch_names", None)

            if attr_branch_name is not None and attr_branch_names is not None:
                raise ValueError(f"Both branch_name and branch_names are defined for {v.name}!")
            elif attr_branch_name is not None and attr_branch_names is None:
                branch_name = attr_branch_name
            elif attr_branch_names is not None and attr_branch_name is None:
                branch_name = attr_branch_names
            else:
                continue

            if type(branch_name) is list:
                list_branch_names = [br for br in branch_name if br is not None]

                if len(list_branch_names) == 0:
                    continue
                else:
                    all_branch_names += list_branch_names

            elif type(branch_name) is str:
                all_branch_names.append(branch_name)
            else:
                raise ValueError(f"Invalid type of branch name for {v.name}!")

        all_branch_names = sorted(list(set(all_branch_names)))

        return all_branch_names

    def branch_name_filter(self, branch: str) -> bool:
        if branch in self.branch_names:
            return True
        else:
            return False

    def as_list(self) -> list[Processor]:
        return list(self.objects.values())

    def __str__(self) -> str:
        str_output = f"Object Collection\n{17 * '-'}\n"

        for name, obj in self.objects.items():
            str_output += f"{name}: {str(obj)}\n"

        return str_output[:-1]


class Variable(Processor):
    name: str = "variableProcessor"
    branch_names: str | list | None = None

    def __init__(self) -> None:
        super().__init__(self.name)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any):
        pass


class VariablesCollection(ProcessorsCollection):
    def __init__(self, *variables: Variable) -> None:
        super().__init__("Variables", *variables)


class Cut(Processor):
    name: str = "cutProcessor"
    branch_names: str | list | None = None

    def __init__(self) -> None:
        super().__init__(self.name)
        self.start_n: int | None = None
        self.end_n: int | None = None

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any):
        pass

    def _run(self, arrays: ak.Array | np.ndarray, **kwargs: Any) -> Cut:
        self.start_n, start_time = len(arrays), time.time()

        arrays, kwargs = copy.deepcopy(arrays), copy.deepcopy(kwargs)
        self._results = self.run(arrays, **kwargs)

        if self._results is not None:
            self.end_n = len(self._results["arrays"])

        self.delta_time = time.time() - start_time

        return self


class CutsCollection(ProcessorsCollection):
    def __init__(self, *cuts: Cut) -> None:
        super().__init__("Cuts", *cuts)


class Weight(Processor):
    name: str = "weightProcessor"
    branch_names: str | list | None = None

    def __init__(self) -> None:
        """MC weights processor.

        References
        ----------
        [1] - https://ipnp.cz/scheirich/?page_id=292

        """
        super().__init__(self.name)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any):
        pass


class WeightsCollection(ProcessorsCollection):
    def __init__(self, *weights: Weight) -> None:
        super().__init__("Weights", *weights)


class HistogramsCollection(ProcessorsCollection):
    def __init__(self, *histograms: HistogramProcessor) -> None:
        super().__init__("Histograms", *histograms)
