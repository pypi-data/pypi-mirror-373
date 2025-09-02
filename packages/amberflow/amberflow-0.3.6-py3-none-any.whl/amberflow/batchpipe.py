# In a new file, e.g., amberflow/distributed.py

import math
import pickle
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from amberflow.pipeline import Pipeline
from amberflow.primitives import BaseCommand


@dataclass
class Batch:
    """A data class representing a batch of systems to be executed."""

    pipeline: Pipeline
    command: BaseCommand
    batch_id: int
    pickle_path: Path


@dataclass
class ExecutionSite:
    """Represents a remote execution site with a queue of batches."""

    command: BaseCommand
    is_busy: bool = False
    process: subprocess.Popen = None
    batch_queue: List[Batch] = field(default_factory=list)


class DistributedRunner:
    """Orchestrates the distribution of pipeline batches across multiple sites."""

    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        self.logger = pipeline.logger
        self.sites: List[ExecutionSite] = [ExecutionSite(command=cmd) for cmd in self.pipeline.remote_commands]
        self.batches: List[Batch] = self._create_batches()

    def _create_batches(self) -> List[Batch]:
        """Splits the pipeline's systems into batches."""
        all_systems = list(self.pipeline.systems.keys())
        batch_size = self.pipeline.systems_per_batch
        num_batches = math.ceil(len(all_systems) / batch_size)

        batches = []
        for i in range(num_batches):
            start_index = i * batch_size
            end_index = start_index + batch_size
            system_subset = all_systems[start_index:end_index]

            # Create a specialized pipeline for this batch
            batch_pipeline = self.pipeline.setup_new_pipeline(
                # Use the command's executor to determine if it's remote
                self.sites[i % len(self.sites)].command.executor
            )
            # Filter the systems for this batch
            batch_pipeline.systems = {
                name: path for name, path in batch_pipeline.systems.items() if name in system_subset
            }

            # Save the batch-specific pipeline to a unique pickle file
            pickle_path = self.pipeline.cwd / f"pipeline_batch_{i}.pkl"
            with open(pickle_path, "wb") as f:
                pickle.dump(batch_pipeline, f)

            # Assign a command to this batch in a round-robin fashion
            command_for_batch = self.sites[i % len(self.sites)].command

            batch = Batch(pipeline=batch_pipeline, command=command_for_batch, batch_id=i, pickle_path=pickle_path)
            batches.append(batch)
            self.logger.info(f"Created batch {i} with {len(system_subset)} systems.")

        return batches

    def run(self):
        """Manages the execution of all batches across all sites."""
        # Assign initial batches to sites
        for i, site in enumerate(self.sites):
            if i < len(self.batches):
                site.batch_queue.append(self.batches[i])

        pending_batches = len(self.batches)
        submitted_batches = 0

        while pending_batches > 0:
            for site in self.sites:
                # If a site is busy, check if its process has finished
                if site.is_busy and site.process.poll() is not None:
                    self.logger.info(f"Site with server {site.command.executor.remote_server} has finished a job.")
                    site.is_busy = False
                    pending_batches -= 1

                # If a site is free and has batches to run, launch the next one
                if not site.is_busy and site.batch_queue:
                    batch = site.batch_queue.pop(0)
                    self.logger.info(
                        f"Submitting batch {batch.batch_id} to remote server {batch.command.executor.remote_server}..."
                    )
                    # Use Popen for non-blocking execution
                    site.process = batch.command.run(
                        ["runflow", str(batch.pickle_path)],
                        cwd=self.pipeline.cwd,
                        logger=self.logger,
                        force=self.pipeline.force_restart,
                        download=True,
                        wait=False,  # Add a 'wait' flag to your Command.run to return Popen object
                    )
                    site.is_busy = True
                    submitted_batches += 1

                    # Assign next batch in queue to this site
                    if submitted_batches < len(self.batches):
                        site.batch_queue.append(self.batches[submitted_batches])

            time.sleep(30)  # Poll every 30 seconds

        self.logger.info("All distributed batches have completed.")
