import glob
import logging
import os

from f9columnar.run import ColumnarEventLoop
from f9columnar.utils.helpers import dump_pickle, get_act_run, load_pickle, make_tar_file


def job_template(
    executable,
    arguments,
    input_files,
    output_files,
    job_name,
    cpu_time=30,
    wall_time=30,
    memory=2000,
    thread_count=1,
):
    return f"""&
(executable="{executable}")
(arguments="{arguments}")
(inputFiles={input_files})
(outputFiles={output_files})
(jobName="{job_name}")
(stdout="run.out")
(join=yes)
(gmlog="arc")
(cpuTime="{cpu_time}")
(wallTime="{wall_time}")
(memory="{memory}")
(count="{thread_count}")
(runtimeenvironment="ENV/SINGULARITY" "/cvmfs/atlas.cern.ch/repo/containers/fs/singularity/x86_64-almalinux9")"""


class ActBatchHandler:
    def __init__(
        self,
        dataset_builder,
        run_name=None,
        processors=None,
        postprocessors=None,
        input_files=None,
        output_files=None,
        working_dir=".",
        executable_path=".",
        tar_name="source.tar",
        venv_version="v0.1.10",
        arccp_tar=False,
        output_datasets=False,
        **job_kwargs,
    ):
        """Class for preparing batch submission for ARC. Makes .xrsl files for submission and pickles datasets.

        Note
        ----
        - Both processors and postprocessors get patched into the dataset objects for pickling.
        - Output files are set from the save_path of the postprocessors.

        References
        ----------
        [1] - https://doc.vega.izum.si/arc/

        """
        self.dataset_builder = dataset_builder
        self.processors = processors
        self.postprocessors = postprocessors

        if run_name is None:
            run_name = "run_0"
            logging.warning(f"Run name is not provided, using default: {run_name}")

        self.run_name = run_name
        self.batch_dir = f"batch/{run_name}"

        os.makedirs(self.batch_dir, exist_ok=True)

        if input_files is None:
            self.input_files = []
        else:
            self.input_files = input_files

        if output_files is None:
            self.output_files = []
        else:
            self.output_files = output_files

        self.executable_path = executable_path
        self.executable = os.path.join(self.executable_path, "act_run.sh")

        self.output_datasets = output_datasets

        self.job_kwargs = job_kwargs

        self.tar_name = tar_name
        self.arccp_tar = arccp_tar

        if self.arccp_tar:
            self.input_files.append(f'("{tar_name}" "davs://dcache.sling.si:2880/atlas/jang/{tar_name}" "cache=renew")')
        else:
            self.input_files.append(f'("out/{tar_name}" "")')

        assert "v" in venv_version, "Please provide the version of the venv in the format 'v0.1.10'"
        venv_version = "".join(venv_version.split("."))
        venv_tar = f"f9columnar_{venv_version}_venv.tar.gz"

        self.input_files += [
            f'("{venv_tar}" "davs://dcache.sling.si:2880/atlas/jang/{venv_tar}" "cache=invariant")',
            f'("{self.executable}" "")',
        ]

        self.output_files += self._get_output_files()

        _export_dct = {
            "RUN_NAME": self.run_name,
            "TAR_NAME": self.tar_name,
            "VENV_TAR": venv_tar,
            "THREAD_COUNT": self.job_kwargs.get("thread_count", 1),
            "CURRENT_DIR": os.path.basename(os.getcwd()),
            "WORKING_DIR": working_dir,
            "EXECUTABLE_PATH": self.executable_path,
            "BATCH_DIR": self.batch_dir,
        }
        self._make_submission_scripts(_export_dct)

    def _get_output_files(self):
        output_files = []
        for proc in self.postprocessors.processors.values():
            f = proc.save_path

            if f is not None:
                output_files.append(os.path.basename(f))

        xrsl_output_files = "".join([f'("{f}" "")' for f in output_files])

        return [xrsl_output_files]

    def _make_submission_scripts(self, export_dct):
        logging.info("Making act_run.sh and act_run.py files.")
        get_act_run()

        envs = ""
        for k, v in export_dct.items():
            envs += f'export {k}="{v}"\n'

        envs += "\n"

        with open("act_run.sh", "r") as f:
            data = f.read()

        with open("act_run.sh", "w") as f:
            f.write(envs + data)

        os.system(f"mv act_run.sh {self.executable_path}")
        os.system(f"mv act_run.py {self.executable_path}")

    def _dump(self, file_name, obj):
        dump_pickle(file_name, obj)

    def configure_rucio_files(self, prefix="../"):
        logging.info("Configuring rucio files.")

        datasets = self.dataset_builder.mc_datasets + self.dataset_builder.data_datasets
        input_files = {"mc": [], "data": []}

        for dataset in datasets:
            root_files, dataset_input_files = [], []

            for rucio_root_file in dataset.dataset_selection["root_file"].tolist():
                root_file = os.path.basename(rucio_root_file)

                root_files.append(root_file)
                dataset_input_files.append(f'("{root_file}" "{rucio_root_file}" "cache=invariant")')

            if dataset.is_data:
                input_files["data"].append(dataset_input_files)
            else:
                input_files["mc"].append(dataset_input_files)

            dataset.dataset_selection["root_file"] = [f"{prefix}{f}" for f in root_files]

        return input_files

    def save_datasets(self):
        logging.info(f"Saving datasets to {self.batch_dir}.")

        datasets = self.dataset_builder.mc_datasets + self.dataset_builder.data_datasets
        saved_datasets = {"mc": [], "data": []}

        data_count, mc_count = 0, 0
        for dataset in datasets:
            dataset.processors, dataset.postprocessors = self.processors, self.postprocessors

            if dataset.is_data:
                name = f"{dataset.name}_{self.run_name}_{data_count}"
                data_count += 1
            else:
                name = f"{dataset.name}_{self.run_name}_{mc_count}"
                mc_count += 1

            self._dump(f"{self.batch_dir}/{name}_dataset.p", dataset)

            if dataset.is_data:
                saved_datasets["data"].append(f'("{self.batch_dir}/{name}_dataset.p" "")')
            else:
                saved_datasets["mc"].append(f'("{self.batch_dir}/{name}_dataset.p" "")')

        return saved_datasets

    def _save_job(self, job_name, job_str):
        with open(f"{self.batch_dir}/{job_name}.xrsl", "w") as f:
            f.write(job_str)

    def make_submission_xrsl(self, input_files, saved_datasets):
        logging.info("Making submission xrsl files.")

        for i, (mc_input_files, mc_saved_dataset) in enumerate(zip(input_files["mc"], saved_datasets["mc"])):
            mc_dataset = self.dataset_builder.mc_datasets[i]

            job_input_files = "".join(self.input_files) + mc_saved_dataset + "".join(mc_input_files)
            job_output_files = "".join(self.output_files)

            if self.output_datasets:
                job_output_files += f'("{mc_saved_dataset.split("/")[-1]}'

            job_name = f"{mc_dataset.name}_{self.run_name}_{i}"

            job = job_template(
                self.executable, self.run_name, job_input_files, job_output_files, job_name, **self.job_kwargs
            )

            self._save_job(job_name, job)

        for i, (data_input_files, data_saved_dataset) in enumerate(zip(input_files["data"], saved_datasets["data"])):
            data_dataset = self.dataset_builder.data_datasets[i]

            job_input_files = "".join(self.input_files) + data_saved_dataset + "".join(data_input_files)
            job_output_files = "".join(self.output_files)

            if self.output_datasets:
                job_output_files += f'("{data_saved_dataset.split("/")[-1]}'

            job_name = f"{data_dataset.name}_{self.run_name}_{i}"

            job = job_template(
                self.executable, self.run_name, job_input_files, job_output_files, job_name, **self.job_kwargs
            )

            self._save_job(job_name, job)

        return self

    def make_code_tar(self, exclude, include):
        logging.info(f"Making {self.tar_name} file.")
        make_tar_file(tar_name=self.tar_name, exclude=exclude, include=include)

        if self.arccp_tar:
            logging.info("Copying tar file to dCache.")
            os.system(f"arccp -f out/{self.tar_name} davs://dcache.sling.si:2880/atlas/jang/")
        else:
            logging.info("Using local tar file.")

        os.makedirs("out", exist_ok=True)
        os.system(f"mv {self.tar_name} out/")

    def prepare(self, exclude=None, include=None):
        logging.info("[red][bold]Preparing batch submission![/bold][/red]")

        input_files = self.configure_rucio_files()
        saved_datasets = self.save_datasets()
        self.make_submission_xrsl(input_files, saved_datasets)
        self.make_code_tar(exclude, include)

    def __call__(self, *args, **kwargs):
        self.prepare(*args, **kwargs)


class ActBatchRunner:
    def __init__(self, run_name, save_dir="out"):
        """Class for running batch jobs on clusters. Runs the ColumnarEventLoop using pickled datasets.

        Parameters
        ----------
        run_name : str
            Name of the current run.
        save_dir : str, optional
            Name of the directory with outputs, by default "out".
        """
        self.run_name = run_name
        os.makedirs(save_dir, exist_ok=True)
        self.save_dir = save_dir

        self.mc_datasets, self.data_datasets = [], []
        self.postprocessors, self.event_loop = None, None

    def _load(self, file_name):
        return load_pickle(file_name)

    def init(self, prefix="../"):
        dataset_files = glob.glob(f"{prefix}batch/{self.run_name}/*_dataset.p")

        assert len(dataset_files) > 0, "No datasets found!"

        for dataset_file in dataset_files:
            dataset = self._load(dataset_file)
            dataset.init_dataloader(processors=dataset.processors)

            if dataset.is_data:
                self.data_datasets.append(dataset)
            else:
                self.mc_datasets.append(dataset)

        self.postprocessors = dataset.postprocessors

        return self

    def run(self):
        self.event_loop = ColumnarEventLoop(
            mc_datasets=self.mc_datasets,
            data_datasets=self.data_datasets,
            postprocessors_graph=self.postprocessors,
            fit_postprocessors=True,
        )

        if len(self.mc_datasets) == 0:
            data_only = True
        else:
            data_only = False

        if len(self.data_datasets) == 0:
            mc_only = True
        else:
            mc_only = False

        self.event_loop.run(mc_only=mc_only, data_only=data_only)

        return self
