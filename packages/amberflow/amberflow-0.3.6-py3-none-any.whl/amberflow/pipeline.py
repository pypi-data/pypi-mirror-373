import logging
import os
import pickle
import re
import subprocess as sp
from copy import deepcopy
from pathlib import Path
from typing import Sequence, Iterable

import networkx as nx
from attr import Converter, Factory
from attrs import define, field

from amberflow.artifacts import (
    TargetProteinPDB,
    ArtifactRegistry,
    BinderLigandPDB,
    BinderLigandSmiles,
    BaseComplexStructureFile,
    BatchArtifacts,
    BaseArtifact,
    ArtifactContainer,
)
from amberflow.checkpoint import PipelineCheckpointer
from amberflow.flows import BaseFlow
from amberflow.primitives import (
    InvalidPipeline,
    UnknownFileType,
    DirHandle,
    conv_build_resnames_set,
    set_logger,
    UnknownArtifactError,
    dirpath_t,
    filepath_t,
    BaseCommand,
    DefaultCommand,
    BaseExecutor,
    RemoteExecutor,
)
from amberflow.schedulers import BaseScheduler
from amberflow.worknodes import BaseWorkNode, WorkNodeDummy, WorkNodeStatus

__all__ = ["Pipeline"]


@define
class Pipeline:
    """
    The main orchestrator for an amberflow simulation workflow.

    This class discovers input data, builds a computational graph of work nodes,
    and uses a scheduler to execute the defined pipeline. It handles checkpointing
    to allow for resuming interrupted workflows.

    Attributes
    ----------
    name : str
        The name of the pipeline.
    cwd : dirpath_t
        The current working directory where systems are located and outputs will be generated.
    target : str
        The name assigned to the target molecule type, typically 'protein' or 'na'.
    binder : str
        The name assigned to the binder molecule type, typically 'ligand'.
    scheduler : BaseScheduler
        The scheduler instance responsible for executing the work nodes.
    command : BaseCommand
        The command execution object, which can be local or remote.
    new_run : bool
        Flag indicating if this is a new run (True) or a resumed run (False).
    ignore_checkpoint : bool
        If True, forces a new run, ignoring any existing checkpoint file.
    force_restart : bool
        If True, ignores checkpoint validation errors and starts fresh.
    checkpoint_filename : str
        The name of the checkpoint file.
    checkpoint_path : Path
        The full path to the checkpoint file.
    logger : logging.Logger
        The logger for the pipeline.
    logging_level : int
        The logging level.
    systems : dict[str, dirpath_t]
        A dictionary mapping system names to their respective directory paths.
    root : WorkNodeDummy
        The root node of the workflow graph.
    leafs : list[BaseWorkNode]
        The leaf nodes of the workflow graph.
    free_md : bool
        If True, allows running simulations without a complex structure.
    user_accepted_resnames : set
        A set of user-provided residue names to be accepted.
    flow : nx.DiGraph
        The NetworkX directed graph representing the workflow.
    flow_ids : set[str]
        A set of all work node IDs in the flow.
    artifacts : dict[str, BatchArtifacts]
        A dictionary storing all artifacts generated during the pipeline execution.
    rootid : str
        The identifier for the root node.
    """

    name: str = field(converter=str)
    cwd: dirpath_t = field(kw_only=True, converter=lambda value: Path(value).resolve())
    target: str = field(kw_only=True, converter=str, default="protein")
    binder: str = field(kw_only=True, converter=str, default="ligand")
    scheduler: BaseScheduler = field(kw_only=True)
    command: BaseCommand = field(kw_only=True, default=Factory(DefaultCommand))
    new_run: bool = field(default=True)
    ignore_checkpoint: bool = field(default=False)
    force_restart: bool = field(default=False)
    checkpoint_filename: str = field(kw_only=True, converter=str, default="checkpoint.pkl")
    checkpoint_path: Path = field(
        init=False, default=Factory(lambda self: Path(self.cwd, self.checkpoint_filename), takes_self=True)
    )
    logger: logging.Logger = field(init=False, default=None)
    logging_level: int = field(kw_only=True, default=logging.INFO)
    systems: dict[str, dirpath_t] = field(init=False, default=Factory(dict))
    root: WorkNodeDummy = field(init=False)
    leafs: list[BaseWorkNode] = field(init=False)
    free_md: bool = field(init=True, default=True)
    user_accepted_resnames: set = field(kw_only=True, converter=Converter(conv_build_resnames_set), default=None)
    flow: nx.DiGraph = field(init=False, default=Factory(nx.DiGraph))
    flow_ids: set[str] = field(init=False, default=Factory(set))
    artifacts: dict[str, BatchArtifacts] = field(init=False, default=Factory(dict))
    checkpointer: PipelineCheckpointer = field(init=False)
    rootid = "Root"

    def __attrs_post_init__(self):
        """
        Initialize the pipeline after all attributes have been set.

        This method serves as the main entry point for setting up the pipeline,
        handling both new runs and continuations from a checkpoint. It discovers
        input systems and their initial artifacts, sets up the root node of the
        workflow graph, and initializes the command executor.
        """
        self.checkpointer = PipelineCheckpointer(
            self.name,
            tracked_obj=self,
            checkpoint_path=self.checkpoint_path,
            ignore_checkpoint=self.ignore_checkpoint,
            force_restart=self.force_restart,
        )

        self.logger = set_logger(
            Path(self.cwd, f"{self.name}.log"),
            logging_level=self.logging_level,
            filemode="w" if self.checkpointer.new_run else "a",
        )
        # Get the root dir system and the starting artifacts to pipe them through the root node.
        starting_artifacts, self.systems = self._walk_main_dir()
        root_artifacts = dict()
        # noinspection PyTypeChecker
        self.root = self._setup_new_node(WorkNodeDummy(wnid=self.rootid))
        for sysname, syspath in self.systems.items():
            self.logger.debug(f"Loading system {sysname}")
            self.root.run(starting_artifacts[sysname], sysname=sysname, cwd=syspath)
            root_artifacts[sysname] = self.root.output_artifacts
        # load them into the artifact tree's root.
        self.artifacts[self.rootid] = BatchArtifacts(self.rootid, root_artifacts)
        self.flow_ids.add(self.rootid)

        if not self.command.initialized:
            # If the command is not initialized, we need to initialize it with the root_dir
            self.command = self.command.replace(local_base_dir=self.cwd)

        if self.checkpointer.new_run:
            self.flow = nx.DiGraph(name="workflow")
            self.flow.add_node(self.root)
            self.leafs = [self.root]
        else:
            # TODO: add hashing to the checkpoint file.
            state = self.checkpointer.load(self.systems, self.logger)
            self.flow, self.leafs, self.artifacts, self.systems = (
                state["flow"],
                state["leafs"],
                state["artifacts"],
                state["systems"],
            )

    def _read_checkpoint(self, checkpoint_path: filepath_t, force_restart: bool) -> None:
        """
        Read and validate the workflow state from a checkpoint file.

        This method loads a previously saved pipeline state, including the
        workflow graph, artifacts, and system information. It then validates
        the state to ensure that all required files for completed nodes are
        present. Failed or canceled nodes are reset to a pending state to be
        re-run.

        Parameters
        ----------
        checkpoint_path : filepath_t
            The path to the checkpoint file.
        force_restart : bool
            If True, validation errors will be ignored, and the pipeline will
            attempt to continue. This can be useful for debugging but may lead
            to unexpected behavior.

        Raises
        ------
        InvalidPipeline
            If the checkpoint is found to be invalid and `force_restart` is False.
        """
        old_systems: dict[str, DirHandle] | None = None
        try:
            with open(checkpoint_path, "rb") as f:
                self.flow, self.artifacts, self.leafs, old_systems = pickle.load(f)
            self.new_run = False
        except FileNotFoundError:
            self.new_run = True
            return

        # Now, check if the systems in the checkpoint match the current systems.
        assert old_systems is not None, "Expected old_systems to be not None when validating checkpoint."
        set_old_systems = set(old_systems.keys())

        valid = True
        err_msg = ""
        is_root = True
        for node in nx.topological_sort(self.flow):
            if is_root:
                if node.id != self.rootid:
                    err_msg += f"Pipeline's root node id is {self.rootid}, but found {node.id}.\n"
                    valid = force_restart
                    break
                is_root = False
            if node.status in (WorkNodeStatus.FAILED, WorkNodeStatus.CANCELLED):
                node.status = WorkNodeStatus.PENDING
                continue
            elif node.status == WorkNodeStatus.COMPLETED:
                if wd := getattr(node, "work_dir", False):
                    if not wd.is_dir():
                        valid = force_restart
                        err_msg += f"WorkNode {node.id} has no work directory ({node.work_dir}).\n"
                        break
                    else:
                        valid = False
                        err_msg += f"WorkNode {node.id} has no work directory but is marked as completed?. Corrupted checkpoint file?"
                        break
                for _, art_list in node.output_artifacts.items():
                    for art in art_list:
                        if hasattr(node, "filepath"):
                            # artifact is file-based
                            if not art.filepath.is_file():
                                valid = False
                                err_msg += f"WorkNode {node.id} has no output artifact {art}.\n"
                                break

        for sysname in self.artifacts[self.rootid].keys():
            if sysname not in set_old_systems:
                self.logger.warning(f"Missing system in the current root dir: {sysname}")

        if not valid:
            err_msg += "Invalid Pipeline. Cannot continue from the checkpoint. Either set `force_restart=True`, or fix the project files."
            self.logger.error(err_msg)
            raise InvalidPipeline(err_msg)

        return

    def _walk_main_dir(self) -> tuple[BatchArtifacts, dict[str, DirHandle]]:
        """
        Discover and collect initial artifacts from system directories.

        This method scans the main working directory (`cwd`) for subdirectories,
        each representing a unique system to be simulated. It collects the initial
        set of artifacts (e.g., PDB files) from each system directory.

        Returns
        -------
        tuple[BatchArtifacts, dict[str, DirHandle]]
            A tuple containing a batch of the initial artifacts for all discovered
            systems and a dictionary mapping system names to their directory paths.
        """
        artifacts: dict[str, ArtifactContainer] = {}
        systems: dict[str, DirHandle] = {}
        for path_object in Path(self.cwd).iterdir():
            if path_object.is_dir():
                if path_object.name.startswith("allow_") or path_object.name.startswith("__"):
                    continue
                sys_artifacts: ArtifactContainer = self._add_system_dir(path_object)
                artifacts[sys_artifacts.id] = sys_artifacts
                systems[sys_artifacts.id] = DirHandle(path_object)

        return BatchArtifacts("Root", artifacts), systems

    def _add_system_dir(self, system_path: Path) -> ArtifactContainer:
        """
        Identify and register artifacts from a single system directory.

        This method scans a given system directory for files that match known
        artifact patterns (e.g., 'target_*.pdb', 'binder_*.sdf'). It creates
        and registers these files as the initial artifacts for the system.

        Parameters
        ----------
        system_path : Path
            The path to the system directory to be scanned.

        Returns
        -------
        ArtifactContainer
            A container holding all the artifacts discovered in the directory.

        Raises
        ------
        InvalidPipeline
            If the directory contains unrecognized files or an invalid combination
            of input files (e.g., multiple targets or binders).
        """
        has_complex: bool = False
        has_target: bool = False
        has_binder: bool = False
        artifacts: list[BaseArtifact] = []
        # The folder name is the system name.
        sysname = str(system_path.name)

        for file in Path(system_path).iterdir():
            if file.is_file():
                try:
                    # TODO: hacky. Can do better.
                    if file.name.startswith("target_"):
                        file_artifact = ArtifactRegistry.create_instance_by_filename(file, tags=(self.target,))
                    elif file.name.startswith("binder_"):
                        file_artifact = ArtifactRegistry.create_instance_by_filename(file, tags=(self.binder,))
                    elif file.name.startswith("complex_"):
                        file_artifact = ArtifactRegistry.create_instance_by_filename(
                            file, tags=(self.target, self.binder)
                        )
                    else:
                        file_artifact = ArtifactRegistry.create_instance_by_filename(file)

                    artifacts.append(file_artifact)
                    artifact_type = type(file_artifact)

                    if issubclass(artifact_type, BaseComplexStructureFile):
                        if has_complex:
                            raise InvalidPipeline(f"System dir {system_path} has multiple complexes.")
                        has_complex = True
                    if issubclass(artifact_type, TargetProteinPDB):
                        if has_target:
                            raise InvalidPipeline(f"System dir {system_path} has multiple targets.")
                        has_target = True
                    if issubclass(artifact_type, BinderLigandPDB) or issubclass(artifact_type, BinderLigandSmiles):
                        if has_binder:
                            raise InvalidPipeline(f"System dir {system_path} has multiple binders.")
                        has_binder = True
                except UnknownFileType:
                    raise InvalidPipeline(f"System dir {system_path} has an unrecognized file ({file}).")
                except UnknownArtifactError as e:
                    self.logger.debug(f"System dir {system_path} has an unrecognized file: {file} which caused {e}.")

        if self.free_md or has_complex or (has_target and has_binder):
            self.systems[sysname] = DirHandle(system_path)
            return ArtifactContainer(sysname, artifacts)
        else:
            raise InvalidPipeline(
                f"Invalid dir: {system_path}. "
                "Structures of target and binder (together or separate) are a prerequisite."
            )

    def run(self) -> None:
        """
        Launch the pipeline execution in a separate process.

        This method pickles the current pipeline state and uses the configured
        command (local or remote) to execute the `runflow` command-line
        interface, which then unpickles and runs the pipeline. This is the
        standard way to run a pipeline, as it ensures a clean execution
        environment.
        """
        other_pipeline = self.setup_new_pipeline(self.command.executor)
        # Pickle the modified pipeline
        pickle_fn = Path(self.cwd, "pipeline.pkl")
        with open(pickle_fn, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(other_pipeline, f)

        # Execute the runner script using the pipeline's command
        self.logger.info(
            f"Executing pipeline using {self.command.__class__.__name__} with {self.command.executor.__class__.__name__}"
        )
        self.command.run(
            ["runflow", str(pickle_fn.name)], cwd=self.cwd, logger=self.logger, force=self.force_restart, download=True
        )
        self.logger.info("Done Pipeline.run()")

    def launch(self) -> None:
        """
        Execute the pipeline directly in the current process.

        This method is primarily intended for debugging and testing purposes.
        For production runs, it is recommended to use the `run()` method to
        ensure a clean and isolated execution environment.
        """
        self.scheduler.launch(
            self.flow,
            self.root,
            systems=self.systems,
            cwd=Path(self.cwd),
            pipeline_artifacts=self.artifacts,
            logger=self.logger,
            checkpointer=self.checkpointer,
        )

    # def run(self) -> None:
    #     """
    #     Launches the pipeline execution.
    #
    #     If remote_commands are provided, it uses the DistributedRunner.
    #     Otherwise, it falls back to the original single-command execution.
    #     """
    #     if self.remote_commands:
    #         # New: Delegate to the DistributedRunner
    #         dist_runner = DistributedRunner(self)
    #         dist_runner.run()
    #     else:
    #         # Original logic for a single execution context
    #         other_pipeline = self.setup_new_pipeline(self.command.executor)
    #         pickle_path = self.cwd / "pipeline.pkl"
    #         with open(pickle_path, "wb") as f:
    #             pickle.dump(other_pipeline, f)
    #
    #         self.command.run(
    #             ["runflow", str(pickle_path)], cwd=self.cwd, logger=self.logger, force=self.force_restart, download=True
    #         )
    #         pickle_path.unlink(missing_ok=True)

    def setup_new_pipeline(self, executor: BaseExecutor) -> "Pipeline":
        """
        Prepare a deep copy of the pipeline for execution.

        This method creates a standalone, serializable copy of the pipeline
        that can be safely executed in a separate process. It ensures that the
        new pipeline will run locally by setting its command to `DefaultCommand`.

        For remote execution, it also adjusts the `cwd` and artifact file paths
        within the new pipeline to point to their expected locations on the
        remote server.

        Parameters
        ----------
        executor : BaseExecutor
            The executor from the original pipeline, used to determine if
            the execution is remote and to get the remote base directory.

        Returns
        -------
        Pipeline
            A new, deep-copied pipeline instance configured for execution.
        """
        other_pipeline = deepcopy(self)
        other_pipeline.command = DefaultCommand()

        # Now, all paths need fixing
        if isinstance(executor, RemoteExecutor):
            # Set the current working directory for the local pipeline to the remote base directory, bypassing
            other_pipeline.cwd = executor.remote_base_dir

            #
            other_pipeline.checkpoint_path = Path(other_pipeline.cwd, self.checkpoint_path.relative_to(self.cwd))

            # If the pipeline is being run remotely, we need to ensure that the all the absolute paths are within the
            # remote base directory.
            other_pipeline.systems = {
                sysname: Path(other_pipeline.cwd, Path(sysdir).relative_to(self.cwd))
                for sysname, sysdir in self.systems.items()
            }
            # If we're starting from a checkpoint, we need to ensure that the artifacts are also set to the remote base directory.
            for batch_artifacts in other_pipeline.artifacts.values():
                for artifact_container in batch_artifacts.values():
                    for artifacts in artifact_container.values():
                        for art in artifacts:
                            if hasattr(art, "filepath"):
                                art.change_base_dir(self.cwd, other_pipeline.cwd)

        return other_pipeline

    def _setup_new_node(self, new_worknode: BaseWorkNode) -> BaseWorkNode:
        """
        Prepare a new work node for inclusion in the pipeline.

        This method configures a new work node with the necessary pipeline-level
        information, such as the list of systems, the root directory, and the
        logging level. It also checks for ID conflicts to prevent duplicate
        nodes in the workflow.

        Parameters
        ----------
        new_worknode : BaseWorkNode
            The work node to be prepared.

        Returns
        -------
        BaseWorkNode
            The configured work node.

        Raises
        ------
        RuntimeError
            If a node with the same ID already exists in the pipeline.
        """
        if new_worknode.id in self.flow_ids:
            err_msg = f"{new_worknode=} already present. Pipeline can't hold WorkNodes with duplicated ids."
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)
        new_worknode.set_systems(tuple(self.systems.keys()))
        new_worknode.root_dir = self.cwd
        new_worknode.logging_level = self.logging_level
        new_worknode.logging_filemode = "w" if self.new_run else "a"

        return new_worknode

    def _check_edge(self, new_worknode: BaseWorkNode, old_worknode: BaseWorkNode) -> None:
        """
        Validate that an edge can be created between two nodes.

        This method ensures that the nodes being connected are valid and that
        the connection itself is logical (e.g., a node cannot be connected
        to itself).

        Parameters
        ----------
        new_worknode : BaseWorkNode
            The source node of the edge.
        old_worknode : BaseWorkNode
            The destination node of the edge.

        Raises
        ------
        RuntimeError
            If the destination node is not in the flow or if the source and
            destination nodes are the same.
        """
        if old_worknode not in self.flow.nodes:
            err_msg = f"{old_worknode=} not found in the Pipeline's flow. Cannot have disjoint graphs."
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)
        if old_worknode.id == new_worknode.id:
            err_msg = "Cannot append a WorkNode to itself."
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)

    def append_node(
        self, new_worknode: BaseWorkNode, old_worknodes: Sequence[BaseWorkNode] = tuple(), update_leafs: bool = True
    ) -> list[BaseWorkNode]:
        """
        Append a new work node to existing nodes in the workflow graph.

        This method adds a new node to the pipeline and connects it to one or
        more existing nodes. If no existing nodes are specified, the new node
        is connected to all current leaf nodes.

        Parameters
        ----------
        new_worknode : BaseWorkNode
            The new node to be added to the graph.
        old_worknodes : Sequence[BaseWorkNode], optional
            A sequence of existing nodes to connect the new node to. If empty,
            the new node will be connected to all current leaf nodes.
        update_leafs : bool, optional
            If True, the `old_worknodes` that are also leaf nodes will be removed from the leaf nodes.

        Returns
        -------
        set[BaseWorkNode]
            The new set of leaf nodes in the workflow graph.

        Raises
        ------
        RuntimeError
            If the new work node's ID already exists in the pipeline or if any
            of the specified `old_worknodes` are not in the flow.
        """
        if not self.nodes_are_new([new_worknode]):
            return self.leafs
        # noinspection PyUnreachableCode
        if not isinstance(old_worknodes, Iterable):
            old_worknodes = (old_worknodes,)
            # self.logger.debug(f"`append_node()`: Single `old_worknode` provided: {old_worknodes}.")
        leafs: set[BaseWorkNode] = set(self.leafs) if len(old_worknodes) == 0 else set(old_worknodes)
        new_worknode = self._setup_new_node(new_worknode)
        for node in leafs:
            self._check_edge(new_worknode, node)
            self.flow.add_edge(node, new_worknode)
        self.flow_ids.add(new_worknode.id)
        # Set up the new leaf nodes.
        if update_leafs:
            # Remove those that are connected to the `new_worknode`. They can't be leafs.
            set_leafs = set(self.leafs)
            set_leafs.difference_update(leafs)
            self.leafs = list(set_leafs)
        self.leafs.append(new_worknode)
        return self.leafs

    def nodes_are_new(self, nodes: Iterable[BaseWorkNode]) -> bool:
        common_nodes_ids: set[str] = set(n.id for n in nodes) & set(n.id for n in self.flow.nodes)
        if len(common_nodes_ids) != 0:
            if self.checkpointer.new_run:
                err_msg = (
                    f"WorkNodes already exist in the pipeline: {common_nodes_ids}. "
                    "Pipeline can't hold WorkNodes with duplicated ids."
                )
                self.logger.error(err_msg)
                raise RuntimeError(err_msg)
            else:
                self.logger.debug(
                    f"WorkNodes already exist in the pipeline: {common_nodes_ids}. "
                    "Assuming you want to continue from a checkpoint and doing nothing."
                )
                return False
        return True

    def append_flow(
        self, flow: BaseFlow, old_worknodes: Iterable[BaseWorkNode] = tuple(), update_leafs: bool = True
    ) -> list[BaseWorkNode]:
        """
        Append a pre-defined flow (a DAG of work nodes) to the pipeline.

        This method allows for the modular composition of complex workflows by
        appending a pre-defined sequence of work nodes (a `BaseFlow`) to the
        existing workflow graph.

        Parameters
        ----------
        flow : BaseFlow
            The flow instance containing the DAG of work nodes to be appended.
        old_worknodes : Union[BaseWorkNode, list[BaseWorkNode]]
            The existing node or nodes in the graph to connect the new flow to.
        update_leafs : bool
            If True, the `old_worknodes` that are also leaf nodes will be removed from the leaf nodes.

        Returns
        -------
        list[BaseWorkNode]
            A list of the exit nodes from the appended flow, which can be used
            for further chaining.

        Raises
        ------
        RuntimeError
            If any node from the flow already exists in the pipeline or if a
            specified `left_worknode` is not found.
        """

        if not self.nodes_are_new(flow.dag.nodes):
            return self.leafs

        # Init the leaf nodes from the current flow
        # noinspection PyUnreachableCode
        if not isinstance(old_worknodes, Iterable):
            old_worknodes = (old_worknodes,)
        leafs: set[BaseWorkNode] = set(self.leafs) if len(old_worknodes) == 0 else set(old_worknodes)

        # Set up each of the new nodes
        for node in flow.dag.nodes:
            self._setup_new_node(node)
            self.flow_ids.add(node.id)
        # Join the 2 graphs
        new_flow = nx.compose(self.flow, flow.dag)
        # _fuse_flows() may remove the root node from the current flow if it is a dummy node, so keep it for later
        backup_leafs = deepcopy(leafs)
        self._fuse_flows(leafs, flow.root, new_flow)
        for leaf_node in leafs:
            new_flow.add_edge(leaf_node, flow.root)

        self.flow = new_flow
        ########################### TODO ###########################
        ########### Can't we just do away with `old_wornodes` and force append_flow to append the new flow too all the
        ########### leafs and then set the new flow leaf as the whole pipeline leaf?
        # Set up the new leaf nodes.
        if update_leafs:
            # Remove those that are connected to the `new_worknode`. They can't be leafs.
            set_leafs = set(self.leafs)
            set_leafs.difference_update(backup_leafs)
            self.leafs = list(set_leafs)

        self.leafs.append(flow.leaf)
        ########################### ###########################
        return self.leafs

    def _fuse_flows(self, leafs: set[BaseWorkNode], root: BaseWorkNode, new_flow: nx.DiGraph) -> None:
        """
        Add edges between the pipeline leaf nodes and the root node of the incoming flow. If it's just dummy nodes
        on both ends, discard the dummy from the incoming flow.

        Parameters
        ----------
        leafs : set[BaseWorkNode]
            The set of leaf nodes that may or may not be just a dummy node.
        root : BaseWorkNode
            The dummy root node from the incoming flow.
        new_flow : nx.DiGraph
            The new flow to which the edges will be added.
        """
        if len(leafs) == 1:
            leaf_node = leafs.pop()
            if isinstance(leaf_node, WorkNodeDummy):
                self.logger.info(f"Fusing dummy {leaf_node} into {root.id}")
                for successor in new_flow.successors(root):
                    new_flow.add_edge(leaf_node, successor)
                new_flow.remove_node(root)
                return
            else:
                new_flow.add_edge(leaf_node, root)
                return
        for leaf_node in leafs:
            new_flow.add_edge(leaf_node, root)

    def add_edge(self, left_worknode: BaseWorkNode, right_worknode: BaseWorkNode) -> BaseWorkNode:
        """
        Add a directed edge between two existing nodes in the workflow.

        This method allows for the creation of more complex, non-linear
        workflows by adding explicit dependencies between nodes that are
        already part of the graph.

        Parameters
        ----------
        left_worknode : BaseWorkNode
            The source node for the edge.
        right_worknode : BaseWorkNode
            The destination node for the edge.

        Returns
        -------
        BaseWorkNode
            The destination work node.

        Raises
        ------
        RuntimeError
            If either of the nodes is not already in the flow.
        """
        if left_worknode.id in self.flow_ids and right_worknode.id in self.flow_ids:
            self.flow.add_edge(left_worknode, right_worknode)
        else:
            err_msg = (
                f"Both {left_worknode=} and {right_worknode=} have to be present in the Pipeline's flow to add an edge."
                " Use `append_node()` instead to add a new node to the flow."
            )
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)

        if left_worknode.id in self.leafs:
            # If the left_worknode is a leaf, it can't be a leaf anymore.
            self.leafs.remove(left_worknode)
        return right_worknode

    def get_node_map(self) -> dict[str, BaseWorkNode]:
        """
        Create a mapping of work node IDs to their corresponding work node instances.

        Useful for checking what the current flow looks like.

        Returns
        -------
        dict[str, BaseWorkNode]
            A dictionary mapping work node IDs to their instances.
        """
        return {node.id: node for node in self.flow.nodes}

    @staticmethod
    def get_amber_version(logger: logging.Logger) -> None:
        """
        Log the version of the pmemd execution engine.

        This function checks for the AMBERHOME environment variable, which is
        standard in AmberTools installations. It then attempts to get the version
        number by running the pmemd command.

        Parameters
        ----------
        logger : logging.Logger
            The logger to use for logging messages.

        Raises
        ------
        EnvironmentError
            If the AMBERHOME environment variable is not set.
        """
        amber_home = os.environ.get("AMBERHOME")
        if not amber_home:
            logger.warning("The AMBERHOME environment variable is not set. Make sure you know what you're doing.")
        else:
            for engine in ("pmemd ", "pmemd.cuda", "pmemd.cuda.MPI"):
                p = sp.run(f"{engine} --version", stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=True)
                try:
                    match = re.search(r"\d+\.\d+", p.stdout.strip())
                    version = float(match.group(0))
                    logger.info(f"Found {engine=} with {version=}")
                except (ValueError, AttributeError):
                    logger.warning(f"Could not find a version number for '{engine}'")

    # noinspection PyUnresolvedReferences
    @force_restart.validator
    def _check_ignore_checkpoint(self, _, value):
        """
        Validate that `force_restart` and `ignore_checkpoint` are not both set to True.

        Parameters
        ----------
        _
            The attribute being validated (unused).
        value : bool
            The value of `force_restart`.

        Raises
        ------
        ValueError
            If both `force_restart` and `ignore_checkpoint` are True.
        """
        if value is True and self.ignore_checkpoint is True:
            raise ValueError("Cannot set `force_restart=True` and `ignore_checkpoint=True` simultaneously.")

    @staticmethod
    def clean(checkpoint_path) -> None:
        """
        Remove the checkpoint file.

        Parameters
        ----------
        checkpoint_path : Path
            The path to the checkpoint file to be removed.
        """
        checkpoint_path.unlink()

    # noinspection PyUnresolvedReferences
    @target.validator
    def _prot_or_rdname(self, attribute, value: str):
        """
        Validate that the 'target' attribute is either 'protein' or 'na'.

        Parameters
        ----------
        attribute
            The attribute being validated (unused).
        value : str
            The value of the 'target' attribute.

        Raises
        ------
        RuntimeError
            If the value is not 'protein' or 'na'.
        """
        if value != "protein" and value != "na":
            raise RuntimeError(f"{attribute} must be 'protein' or 'na'")

    def __getstate__(self) -> dict:
        """
        Customize the pickling process for the Pipeline class.

        This method excludes the unpicklable 'logger' attribute from the
        state that is saved during pickling. The rest of the attributes
        are handled automatically by the `attrs` library.

        Returns
        -------
        dict
            A dictionary representing the state of the object to be pickled.
        """
        # Remove the logger and `__weakref__`  from the state to avoid pickling issues
        # noinspection PyUnresolvedReferences
        state = {
            slot: getattr(self, slot) for slot in self.__class__.__slots__ if slot not in ("logger", "__weakref__")
        }
        return state

    def __setstate__(self, state: dict):
        """
        Customize the unpickling process for the Pipeline class.

        This method re-initializes the logger after all other attributes have
        been restored from the pickled state. This ensures that the pipeline
        can continue logging correctly after being unpickled.

        Parameters
        ----------
        state : dict
            A dictionary representing the pickled state of the object.
        """
        # Manually set the attributes from the state dictionary
        for key, value in state.items():
            super().__setattr__(key, value)

        # Re-create the logger instance, ensuring it appends to the existing log file
        self.logger = set_logger(
            Path(self.cwd, f"{self.name}.log"),
            logging_level=self.logging_level,
            filemode="a",  # Always append ('a') to the log file from a pickled instance
        )
