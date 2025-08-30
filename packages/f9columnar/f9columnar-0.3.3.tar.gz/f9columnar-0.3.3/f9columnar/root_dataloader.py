from __future__ import annotations

import copy
import logging
import os
from collections.abc import Callable, Iterator
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from typing import Any

import awkward as ak
import numpy as np
import pandas as pd
import torch
import uproot
from torch import multiprocessing
from torch.utils.data import DataLoader, IterableDataset

from f9columnar.processors import Processor, ProcessorsGraph
from f9columnar.utils.helpers import get_file_size


@dataclass
class RootFile:
    file_name: str
    key: str

    file_size: float = 0.0
    num_entries: int = 0
    tree: uproot.TTree = None

    def __post_init__(self) -> None:
        if not os.path.exists(self.file_name):
            raise RuntimeError(f"File {self.file_name} does not exist.")

        if not os.path.isfile(self.file_name):
            raise RuntimeError(f"{self.file_name} is not a file.")

        if not self.file_name.endswith(".root"):
            raise ValueError(f"File {self.file_name} is not a ROOT file.")

        self.file_size = get_file_size(self.file_name)

        self.file_name = f"{self.file_name}:{self.key}"

    def open(self) -> uproot.TTree:
        self.tree = uproot.open(self.file_name)
        self.num_entries = self.tree.num_entries
        return self

    def close(self) -> RootFile:
        self.tree.close()
        return self


@dataclass
class RootFiles:
    file_names: list[str]
    key: str | list[str]

    files_dct: dict[str, RootFile] = field(default_factory=dict)

    file_size_dct: dict[str, float] = field(default_factory=dict)
    num_entries_dct: dict[str, int] = field(default_factory=dict)

    total_file_size: float = 0.0
    total_num_entries: int = 0

    def load(self) -> RootFiles:
        for i, file_name in enumerate(self.file_names):
            if type(self.key) is list:
                root_file = RootFile(file_name, self.key[i])
            elif type(self.key) is str:
                root_file = RootFile(file_name, self.key)
            else:
                raise ValueError(f"Key {self.key} is not a valid type.")

            root_file = root_file.open()

            self.files_dct[file_name] = root_file
            self.file_size_dct[file_name] = root_file.file_size

            num_entries = root_file.num_entries

            root_file.close()

            if num_entries == 0:
                continue

            self.num_entries_dct[file_name] = num_entries

            self.total_file_size += root_file.file_size
            self.total_num_entries += num_entries

        return self

    def __getitem__(self, file_name: str) -> RootFile:
        return self.files_dct[file_name]


class UprootIteratorsDfMaker:
    def __init__(
        self,
        name: str,
        files: list[str],
        key: str | list[str],
        step_size: int,
        num_workers: int,
    ) -> None:
        self.name = name
        self.files, self.key = files, key
        self.num_workers = num_workers
        self.step_size = step_size

        self.total_num_entries = 0
        self.all_num_entries_dct: dict[str, int] = {}

    def _log_info(self, total_files_size: float, total_num_entries: int) -> None:
        info_str = "\n" + 15 * "=" + " info " + 15 * "="
        info_str += f"\nName: {self.name}\n"
        info_str += f"Number of ROOT files: {len(self.files)}\n"
        info_str += f"Total size: {total_files_size:.3f} GB\n"
        info_str += f"Total number of entries: {total_num_entries}\n"
        info_str += 36 * "="

        logging.info(info_str)

    @staticmethod
    def _run_get_root_files(files_lst: list[str], key: str | list[str], it) -> RootFiles:
        return RootFiles(files_lst, key).load()

    def _join_root_files(self, root_files: list[RootFiles]) -> RootFiles:
        combined_files, combined_file_size_dct, combined_num_entries_dct = {}, {}, {}

        total_file_size, total_num_entries = 0.0, 0

        for root_file in root_files:
            combined_files.update(root_file.files_dct)
            combined_file_size_dct.update(root_file.file_size_dct)
            combined_num_entries_dct.update(root_file.num_entries_dct)

            total_file_size += root_file.total_file_size
            total_num_entries += root_file.total_num_entries

        return RootFiles(
            list(combined_files.keys()),
            key=self.key,
            files_dct=combined_files,
            file_size_dct=combined_file_size_dct,
            num_entries_dct=combined_num_entries_dct,
            total_file_size=total_file_size,
            total_num_entries=total_num_entries,
        )

    def _split(self) -> list[dict[str, list[int]]]:
        logging.info("Preparing ROOT files (this may take a while).")

        jobs_idx_split = np.array_split(np.arange(len(self.files)), self.num_workers)

        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            for it, job_idx in enumerate(jobs_idx_split):
                files_lst = [self.files[i] for i in job_idx]
                futures.append(executor.submit(self._run_get_root_files, files_lst, self.key, it))

        root_files_results = []
        for future in futures:
            root_files_results.append(future.result())

        root_files = self._join_root_files(root_files_results)

        self._log_info(root_files.total_file_size, root_files.total_num_entries)

        total_num_entries = root_files.total_num_entries
        self.total_num_entries = total_num_entries

        # how many entries each worker will process
        splits = [total_num_entries // self.num_workers] * self.num_workers
        splits[-1] += total_num_entries % self.num_workers

        self.all_num_entries_dct = root_files.num_entries_dct
        num_entries_dct = copy.deepcopy(root_files.num_entries_dct)

        # keep track of the start and stop entries for each root file
        root_files_start_dct: dict[str, int] = {root_file: 0 for root_file in self.files}

        split_result: list[dict[str, list[int]]] = [{} for _ in range(len(splits))]

        done = []
        for i, split in enumerate(splits):
            total = 0
            for root_file, num_entries in num_entries_dct.items():
                if root_file in done:
                    continue

                entry_start = root_files_start_dct[root_file]

                total += num_entries

                if total <= split:
                    split_result[i][root_file] = [entry_start, self.all_num_entries_dct[root_file]]
                    done.append(root_file)

                    if total == split:
                        break
                    else:
                        continue

                if total > split:
                    delta = num_entries - (total - split)
                    split_result[i][root_file] = [entry_start, entry_start + delta]
                    root_files_start_dct[root_file] += delta
                    num_entries_dct[root_file] -= delta
                    break

        return split_result

    def make(self) -> pd.DataFrame:
        split_result = self._split()

        worker_df: dict[str, list] = {"worker_id": [], "file": [], "start": [], "stop": [], "step_size": []}

        check_total = 0
        for i, result_dct in enumerate(split_result):
            for root_file, start_stop in result_dct.items():
                entry_start, entry_stop = start_stop
                check_total += entry_stop - entry_start

                delta_entry = entry_stop - entry_start
                num_entries = self.all_num_entries_dct[root_file]

                if self.step_size > delta_entry:
                    step_size = delta_entry
                elif self.step_size > num_entries:
                    step_size = num_entries
                else:
                    step_size = self.step_size

                worker_df["worker_id"].append(i)
                worker_df["file"].append(f"{root_file}:{self.key}")
                worker_df["start"].append(entry_start)
                worker_df["stop"].append(entry_stop)
                worker_df["step_size"].append(step_size)

        if check_total != self.total_num_entries:
            raise ValueError("Total number of entries does not match.")

        return pd.DataFrame(worker_df)


class RootLoaderIterator:
    def __init__(
        self,
        name: str,
        iterators_df: pd.DataFrame,
        processors: list[Callable[[ak.Array, dict], tuple[ak.Array, dict]]] | ProcessorsGraph | None = None,
        filter_name: Callable[[str], bool] | None = None,
        root_files_desc_dct: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.name = name
        self.iterators_df = iterators_df
        self.processors = processors
        self.filter_name = filter_name
        self.root_files_desc_dct = root_files_desc_dct

        self.iterator: Iterator
        self.tree: uproot.TTree

        self.current_df_idx, self.current_iterator_idx = 0, 0

    def _make_uproot_iterator(self, df: pd.Series) -> tuple[Iterator, uproot.TTree]:
        tree = uproot.open(df["file"])

        iterator = tree.iterate(
            library="ak",
            report=True,
            step_size=df["step_size"],
            filter_name=self.filter_name,
            entry_start=df["start"],
            entry_stop=df["stop"],
        )

        return iterator, tree

    def _iterate_df(self) -> None:
        df = self.iterators_df.iloc[self.current_iterator_idx]
        self.iterator, self.tree = self._make_uproot_iterator(df)
        self.current_df_idx += 1

    def _run_processors(self, arrays: ak.Array, reports: dict) -> tuple[ak.Array, dict] | dict[str, Processor]:
        if self.processors is None:
            return arrays, reports
        elif type(self.processors) is list:
            for proc in self.processors:
                arrays, reports = proc(arrays, reports)
            return arrays, reports
        elif type(self.processors) is ProcessorsGraph:
            return self.processors.fit(arrays, reports)
        else:
            raise ValueError(f"Processors {self.processors} is not a valid type.")

    def _make_report(self, reports: Any) -> dict:
        file_path = reports._source._file._file_path
        file_name = os.path.basename(file_path)
        start, stop = reports._tree_entry_start, reports._tree_entry_stop

        reports = {
            "name": self.name,
            "worker_id": self.iterators_df.iloc[self.current_iterator_idx]["worker_id"],
            "file_path": file_path,
            "file": file_name,
            "start": start,
            "stop": stop,
        }

        if self.root_files_desc_dct is not None:
            reports = reports | self.root_files_desc_dct[file_name]

        return reports

    def __iter__(self) -> RootLoaderIterator:
        return self

    def __next__(self) -> tuple[ak.Array, dict] | dict[str, Processor]:
        try:
            if self.current_df_idx == self.current_iterator_idx:
                self._iterate_df()

            arrays, reports = next(self.iterator)

        except StopIteration:
            self.tree.close()
            self.current_iterator_idx += 1

            if self.current_iterator_idx == len(self.iterators_df):
                raise StopIteration

            if self.current_df_idx == self.current_iterator_idx:
                self._iterate_df()

            arrays, reports = next(self.iterator)

        reports = self._make_report(reports)

        processors_return = self._run_processors(arrays, reports)

        return processors_return


class RootIterableDataset(IterableDataset):
    def __init__(
        self,
        name: str,
        worker_iterators_df: pd.DataFrame,
        processors: list[Callable[[ak.Array, dict], tuple[ak.Array, dict]]] | ProcessorsGraph | None = None,
        filter_name: Callable[[str], bool] | None = None,
        root_files_desc_dct: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.name = name
        self.worker_iterators_df = worker_iterators_df
        self.processors = processors
        self.filter_name = filter_name
        self.root_files_desc_dct = root_files_desc_dct

    def __iter__(self) -> RootLoaderIterator:
        worker_info = torch.utils.data.get_worker_info()

        if worker_info is None:
            worker_id = 0
        else:
            worker_id = worker_info.id

        iterators_df = self.worker_iterators_df[self.worker_iterators_df["worker_id"] == worker_id].copy()

        return RootLoaderIterator(
            self.name,
            iterators_df,
            processors=self.processors,
            filter_name=self.filter_name,
            root_files_desc_dct=self.root_files_desc_dct,
        )


def get_root_dataloader(
    name: str,
    files: list[str],
    key: str,
    step_size: int,
    num_workers: int,
    processors: list[Callable[[ak.Array, dict], tuple[ak.Array, dict]]] | ProcessorsGraph | None = None,
    filter_name: Callable[[str], bool] | None = None,
    root_files_desc_dct: dict[str, dict[str, Any]] | None = None,
    split_uniform_factor: int | None = None,
    dataloader_kwargs: dict[str, Any] | None = None,
) -> tuple[DataLoader, int]:
    if multiprocessing.get_start_method() == "fork" and num_workers > 0:
        logging.debug("Using 'fork' start method. Consider using 'spawn' or 'forkserver'.")

    if num_workers == -1:
        num_workers = multiprocessing.cpu_count()

    if split_uniform_factor is not None:
        original_num_workers = num_workers
        num_workers = 1

    if dataloader_kwargs is None:
        dataloader_kwargs = {}

    logging.info("Making ROOT dataloader!")

    df_maker = UprootIteratorsDfMaker(name, files, key, step_size, num_workers)
    worker_iteratorts_df = df_maker.make()

    if split_uniform_factor is not None:
        logging.info(f"Splitting the dataset into {split_uniform_factor} uniform parts.")

        uniform_dct: dict[str, list[Any]] = {"worker_id": [], "file": [], "start": [], "stop": [], "step_size": []}
        for _, row in worker_iteratorts_df.iterrows():
            start, stop, step_size = row["start"], row["stop"], row["step_size"]
            total_num_entries = stop - start

            splits = [total_num_entries // split_uniform_factor] * split_uniform_factor
            splits[-1] += total_num_entries % split_uniform_factor

            current_start = start
            for split_idx in range(split_uniform_factor):
                split_size = splits[split_idx]
                new_start = current_start
                new_stop = new_start + split_size
                current_start = new_stop

                new_step_size = min(step_size, new_stop - new_start)

                uniform_dct["worker_id"].append(row["worker_id"])
                uniform_dct["file"].append(row["file"])
                uniform_dct["start"].append(new_start)
                uniform_dct["stop"].append(new_stop)
                uniform_dct["step_size"].append(new_step_size)

        worker_iteratorts_df = pd.DataFrame(uniform_dct)

        worker_ids = np.random.choice(np.arange(original_num_workers), size=len(worker_iteratorts_df), replace=True)
        worker_iteratorts_df["worker_id"] = worker_ids

    total_num_entries = df_maker.total_num_entries

    root_iterable_dataset = RootIterableDataset(
        name,
        worker_iteratorts_df,
        processors=processors,
        filter_name=filter_name,
        root_files_desc_dct=root_files_desc_dct,
    )

    prefetch_factor = dataloader_kwargs.get("prefetch_factor", None)

    root_dataloader = DataLoader(
        root_iterable_dataset,
        batch_size=None,
        num_workers=num_workers,
        prefetch_factor=prefetch_factor,
        **dataloader_kwargs,
    )

    return root_dataloader, total_num_entries
