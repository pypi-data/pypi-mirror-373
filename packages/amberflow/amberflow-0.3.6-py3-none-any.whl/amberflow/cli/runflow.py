# In a new file, e.g., amberflow/cli.py
import argparse
import pickle
from pathlib import Path
from typing import Optional

try:
    import amberflow
except ModuleNotFoundError:
    raise ModuleNotFoundError("Install amberflow: pip install amberflow")
except Exception as ee:
    raise ModuleNotFoundError("Unknown error when trying to import amberflow") from ee

__all__ = ("runflow",)


def get_opts() -> tuple[Path, Optional[list[str]]]:
    parser = argparse.ArgumentParser(description="Run an AmberFlow pipeline from a pickled file.")
    parser.add_argument("pickle_path", type=Path, help="The path to the pipeline.pkl file to execute.")
    parser.add_argument(
        "--systems",
        nargs="+",  # This allows for 0 or more arguments
        metavar="SYSTEM_NAME",
        help="Optional: a space-separated list of specific systems to run. "
        "If not provided, all systems in the pipeline will be run.",
    )

    args = parser.parse_args()
    pickle_path: Path = args.pickle_path

    if not pickle_path.exists():
        raise FileNotFoundError(f"Error: Could not find '{pickle_path}'.")

    return pickle_path, args.systems


def runflow():
    """
    Command-line entry point to load and run a pickled Pipeline.

    This function looks for 'pipeline.pkl' in the current working
    directory, unpickles it, and calls its launch() method.
    """
    pickle_path, systems = get_opts()

    print(systems)

    with open(pickle_path, "rb") as f:
        try:
            pipeline = pickle.load(f)
        except pickle.UnpicklingError as e:
            raise RuntimeError(f"Error unpickling the pipeline from {pickle_path}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while unpickling the pipeline: {e}") from e
        print("Pipeline unpickled. Launching scheduler...")
        # pipeline.launch(systems=systems)
        pipeline.launch()
        print("Pipeline launch complete.")


if __name__ == "__main__":
    runflow()
