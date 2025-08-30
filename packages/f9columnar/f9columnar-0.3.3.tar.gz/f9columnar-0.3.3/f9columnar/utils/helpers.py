import datetime
import itertools
import json
import logging
import os
import pickle
import subprocess
import tarfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import uproot
import yaml
from matplotlib import rc
from tqdm import tqdm
from uncertainties import unumpy
from uproot.exceptions import KeyInFileError


def load_pickle(name):
    with open(name, "rb") as f:
        data = pickle.load(f)
    return data


def dump_pickle(name, data):
    with open(name, "wb") as f:
        pickle.dump(data, f)
    return True


def load_json(path):
    with open(path, "r") as f:
        dct = json.load(f)
    return dct


def dump_json(dct, path, indent=2):
    with open(path, "w") as f:
        json.dump(dct, f, indent=indent)


def load_yaml(file_path):
    with open(file_path, "r") as f:
        try:
            dct = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            logging.error(f"Error reading yaml file: {exc}")
            dct = None

    return dct


def dump_yaml(dct, file_path, indent=2):
    with open(file_path, "w") as f:
        yaml.dump(dct, f, default_flow_style=False, indent=indent)


def get_ms_time():
    return time.time_ns() // 1_000_000


def get_ms_datetime():
    ms_time = get_ms_time()
    return datetime.datetime.fromtimestamp(int(ms_time) // 1000)


def get_file_size(f, convert_to="gb"):
    byte_size = os.path.getsize(f)

    if convert_to.lower() == "gb":
        return byte_size / 1024 / 1024 / 1024
    elif convert_to.lower() == "mb":
        return byte_size / 1024 / 1024
    elif convert_to.lower() == "kb":
        return byte_size / 1024
    else:
        return byte_size


def set_df_print(max_rows=None, max_cols=None, width=None, max_colwidth=None):
    pd.set_option("display.max_rows", max_rows)
    pd.set_option("display.max_columns", max_cols)
    pd.set_option("display.width", width)
    pd.set_option("max_colwidth", max_colwidth)


def flatten_list(lst):
    return list(itertools.chain(*lst))


def load_luminosity(json_path=None):
    if json_path is None:
        json_path = f"{os.path.dirname(os.path.abspath(__file__))}/../data/luminosity.json"

    lumi_dct = load_json(json_path)

    lumi = {int(k): float(v) for k, v in lumi_dct["lumi"].items()}
    lumi_scale = {int(k): float(v) for k, v in lumi_dct["lumi_scale"].items()}

    return {"lumi": lumi, "lumi_scale": lumi_scale}


def load_periods(json_path=None):
    if json_path is None:
        json_path = f"{os.path.dirname(os.path.abspath(__file__))}/../data/periods.json"

    periods_dct = load_json(json_path)

    periods = {int(k): v for k, v in periods_dct["periods"].items()}

    return periods


def get_act_run():
    run_file_names = ["act_run.py", "act_run.sh"]

    for run_file in run_file_names:
        file_path = f"{os.path.dirname(os.path.abspath(__file__))}/../submit/{run_file}"
        os.system(f"cp {file_path} .")


def open_root_file(file_path, branches=None, to_arrays=True, key="physics"):
    if branches is not None:
        assert type(branches) is list

    with uproot.open(file_path) as f:
        f_data = f[key]

    if to_arrays:
        return f_data.arrays(branches if branches else f_data.keys())
    else:
        return f_data


def get_num_entries(file_path, key="physics"):
    try:
        with uproot.open(file_path) as f:
            f_data = f[key]
            num_entries = f_data.num_entries
        return num_entries
    except KeyInFileError:
        logging.error(f"Key {key} not found in file {file_path}.")
        return 0


def hist_to_unumpy(h, flatten=False, zero_to_nan=False, std=True):
    if flatten:
        values, err = h.values().flatten(), h.variances().flatten()
    else:
        values, err = h.values(), h.variances()

    if zero_to_nan:
        values[np.where(values == 0.0)[0]] = np.nan
        err[np.where(err == 0.0)[0]] = np.nan

    if std:
        err = np.sqrt(err)

    return unumpy.uarray(values, err)


def handle_plot_exception(func):
    """Decorator to handle all exceptions in plotting functions."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Plotting of {func.__name__} failed with exception: {e}")
            return None

    return wrapper


def set_default_font_family():
    """Set the matplotlib default font family to Latin Modern sans."""
    rc("font", **{"family": "serif", "serif": ["Latin Modern sans"]})


def url_download(url, data_dir, fname=None, chunk_size=1024):
    """Downloads file from url to data_dir.

    Parameters
    ----------
    url : str
        URL of file to download.
    data_dir : str
        Downloaded in this directory (needs to exist).
    fname : str, optional
        File name, by default None.
    chunk_size : int, optional
        Chunk size for downloading, by default 1024

    References
    [1] - https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51

    Returns
    -------
    str
        File name.

    """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if fname is None:
        fname = data_dir + url.split("/")[-1]
    else:
        fname = data_dir + fname

    if Path(fname).is_file() is not True:
        logging.info(f"Started downloading from {url} ...")

        resp = requests.get(url, stream=True)
        total = int(resp.headers.get("content-length", 0))

        with (
            open(fname, "wb") as file,
            tqdm(desc=fname, total=total, unit="iB", unit_scale=True, unit_divisor=1024) as bar,
        ):
            for data in resp.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                bar.update(size)
    else:
        logging.info(f"Already downloaded {fname}!")

    return fname


def make_tar_file(base_path=None, tar_name=None, exclude=None, include=None):
    current_dir = os.getcwd()

    if base_path is None:
        base_path = os.path.basename(current_dir)

    if tar_name is None:
        tar_name = f"{base_path}.tar"

    try:
        os.remove(tar_name)
    except FileNotFoundError:
        pass

    if exclude is None:
        exclude = []

    if include is None:
        include = []

    include += subprocess.check_output("git ls-files", shell=True).splitlines()
    include += subprocess.check_output("git ls-files --others --exclude-standard", shell=True).splitlines()

    include = list(set(include))

    for i, inc in enumerate(include):
        try:
            include[i] = str(inc, "utf-8")
        except TypeError:
            pass

        include[i] = f"{base_path}/{include[i]}"

    os.chdir("..")

    with tarfile.open(tar_name, "w") as tar:
        for file in include:
            skip_file = False

            for exclude_dir in exclude:
                if exclude_dir in file:
                    skip_file = True
                    break

            if not skip_file:
                try:
                    tar.add(file)
                except FileNotFoundError:
                    logging.warning(f"File {file} not found.")
            else:
                skip_file = False

    os.system(f"mv {tar_name} {base_path}/")
    os.chdir(current_dir)
