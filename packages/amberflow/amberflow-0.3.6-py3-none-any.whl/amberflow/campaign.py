import logging
import pickle
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Sequence

from amberflow.pipeline import Pipeline
from amberflow.primitives import BaseCommand, set_logger, dirpath_t


class BatchStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=False)
class Batch:
    id: str
    systems: List[str]
    dir: Path
    status: BatchStatus  # PENDING, RUNNING, COMPLETED, FAILED


class Campaign:
    """
    Orchestrates the execution of a Pipeline across multiple systems,
    batched and distributed across multiple execution sites.
    """

    def __init__(
        self,
        name: str,
        pipeline: Pipeline,
        sites: Sequence[BaseCommand],
        cwd: Path,
        checkpoint_filename: str = "campaign_checkpoint.pkl",
        logging_level: int = logging.INFO,
        ignore_checkpoint: bool = False,
    ):
        self.name = name
        self._setup_cwd(cwd)
        self.checkpoint_filename = checkpoint_filename
        self.new_run = self._setup_checkpoint(self.cwd, ignore_checkpoint)
        self.logger = self._setup_logger(logging_level, self.new_run)
        self.pipeline = pipeline
        self.sites = sites
        self.batches: list[Batch] = self._setup_batches(self.sites)

    def _setup_cwd(self, cwd: dirpath_t) -> None:
        self.cwd = Path(cwd)
        if not self.cwd.is_dir():
            err_msg = f"Provided cwd {self.cwd} is not a directory."
            raise NotADirectoryError(err_msg)

    def _setup_checkpoint(self, cwd: dirpath_t, ignore_checkpoint: bool) -> bool:
        self.checkpoint_path = Path(cwd, self.checkpoint_filename)
        # If user sets `ignore_checkpoint` to True, we will always start a new run.
        self.ignore_checkpoint = ignore_checkpoint
        return not self.checkpoint_path.is_file() or self.ignore_checkpoint

    def _setup_logger(self, logging_level: int, new_run: bool) -> logging.Logger:
        self.logging_level = logging_level
        return set_logger(
            Path(self.cwd, f"{self.name}.log"),
            logging_level=self.logging_level,
            filemode="w" if new_run else "a",
        )

    def _setup_batches(self, sites: Sequence[BaseCommand]) -> list[Batch]:
        """Splits systems into batches and initializes self.batches."""
        all_systems = sorted(list(self.pipeline.systems.keys()))
        system_batches = [all_systems[i : i + len(sites)] for i in range(0, len(all_systems), len(sites))]

        batches = []
        for i, system_group in enumerate(system_batches):
            batch_id = f"allow_batch_{i:03d}"
            batch_dir = self.cwd / batch_id
            batch_dir.mkdir(exist_ok=True)
            batches.append(Batch(id=batch_id, systems=system_group, dir=batch_dir, status=BatchStatus.PENDING))
        return batches

    def launch(self):
        """
        Launches the campaign, distributing batches across sites.
        """
        # Load state from checkpoint or prepare new batches
        if self.checkpoint_path.exists():
            with open(self.checkpoint_path, "rb") as f:
                self.batches = pickle.load(f)
            self.logger.info("Resuming campaign from checkpoint.")
        else:
            self._write_checkpoint()

        sitio = self.sites[0]
        if not sitio.initialized:
            # If the command is not initialized, we need to initialize it with the root_dir
            sitio = sitio.replace(local_base_dir=self.cwd)
        self._run_batch(self.batches[0], sitio)

        # # Filter for batches that need to be run
        # jobs_to_run = [b for b in self.batches if b.status in (BatchStatus.PENDING, BatchStatus.FAILED)]
        #
        # with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.sites)) as executor:
        #     future_to_batch = {
        #         executor.submit(self._run_batch, batch, site): batch for batch, site in zip(jobs_to_run, self.sites)
        #     }
        #
        #     remaining_jobs = jobs_to_run[len(self.sites) :]
        #
        #     for future in concurrent.futures.as_completed(future_to_batch):
        #         batch = future_to_batch[future]
        #         try:
        #             future.result()
        #             batch.status = BatchStatus.COMPLETED
        #             self.logger.info(f"Batch {batch.id} completed successfully.")
        #         except Exception as e:
        #             batch.status = BatchStatus.FAILED
        #             self.logger.error(f"Batch {batch.id} failed: {e}")
        #         finally:
        #             # Checkpoint the final status of the completed batch
        #             self._write_checkpoint()
        #
        #         if remaining_jobs:
        #             next_job = remaining_jobs.pop(0)
        #             # A simple way to find a free site is to assume the pool manages it.
        #             # For a more advanced scheduler, you'd track site availability.
        #             # Here, we just re-submit to one of the sites.
        #             free_site = self.sites[0]  # Simplified for this example
        #             new_future = executor.submit(self._run_batch, next_job, free_site)
        #             future_to_batch[new_future] = next_job

    def _run_batch(self, batch: Batch, site: BaseCommand):
        """
        Prepares and runs a single batch on a specific site.
        """
        self.logger.info(f"Preparing batch {batch.id} for execution on site.")

        # Update status to RUNNING and checkpoint immediately
        batch.status = BatchStatus.RUNNING
        self._write_checkpoint()

        sub_pipeline = deepcopy(self.pipeline)
        sub_pipeline.systems = {sys_name: self.pipeline.systems[sys_name] for sys_name in batch.systems}
        root_artifacts = sub_pipeline.artifacts["Root"]
        pruned_root_data = {sys_name: root_artifacts[sys_name] for sys_name in batch.systems}
        root_artifacts._data = pruned_root_data

        final_pipeline = sub_pipeline.setup_new_pipeline(site.executor)

        pickle_fn = batch.dir / "pipeline.pkl"
        with open(pickle_fn, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(final_pipeline, f)

        self.logger.info(f"Executing batch {batch.id}...")
        site.run(
            ["runflow", str(pickle_fn.relative_to(batch.dir))],  # Use relative path for the command
            cwd=batch.dir,
            logger=self.logger,
        )

    def _write_checkpoint(self):
        """Saves the current state of self.batches to the checkpoint file."""
        with open(self.checkpoint_path, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(self.batches, f)
