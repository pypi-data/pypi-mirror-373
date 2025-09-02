import contextlib
import os
import sys
from io import StringIO
from logging import Logger
from pathlib import Path
import subprocess as sp
from typing import Final, Iterable, Optional

import parmed as pmd

from amberflow.primitives.primitives import filepath_t, FileHandle, dirpath_t

__all__ = [
    "conv_build_resnames_set",
    "get_ngpus",
    "get_dir_size",
    "amb_to_pdb",
    "capture_stdout",
    "_run_command",
]


def conv_build_resnames_set(value):
    if isinstance(value, str):
        return {value}
    elif isinstance(value, Iterable):
        return set(value)
    else:
        return set()


def get_ngpus():
    try:
        p = sp.run(
            "nvidia-smi -L | wc -l",
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            shell=True,
            text=True,
        )
        ngpus = int(p.stdout)
        assert ngpus != 0
    except (ValueError, AssertionError, Exception):
        raise RuntimeError("No GPUs detected. Can't run locuaz.")
    return ngpus


def get_dir_size(folder: Path) -> float:
    B_TO_MB: Final = 1048576
    total_size = 0
    for path, _, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.path.getsize(fp)  # type: ignore
    return total_size / B_TO_MB


def amb_to_pdb(top_filepath: filepath_t, rst_filepath: filepath_t) -> FileHandle:
    """
    Convert AMBER topology and restart files to PDB format.

    Parameters
    ----------
    top_filepath : Path
        The path to the AMBER topology file.
    rst_filepath : Path
        The path to the AMBER restart file.

    Returns
    -------
    FileHandle
        A `FileHandle` object pointing to the generated PDB file.
    """
    amb = pmd.load_file(str(top_filepath), str(rst_filepath))
    pdb_path = top_filepath.with_suffix(".pdb")
    amb.save(str(pdb_path))  # type: ignore
    return FileHandle(pdb_path)


@contextlib.contextmanager
def capture_stdout(new_stdout: Optional[StringIO] = None):
    """
    A context manager to temporarily suppress stdout.

    Args:
        new_stdout: An optional StringIO object to capture the output.
                    If None, output is discarded.

    Yields:
        The StringIO object that captured the output.
    """
    # If no buffer is provided, create a dummy one to discard output
    if new_stdout is None:
        new_stdout = StringIO()

    # Save the original stdout so we can restore it later
    original_stdout = sys.stdout

    # Redirect stdout to the new buffer
    sys.stdout = new_stdout
    try:
        # Yield control back to the 'with' block
        yield new_stdout
    finally:
        # Always restore the original stdout, even if errors occur
        sys.stdout = original_stdout


def _run_command(
    command: str, cwd: dirpath_t, logger: Logger, env: Optional[dict] = None, check: bool = True
) -> sp.CompletedProcess:
    try:
        p = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, text=True, cwd=str(cwd), env=env, check=check, shell=True)
        if p.stdout:
            logger.debug(f"STDOUT: {p.stdout}")
        if p.stderr:
            logger.debug(f"STDERR: {p.stderr}")
        return p
    except sp.CalledProcessError as e:
        err_msg = f"Command failed with exit code {e.returncode}: {command}"
        logger.error(err_msg)
        logger.error(f"STDOUT:\n{e.stdout}")
        logger.error(f"STDERR:\n{e.stderr}")
        raise RuntimeError(err_msg) from e
    except Exception as e:
        err_msg = f"Unknown error running command {e}"
        logger.error(err_msg)
        raise RuntimeError(err_msg)
