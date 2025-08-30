from __future__ import annotations

import copy
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd
from torch.utils.data import DataLoader

from f9columnar.hdf5_dataloader import get_hdf5_dataloader
from f9columnar.processors import ProcessorsGraph
from f9columnar.root_dataloader import get_root_dataloader
from f9columnar.utils.config_utils import apply_config_to_db
from f9columnar.utils.rucio_db import RucioDB
from f9columnar.utils.rucio_utils import make_rucio_url
from f9columnar.utils.xsec_db import XsecDB


class PhysicsDataset(ABC):
    def __init__(self, name: str, is_data: bool) -> None:
        self.name = name
        self.is_data = is_data

        self.file_desc_dct: dict[str, Any] | None = None
        self.dataloader_config: dict[str, Any]
        self.dataloader: DataLoader
        self.num_entries: int

    @abstractmethod
    def _setup_file_desc_dct(self) -> dict[str, Any]:
        pop_attrs = ["dataloader", "num_entries", "file_desc_dct"]

        desc_dct = copy.deepcopy(self.__dict__)
        for attr in pop_attrs:
            desc_dct.pop(attr, None)

        return desc_dct

    @abstractmethod
    def setup_dataloader(self, **kwargs: Any):
        pass

    @abstractmethod
    def init_dataloader(self, processors: ProcessorsGraph | None = None):
        pass


class RootPhysicsDataset(PhysicsDataset):
    def __init__(self, name: str, root_files: list[str] | str, is_data: bool) -> None:
        super().__init__(name, is_data=is_data)

        if type(root_files) is list:
            self.root_files = root_files
        elif type(root_files) is str:
            self.root_files = [root_files]
        else:
            raise TypeError("root_files should be a list of strings or a string!")

    def __add__(self, other: str | list[str] | RootPhysicsDataset) -> RootPhysicsDataset:
        if type(other) is str:
            other = [other]
        elif type(other) is RootPhysicsDataset:
            other = other.root_files
        elif type(other) is list:
            pass
        else:
            raise TypeError("Other should be a RootPhysicsDataset, file name or a list of file names!")

        self.root_files += other

        return self

    def _setup_file_desc_dct(self) -> dict[str, Any]:
        pop_attrs = ["root_files", "dataloader", "num_entries", "file_desc_dct"]
        file_desc_dct = {}

        for root_file in self.root_files:
            dct = copy.deepcopy(self.__dict__)

            for attr in pop_attrs:
                dct.pop(attr, None)

            file_desc_dct[os.path.basename(root_file)] = dct

        return file_desc_dct

    def setup_dataloader(self, **kwargs: Any) -> RootPhysicsDataset:
        if "processors" in kwargs:
            raise ValueError("Processors should not be passed in setup_dataloader!")

        self.dataloader_config = kwargs

        if self.file_desc_dct is None:
            self.file_desc_dct = self._setup_file_desc_dct()
        else:
            if set(self.root_files) != set(self.file_desc_dct.keys()):
                raise ValueError("Root files and file_desc_dct keys do not match!")

        return self

    def init_dataloader(self, processors: ProcessorsGraph | None = None) -> RootPhysicsDataset:
        self.dataloader, self.num_entries = get_root_dataloader(
            self.name,
            self.root_files,
            key=self.dataloader_config.pop("key"),
            step_size=self.dataloader_config.pop("step_size"),
            num_workers=self.dataloader_config.pop("num_workers", 1),
            processors=processors,
            filter_name=self.dataloader_config.pop("filter_name", None),
            root_files_desc_dct=self.file_desc_dct,
            split_uniform_factor=self.dataloader_config.pop("split_uniform_factor", None),
            **self.dataloader_config,
        )

        return self


class Hdf5PhysicsDataset(PhysicsDataset):
    def __init__(
        self,
        name: str,
        hdf5_files: str | list[str],
        is_data: bool,
        dataset_names: str | list[str] | None,
    ) -> None:
        super().__init__(name, is_data=is_data)
        self.hdf5_files = hdf5_files

        self.dataset_names: str | list[str]

        if dataset_names is None:
            self.dataset_names = "data" if is_data else "mc"
        else:
            self.dataset_names = dataset_names

    def _setup_file_desc_dct(self) -> dict[str, Any]:
        pop_attrs = ["hdf5_files", "dataloader", "num_entries", "file_desc_dct"]
        file_desc_dct = {}

        for hdf5_file in self.hdf5_files:
            dct = copy.deepcopy(self.__dict__)

            for attr in pop_attrs:
                dct.pop(attr, None)

            file_desc_dct[os.path.basename(hdf5_file)] = dct

        return file_desc_dct

    def setup_dataloader(self, **kwargs: Any) -> Hdf5PhysicsDataset:
        if "processors" in kwargs:
            raise ValueError("Processors should not be passed in setup_dataloader!")

        if "dataset_names" in kwargs:
            raise ValueError("Dataset names should not be passed in setup_dataloader!")

        self.dataloader_config = kwargs

        self.file_desc_dct = self._setup_file_desc_dct()

        return self

    def init_dataloader(self, processors: ProcessorsGraph | None = None) -> Hdf5PhysicsDataset:
        self.dataloader, self.num_entries = get_hdf5_dataloader(
            self.name,
            files=self.hdf5_files,
            dataset_names=self.dataset_names,
            processors=processors,
            hdf5_files_desc_dct=self.file_desc_dct,
            **self.dataloader_config,
        )
        return self


class NtuplePhysicsDataset(PhysicsDataset):
    def __init__(self, name: str, is_data: bool, dataset_selection: pd.DataFrame) -> None:
        super().__init__(name, is_data=is_data)
        self.dataset_selection = dataset_selection

    def _setup_file_desc_dct(self) -> dict[str, Any]:
        pop_attrs = ["dataloader", "num_entries", "file_desc_dct", "dataset_selection"]
        file_desc_dct = {}

        root_files = self.dataset_selection["root_file"]

        for root_file in root_files:
            dct = copy.deepcopy(self.__dict__)

            for attr in pop_attrs:
                dct.pop(attr, None)

            file_desc_dct[os.path.basename(root_file)] = dct

        return file_desc_dct

    def setup_dataloader(self, **kwargs: Any) -> NtuplePhysicsDataset:
        if "processors" in kwargs:
            raise ValueError("Processors should not be passed in setup_dataloader!")

        self.dataloader_config = kwargs

        if self.file_desc_dct is None:
            self.file_desc_dct = self._setup_file_desc_dct()

        return self

    def init_dataloader(self, processors: ProcessorsGraph | None = None) -> NtuplePhysicsDataset:
        root_files = self.dataset_selection["root_file"].tolist()

        self.dataloader, self.num_entries = get_root_dataloader(
            self.name,
            root_files,
            key=self.dataloader_config.pop("key"),
            step_size=self.dataloader_config.pop("step_size"),
            num_workers=self.dataloader_config.pop("num_workers", 1),
            processors=processors,
            filter_name=self.dataloader_config.pop("filter_name", None),
            root_files_desc_dct=self.file_desc_dct,
            split_uniform_factor=self.dataloader_config.pop("split_uniform_factor", None),
            **self.dataloader_config,
        )

        return self


class NtupleMCDataset(NtuplePhysicsDataset):
    def __init__(self, name: str, dataset_selection: pd.DataFrame, use_weights: bool = True) -> None:
        super().__init__(name=name, dataset_selection=dataset_selection, is_data=False)
        self.use_weights = use_weights

        self.sample_weights: dict[str, float] | None = None

        if use_weights:
            self.sample_weights = self._setup_weights()

    def _setup_weights(self) -> dict[str, float]:
        root_files = self.dataset_selection["root_file"]

        eff_xsecs = self.dataset_selection["eff_xsec"]
        sows = self.dataset_selection["initial_sow"]

        sample_weights = {}
        for root_file, eff_xsec, sow in zip(root_files, eff_xsecs, sows):
            sample_weights[os.path.basename(root_file)] = eff_xsec / sow

        return sample_weights

    def __str__(self) -> str:
        return f"NtupleMCDataset(name={self.name})"


class NtupleDataDataset(NtuplePhysicsDataset):
    def __init__(self, name: str, dataset_selection: pd.DataFrame) -> None:
        super().__init__(name=name, dataset_selection=dataset_selection, is_data=True)

    def __str__(self) -> str:
        return f"NtupleDataDataset(name={self.name})"


class NtupleMergedPhysicsDataset:
    def __init__(self, name: str, datasets: list[NtupleDataDataset] | list[NtupleMCDataset], is_data: bool) -> None:
        self.name = name
        self.datasets = datasets
        self.is_data = is_data

        self.dataset_selection: list[pd.DataFrame] = []
        self.file_desc_dct: dict[str, Any] = {}

        self.dataloader_config: dict[str, Any]
        self.dataloader: DataLoader
        self.num_entries: int

    def merge(self) -> NtupleMergedPhysicsDataset:
        dataloader_configs = []

        for dataset in self.datasets:
            dataloader_configs.append(dataset.dataloader_config)
            self.dataset_selection.append(dataset.dataset_selection)

            self.file_desc_dct.update(dataset.file_desc_dct)  # type: ignore

        logging.info(f"[green]Merged {len(self.datasets)} datasets into {self.name} dataset![/green]")

        self.dataloader_config = dataloader_configs[0]
        logging.info("Using first dataloader config.")

        return self

    def setup_dataloader(self, **kwargs: Any) -> NtupleMergedPhysicsDataset:
        logging.warning("setup_dataloader should already be called on datasets!")
        return self

    def init_dataloader(self, processors: ProcessorsGraph | None = None) -> NtupleMergedPhysicsDataset:
        dataset_selection = pd.concat(self.dataset_selection)
        root_files = dataset_selection["root_file"].tolist()

        self.dataloader, self.num_entries = get_root_dataloader(
            self.name,
            root_files,
            key=self.dataloader_config.pop("key"),
            step_size=self.dataloader_config.pop("step_size"),
            num_workers=self.dataloader_config.pop("num_workers", 1),
            processors=processors,
            filter_name=self.dataloader_config.pop("filter_name", None),
            root_files_desc_dct=self.file_desc_dct,
            split_uniform_factor=self.dataloader_config.pop("split_uniform_factor", None),
            **self.dataloader_config,
        )

        return self


class DatasetBuilder(ABC):
    def __init__(self, data_path: str | None = None) -> None:
        self.data_path = data_path

        if self.data_path is not None:
            self.data_path = data_path
        else:
            self.data_path = os.environ.get("DATA_PATH", None)

        if self.data_path is None:
            raise ValueError("DATA_PATH not set!")

    @abstractmethod
    def build_mc_datasets(self):
        """Build MC datasets. Returns a list of MCDataset instances."""
        pass

    @abstractmethod
    def build_data_datasets(self):
        """Build data datasets. Returns a list of DataDataset instances."""
        pass

    @abstractmethod
    def setup_dataloaders(self, dataloader_config: dict[str, Any] | None = None):
        """Setup dataloaders for MC and data datasets."""
        pass

    @abstractmethod
    def init_dataloaders(self, processors: ProcessorsGraph | None = None):
        """Initialize dataloaders for MC and data datasets."""
        pass

    @abstractmethod
    def build(self, dataloader_config: dict[str, Any] | None = None):
        """Build datasets, setup dataloaders and initialize dataloaders."""
        pass

    @abstractmethod
    def init(self, processors: ProcessorsGraph | None = None):
        """Initialize dataloaders."""
        pass


class NtupleDatasetBuilder(DatasetBuilder):
    def __init__(
        self,
        config_name: str | None = None,
        data_path: str | None = None,
        ntuple_location: str | None = None,
        max_root_files: int | None = None,
        pmg_mc: str = "mc16",
        df_id: str = "hist",
    ) -> None:
        super().__init__(data_path=data_path)
        self.ntuple_location = ntuple_location

        if self.ntuple_location is not None:
            self.ntuple_location = ntuple_location
        else:
            self.ntuple_location = os.environ.get("NTUPLE_LOCATION", None)

        self.rucio_db: pd.DataFrame = RucioDB(data_path=self.data_path)(df_id)

        if config_name:
            self.rucio_db = apply_config_to_db(config_name, self.rucio_db)

        self.max_root_files = max_root_files

        self.xsec_db: pd.DataFrame = XsecDB(pmg_mc)()

        self.mc_datasets: list[NtupleMCDataset] | list[NtupleMergedPhysicsDataset] = []
        self.data_datasets: list[NtupleDataDataset] | list[NtupleMergedPhysicsDataset] = []

    def _make_root_files(
        self,
        files: list[str],
        users: list[str] | None = None,
        return_base_files: bool = False,
    ) -> tuple[list[str], list[str]] | list[str]:
        root_base_files = [f"{f}.tree.root" for f in files]

        if self.ntuple_location == "rucio":
            if users is None:
                raise ValueError("Users should be provided if rucio location!")

            root_files = []
            for user, root_file in zip(users, root_base_files):
                root_files.append(make_rucio_url(user, root_file))
        else:
            if self.ntuple_location is None:
                raise ValueError("NTUPLE_LOCATION not set!")

            root_files = [os.path.join(self.ntuple_location, root_file) for root_file in root_base_files]

        if return_base_files:
            return root_files, root_base_files
        else:
            return root_files

    def _split_for_max_root_files(self, df: pd.DataFrame) -> list[pd.DataFrame]:
        if self.max_root_files is None:
            raise ValueError("max_root_files should be set!")

        split_df = []

        for i in range(len(df) // self.max_root_files + 1):
            split = df[i * self.max_root_files : (i + 1) * self.max_root_files]
            if len(split) != 0:
                split_df.append(split)

        return split_df

    def build_mc_datasets(self) -> list[NtupleMCDataset]:
        logging.info("[green]Building MC datasets![/green]")

        mc_df = self.rucio_db[self.rucio_db["is_data"] == False]

        dataset_names = mc_df["dataset_name"].unique()

        mc_datasets = []
        for dataset_name in dataset_names:
            dataset_selection = mc_df[mc_df["dataset_name"] == dataset_name].copy()

            full_file_names = dataset_selection["full_file_name"]
            users = dataset_selection["user"]

            dataset_selection["root_file"] = self._make_root_files(full_file_names, users)

            dsids = dataset_selection["dsid"].astype(int).tolist()
            eff_xsecs = []

            for dsid in dsids:
                eff_xsec = self.xsec_db[self.xsec_db["dataset_number"] == dsid]["effectiveCrossSection"]
                eff_xsecs.append(eff_xsec.values[0])

            dataset_selection["eff_xsec"] = eff_xsecs

            if self.max_root_files is not None:
                dataset_selection = self._split_for_max_root_files(dataset_selection)
            else:
                dataset_selection = [dataset_selection]

            for df in dataset_selection:
                mc_datasets.append(NtupleMCDataset(dataset_name, df, use_weights=True))

        return mc_datasets

    def build_data_datasets(self) -> list[NtupleDataDataset]:
        logging.info("[green]Building data datasets![/green]")

        data_df = self.rucio_db[self.rucio_db["is_data"] == True]

        dataset_names = data_df["dataset_name"].unique()

        data_datasets = []
        for dataset_name in dataset_names:
            dataset_selection = data_df[data_df["dataset_name"] == dataset_name].copy()

            full_file_names = dataset_selection["full_file_name"]
            users = dataset_selection["user"]

            dataset_selection["root_file"] = self._make_root_files(full_file_names, users)

            if self.max_root_files is not None:
                dataset_selection = self._split_for_max_root_files(dataset_selection)
            else:
                dataset_selection = [dataset_selection]

            for df in dataset_selection:
                data_datasets.append(NtupleDataDataset(dataset_name, df))

        return data_datasets

    def setup_dataloaders(self, dataloader_config: dict[str, Any] | None = None) -> NtupleDatasetBuilder:
        if dataloader_config is None:
            dataloader_config = {}

        logging.info("[green]Setting up MC dataloaders![/green]")
        for mc in self.mc_datasets:
            mc.setup_dataloader(**dataloader_config)

        logging.info("[green]Setting up data dataloaders![/green]")
        for data in self.data_datasets:
            data.setup_dataloader(**dataloader_config)

        return self

    def init_dataloaders(self, processors: ProcessorsGraph | None = None) -> NtupleDatasetBuilder:
        logging.info("[green]Initializing MC dataloaders![/green]")
        for mc in self.mc_datasets:
            mc.init_dataloader(processors=processors)

        logging.info("[green]Initializing data dataloaders![/green]")
        for data in self.data_datasets:
            data.init_dataloader(processors=processors)

        return self

    def build(self, dataloader_config: dict[str, Any] | None = None, merge: bool = False) -> NtupleDatasetBuilder:
        self.mc_datasets = self.build_mc_datasets()
        self.data_datasets = self.build_data_datasets()

        self.setup_dataloaders(dataloader_config)

        if merge:
            if len(self.mc_datasets) != 0:
                self.mc_datasets = [NtupleMergedPhysicsDataset("MC", self.mc_datasets, is_data=False).merge()]
            else:
                logging.warning("No MC datasets to merge!")

            if len(self.data_datasets) != 0:
                self.data_datasets = [NtupleMergedPhysicsDataset("Data", self.data_datasets, is_data=True).merge()]
            else:
                logging.warning("No data datasets to merge!")

        return self

    def init(
        self, processors: ProcessorsGraph | None = None
    ) -> tuple[
        list[NtupleMCDataset] | list[NtupleMergedPhysicsDataset],
        list[NtupleDataDataset] | list[NtupleMergedPhysicsDataset],
    ]:
        self.init_dataloaders(processors=processors)
        return self.mc_datasets, self.data_datasets
