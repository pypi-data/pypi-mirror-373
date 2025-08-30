from __future__ import annotations

import logging
import os
from typing import Any, TypeVar

import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np

from f9columnar.dataset_builder import PhysicsDataset
from f9columnar.processors import PostprocessorsGraph, Processor
from f9columnar.processors_collection import Cut
from f9columnar.utils.helpers import dump_json, get_ms_datetime, set_default_font_family
from f9columnar.utils.loggers import get_progress, timeit

PhysicsDatasetType = TypeVar("PhysicsDatasetType", bound=PhysicsDataset, covariant=True)


class CutFlow:
    def __init__(self) -> None:
        """Logging class for cut flow of processors."""
        self.cut_flow: dict[str, dict[str, list[tuple[int, int] | float]]] = {"mc": {}, "data": {}}

        self.save_dir = f"logs/cut_flow/{get_ms_datetime()}"
        os.makedirs(self.save_dir, exist_ok=True)

    @staticmethod
    def _get_n_cuts(cut_processors: dict[str, Processor]) -> dict[str, tuple[int, int]]:
        processors_cut_dct = {}

        for processor_name, processor in cut_processors.items():
            if isinstance(processor, Cut):
                start_n, end_n = processor.start_n, processor.end_n

                if start_n is None or end_n is None:
                    raise RuntimeError(f"Number of events for {processor_name} is None!")

                processors_cut_dct[processor_name] = (start_n, end_n)

        return processors_cut_dct

    def _add_to_cut_flow(self, dct_key: str, n_dct: dict[str, Any]) -> CutFlow:
        for processor_name in n_dct.keys():
            if processor_name not in self.cut_flow[dct_key]:
                self.cut_flow[dct_key][processor_name] = []

        for processor_name, cut_values_lst in n_dct.items():
            self.cut_flow[dct_key][processor_name].append(cut_values_lst)

        return self

    def add(self, cut_processors: dict[str, Processor], is_data: bool = False) -> CutFlow:
        n_dct = self._get_n_cuts(cut_processors)

        if is_data:
            self._add_to_cut_flow("data", n_dct)
        else:
            self._add_to_cut_flow("mc", n_dct)

        return self

    def plot(self, is_data: bool = False, n_start: bool = False) -> None:
        set_default_font_family()

        if is_data:
            flow_dct, postfix = self.cut_flow["data"], "data"
        else:
            flow_dct, postfix = self.cut_flow["mc"], "mc"

        dump_json(flow_dct, f"{self.save_dir}/cut_flow_{postfix}.json")

        if len(flow_dct) == 0:
            logging.warning("No processors in cut flow!")
            return None

        x_values, y_values = np.arange(len(flow_dct)), []
        for name, n_lst in flow_dct.items():
            cut_values = np.array(n_lst)

            if n_start:
                y_values.append(np.sum(cut_values[:, 0]))
            else:
                y_values.append(np.sum(cut_values[:, 1]))

        processor_names = list(flow_dct.keys())

        fig, ax = plt.subplots(figsize=(2.0 + len(processor_names) * 0.5, 8.0))
        hep.atlas.label(loc=0, llabel="Work in Progress", rlabel="", ax=ax, fontname="Latin Modern sans")

        ax.bar(x_values, y_values)
        ax.set_xticks(x_values)
        ax.set_xticklabels(processor_names, rotation=90)
        ax.set_ylabel(f"Cut flow for {name}")
        ax.set_yscale("log")

        fig.tight_layout()

        i = 0
        while os.path.exists(f"{self.save_dir}/{name}_{i}.pdf"):
            i += 1

        fig.savefig(f"{self.save_dir}/{name}_{i}.pdf")
        plt.close(fig)


class TimeFlow(CutFlow):
    def __init__(self) -> None:
        super().__init__()
        """Logging class for time execution (flow) of processors."""

        self.save_dir = f"logs/time_flow/{get_ms_datetime()}"
        os.makedirs(self.save_dir, exist_ok=True)

    @staticmethod
    def _get_n_time(cut_processors: dict[str, Processor]) -> dict[str, float]:
        processors_cut_dct = {}

        for processor_name, processor in cut_processors.items():
            delta_time = processor.delta_time
            processors_cut_dct[processor_name] = delta_time

        return processors_cut_dct

    def add(self, cut_processors: dict[str, Processor], is_data: bool = False) -> CutFlow:
        n_dct = self._get_n_time(cut_processors)

        if is_data:
            self._add_to_cut_flow("data", n_dct)
        else:
            self._add_to_cut_flow("mc", n_dct)

        return self

    def plot(self, is_data: bool = False, n_start=None) -> None:
        if n_start is not None:
            raise ValueError("n_start is not used in TimeFlow plot!")

        set_default_font_family()

        if is_data:
            flow_dct, postfix = self.cut_flow["data"], "data"
        else:
            flow_dct, postfix = self.cut_flow["mc"], "mc"

        dump_json(flow_dct, f"{self.save_dir}/time_flow_{postfix}.json")

        if len(flow_dct) == 0:
            logging.warning("No processors in cut flow!")
            return None

        x_values, y_values = np.arange(len(flow_dct)), []
        for name, n_lst in flow_dct.items():
            time_values = np.array(n_lst)
            y_values.append(np.sum(time_values))

        processor_names = list(flow_dct.keys())

        fig, ax = plt.subplots(figsize=(2.0 + len(processor_names) * 0.5, 8.0))
        hep.atlas.label(loc=0, llabel="Work in Progress", rlabel="", ax=ax, fontname="Latin Modern sans")

        sort_idx = np.argsort(y_values)[::-1]
        y_values = np.array(y_values)[sort_idx]
        processor_names = np.array(processor_names)[sort_idx]

        ax.bar(x_values, 1000 * y_values)
        ax.set_xticks(x_values)
        ax.set_xticklabels(processor_names, rotation=90)
        ax.set_ylabel(rf"Time flow for {name} [ms $\times$ num. workers]")
        ax.set_yscale("log")

        fig.tight_layout()

        i = 0
        while os.path.exists(f"{self.save_dir}/{name}_{i}.pdf"):
            i += 1

        fig.savefig(f"{self.save_dir}/{name}_{i}.pdf")
        plt.close(fig)


class ColumnarEventLoop:
    def __init__(
        self,
        mc_datasets: list[PhysicsDatasetType] | None = None,
        data_datasets: list[PhysicsDatasetType] | None = None,
        postprocessors_graph: PostprocessorsGraph | None = None,
        fit_postprocessors: bool = True,
        cut_flow: bool = False,
        disable_rich: bool = False,
    ):
        """Loop over MC and data datasets using root dataloader and run postprocessors.

        Parameters
        ----------
        mc_datasets : list[PhysicsDataset]
            List of MC datasets.
        data_datasets : list[PhysicsDataset]
            List of data datasets.
        postprocessors_graph : PostprocessorsGraph
            Graph of postprocessors to run.
        fit_postprocessors : bool
            Fit postprocessors flag.
        cut_flow : bool
            Cut flow flag. If True will log cut (only for Cut type) and time (all) flow of processors.
        disable_rich : bool
            Disable rich progress bar if True.

        """
        self.mc_datasets = mc_datasets
        self.data_datasets = data_datasets
        self.postprocessors_graph = postprocessors_graph
        self.fit_postprocessors = fit_postprocessors

        if cut_flow:
            logging.info("[yellow]Cut flow enabled![/yellow]")
            self.use_cut_flow = True
            self.cut_flow, self.time_flow = CutFlow(), TimeFlow()
        else:
            self.use_cut_flow = False

        self.disable_rich = disable_rich

    @property
    def postprocessors(self) -> dict[str, Processor] | None:
        if self.postprocessors_graph is not None:
            return self.postprocessors_graph.processors
        else:
            return None

    def _fit_postprocessors(self, fitted_processors: dict[str, Processor], is_data: bool) -> ColumnarEventLoop | None:
        if self.postprocessors_graph is None:
            return None

        self.postprocessors_graph.fit(fitted_processors, is_data=is_data)

        return self

    def _iterate_dataloaders(self, datasets: list[PhysicsDatasetType], is_data: bool) -> ColumnarEventLoop:
        if not self.disable_rich:
            progress = get_progress()
            progress.start()
            ds_bar = progress.add_task("Iterating datasets", total=len(datasets))

        for dataset in datasets:
            dataloader, num_entries = dataset.dataloader, dataset.num_entries

            if not self.disable_rich:
                dl_bar = progress.add_task(f"Iterating dataloader for {dataset.name}", total=num_entries)

            total = 0
            if dataloader is not None:
                for fitted_processors in dataloader:
                    if self.fit_postprocessors:
                        self._fit_postprocessors(fitted_processors, is_data)

                    if "input" in fitted_processors:
                        n_events = fitted_processors["input"].n_events

                        if not self.disable_rich:
                            progress.update(dl_bar, advance=n_events)

                        total += n_events

                    if self.use_cut_flow:
                        self.cut_flow.add(fitted_processors, is_data)
                        self.time_flow.add(fitted_processors, is_data)

                    if self.fit_postprocessors:
                        for k in fitted_processors.keys():
                            fitted_processors[k] = None
            else:
                logging.warning(f"[yellow]No dataloader found for {dataset.name}![/yellow]")

            if not self.disable_rich:
                progress.update(ds_bar, advance=1)
                progress.remove_task(dl_bar)

        if not self.disable_rich:
            progress.stop()

        logging.info(f"Total number of events processed: {total}")

        if self.use_cut_flow:
            self.cut_flow.plot(is_data)
            self.time_flow.plot(is_data)

        return self

    @timeit(unit="s")
    def run(
        self, mc_only: bool = False, data_only: bool = False
    ) -> ColumnarEventLoop | dict[str, ColumnarEventLoop | None]:
        if mc_only and data_only:
            raise ValueError("Cannot run both MC and data only!")

        if not self.fit_postprocessors:
            logging.info("[yellow]Not fitting postprocessors! Will return fitted processors for MC and data.[/yellow]")

        logging.info("[red][bold]Running event tensor loop![/bold][red]")

        results: dict[str, ColumnarEventLoop | None] = {}

        if mc_only:
            if self.mc_datasets is None:
                raise ValueError("No MC datasets found!")

            results["mc"] = self._iterate_dataloaders(self.mc_datasets, is_data=False)
            results["data"] = None
        elif data_only:
            if self.data_datasets is None:
                raise ValueError("No data datasets found!")

            results["data"] = self._iterate_dataloaders(self.data_datasets, is_data=True)
            results["mc"] = None
        else:
            if self.mc_datasets is None or self.data_datasets is None:
                raise ValueError("No MC or data datasets found!")

            results["mc"] = self._iterate_dataloaders(self.mc_datasets, is_data=False)
            results["data"] = self._iterate_dataloaders(self.data_datasets, is_data=True)

        logging.info("[red][bold]Done running event tensor loop![/bold][red]")

        if self.fit_postprocessors:
            if self.postprocessors_graph is None:
                raise ValueError("No postprocessors found!")

            for postprocessor in self.postprocessors_graph.processors.values():
                postprocessor.save()

            return self
        else:
            return results
