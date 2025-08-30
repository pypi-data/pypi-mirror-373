import argparse

from f9columnar.submit.act_handler import ActBatchRunner
from f9columnar.utils.loggers import setup_logger

if __name__ == "__main__":
    setup_logger()

    parser = argparse.ArgumentParser(description="Batch runner.")

    parser.add_argument(
        "-n",
        "--run_name",
        default="run_0",
        type=str,
        help="Run name.",
    )
    args = parser.parse_args()

    batch_run = ActBatchRunner(args.run_name, save_dir=f"out/{args.run_name}")
    batch_run.init()
    batch_run.run()
