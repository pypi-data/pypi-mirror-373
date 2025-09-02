import pickle
import re
import subprocess as sp
import time
from logging import Logger
from pathlib import Path
from typing import Any, Optional, Sequence, Union, Final

from typing_extensions import override

from amberflow.primitives import (
    CommandError,
    CommandRunningError,
    dirpath_t,
    filepath_t,
    RemoteExecutor,
    LocalExecutor,
    SLURMError,
    BaseDataMover,
)

__all__ = ("CommandRegistryMeta", "BaseCommand", "DefaultCommand", "SLURMCommand")


class CommandRegistryMeta(type):
    """
    Metaclass to register Command objects.
    """

    name: dict[str, type] = {}

    # noinspection PyMethodParameters
    def __new__(meta_cls, cls_name: str, bases: tuple, cls_dict: dict[str, Any]):
        new_cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        if not cls_name.startswith("Base"):
            if cls_name in meta_cls.name:
                raise CommandError(f"Command class '{cls_name}' already registered by name.")
            meta_cls.name[cls_name] = new_cls
        return new_cls


class BaseCommand(metaclass=CommandRegistryMeta):
    """
    Base class for command execution. It is immutable.
    It holds an executor instance (local or remote) to run commands.
    """

    __slots__ = ("executor", "initialized")

    def __init__(
        self,
        remote_server: Optional[str] = None,
        remote_base_dir: Optional[str] = None,
        local_base_dir: Optional[dirpath_t] = None,
        keyfile: Optional[filepath_t] = None,
        data_mover: Optional[BaseDataMover] = None,
        **kwargs: Any,
    ):
        # Determine if local or remote. `local_base_dir` may be set at a later stage, so we don't check it here.
        is_local = all([remote_server is None, remote_base_dir is None])
        is_remote = all([remote_server is not None, remote_base_dir is not None])

        if not (is_local or is_remote):
            raise ValueError(
                "Cannot determine if Command must be local or remote. Either set both of "
                f"remote_server({remote_server=}) and remote_base_dir({remote_base_dir=}) or none of them"
            )

        if is_remote:
            executor = RemoteExecutor(
                remote_server,
                remote_base_dir,
                local_base_dir,
                keyfile=keyfile,
                data_mover=data_mover,
            )
        else:
            executor = LocalExecutor()
        super().__setattr__("executor", executor)
        super().__setattr__("initialized", executor.initialized)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "initialized", False):
            raise AttributeError(f"'{self.__class__.__name__}' instances are immutable.")
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if hasattr(self, "initialized") and self.initialized:
            raise AttributeError(f"'{self.__class__.__name__}' instances are immutable.")
        super().__delattr__(name)

    def __getstate__(self) -> dict[str, Any]:
        return {slot: getattr(self, slot) for slot in self.__slots__ if hasattr(self, slot)}

    def __setstate__(self, state: dict[str, Any]) -> None:
        for key, value in state.items():
            super().__setattr__(key, value)
        if "initialized" not in state:
            super().__setattr__("initialized", True)

    def replace(self, **changes: Any) -> "BaseCommand":
        """
        Returns a new instance of the command with specified attributes replaced.
        """
        # Collect all slots from the entire MRO
        all_slots = set()
        for cls in self.__class__.__mro__:
            if hasattr(cls, "__slots__"):
                all_slots.update(cls.__slots__)

        constructor_slots = [s for s in all_slots if not s.startswith("_")]
        current_args = {slot: getattr(self, slot, None) for slot in constructor_slots}

        # This part is a bit tricky because __init__ args don't map 1-to-1 with slots.
        # We reconstruct the init args from the executor's state.
        if isinstance(self.executor, RemoteExecutor):
            current_args["remote_server"] = self.executor.remote_server
            current_args["remote_base_dir"] = self.executor.remote_base_dir
            current_args["local_base_dir"] = self.executor.local_base_dir
            current_args["keyfile"] = self.executor.keyfile
            current_args["data_mover"] = self.executor.data_mover

        # Remove executor as it's not a direct __init__ arg
        current_args.pop("executor", None)

        for key, value in changes.items():
            if key not in current_args:
                raise TypeError(f"'{key}' is not a valid keyword argument for {self.__class__.__name__}")
            current_args[key] = value

        return self.__class__(**current_args)

    def run(
        self,
        cmd: list[str],
        *args,
        cwd: filepath_t,
        logger: Logger,
        walltime_mins: Optional[int] = None,
        force: bool = False,
        **kwargs,
    ) -> None:
        raise NotImplementedError


class DefaultCommand(BaseCommand):
    """
    A command that runs a simple shell command either locally or remotely.
    It is immutable by inheritance from BaseCommand.
    """

    asynch: bool
    __slots__ = BaseCommand.__slots__ + ("asynch",)

    # noinspection PyUnusedLocal
    def __init__(
        self,
        remote_server: Optional[str] = None,
        remote_base_dir: Optional[str] = None,
        local_base_dir: Optional[dirpath_t] = None,
        keyfile: Optional[filepath_t] = None,
        asynch: bool = False,
        **kwargs: Any,
    ):
        super().__init__(remote_server, remote_base_dir, local_base_dir, keyfile)
        object.__setattr__(self, "asynch", asynch)

    @override
    def run(
        self,
        cmd: list[str],
        *args,
        cwd: filepath_t,
        logger: Logger,
        expected: Optional[Sequence[filepath_t]] = None,
        walltime_mins: Optional[int] = None,
        force: bool = False,
        **kwargs,
    ) -> None:
        if self.asynch:
            cmd.insert(0, "nohup")
            cmd.append("&")
        # we're not yet using the `force` or `walltime_mins` parameters here,
        self.executor.run(cmd, cwd, logger, **kwargs)
        if expected:
            self.executor.validate(cwd, expected, logger)


class SLURMScript:
    """
    A pseudo-immutable representation of a Slurm submission script configuration.
    The instance will be immutable after the first call to `get_sbatch_params()`.
    To create a modified copy, use the `replace()` method.
    """

    __slots__ = (
        "sbatch_params",
        "lines_before_cmd",
        "lines_after_cmd",
        "slurmout",
        "initialized",
    )

    DEFAULT_SBATCH_PARAMS: dict[str, Any] = {
        "job-name": "default_job_name",
        "output": "default_job_name.slurmout",
        "nodes": 1,
        "ntasks-per-node": 1,
        "time": "01:00:00",
    }

    def __init__(
        self,
        sbatch_params: Optional[dict[str, Any]] = None,
        lines_before_cmd: Optional[list[str]] = None,
        lines_after_cmd: Optional[list[str]] = None,
    ):
        almost_final_params = self.DEFAULT_SBATCH_PARAMS.copy()
        if sbatch_params is not None:
            almost_final_params.update(sbatch_params)

        super().__setattr__("sbatch_params", almost_final_params)
        super().__setattr__("lines_before_cmd", tuple(lines_before_cmd or ()))
        super().__setattr__("lines_after_cmd", tuple(lines_after_cmd or ()))
        super().__setattr__("slurmout", almost_final_params.get("output"))

    def get_sbatch_params(self, sbatch_params: Optional[dict[str, Any]] = None) -> str:
        """
        Initializes the class with the effective sbatch parameters and the name of the slurm output file.
        Parameters
        ----------
        sbatch_params : Optional[dict[str, Any]]
            Additional sbatch parameters to override the defaults.
        Returns
        -------
        str
            The name of the slurm output file.
        """
        if sbatch_params is not None:
            self.sbatch_params.update(sbatch_params)
        super().__setattr__("slurmout", self.sbatch_params.get("output"))
        super().__setattr__("initialized", True)

        return self.slurmout

    def write_slurm_script(
        self, cmd: list[str], cwd: dirpath_t, sbatch_params: Optional[dict[str, Any]] = None
    ) -> tuple[Path, str]:
        slurmout = self.get_sbatch_params(sbatch_params)
        lines = self._get_header_lines(self.sbatch_params)
        if self.lines_before_cmd is not None:
            lines.extend(self.lines_before_cmd)
        lines.append(" ".join(cmd))
        if self.lines_after_cmd is not None:
            lines.extend(self.lines_after_cmd)
        script = "\n".join(lines) + "\n"

        script_path = Path(cwd) / "slurm_script.sh"
        with open(script_path, "w") as script_file:
            script_file.write(script)
        return script_path, slurmout

    @staticmethod
    def _get_header_lines(effective_sbatch_params: dict[str, Any]) -> list[str]:
        lines = ["#!/bin/bash"]
        for key, value in effective_sbatch_params.items():
            lines.append(f"#SBATCH --{key}={value}")
        lines.append("")
        return lines

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "initialized", False):
            raise AttributeError(f"'{type(self).__name__}' objects are immutable")
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"'{type(self).__name__}' objects are immutable")

    def replace(self, **changes: Any) -> "SLURMScript":
        """Returns a new SlurmScript instance with specified attributes replaced."""
        current_args = {
            "sbatch_params": dict(self.sbatch_params),
            "lines_before_cmd": list(self.lines_before_cmd),
            "lines_after_cmd": list(self.lines_after_cmd),
        }
        current_args.update(changes)
        return type(self)(**current_args)


class SLURMCommand(BaseCommand):
    """
    Represents an immutable command to be executed as a Slurm batch job.
    """

    # Define slots for the attributes specific to this subclass
    __slots__ = ("script_generator", "submission_regex", "poll_interval_mins")

    # SLURM and State related constants
    _JOB_STATE_FILE = "job_state.pkl"
    _TERMINAL_STATES: Final[tuple[str]] = (
        "CD",
        "COMPLETED",
        "CG",
        "F",
        "FAILED",
        "CA",
        "CANCELLED",
        "TO",
        "TIMEOUT",
        "NF",
        "NODE_FAIL",
    )
    _SUCCESS_STATES: Final[tuple[str]] = ("CD", "COMPLETED", "CG", "")
    _RUNNING_STATES: Final[tuple[str]] = ("SUBMITTED", "R", "PD", "PENDING")
    _MAX_WALLTIME_MINS: Final[int] = 60 * 24 * 2  # Default to 2 days

    # noinspection PyUnusedLocal
    def __init__(
        self,
        sbatch_params: Optional[dict[str, Any]] = None,
        lines_before_cmd: Optional[list[str]] = None,
        lines_after_cmd: Optional[list[str]] = None,
        script_generator: Optional[SLURMScript] = None,
        submission_regex: str = r"Submitted batch job (\d+)",
        poll_interval_mins: int = 5,
        remote_server: Optional[str] = None,
        remote_base_dir: Optional[str] = None,
        local_base_dir: Optional[dirpath_t] = None,
        **kwargs: Any,
    ):
        super().__init__(remote_server, remote_base_dir, local_base_dir)
        # Use object.__setattr__ because the instance is already locked by the parent __init__
        if script_generator is None:
            object.__setattr__(self, "script_generator", SLURMScript(sbatch_params, lines_before_cmd, lines_after_cmd))
        else:
            # when using `.replace()` we can pass an existing SLURMScript instance
            assert isinstance(script_generator, SLURMScript), (
                f"Expected 'script_generator' to be an instance of SLURMScript, got {type(script_generator)}"
            )
            object.__setattr__(self, "script_generator", script_generator)
        object.__setattr__(self, "submission_regex", submission_regex)
        object.__setattr__(self, "poll_interval_mins", poll_interval_mins)

    @override
    def run(
        self,
        cmd: list[str],
        *args,
        cwd: dirpath_t,
        logger: Logger,
        expected: Optional[Sequence[filepath_t]] = None,
        sbatch_params: Optional[dict[str, Any]] = None,
        walltime_mins: Optional[int] = None,
        force: bool = False,
        download: bool = False,
        **kwargs,
    ) -> None:
        job_state_pkl = Path(cwd, self._JOB_STATE_FILE)
        state = self._read_job_state(job_state_pkl, logger)
        jobid, slurmout = None, None

        if state is None or force:
            script_path, slurmout = self.script_generator.write_slurm_script(cmd, cwd, sbatch_params)
            p = self.executor.run(["sbatch", script_path.name], cwd, logger, download=False, **kwargs)
            jobid = self._parse_jobid(p, logger)
            self._write_job_state(job_state_pkl, {"jobid": jobid, "status": "SUBMITTED", "slurmout": slurmout}, logger)
        else:
            logger.info(f"Found existing slurm job data for job {state['jobid']} with status {state['status']}")
        try:
            self._wait_for_job_completion(job_state_pkl, cwd, logger, walltime_mins)
        except SLURMError:
            err_msg = f"Slurm job {jobid} failed. Check {cwd / slurmout}"
            self.executor.download(cwd / slurmout, logger)
            self._cleanup_state_file(job_state_pkl, logger)
            logger.error(err_msg)
            raise
        if expected or download:
            self.executor.download(cwd, logger)
        if expected:
            self.executor.validate(cwd, expected, logger)

    @staticmethod
    def _write_job_state(job_state_pkl: filepath_t, data: dict[str, Any], logger: Logger) -> None:
        logger.info(f"Updating existing SLURM state file: {job_state_pkl} with {data}")
        try:
            with open(job_state_pkl, "wb") as f:
                # noinspection PyTypeChecker
                pickle.dump(data, f)
        except IOError as e:
            logger.warning(f"Could not write SLURM state file to {job_state_pkl}: {e}")

    @staticmethod
    def _read_job_state(job_state_pkl: filepath_t, logger: Logger) -> Optional[dict[str, str]]:
        existing_state: Union[dict[str, Any], None] = None
        if job_state_pkl.exists():
            try:
                with open(job_state_pkl, "rb") as f:
                    existing_state = pickle.load(f)

            except (pickle.UnpicklingError, EOFError, IOError) as e:
                logger.warning(f"Could not read or parse state file {job_state_pkl}, will ignore. Error: {e}")
                Path(job_state_pkl).unlink()  # Corrupted file, remove it

            if not all(["jobid" in existing_state, "status" in existing_state, "slurmout" in existing_state]):
                logger.warning(
                    f"SLURM state file {job_state_pkl} is missing required keys: {existing_state=}. Will ignore."
                )
                existing_state = None
        return existing_state

    @staticmethod
    def _cleanup_state_file(job_state_pkl: filepath_t, logger: Logger):
        if job_state_pkl.exists():
            job_state_pkl.unlink()
            logger.debug(f"Removed SLURM state file: {job_state_pkl}")

    def _parse_jobid(self, process: sp.CompletedProcess, logger: Logger) -> str:
        try:
            output = process.stdout.strip()
            match = re.search(self.submission_regex, output)
            if match:
                jobid = match.group(1)
                logger.info(f"Slurm job submitted successfully. Job ID: {jobid}")
                return jobid
            raise RuntimeError(f"Could not parse Slurm Job ID from sbatch output: {output}")
        except sp.CalledProcessError as e:
            raise RuntimeError(f"sbatch submission failed: {e.stderr}") from e

    def _check_job_status(
        self, job_state_pkl: filepath_t, cwd: dirpath_t, logger: Logger, update: bool = True
    ) -> dict[str, str]:
        state = self._read_job_state(job_state_pkl, logger)
        # Set check=False to avoid raising an error if the job is not found
        p = self.executor.run(
            ["squeue", f"-j {state['jobid']}", "-h", "-o", "%t"], cwd, logger, check=False, download=False, upload=False
        )
        if p.returncode == 0:
            status = p.stdout.strip()
        else:
            remote_stderr: str = p.stderr.strip()
            if remote_stderr.startswith("slurm_load_jobs"):
                status = ""  # Job not found, assume it has finished
            else:
                err_msg = f"Local command failed with exit code {p.returncode}."
                logger.error(err_msg)
                logger.error(f"STDOUT:\n{p.stdout.decode()}")
                logger.error(f"STDERR:\n{p.stderr.decode()}")
                raise CommandRunningError(err_msg)
        state["status"] = status
        if update:
            self._write_job_state(job_state_pkl, state, logger)
        return state

    def _wait_for_job_completion(
        self, job_state_pkl: filepath_t, cwd: dirpath_t, logger: Logger, walltime_mins: Optional[int] = None
    ) -> None:
        start_time = time.monotonic()
        timeout_seconds = self._MAX_WALLTIME_MINS if walltime_mins is None else walltime_mins * 60
        while True:
            state = self._check_job_status(job_state_pkl, cwd, logger)
            jobid = state["jobid"]
            status = state["status"]
            logger.debug(f"Job {jobid} status: {status}")

            if status in self._SUCCESS_STATES:
                logger.info(f"Job {state['jobid']} completed successfully.")
                return
            elif status in self._TERMINAL_STATES:
                err_msg = f"Found previously failed SLURM job {jobid=} with {status=}."
                logger.error(err_msg)
                raise SLURMError(err_msg)
            elif status in self._RUNNING_STATES:
                logger.info(f"Slurm job {jobid} Status: {status}")
            else:
                err_msg = f"Slurm job {jobid} with unexpected status: {status}"
                logger.error(err_msg)
                self._write_job_state(job_state_pkl, state, logger)
                raise CommandRunningError(err_msg)

            if time.monotonic() - start_time > timeout_seconds:
                err_msg = f"Polling for job {state['jobid']} exceeded walltime of {walltime_mins} mins. Attempting to cancel job {state['jobid']}"
                self.executor.run(f"scancel {state['jobid']}", cwd, logger, download=False, upload=False)
                logger.error(err_msg)
                state["TIMEOUT"] = status
                self._write_job_state(job_state_pkl, state, logger)
                raise TimeoutError(err_msg)

            time.sleep(self.poll_interval_mins * 60)
