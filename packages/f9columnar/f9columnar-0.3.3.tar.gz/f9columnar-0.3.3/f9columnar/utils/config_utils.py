import copy
import logging
import os

import pandas as pd

from f9columnar.utils.helpers import dump_yaml, load_yaml
from f9columnar.utils.rucio_db import RucioDB


class NtupleConfigGenerator:
    def __init__(self, data_path=None, df_id="hist"):
        if data_path is not None:
            self.data_path = data_path
        else:
            self.data_path = os.environ.get("DATA_PATH", None)

        self.rucio_db = RucioDB()(df_id)

    def generate_default_config(self, force=False):
        yaml_path = f"{self.data_path}/default_config.yaml"

        if os.path.exists(yaml_path):
            logging.info("default_config.yaml already exists")

            if not force:
                return None
            else:
                logging.warning("Making a new default_config.yaml")

        data_selection = self.rucio_db[self.rucio_db["is_data"] == True]
        data = data_selection["dataset_name"].unique()
        data = sorted(data.tolist())

        mc_selection = self.rucio_db[self.rucio_db["is_data"] == False]
        mc = mc_selection["dataset_name"].unique()
        mc = sorted(mc.tolist())

        mc_dsids = {}

        for mc_name in mc:
            dsids = mc_selection[mc_selection["dataset_name"] == mc_name]["dsid"].unique()
            mc_dsids[mc_name] = sorted(dsids.astype(int).tolist())

        yaml_dct = {"data": data, "mc": mc_dsids}

        dump_yaml(yaml_dct, yaml_path)

        return self

    def load_default_config(self):
        yaml_path = f"{self.data_path}/default_config.yaml"

        if not os.path.exists(yaml_path):
            logging.error("default_config.yaml does not exist")
            return None

        return load_yaml(yaml_path)

    def modify_config(self, new_config_name, drop_years=None, drop_mc_names=None, drop_campaigns=None):
        yaml_path = f"{self.data_path}/default_config.yaml"

        if not os.path.exists(yaml_path):
            logging.error("default_config.yaml does not exist")
            return None

        if drop_mc_names is None:
            drop_mc_names = []

        if drop_years is None:
            drop_years = []

        if drop_campaigns is None:
            drop_campaigns = []

        yaml_dct = load_yaml(yaml_path)
        new_yaml_dct = copy.deepcopy(yaml_dct)

        for data_year in yaml_dct["data"]:
            for year in drop_years:
                if str(year) in data_year:
                    new_yaml_dct["data"].remove(data_year)

        for mc_name in yaml_dct["mc"].keys():
            for campaign in drop_campaigns:
                if campaign in mc_name:
                    new_yaml_dct["mc"].pop(mc_name, None)

            for name in drop_mc_names:
                if name == mc_name[:-6]:
                    new_yaml_dct["mc"].pop(mc_name, None)

        new_yaml_path = f"{self.data_path}/{new_config_name}.yaml"

        dump_yaml(new_yaml_dct, new_yaml_path)

        return self


def apply_config_to_db(config_name, rucio_db, data_path=None):
    if data_path is not None:
        data_path = data_path
    else:
        data_path = os.environ.get("DATA_PATH", None)

    config = load_yaml(f"{data_path}/{config_name}.yaml")

    dfs = []

    for data_name in config["data"]:
        data_selection = rucio_db[rucio_db["dataset_name"] == data_name]
        dfs.append(data_selection)

    for mc_name, dsids in config["mc"].items():
        mc_selection = rucio_db[rucio_db["dataset_name"] == mc_name]

        for dsid in dsids:
            dsid_selection = mc_selection[mc_selection["dsid"] == dsid]
            dfs.append(dsid_selection)

    new_rucio_db = pd.concat(dfs)
    new_rucio_db.reset_index(drop=True, inplace=True)

    return new_rucio_db
