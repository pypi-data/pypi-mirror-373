import glob
import logging
import os

from f9columnar.utils.helpers import dump_pickle, load_pickle


class ActMerger:
    def __init__(self, run_name, save=True):
        self.run_name = run_name
        self.save = save

    def merge(self):
        out_dir = f"out/{self.run_name}"

        dirs = [f.path for f in os.scandir(out_dir) if f.is_dir()]
        logging.info(f"Found {len(dirs)} output directories.")

        output_pickles = []
        for d in dirs:
            p_files = glob.glob(f"{d}/*.p")

            if len(p_files) == 0:
                logging.warning(f"No output pickles found in {d}!")

            output_pickles.append(p_files)

        assert len(dirs) == len(output_pickles), "Number of directories and pickles do not match!"

        merged_outputs = {}

        for output_pickles_lst in output_pickles:
            for f_name in output_pickles_lst:
                key = os.path.basename(f_name)[:-2]
                if key not in merged_outputs:
                    merged_outputs[key] = []

                merged_outputs[key].append(load_pickle(f_name))

        for k in merged_outputs.keys():
            logging.info(f"Found {len(merged_outputs[k])} outputs for {k}.")

        if self.save:
            logging.info(f"Saving merged outputs to {out_dir}/merged_outputs.p.")
            dump_pickle(f"{out_dir}/merged_outputs.p", {"outputs": merged_outputs})

        return merged_outputs


def merge_batch_histograms(merged_pickle, output_key, return_data=True):
    """Merge output histograms from act_merge.

    Parameters
    ----------
    merged_pickle : str
        Path to the merged pickle file.
    output_key : str
        Key of the output histograms (i.e. "el_histograms").
    return_data : bool, optional
        If True pop data key from merged and return it, by default True.

    Returns
    -------
    dict or (dict, dict)
        Merged (summed) histograms for each variable in each histogram name.
    """
    merged = load_pickle(merged_pickle)

    outputs = merged["outputs"]
    hists = outputs[output_key]

    merge_hist_dct = {}
    for hs in hists:
        for hist_name, hist_dct in hs.items():
            if len(hist_dct) == 0:
                continue

            if hist_name not in merge_hist_dct:
                merge_hist_dct[hist_name] = {}

            for var_name, var_hist in hist_dct.items():
                if var_name not in merge_hist_dct[hist_name]:
                    merge_hist_dct[hist_name][var_name] = []

                merge_hist_dct[hist_name][var_name].append(var_hist)

    for hist_name, var_dct in merge_hist_dct.items():
        for var_name, var_hist_lst in var_dct.items():
            merge_hist_dct[hist_name][var_name] = sum(var_hist_lst)

    if return_data:
        return merge_hist_dct, merge_hist_dct.pop("Data")
    else:
        return merge_hist_dct
