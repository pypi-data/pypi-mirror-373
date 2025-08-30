import logging
import os

import pandas as pd


class XsecDB:
    def __init__(self, pmg_mc, names=None, add_effective_xsec=True, add_br=True, correct_higher_order=True):
        assert pmg_mc in ["mc16", "mc21"]
        file_name = f"PMGxsecDB_{pmg_mc}.txt"

        self.path = f"{os.path.dirname(os.path.abspath(__file__))}/../data/{file_name}"
        self.add_effective_xsec = add_effective_xsec
        self.add_br = add_br
        self.correct_higher_order = correct_higher_order

        if names is None:
            self.names = [
                "dataset_number",
                "physics_short",
                "crossSection",
                "genFiltEff",
                "kFactor",
                "relUncertUP",
                "relUncertDOWN",
                "generator_name",
                "etag",
            ]
        else:
            self.names = names

        self.xsec_db = None

    def read_xsec(self):
        xsec_db = pd.read_csv(
            self.path,
            header=None,
            delimiter=r"\s+",
            names=self.names,
            engine="python",
        )

        self.xsec_db = xsec_db

        if self.add_br and "branchingratio" not in [name.lower() for name in self.names]:
            self.xsec_db["branchingRatio"] = 1.0

        if self.correct_higher_order:
            logging.warning("Correcting higher order cross sections.")
            self._higher_order_cross_sections()

        if self.add_effective_xsec:
            self.calculate_effective_xsec()

        return self.xsec_db

    def _higher_order_cross_sections(self):
        """https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/PmgWeakBosonProcesses#Higher_order_cross_sections"""

        Z_to_ll = ["Sh_2211_Zee", "Sh_2211_Zmumu", "Sh_2211_Ztautau", "Sh_2211_Ztt"]
        W_to_lnu = ["Sh_2211_Wenu", "Sh_2211_Wmunu", "Sh_2211_Wtaunu"]

        idx_Z_to_ll = self.xsec_db["physics_short"].str.contains("|".join(Z_to_ll))
        idx_W_to_lnu = self.xsec_db["physics_short"].str.contains("|".join(W_to_lnu))

        self.xsec_db.loc[idx_Z_to_ll, ["kFactor"]] = 0.95
        self.xsec_db.loc[idx_W_to_lnu, ["kFactor"]] = 0.95

        return self

    def calculate_effective_xsec(self):
        self.xsec_db["effectiveCrossSection"] = (
            self.xsec_db["crossSection"]
            * self.xsec_db["branchingRatio"]
            * self.xsec_db["genFiltEff"]
            * self.xsec_db["kFactor"]
        )
        return self

    def slim(self, dsids, overwrite=False, save=None):
        slim_xsec_db = self.xsec_db[self.xsec_db["dataset_number"].isin(dsids)]

        if overwrite:
            self.xsec_db = slim_xsec_db

        if save:
            logging.info(f"Saving slimmed xsec db to {save}.")
            slim_xsec_db.to_csv(save, sep=" ", index=False, header=False)

        return self

    def __call__(self):
        return self.read_xsec()
