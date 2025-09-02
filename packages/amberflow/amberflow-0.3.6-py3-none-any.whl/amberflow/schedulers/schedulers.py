import logging
from abc import abstractmethod, ABC
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from sys import maxsize as sysmaxsize
from typing import Sequence, Any, Union, Optional

import networkx as nx
from typing_extensions import override

from amberflow.artifacts import BatchArtifacts
from amberflow.checkpoint import BaseCheckpointer
from amberflow.primitives import (
    dirpath_t,
    CyclicalContainer,
    CommandRegistryMeta,
    BaseCommand,
    get_gpu_count,
)
from amberflow.worknodes import BaseBatchWorkNode, WorkNodeStatus, BaseSingleWorkNode

__all__ = [
    "BaseScheduler",
    "ReferenceScheduler",
    "DefaultScheduler",
]


class BaseScheduler(ABC):
    """Abstract base class for workflow schedulers.

    Defines the interface that all scheduler implementations must follow.
    """

    @abstractmethod
    def launch(self, *args, **kwargs) -> None:
        pass

    def yield_completed(self, dag: nx.DiGraph, nodes: Sequence, logger: logging.Logger, max_checks: int = 10) -> Any:
        """Yield nodes that have completed execution once their ancestors are done.

        Args:
            dag: Directed acyclic graph of work nodes
            nodes: Sequence of nodes to check for completion
            logger: Logger instance for error reporting
            max_checks: Maximum number of completion checks per node

        Yields:
            Completed work nodes

        Raises:
            RuntimeError: If nodes fail to complete after max checks or cycles detected
        """
        pending_nodes = deque(nodes)
        check_counts = {node.id: 0 for node in nodes}

        while pending_nodes:
            node = pending_nodes.popleft()
            valor = self.ancestors_are_done(dag, node)
            if valor:
                yield node
            else:
                if check_counts[node.id] >= max_checks:
                    err_msg = (
                        f"Node '{node.id}' failed: Ancestors did not complete after {max_checks} checks. "
                        f"Potential cycle involving nodes: {[n.id for n in pending_nodes] + [node.id]}"
                    )
                    logger.error(err_msg)
                    raise RuntimeError(err_msg)
                check_counts[node.id] += 1
                # Requeue the node at the end
                pending_nodes.append(node)

    @staticmethod
    def ancestors_are_done(dag: nx.DiGraph, source_node) -> bool:
        """Check if all ancestors of a node have completed execution.

        Args:
            dag: Directed acyclic graph of work nodes
            source_node: Node to check ancestors for

        Returns:
            True if all ancestor nodes are completed, False otherwise
        """
        return all([n.status == WorkNodeStatus.COMPLETED for n in nx.ancestors(dag, source=source_node)])

    @staticmethod
    def get_output_from_ancestors(
        dag: nx.DiGraph, entering_node, artifacts: dict[str, BatchArtifacts], logger: logging.Logger
    ) -> BatchArtifacts:
        """Gather output artifacts from all ancestors of a node.

        Args:
            dag: Directed acyclic graph of work nodes
            entering_node: Node to gather ancestor artifacts for
            artifacts: Dictionary mapping node IDs to their output artifacts
            logger: Logger instance for error reporting

        Returns:
            BatchArtifacts containing combined outputs from all ancestors

        Raises:
            RuntimeError: If ancestor artifacts are missing
        """
        data = {}
        for n in dag.predecessors(entering_node):
            if n.id not in artifacts:
                err_msg = f"Failed {entering_node.id}. Node {n.id} is not in the artifacts. This shouldn't happen."
                logger.error(err_msg)
                raise RuntimeError(err_msg)
            for sysname, art_container in artifacts[n.id].items():
                if sysname not in data:
                    data[sysname] = art_container
                else:
                    common_artifacts = set(data[sysname].keys()).intersection(set(art_container.keys()))
                    if len(common_artifacts) > 0 and not entering_node.takes_multiple_artifacts:
                        err_msg = (
                            f"Node {entering_node.id} has ancestors which output the same artifacts. "
                            f"Common artifacts: {common_artifacts}. Use a WorkNodeFilter on one of its parents: "
                            f"{[n.id for n in dag.predecessors(entering_node)]}."
                        )
                        logger.error(err_msg)
                        raise RuntimeError(err_msg)
                    else:
                        data[sysname] = data[sysname] | art_container

        return BatchArtifacts(f"{entering_node.id}_input_artifacts", data=data)

    @staticmethod
    def get_workers(
        max_cores: int,
        max_gpus: int,
        *,
        cuda_visible_devices: CyclicalContainer,
        node: BaseSingleWorkNode,
        allow_gpu_oversubscription: bool = False,
        logger: logging.Logger,
    ) -> tuple[int, dict[str, tuple[int]]]:
        """Calculate the maximum number of workers and GPU mappings for a node.

        Args:
            max_cores: Maximum number of CPU cores available
            max_gpus: Maximum number of GPUs available
            cuda_visible_devices: Cyclical container for GPU indices
            node: Work node to calculate resources for
            allow_gpu_oversubscription: Whether to allow oversubscription of GPUs
            logger: Logger instance for error reporting

        Returns:
            Tuple containing:
                - Maximum number of workers that can be allocated
                - Dictionary mapping system names to list of GPU indices

        Raises:
            RuntimeError: If insufficient resources are available
        """

        # If WorkNode sets a max number of systems that can be run in parallel, then this will override the max_workers
        if node.max_systems != 0:
            max_workers = node.max_systems
            gpu_mapping: dict[str, tuple[int]] = {sys: cuda_visible_devices.items() for sys in node.systems}
        else:
            max_cpu_workers = max_cores // node.min_cores
            max_gpu_workers = max_gpus // node.min_gpus if node.min_gpus != 0 else sysmaxsize
            if allow_gpu_oversubscription:
                max_workers = max_cpu_workers
            else:
                max_workers = min(max_cpu_workers, max_gpu_workers)
            if max_workers < 1:
                err_msg = (
                    f"Not enough resources to run {node}, asking for {node.min_gpus} GPUs "
                    f"and {node.min_cores} CPUs. Available GPUs: {max_gpus} and CPUS: {max_cores}."
                )
                logger.error(err_msg)
                raise RuntimeError(err_msg)
            gpu_mapping: dict[str, tuple[int]] = {
                sys: tuple(cuda_visible_devices.get(node.min_gpus)) for sys in node.systems
            }

        return max_workers, gpu_mapping

    @staticmethod
    def _lacks_gpus(max_gpus: int) -> bool:
        """Check if there are enough GPUs

        Args:
            max_gpus: number of GPUs requested by the scheduler

        Returns:
            bool: True if the scheduler is asking for more GPUs than available, False otherwise
        """
        return max_gpus > get_gpu_count()


class ReferenceScheduler(BaseScheduler):
    """Reference workflow scheduler implementation that manages resource allocation and execution.

    It executes work nodes sequentially, for easier debugging and testing.

    Args:

    """

    supported_node_types: tuple[str] = ("BaseBatchWorkNode", "BaseSingleWorkNode")
    max_cores: int = 1
    max_gpus: int = 1

    def __init__(
        self,
        max_cores: int = 1,
        max_memory: int = 16,
        max_gpus: int = 1,
        *,
        allow_gpu_oversubscription: bool = False,
        skip_completed_nodes: bool = True,
    ) -> None:
        self.trackdag = nx.DiGraph(name="trackdag")
        self.max_cores = max_cores
        self.max_memory = max_memory
        if not allow_gpu_oversubscription and super()._lacks_gpus(max_gpus):
            err_msg = f"Not enough GPUs available. Requested: {max_gpus}, available: {get_gpu_count()}."
            raise RuntimeError(err_msg)
        self.max_gpus = max_gpus
        self.allow_gpu_oversubscription = allow_gpu_oversubscription
        self.cuda_visible_devices = CyclicalContainer(max_gpus)
        self.skip_completed_nodes = skip_completed_nodes

    # noinspection PyUnreachableCode
    @override
    def launch(
        self,
        dag: nx.DiGraph,
        root,
        *,
        systems: dict[str, dirpath_t],
        cwd: dirpath_t,
        pipeline_artifacts: dict[str, BatchArtifacts],
        biomolecule: str = "protein",
        logger: logging.Logger,
        checkpointer: BaseCheckpointer,
    ) -> None:
        for node in nx.topological_sort(dag):
            if node.status == WorkNodeStatus.COMPLETED:
                logger.info(f"Skipping {node}. Status is {node.status}.")
                continue
            else:
                logger.info(f"Start {node}.")
            node_output_artifacts = {}
            if isinstance(node, BaseBatchWorkNode):
                input_artifacts = super().get_output_from_ancestors(dag, node, pipeline_artifacts, logger)
                node.run(
                    input_artifacts,
                    root_dir=cwd,
                    cwd=cwd / "allow_temp_cwd",
                    systems=systems,
                    gpus=self.cuda_visible_devices,
                    skippable=self.skip_completed_nodes,
                )
                node_output_artifacts = node.output_artifacts
            elif isinstance(node, BaseSingleWorkNode):
                max_workers, gpu_mapping = super().get_workers(
                    self.max_cores,
                    self.max_gpus,
                    cuda_visible_devices=self.cuda_visible_devices,
                    node=node,
                    allow_gpu_oversubscription=self.allow_gpu_oversubscription,
                    logger=logger,
                )
                input_artifacts = super().get_output_from_ancestors(dag, node, pipeline_artifacts, logger)
                for sysname in node.systems:
                    try:
                        node_output_artifacts[sysname] = node.run(
                            input_artifacts[sysname],
                            root_dir=cwd,
                            cwd=systems[sysname],
                            sysname=sysname,
                            gpus=gpu_mapping[sysname],
                            skippable=self.skip_completed_nodes,
                        )
                        logger.info(f"Node {node.id} completed on system {sysname}")
                    except KeyError:
                        err_msg = f"Cannot run WorkNode {node.id} on system {sysname} the previous node failed."
                        logger.error(err_msg)
                node_output_artifacts = BatchArtifacts(node.id, node_output_artifacts)
            else:
                err_msg = f"Unknown node type: {type(node)}. Nodes must be one of {self.supported_node_types}."
                logger.error(err_msg)
                raise TypeError(err_msg)
            pipeline_artifacts[node.id] = node_output_artifacts
            node.status = WorkNodeStatus.COMPLETED
            checkpointer.save(logger)


class DefaultScheduler(BaseScheduler):
    """Default workflow scheduler implementation that manages resource allocation and execution.

    Handles scheduling of batch and single work nodes while managing CPU cores, memory and GPU resources.

    Args:
        max_cores: Maximum number of CPU cores available
        max_memory: Maximum memory in GB available
        max_gpus: Maximum number of GPUs available
    """

    def __init__(
        self,
        max_cores: int = 1,
        max_memory: int = 16,
        max_gpus: int = 1,
        *,
        allow_gpu_oversubscription: bool = False,
        command: Optional[str] = None,
        remote_server: Optional[str] = None,
        remote_base_dir: Optional[str] = None,
        skip_completed_nodes: bool = True,
    ) -> None:
        self.trackdag = nx.DiGraph(name="trackdag")
        self.max_cores = max_cores
        self.max_memory = max_memory
        if not allow_gpu_oversubscription and super()._lacks_gpus(max_gpus):
            err_msg = f"Not enough GPUs available. Requested: {max_gpus}, available: {get_gpu_count()}."
            raise RuntimeError(err_msg)
        self.max_gpus = max_gpus
        self.allow_gpu_oversubscription = allow_gpu_oversubscription
        self.cuda_visible_devices = CyclicalContainer(max_gpus)

        self.command: Union[None, BaseCommand] = None
        self.command_str = command
        self.remote_server = remote_server
        self.remote_base_dir = remote_base_dir
        self.skip_completed_nodes = skip_completed_nodes

    # noinspection PyUnreachableCode
    @override
    def launch(
        self,
        dag: nx.DiGraph,
        root,
        *,
        systems: dict[str, dirpath_t],
        cwd: dirpath_t,
        pipeline_artifacts: dict[str, BatchArtifacts],
        logger: logging.Logger,
        checkpointer: BaseCheckpointer,
    ) -> None:
        self._setup_command(cwd, logger)
        for node in nx.topological_sort(dag):
            if node.status == WorkNodeStatus.COMPLETED:
                logger.info(f"Skipping {node}. Status is {node.status}.")
                continue
            else:
                logger.info(f"Start {node}.")
            node_output_artifacts = {}
            if self.command is not None and node.command is None:
                logger.info(f"Setting command for node {node.id} to {self.command}.")
                node.command = self.command

            if isinstance(node, BaseBatchWorkNode):
                input_artifacts = super().get_output_from_ancestors(dag, node, pipeline_artifacts, logger)
                node.run(
                    input_artifacts,
                    cwd=cwd / "allow_temp_cwd",
                    systems=systems,
                    gpus=self.cuda_visible_devices,
                    skippable=self.skip_completed_nodes,
                )
                node_output_artifacts = node.output_artifacts
            elif isinstance(node, BaseSingleWorkNode):
                futuros = {}
                max_workers, gpu_mapping = self.get_workers(
                    self.max_cores,
                    self.max_gpus,
                    cuda_visible_devices=self.cuda_visible_devices,
                    allow_gpu_oversubscription=self.allow_gpu_oversubscription,
                    node=node,
                    logger=logger,
                )
                with ProcessPoolExecutor(max_workers=max_workers) as ex:
                    input_artifacts = super().get_output_from_ancestors(dag, node, pipeline_artifacts, logger)
                    for sysname in node.systems:
                        try:
                            futu = ex.submit(
                                node.run,
                                input_artifacts[sysname],
                                cwd=systems[sysname],
                                sysname=sysname,
                                gpus=gpu_mapping[sysname],
                                skippable=self.skip_completed_nodes,
                            )
                        except KeyError:
                            err_msg = f"Cannot run WorkNode {node.id} on system {sysname} the previous node failed."
                            logger.error(err_msg)

                        futuros[futu] = sysname
                    for futu in as_completed(futuros):
                        sysname = futuros[futu]
                        logger.info(f"Node {node.id} completed on system {sysname}")
                        try:
                            node_output_artifacts[sysname] = futu.result()
                        except Exception as e:
                            err_msg = f"Node {node.id} failed on system {sysname} with exception: {e}."
                            logger.error(err_msg)
                            # keep going, other systems might work
                node_output_artifacts = BatchArtifacts(node.id, node_output_artifacts)
            else:
                err_msg = f"Unknown node type: {type(node)}. Nodes must be either `BaseBatchWorkNode` or `BaseSingleWorkNode`."
                logger.error(err_msg)
                raise TypeError(err_msg)
            pipeline_artifacts[node.id] = node_output_artifacts
            node.status = WorkNodeStatus.COMPLETED
            checkpointer.save(logger)

    def _setup_command(
        self,
        cwd: dirpath_t,
        logger: logging.Logger,
    ) -> None:
        if self.command_str is not None:
            logger.info(f"Setting up flow-wide command to all nodes: {self.command_str}")
            self.command = CommandRegistryMeta.name[self.command_str](self.remote_server, self.remote_base_dir, cwd)
