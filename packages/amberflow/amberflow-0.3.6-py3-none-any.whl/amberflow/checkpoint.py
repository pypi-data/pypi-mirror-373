import pickle
from logging import Logger
from pathlib import Path
from typing import Any, TYPE_CHECKING

import networkx as nx

from amberflow.artifacts import BatchArtifacts, ArtifactContainer
from amberflow.primitives import dirpath_t, InvalidPipeline, filepath_t, CheckpointError
from amberflow.worknodes import WorkNodeStatus

if TYPE_CHECKING:
    # noinspection PyUnusedImports
    from amberflow.pipeline import Pipeline

    # noinspection PyUnusedImports
    from amberflow.campaign import Campaign


__all__ = [
    "BaseCheckpointer",
    "PipelineCheckpointer",
    "CampaignCheckpointer",
]


class BaseCheckpointer:
    """An abstract base class for managing the saving and loading of state.

    This class provides a common interface for checkpointing different
    components of the workflow, such as Pipelines or Campaigns.

    Parameters
    ----------
    name : str
        An identifier for the checkpointer instance.
    checkpoint_path : filepath_t
        The full path to the checkpoint file.
    tracked_attrs : tuple[str], optional
        A tuple of attribute names to be saved from the tracked object.
    ignore_checkpoint : bool, optional
        If True, forces a new run by ignoring any existing checkpoint file,
        by default False.
    force_restart : bool, optional
        If True, ignores validation errors found within a checkpoint file and
        attempts to resume, by default False.

    Attributes
    ----------
    name : str
        Identifier for the checkpointer.
    checkpoint_path : pathlib.Path
        The path to the checkpoint file.
    tracked_attrs : tuple[str]
        The names of the attributes that this checkpointer will save.
    new_run : bool
        True if no valid checkpoint exists or if it's ignored.
    force_restart : bool
        Flag to control behavior on validation failure.
    """

    def __init__(
        self,
        name: str,
        *,
        tracked_obj: "Pipeline | Campaign | Any",
        checkpoint_path: filepath_t,
        ignore_checkpoint: bool = False,
        force_restart: bool = False,
        tracked_attrs: tuple[str] = tuple(),
    ) -> None:
        self.name = name
        self.tracked_obj = tracked_obj
        self.checkpoint_path = Path(checkpoint_path)
        if len(tracked_attrs) == 0:
            raise ValueError("At least one attribute must be tracked for checkpointing.")
        self.tracked_attrs = tracked_attrs
        self.new_run = not self.checkpoint_path.is_file() or ignore_checkpoint
        self.force_restart = force_restart

    def save(
        self,
        logger: Logger,
    ) -> None:
        """Saves the specified attributes of an object to a checkpoint file.

        Parameters
        ----------

        logger : logging.Logger
            The logger instance to record the save operation.
        """
        state = {}
        for each in self.tracked_attrs:
            if not hasattr(self.tracked_obj, each):
                logger.warning(
                    f"Tracked object {self.tracked_obj.__class__.__name__} does not have attribute: '{each}'"
                )
            state[each] = getattr(self.tracked_obj, each)

        with open(self.checkpoint_path, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(state, f)
        logger.debug(
            f"Checkpoint saved to {self.checkpoint_path} with attributes "
            f"{self.tracked_attrs} from {self.tracked_obj.__class__.__name__}"
        )

    def _load(self, logger: Logger) -> dict[str, Any]:
        """Loads the state from the checkpoint file.

        Parameters
        ----------
        logger : logging.Logger
            The logger instance to record the load operation.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the state loaded from the checkpoint file.

        Raises
        ------
        CheckpointError
            If the checkpoint file does not exist.
        """
        if not self.checkpoint_path.is_file():
            err_msg = f"Cannot load. Checkpoint file does not exist: {self.checkpoint_path}"
            logger.error(err_msg)
            raise CheckpointError(err_msg)

        with open(self.checkpoint_path, "rb") as f:
            state = pickle.load(f)
        return state

    def _validate_checkpoint(self, *args, **kwargs) -> None:
        """Abstract method for validating a loaded checkpoint."""
        raise NotImplementedError


class PipelineCheckpointer(BaseCheckpointer):
    """A checkpointer specifically for saving and loading Pipeline state."""

    def __init__(
        self,
        name: str,
        *,
        tracked_obj: "Pipeline",
        checkpoint_path: filepath_t,
        ignore_checkpoint: bool = False,
        force_restart: bool = False,
    ) -> None:
        """Initializes the PipelineCheckpointer.

        Parameters
        ----------
        name : str
            An identifier for the checkpointer instance.
        checkpoint_path : filepath_t
            The full path to the checkpoint file.
        ignore_checkpoint : bool, optional
            If True, forces a new run by ignoring any existing checkpoint file.
        force_restart : bool, optional
            If True, ignores validation errors and attempts to resume.
        """
        super().__init__(
            name,
            tracked_obj=tracked_obj,
            tracked_attrs=("flow", "leafs", "artifacts", "systems"),
            checkpoint_path=checkpoint_path,
            ignore_checkpoint=ignore_checkpoint,
            force_restart=force_restart,
        )

    def load(self, systems: dict[str, dirpath_t], logger: Logger, validate: bool = True) -> dict[str, Any]:
        """Loads and validates the pipeline state from the checkpoint file.

        Parameters
        ----------
        systems : dict[str, dirpath_t]
            The current dictionary of systems discovered in the working directory.
        logger : logging.Logger
            The logger instance for recording validation steps.
        validate : bool, optional
            If True, performs validation checks on the loaded state, by default True.

        Returns
        -------
        dict[str, Any]
            The loaded state dictionary containing the flow, artifacts, and other data.
        """
        state = super()._load(logger=logger)
        if validate:
            self._validate_checkpoint(
                old_systems=state["systems"],
                new_systems=systems,
                old_flow=state["flow"],
                old_artifacts=state["artifacts"],
                force_restart=self.force_restart,
                logger=logger,
            )
        return state

    @staticmethod
    def _validate_checkpoint(
        old_systems: dict[str, dirpath_t],
        new_systems: dict[str, dirpath_t],
        old_flow: nx.DiGraph,
        old_artifacts: dict[str, BatchArtifacts],
        force_restart: bool,
        logger: Logger,
    ) -> None:
        """Validates the consistency of a loaded pipeline checkpoint.

        This method checks for discrepancies between the saved and current
        systems, resets the status of failed nodes, and verifies that the
        output files of completed nodes still exist.

        Parameters
        ----------
        old_systems : dict[str, dirpath_t]
            The dictionary of systems saved in the checkpoint.
        new_systems : dict[str, dirpath_t]
            The dictionary of systems currently found in the directory.
        old_flow : nx.DiGraph
            The workflow graph loaded from the checkpoint.
        old_artifacts : dict[str, BatchArtifacts]
            The artifacts loaded from the checkpoint.
        force_restart : bool
            If True, validation errors will be logged as warnings instead of
            raising an exception.
        logger : logging.Logger
            The logger instance for recording validation results.

        Raises
        ------
        InvalidPipeline
            If validation fails and `force_restart` is False.
        """
        # Now, check if the systems in the checkpoint match the current systems
        assert old_systems is not None, "Expected old_systems to be not None when validating checkpoint."
        set_old_systems = set(old_systems.keys())
        set_new_systems = set(new_systems.keys())

        in_common = set_old_systems.intersection(set_new_systems)
        missing = set_old_systems.difference(set_new_systems)
        new = set_new_systems.difference(set_old_systems)
        if len(missing) > 0:
            logger.warning(f"Missing systems in the current root dir: {missing}")
        if len(new) > 0:
            logger.warning(f"New systems in the current root dir: {new}")

        valid = True
        err_msg = ""
        for node in nx.topological_sort(old_flow):
            if node.status in (WorkNodeStatus.FAILED, WorkNodeStatus.CANCELLED):
                node.status = WorkNodeStatus.PENDING
                continue

            elif node.status == WorkNodeStatus.COMPLETED:
                if node.id not in old_artifacts:
                    valid = force_restart
                    err_msg += f"Missing artifacts for completed WorkNode {node.id}\n"
                    break
                batch_artifacts: BatchArtifacts = old_artifacts[node.id]
                for sysname in in_common:
                    if sysname not in batch_artifacts:
                        valid = force_restart
                        err_msg += f"Missing artifacts for system {sysname} on WorkNode {node.id}\n"
                        break
                    artifact_container: ArtifactContainer = batch_artifacts[sysname]
                    for art_list in artifact_container.values():
                        for art in art_list:
                            if hasattr(art, "filepath") and not art.filepath.exists():
                                valid = force_restart
                                err_msg += f"WorkNode {node.id} is missing output artifact {art}\n"
                                break
                        if not valid:
                            break
            if not valid:
                break

        if not valid:
            err_msg += "Invalid Pipeline state. Cannot continue from checkpoint. Set `force_restart=True` to override."
            logger.error(err_msg)
            raise InvalidPipeline(err_msg)


class CampaignCheckpointer(BaseCheckpointer):
    """A checkpointer specifically for saving and loading Campaign state."""

    def __init__(
        self,
        name: str,
        *,
        tracked_obj: "Campaign",
        checkpoint_path: filepath_t,
        ignore_checkpoint: bool = False,
        force_restart: bool = False,
    ) -> None:
        """Initializes the CampaignCheckpointer.

        Parameters
        ----------
        name : str
            An identifier for the checkpointer instance.
        checkpoint_path : filepath_t
            The full path to the checkpoint file.
        ignore_checkpoint : bool, optional
            If True, forces a new run by ignoring any existing checkpoint file.
        force_restart : bool, optional
            If True, ignores validation errors and attempts to resume.
        """
        super().__init__(
            name,
            tracked_obj=tracked_obj,
            tracked_attrs=("pipeline", "systems", "batches", "flows"),
            checkpoint_path=checkpoint_path,
            ignore_checkpoint=ignore_checkpoint,
            force_restart=force_restart,
        )

    def load(self, systems: dict[str, dirpath_t], logger: Logger, validate: bool = True) -> dict[str, Any]:
        """Loads and validates the campaign state from the checkpoint file.

        Parameters
        ----------
        systems : dict[str, dirpath_t]
            The current dictionary of systems discovered in the working directory.
        logger : logging.Logger
            The logger instance for recording validation steps.
        validate : bool, optional
            If True, performs validation checks on the loaded state, by default True.

        Returns
        -------
        dict[str, Any]
            The loaded state dictionary containing the campaign data.
        """
        state = super()._load(logger=logger)
        if validate:
            self._validate_checkpoint(
                systems,
                logger=logger,
            )
        return state

    @staticmethod
    def _validate_checkpoint(
        systems: dict[str, dirpath_t],
        logger: Logger,
    ) -> None:
        """Validates the consistency of a loaded campaign checkpoint.

        (Currently a placeholder).

        Parameters
        ----------
        systems : dict[str, dirpath_t]
            The dictionary of systems currently found in the directory.
        logger : logging.Logger
            The logger instance for recording validation results.
        """
        pass
