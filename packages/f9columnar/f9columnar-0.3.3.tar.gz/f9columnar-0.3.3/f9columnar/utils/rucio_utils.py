import logging
import os
import re
from glob import glob


class RucioHandler:
    def __init__(self, rucio_sample_str=None, data_path=None):
        if rucio_sample_str is not None:
            self.rucio_sample_str = rucio_sample_str
        else:
            self.rucio_sample_str = os.environ.get("RUCIO_SAMPLE_STR", None)

        if data_path is not None:
            self.data_path = data_path
        else:
            self.data_path = os.environ.get("DATA_PATH", None)

        assert self.rucio_sample_str is not None, "RUCIO_SAMPLE_STR not set!"
        assert self.data_path is not None, "DATA_PATH not set!"

        os.makedirs(self.data_path, exist_ok=True)

    def get_hists_dids(self):
        hists_path = f"{self.data_path}/hists"
        os.makedirs(hists_path, exist_ok=True)

        if not os.path.exists(f"{hists_path}/hists_dids.txt"):
            os.system(f"rucio ls {self.rucio_sample_str}.*_hist > {hists_path}/hists_dids.txt")
        else:
            logging.warning("hists_dids.txt already exists")

        with open(f"{hists_path}/hists_dids.txt", "r") as f:
            dids_file = f.readlines()

        pattern = r"\buser\.[^\s|]+"

        dids = []
        for line in dids_file:
            match = re.search(pattern, line)

            if match:
                dids.append(match.group())

        assert len(dids) > 0, "No hists found!"

        return dids

    def get_hists(self):
        hists_path = f"{self.data_path}/hists"

        hists_dirs = glob(f"{hists_path}/*/", recursive=True)

        if len(hists_dirs) > 0:
            logging.warning("Hists already downloaded!")
            return hists_dirs

        self.get_hists_dids()

        os.system(f"rucio download --dir {hists_path} {self.rucio_sample_str}.*_hist")

        hists_dirs = glob(f"{hists_path}/*/", recursive=True)

        assert len(hists_dirs) > 0, "No hists downloaded!"

        return hists_dirs

    def make_rse_files(self, rse="SIGNET_LOCALGROUPDISK"):
        if not os.path.exists(f"{self.data_path}/datasets_rse.txt"):
            os.system(f"rucio list-datasets-rse {rse} > {self.data_path}/rse_files.txt")
        else:
            logging.warning("datasets_rse.txt already exists!")

        with open(f"{self.data_path}/rse_files.txt", "r") as f:
            rse_files = f.readlines()

        return rse_files

    def download_from_file_list(self, file_lst, dir_name):
        files_path = f"{self.data_path}/{dir_name}"

        present_files = glob(f"{files_path}/*")
        for f in present_files:
            base_f = os.path.basename(f)
            if base_f in file_lst:
                file_lst.remove(base_f)

        if len(file_lst) == 0:
            logging.warning("All files already downloaded!")
            return None
        else:
            files = " ".join(file_lst)

        os.system(f"rucio download {files} --no-subdir --dir {files_path}")

        return file_lst


def make_rucio_url(user, file):
    """Make a rucio URL for batch processing.

    Example
    -------
    rucio://rucio-lb-prod.cern.ch/replicas/user.jedebevc/user.jedebevc.00278912.physics_Main.r9264_p3083_p5314.39484806._000035.tree.root

    Parameters
    ----------
    user : str
        Rucio user.
    file : str
        Root file.

    Returns
    -------
    str
        URL for rucio file.
    """
    base_url = "rucio://rucio-lb-prod.cern.ch/replicas"
    return f"{base_url}/user.{user}/{file}"
