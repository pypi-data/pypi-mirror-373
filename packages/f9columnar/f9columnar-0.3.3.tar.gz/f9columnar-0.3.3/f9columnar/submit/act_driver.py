import copy
import glob
import logging
import os
import time

import pandas as pd

CLUSTERS = {
    "pikolit": "https://pikolit.ijs.si/batch",
    "rebula": "https://rebula.ijs.si/batch",
    "nsc": " https://nsc.ijs.si/gridlong",
    "arnes": "https://hpc.arnes.si/all",
    "vega01": "https://arc01.vega.izum.si/cpu",
    "vega02": "https://arc02.vega.izum.si/cpu",
}


class ActInterface:
    def __init__(self, jobs_dir):
        self.jobs_dir = jobs_dir
        self.run_name = jobs_dir.split("/")[-1]

        self.output_dir = f"out/{self.run_name}"
        os.makedirs(self.output_dir, exist_ok=True)

        self.state = None

    def get_jobs(self):
        return glob.glob(f"{self.jobs_dir}/*.xrsl")

    def get_downloaded(self, basename=False):
        downloaded_dirs = glob.glob(f"{self.output_dir}/*")

        if basename:
            downloaded_dirs = [os.path.basename(downloaded_dir) for downloaded_dir in downloaded_dirs]

        return downloaded_dirs

    def read_state(self):
        os.system(f"act stat -a > {self.output_dir}/act_stat.txt")

        try:
            self.state = pd.read_csv(f"{self.output_dir}/act_stat.txt", delimiter=r"\s+").iloc[1:]
        except pd.errors.EmptyDataError:
            self.state = None

        os.system(f"rm -f {self.output_dir}/act_stat.txt")

        return self.state


class ActBatchSubmitter(ActInterface):
    def __init__(self, jobs_dir, cluster_names=None):
        super().__init__(jobs_dir)

        if cluster_names is None:
            cluster_names = list(CLUSTERS.keys())

        cluster_lst = [CLUSTERS[cluster_name] for cluster_name in cluster_names]

        logging.info(f"Submitting to clusters: {', '.join(cluster_names)}")

        self.cluster_lst = ",".join(cluster_lst) if cluster_lst is not None else None

    def submit(self, jobs_lst=None, exclude_downloaded=True, exclude_jobs_lst=None):
        if jobs_lst is None:
            jobs_lst = self.get_jobs()

        if exclude_downloaded:
            downloaded_jobs = self.get_downloaded(basename=True)
            downloaded_jobs = [f"{self.jobs_dir}/{j}.xrsl" for j in downloaded_jobs]
            jobs_lst = list(set(jobs_lst) - set(downloaded_jobs))

        if exclude_jobs_lst is not None:
            jobs_lst = list(set(jobs_lst) - set(exclude_jobs_lst))

        if len(jobs_lst) == 0:
            return None

        jobs = " ".join(jobs_lst)
        os.system(f"act sub {jobs} --clusterlist {self.cluster_lst}")

        return self


class ActBatchGetter(ActInterface):
    def __init__(self, jobs_dir):
        super().__init__(jobs_dir)

    def get(self, ids_lst=None, clean=False):
        if ids_lst is None:
            df = self.read_state()
            ids_lst = df[(df["State"] == "Finished") & (df["arcstate"] == "done")]["id"].values.tolist()
        else:
            assert type(ids_lst) is list

        if len(ids_lst) == 0:
            return None

        ids = ",".join(ids_lst)

        current_dir = os.getcwd()
        os.chdir(self.output_dir)

        if clean:
            os.system(f"act get --use-jobname --noclean --id {ids} >/dev/null 2>&1")
            os.system(f"act clean --id {ids} >/dev/null 2>&1")
        else:
            os.system(f"act get --use-jobname --noclean --id {ids} >/dev/null 2>&1")

        os.chdir(current_dir)

        return self


class ActDriver(ActInterface):
    def __init__(self, jobs_dir, cluster_names=None, max_resub=3, refresh_time=5.0):
        super().__init__(jobs_dir)
        logging.info(f"[green][bold]Activating act driver for {self.run_name}![/bold][/green]")

        self.max_resub = max_resub
        self.refresh_time = refresh_time

        self.submitter = ActBatchSubmitter(jobs_dir, cluster_names)
        self.getter = ActBatchGetter(jobs_dir)

        self.all_jobs = self.get_jobs()
        self.all_jobs_dct = {".".join(os.path.basename(job).split(".")[:-1]): job for job in self.all_jobs}

        self.max_resub_dct = {job: 0 for job in self.all_jobs_dct.keys()}

    def _get_missing(self, remove=False):
        downloaded_dirs = self.get_downloaded()

        missing = []
        for dir_name in downloaded_dirs:
            if os.path.isfile(dir_name):
                continue

            if not os.path.isfile(f"{dir_name}/arc/output"):
                missing.append(os.path.basename(dir_name))
                if remove:
                    os.system(f"rm -rf {dir_name}")
                continue

            with open(f"{dir_name}/arc/output", "r") as f:
                log_output = f.read().splitlines()

            log_output = list(set([line[1:] for line in log_output]))
            log_output = [line.split("/")[0] for line in log_output]

            output = glob.glob(f"{dir_name}/*")
            output = [os.path.basename(out) for out in output]

            if len(list(set(log_output) - set(output))) != 0:
                missing.append(os.path.basename(dir_name))

                if remove:
                    os.system(f"rm -rf {dir_name}")

        return missing

    def _resub_mising(self, missing):
        resub_missing = copy.deepcopy(missing)

        for m in missing:
            self.max_resub_dct[m] += 1

            if self.max_resub_dct[m] > self.max_resub:
                logging.warning(f"Job {m} resubmitted {self.max_resub} times. Skipping.")
                resub_missing.remove(m)
            else:
                logging.info(f"Resubmitting missing job {m}.")

        resub_missing = [self.all_jobs_dct[m] for m in resub_missing]

        self.submitter.submit(jobs_lst=resub_missing)

        return self

    def _get(self, df):
        done_df = df[(df["State"] == "Finished") & (df["arcstate"] == "done")]
        done_ids, done_names = done_df["id"], done_df["jobname"]

        downloaded_names = self.get_downloaded(basename=True)

        to_download_names = list(set(done_names) - set(downloaded_names))
        to_download_ids = done_ids[done_names.isin(to_download_names)]

        if len(to_download_ids) != 0:
            logging.info(f"[green]Downloading {len(to_download_ids)} jobs.[/green]")

        self.getter.get(ids_lst=list(to_download_ids), clean=True)

        return self

    def _get_failed(self, df):
        failed_df = df[(df["State"] == "Failed") & (df["arcstate"] == "failed")]
        failed_names = failed_df["jobname"].values.tolist()

        if len(failed_names) != 0:
            logging.warning(f"[yellow][bold]Failed jobs:[/bold] {', '.join(failed_names)}[/yellow]")
            return failed_df

        return None

    def _submit(self, df):
        job_names = list(self.all_jobs_dct.keys())
        present_job_names = list(set(df["jobname"].values.tolist()))

        downloaded_jobs = self.get_downloaded(basename=True)

        submit_job_names = list(set(job_names) - set(present_job_names) - set(downloaded_jobs))
        submit_jobs = [self.all_jobs_dct[job] for job in submit_job_names]

        self.submitter.submit(jobs_lst=submit_jobs)

        return self

    def _get_states(self, run_df, as_dict=False):
        state, arc_state = run_df["State"].value_counts().to_dict(), run_df["arcstate"].value_counts().to_dict()

        if as_dict:
            return state, arc_state

        state_str = ", ".join([f"{k.lower()}: {v}" for k, v in state.items()])
        arc_state_str = ", ".join([f"{k.lower()}: {v}" for k, v in arc_state.items()])

        return state_str, arc_state_str

    def _run(self, run_df):
        self._submit(run_df)

        self._get(run_df)
        failed_df = self._get_failed(run_df)

        if failed_df is not None and len(run_df) == len(failed_df):
            logging.warning("[yellow][bold]Only have failed jobs![/bold][/yellow]")
            return None

        missing = self._get_missing(remove=True)
        self._resub_mising(missing)

        return self

    def run(self):
        logging.info(f"Starting act driver for {self.run_name}!")

        n_all_jobs, n_steps = len(self.all_jobs), 0

        while True:
            df = self.read_state()

            if df is None and n_steps == 0:
                self.submitter.submit(exclude_downloaded=True)
                n_steps += 1
                continue

            if df is None and n_steps != 0:
                logging.info("[green][bold]Done with all jobs![/bold][/green]")
                break

            run_df = df[df["jobname"].str.contains(self.run_name)]

            if len(run_df) == 0 and n_steps != 0:
                logging.info("[green][bold]Done with all jobs![/bold][/green]")
                break

            state_str, arc_state_str = self._get_states(run_df)
            logging.info(f"[bold]State[/bold] - {state_str} | [bold]Arcstate[/bold] - {arc_state_str}")

            if n_steps != 0:
                finished_jobs = n_all_jobs - len(run_df)
                logging.info(f"[bold]Progress:[/bold] {finished_jobs}/{n_all_jobs} | {finished_jobs / n_all_jobs:.2%}")

            run_return = self._run(run_df)

            if run_return is None:
                break

            time.sleep(self.refresh_time)
            n_steps += 1

        return self
